# test_node1.py

from layer2_ai_agent.nodes.node1_intent import analyze_intent, AgentState

def run_test():
    print("=== BẮT ĐẦU TEST NODE 1 ===")
    
    # 1. Tạo một Mock State với câu lệnh giả lập từ Admin
    mock_state: AgentState = {
        "user_prompt": "Cài cho tôi cái nginx lên con server ubuntu nhé",
        "intent": "",
        "plan": {},
        "raw_log": ""
    }
    
    # 2. Gọi thẳng hàm của Node 1
    print(f"Câu lệnh đầu vào: '{mock_state['user_prompt']}'")
    result = analyze_intent(mock_state)
    
    # 3. In kết quả trả về để kiểm tra
    print("\n=== KẾT QUẢ TRẢ VỀ TỪ NODE 1 ===")
    print(result)

if __name__ == "__main__":
    run_test()
