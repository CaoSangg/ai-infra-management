# test_node2.py

from layer2_ai_agent.nodes.node2_planner import generate_plan, AgentState
import json

def run_test():
    print("=== BẮT ĐẦU TEST NODE 2 ===")
    
    # Giả lập State đã được xử lý qua Node 1
    mock_state: AgentState = {
        "user_prompt": "",
        "intent": "Hệ thống hiểu bạn muốn cài đặt Nginx lên server Ubuntu.",
        "plan": {},
        "raw_log": ""
    }
    
    print(f"Ý định đầu vào: '{mock_state['intent']}'\n")
    
    # Gọi Node 2
    result = generate_plan(mock_state)
    
    print("\n=== KẾT QUẢ TRẢ VỀ TỪ NODE 2 (JSON) ===")
    # In ra dưới dạng JSON format cho dễ nhìn
    print(json.dumps(result["plan"], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run_test()
