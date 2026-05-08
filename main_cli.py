import json
import sys
import time
import io
import re
from ai_agent.graph import app_graph
from mcp_server.dispatcher import dispatch_tool

# Terminal local xử lý tiếng Việt
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_cli():
    print("=== HỆ THỐNG QUẢN TRỊ HẠ TẦNG THÔNG MINH ===")
    print("Gõ 'exit' hoặc 'quit' để thoát.\n")

    while True:
        try:
            user_input = input("Admin Prompt >> ")
        except EOFError:
            break

        if user_input.lower() in ['exit', 'quit']:
            print("Đang thoát hệ thống...")
            break

        if not user_input.strip():
            continue

        initial_state = {
            "user_prompt": user_input,
            "raw_input": user_input,   
            "raw_user_input": user_input,
            "intent": "",
            "plan": {},
            "raw_log": ""
        }

        print("\n[System] Đang đẩy yêu cầu qua AI Agent Layer...")

        try:
            # Chạy đồ thị LangGraph
            result_state = app_graph.invoke(initial_state)

            # Trích xuất plan an toàn
            plan_data = result_state.get("plan", {})

            # Xư lý nếu AI trả về chuỗi JSON thay vì dict (để phòng hờ Hallucination)
            if isinstance(plan_data, str):
                plan_data = json.loads(plan_data)

            plan_output = plan_data.get("plan", [])

            if not plan_output:
                print("[Thông báo] AI không tìm thấy hành động nào phù hợp cho yêu cầu này.")
                continue

            print("\n=== KẾT QUẢ LẬP KẾ HOẠCH ===")
            print(json.dumps(plan_output, indent=2, ensure_ascii=False))

            print("CẢNH BÁO PHÊ DUYỆT \n")
            print("AI đã lập xong kế hoạch thay đổi hạ tầng thực tế.")
            approval = input("Bạn có đồng ý thực thi kế hoạch này không? (y/n/c - yes/no/cancel): ").strip().lower()

            if approval not in ['y', 'yes']:
                print("[System] Đã hủy quá trình thực thi. Hạ tầng được giữ nguyên.")
                print("-------------------------------------------------\n")
                continue # Quay lại vòng lặp chờ lệnh mới

            print("[Node 3] Quản trị viên đã phê duyệt. Cấp quyền cho Dispatcher...")
            print("!"*50 + "\n")

            # Thực thi qua Layer 3
            print("\n[System] Bắt đầu gọi xuống Layer 3 (MCP Dispatcher)...")
            
            # Bộ nhớ tạm để truyền IP 
            shared_vars = {} 

            for action in plan_output:
                tool_name = action.get("tool_name")
                args = action.get("tool_arguments", {})

                print(f"\n[Step {action.get('step')}] {action.get('action_description')}")

                # GUARDRAIL
                # Ép đổi tên tool nếu AI bị "ảo giác" 
                if tool_name == "run_ansible_playbook":
                    tool_name = "execute_ansible_playbook"
                    
                # Lôi tham số ra ngoài nếu AI lỡ nhét nó vào trong extra_vars
                if "extra_vars" in args and isinstance(args["extra_vars"], dict):
                    if "public_ip" in args["extra_vars"]:
                        args["public_ip"] = args["extra_vars"].pop("public_ip")
                    if "instance_name" in args["extra_vars"]:
                        args["instance_name"] = args["extra_vars"].pop("instance_name")
                    if "bastion_ip" in args["extra_vars"]:
                        args["bastion_ip"] = args["extra_vars"].pop("bastion_ip")
           
                # Logic Inject: tìm và tráo IP cho Ansible 
                if tool_name == "execute_ansible_playbook":
                    instance_name = args.get("instance_name", "")
                    safe_name = instance_name.replace("-", "_")
                    target_ip_req = args.get("public_ip")
                    
                    # 1. Tìm IP máy target 
                    if target_ip_req in ["AUTO_FILL", "AUTO_FILL_PRIVATE"]:
                        print(f"[State Fetcher] Đang tìm IP đích của máy '{instance_name}'...")
                        ip_found = None
                        is_private = (target_ip_req == "AUTO_FILL_PRIVATE")
                        ip_key = f"private_ip_{safe_name}" if is_private else f"public_ip_{safe_name}"
                        
                        # Thử bộ nhớ tạm
                        if ip_key in shared_vars:
                            ip_found = shared_vars[ip_key]
                            print(f"[State Injector] Thấy IP từ bộ nhớ: {ip_found}")
                        
                        # Thử AWS State
                        if not ip_found:
                            from mcp_server.tools.state_fetcher import fetch_actual_state
                            state_result = fetch_actual_state(resource_type="ec2")
                            if state_result.get("status") == "success":
                                for res in state_result["actual_state"]["resources"]:
                                    if instance_name == res.get("tags", {}).get("Name", "") or safe_name == res.get("name", ""):
                                        ip_found = res.get("private_ip") if is_private else res.get("public_ip")
                                        if ip_found:
                                            print(f"[State Fetcher] Lấy được IP từ AWS: {ip_found}")
                                        break
                        
                        if ip_found:
                            args["public_ip"] = ip_found # Ghi đè vào args cho Ansible chạy
                            if ip_key in shared_vars:
                                print("[Hệ thống] Đang chờ 20 giây để EC2 khởi động dịch vụ SSH...")
                                time.sleep(20)
                        else:
                            print(f"[Lỗi] Không tìm thấy IP đích cho '{instance_name}'.")
                            break
                            
                    # 2. Tìm IP bastion
                    if args.get("bastion_ip") == "AUTO_FILL_BASTION":
                        print(f"[State Fetcher] Đang tìm một máy Public làm trạm gác...")
                        bastion_found = None
                        
                        # Ưu tiên lấy trạm gác từ những máy vừa tạo
                        for k, v in shared_vars.items():
                            if k.startswith("public_ip_"):
                                bastion_found = v
                                print(f"[State Injector] Đã chọn Bastion IP từ bộ nhớ: {bastion_found}")
                                break
                        
                        # Nếu không có, quét trên AWS xem có máy public nào không
                        if not bastion_found:
                            from mcp_server.tools.state_fetcher import fetch_actual_state
                            state_result = fetch_actual_state(resource_type="ec2")
                            if state_result.get("status") == "success":
                                for res in state_result["actual_state"]["resources"]:
                                    if res.get("public_ip"):
                                        bastion_found = res.get("public_ip")
                                        print(f"[State Fetcher] Đã chọn Bastion IP từ AWS: {bastion_found}")
                                        break
                        
                        if bastion_found:
                            args["bastion_ip"] = bastion_found
                        else:
                            print("[Lỗi] Mạng Private nhưng không tìm thấy máy Bastion/Public nào để nhảy qua!")
                            break

                print(f"[Executor] Gọi Dispatcher: '{tool_name}'")

                # Gọi hàm điều phối
                tool_result = dispatch_tool(tool_name, args)
                status = tool_result.get('status', 'ERROR').upper()

                # Logic Extract: Lấy IP từ log Terraform (Lấy cả Public lẫn Private)
                if status == "SUCCESS" and tool_name == "provision_aws_infrastructure":
                    log_output = tool_result.get('raw_log', '')
                    matches = re.findall(r'((?:public|private)_ip_[a-zA-Z0-9_]+)\s*=\s*"([^"]+)"', log_output)
                    for key, ip in matches:
                        shared_vars[key] = ip
                        print(f"[State Extractor] Đã lưu vào bộ nhớ: {key} = {ip}")

                # In kết quả
                print("--- KẾT QUẢ THỰC THI ---")
                print(f"Trạng thái: {status}")

                if status == "SUCCESS":
                    print(f"Thời gian: {tool_result.get('execution_time', 0)}s")
                    logs = tool_result.get('raw_log', '').split('\n')
                    print("Log (10 dòng cuối):")
                    print('\n'.join(logs[-10:]))
                else:
                    # Ngắt chuỗi nếu 1 bước bị lỗi
                    print(f"Lỗi: {tool_result.get('raw_log')}")
                    print(f"[Executor] Thất bại ở Step {action.get('step')}. Dừng toàn bộ kế hoạch!")
                    break 

        except Exception as e:
            print(f"[Lỗi Hệ Thống]: {str(e)}")

        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    run_cli()
