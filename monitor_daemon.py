import time
import json
from mcp_server.tools.state_fetcher import fetch_actual_state
from ai_agent.graph import app_graph
from mcp_server.dispatcher import dispatch_tool

# Hàm monitor
def trigger_ai_healing():

    print("\n[CẢNH BÁO] Phát hiện hạ tầng bị mất! Kích hoạt quy trình Tự phục hồi...")

    # Prompt khẩn cấp
    emergency_prompt = "Máy chủ EC2 đã bị sập hoặc mất tích. Hãy khẩn cấp tạo lại một máy ảo EC2 t2.micro để phục hồi dịch vụ."

    initial_state = {
        "user_prompt": emergency_prompt,
        "intent": {},
        "plan": {},
        "raw_log": ""
    }

    try:
        print("[System] Đang đẩy lệnh cấp cứu cho AI Agent...")
        result_state = app_graph.invoke(initial_state)

        plan_data = result_state.get("plan", {})
        if isinstance(plan_data, str):
            import re
            plan_data = json.loads(re.sub(r"```json|```", "", plan_data))

        plan_list = plan_data.get("plan", [])

        if not plan_list:
            print("[Lỗi] AI không thể lập kế hoạch phục hồi!")
            return

        print("\n=== AI ĐÃ LẬP KẾ HOẠCH TỰ PHỤC HỒI ===")
        print(json.dumps(plan_list, indent=2, ensure_ascii=False))

        # Thực thi kế hoạch cứu trợ
        for action in plan_list:
            tool = action.get("tool_name")
            args = action.get("tool_arguments", {})
            print(f"\n[Thực thi] {action.get('action_description')}")

            res = dispatch_tool(tool, args)
            print(f"-> Kết quả: {res.get('status').upper()}")

    except Exception as e:
        print(f"[Lỗi Hệ Thống Phục Hồi]: {e}")

def run_monitor():
    print("=== HỆ THỐNG GIÁM SÁT HẠ TẦNG (NODE 7) ===")
    print("Đang quét trạng thái định kỳ. Bấm Ctrl+C để dừng.\n")

    try:
        while True:
            print("[Monitor] Đang quét kiểm tra (Heartbeat)...")
            state_data = fetch_actual_state(resource_type="ec2")

            # Lấy danh sách tài nguyên
            resources = state_data.get("actual_state", {}).get("resources", [])

            # Kiểm tra xem có máy ảo nào đang sống không
            is_healthy = False
            for res in resources:
                if res.get("instance_state") == "running":
                    is_healthy = True
                    break

            if is_healthy:
                print("[Monitor] Hạ tầng đang hoạt động ổn định")
                time.sleep(10)
            else:
                # Nếu không có máy nào running -> Kích hoạt Healing
                trigger_ai_healing()
                print("\n[Monitor] Đã phục hồi xong! Tiếp tục theo dõi...")
                time.sleep(10)
                
    except KeyboardInterrupt:
        print("\nĐã tắt hệ thống giám sát.")

if __name__ == "__main__":
    run_monitor()
