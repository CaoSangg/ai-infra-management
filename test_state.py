from mcp_server.tools.state_fetcher import fetch_actual_state
import json

print("Đang quét check Actual State...")
result = fetch_actual_state(resource_type="ec2")

if result["status"] == "success":
    print("\n=== KẾT QUẢ QUÉT HẠ TẦNG ===")
    print(json.dumps(result["actual_state"], indent=2, ensure_ascii=False))
else:
    print(f"\n[LỖI] {result['message']}")
