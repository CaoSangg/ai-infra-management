import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from ai_agent.agent_setup import main_agent
from ai_agent.prompts.planner_prompts import NODE_2_SYSTEM_PROMPT
from ai_agent.nodes.node1_intent import AgentState

# Định nghĩa Pydantic Model
class ToolCall(BaseModel):
    step: int = Field(description="Số thứ tự bước thực hiện")
    action_description: str = Field(description="Mô tả hành động")
    tool_name: str = Field(description="Tên của tool cần gọi")
    tool_arguments: Dict[str, Any] = Field(description="Các tham số truyền vào tool")

class PlanOutput(BaseModel):
    plan: List[ToolCall] = Field(description="Danh sách các hành động/tool cần thực thi")

# Lập kế hoạch dựa trên Intent từ Node 1
def generate_plan(state: AgentState) -> dict:

    raw_intent = state.get("intent", "")

    # Xử lý nếu Node 1 trả về chuỗi JSON (String) thì parse lấy intent_summary cho sạch
    if isinstance(raw_intent, str) and "{" in raw_intent:
        try:
            intent_data = json.loads(raw_intent)
            intent_text = intent_data.get("intent_summary", raw_intent)
        except:
            intent_text = raw_intent
    else:
        intent_text = raw_intent

    print(f"[Node 2] Ý định đã nhận: {intent_text}")

    # Tool Schema
    mock_tool_descriptions = """
    [
      {
        "tool_name": "run_ansible_playbook",
        "description": "Dùng để cài đặt phần mềm, cấu hình OS Linux.",
        "parameters": {
          "playbook_name": "string (Tên file playbook)",
          "extra_vars": "object (Các biến môi trường)"
        }
      },
      {
        "tool_name": "provision_aws_infrastructure",
        "description": "Dùng để quản lý vòng đời hạ tầng AWS (EC2, S3...).",
        "parameters": {
          "action": "string (BẮT BUỘC. Chỉ chọn 'apply' để tạo/sửa, hoặc 'destroy' để xóa tài nguyên)",
          "resource_type": "string (VD: 'ec2')",
          "config": "object (BẮT BUỘC chứa ami_id, instance_type)"
        }
      }
    ]
    """

    system_prompt = NODE_2_SYSTEM_PROMPT.format(tool_descriptions=mock_tool_descriptions)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Ý định của quản trị viên: {intent_text}")
    ]

    # Sử dụng structured_output để ép AI trả về object đúng chuẩn Pydantic
    structured_llm = main_agent.with_structured_output(PlanOutput)

    try:
        response = structured_llm.invoke(messages)
        # Chuyển đổi Pydantic sang Dict
        plan_dict = response.model_dump()
        print("[Node 2] Kế hoạch đã được lập thành công!")
        return {"plan": plan_dict}
    except Exception as e:
        print(f"[Node 2 Error] Không thể lập kế hoạch: {e}")
        return {"plan": {"plan": []}}
