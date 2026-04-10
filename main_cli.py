import json
import sys
import io
from ai_agent.graph import app_graph
from mcp_server.dispatcher import dispatch_tool

# Đảm bảo Terminal local xử lý tốt tiếng Việt
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
            "intent": "",
            "plan": {},
            "raw_log": ""
        }

        print("\n[System] Đang đẩy yêu cầu qua AI Agent Layer...")

        try:
            # Chạy đồ thị LangGraph
            result_state = app_graph.invoke(initial_state)

            # Trích xuất bản kế hoạch an toàn
            plan_data = result_state.get("plan", {})

            # Nếu AI trả về chuỗi JSON thay vì dict (phòng hờ Hallucination)
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
            for action in plan_output:
                tool_name = action.get("tool_name")
                # Đã khớp key 'tool_arguments' với Pydantic ở Node 2
                args = action.get("tool_arguments", {})

                print(f"\n[Step {action.get('step')}] {action.get('action_description')}")
                print(f"[Executor] Gọi Dispatcher: '{tool_name}'")

                # Gọi hàm điều phối
                tool_result = dispatch_tool(tool_name, args)

                # In kết quả
                print("--- KẾT QUẢ THỰC THI ---")
                status = tool_result.get('status', 'ERROR').upper()
                print(f"Trạng thái: {status}")

                if status == "SUCCESS":
                    print(f"Thời gian: {tool_result.get('execution_time', 0)}s")
                    # Chỉ in 10 dòng cuối của log để tránh tràn màn hình
                    logs = tool_result.get('raw_log', '').split('\n')
                    print("Log (10 dòng cuối):")
                    print('\n'.join(logs[-10:]))
                else:
                    print(f"Lỗi: {tool_result.get('raw_log')}")

        except Exception as e:
            print(f"[Lỗi Hệ Thống]: {str(e)}")

        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    run_cli()
