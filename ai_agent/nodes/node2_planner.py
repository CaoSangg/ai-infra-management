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
    tool_arguments: Dict[str, Any] = Field(description="Các tham số truyền vào tool. Không bắt buộc key nào, tùy thuộc vào tool_name.")

class PlanOutput(BaseModel):
    plan: List[ToolCall] = Field(description="Danh sách các hành động/tool cần thực thi")

def generate_plan(state: AgentState) -> dict:
    from langchain_core.messages import SystemMessage, HumanMessage
    import json

    # 1. Lấy Intent từ Node 1 (Giữ nguyên JSON)
    intent_json_string = state.get("intent", "")

    # 2. Lấy Raw User Input (Câu gốc của Admin)
    # ĐỔI THÀNH "user_prompt" ĐỂ KHỚP VỚI MAIN_CLI
    user_input = state.get("user_prompt", "") 
    
    if not user_input and state.get("messages"):
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                user_input = msg.content
                break

    print(f"[Node 2] Intent JSON: {intent_json_string}")
    print(f"[Node 2] Raw Input: {user_input}")

    # 3. Tool Schema
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
        "description": "Dùng để tạo hoặc quản lý tài nguyên AWS (network, ec2, s3, iam).",
        "parameters": {
          "action": "string (BẮT BUỘC. Chọn 'apply' để tạo/sửa, 'destroy' để xóa)",
          "resource_type": "string (BẮT BUỘC. Phải chọn 'network', 'ec2', 's3' hoặc 'iam')",
          "config": "object (Nếu ec2 CÓ THỂ DÙNG: ami_id, instance_type, instance_name, target_subnet_id. Nếu network: vpc_cidr, public_subnet_cidr, private_subnet_cidr)"
        }
      }
    ]
    """

    system_prompt = NODE_2_SYSTEM_PROMPT.format(tool_descriptions=mock_tool_descriptions)

    # 4. Truyền cả Intent JSON và User Input vào HumanMessage
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""
[PARSED_INTENT_JSON]
{intent_json_string}

[RAW_USER_INPUT]
{user_input}
""")
    ]

    # Sử dụng structured_output để ép AI trả về object đúng chuẩn Pydantic
    structured_llm = main_agent.with_structured_output(PlanOutput)
    
    try:
        response = structured_llm.invoke(messages)
        plan_dict = response.model_dump()
        print("[Node 2] Kế hoạch đã được lập thành công!")
        return {"plan": plan_dict}
    except Exception as e:
        print(f"[Node 2 Error] Không thể lập kế hoạch: {e}")
        return {"plan": {"plan": []}}
