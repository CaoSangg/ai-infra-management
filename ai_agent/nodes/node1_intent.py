import json
import re
from typing import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage

from ai_agent.agent_setup import sub_agent
from ai_agent.prompts.intent_prompts import NODE_1_SYSTEM_PROMPT

# 1. Định nghĩa cấu trúc State
# Chuyển intent thành dict để đồng bộ dữ liệu chuẩn JSON cho toàn hệ thống
class AgentState(TypedDict):
    user_prompt: str
    intent: dict  # Đã nâng cấp từ str sang dict
    plan: dict
    raw_log: str

def analyze_intent(state: AgentState) -> dict:
    """
    Node 1: Phân tích ý định của người dùng và trả về kết quả dạng JSON.
    """
    user_prompt = state["user_prompt"]

    messages = [
        SystemMessage(content=NODE_1_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]

    print("[Node 1] Đang phân tích ý định bằng Agent phụ...")
    response = sub_agent.invoke(messages)

    raw_content = response.content

    # Bước 1: Trích xuất nội dung văn bản (xử lý cả trường hợp trả về list content blocks)
    if isinstance(raw_content, list):
        extracted_text = "".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in raw_content
        ).strip()
    else:
        extracted_text = str(raw_content).strip()

    # Bước 2: Dọn dẹp Markdown (loại bỏ các dấu ```json và ``` nếu AI tự thêm vào)
    # Đây là bước quan trọng để hàm json.loads không bị lỗi
    clean_json_str = re.sub(r"```json|```", "", extracted_text).strip()

    # Bước 3: Chuyển đổi chuỗi text thành Dictionary Python
    try:
        # Thử parse JSON
        intent_dict = json.loads(clean_json_str)
        print(f"[Node 1] Phân tích thành công. Ý định: {intent_dict.get('intent_summary')}")
    except Exception as e:
        # Fallback: Nếu AI trả về format không phải JSON, ta tự đóng gói nó vào dict
        print(f"[Node 1 Warning] AI trả về format lạ, đang thực hiện ép kiểu thủ công.")
        intent_dict = {
            "intent_summary": extracted_text,
            "is_risky": False,
            "extracted_entities": {
                "resource_target": "unknown",
                "action": "unknown"
            }
        }

    # Trả về kết quả là một Dictionary thực thụ
    return {"intent": intent_dict}
