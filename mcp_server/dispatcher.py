import os
import json
from mcp_server.tools.terraform_tool import provision_aws_infrastructure
from tool_executor.wrapper import SanitizationWrapper
from mcp_server.tools.ansible_tool import execute_ansible_playbook
from mcp_server.tools.state_fetcher import fetch_actual_state

# Phân luồng chạy tool
def dispatch_tool(tool_name: str, tool_args: dict) -> dict:
    print(f"[Dispatcher] Nhận yêu cầu chạy tool: {tool_name}")

    # Ansible
    if tool_name == "run_ansible_playbook":
        playbook_name = tool_args.get("playbook_name")
        extra_vars = tool_args.get("extra_vars", {})

        return execute_ansible_playbook(playbook_name, extra_vars)

    # Terraform
    elif tool_name == "provision_aws_infrastructure":

        action = tool_args.get("action", "apply")

        # Render Terraform từ Jinja2
        render_result = provision_aws_infrastructure(
            resource_type=tool_args.get("resource_type"),
            config=tool_args.get("config")
        )

        if render_result["status"] == "error":
            return render_result

        # Execute Terraform qua wrapper
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        environments_dir = os.path.join(
            base_dir, 'tool_executor', 'terraform', 'environments'
        )

        wrapper = SanitizationWrapper(target_dir=environments_dir)
        exec_result = wrapper.execute_terraform(action=action)

        return {
            "status": "success" if exec_result["status_code"] == 0 else "error",
            "status_code": exec_result["status_code"],
            "raw_log": exec_result["clean_log"],
            "execution_time": exec_result.get("execution_time", 0)
        }

    # Fetch trạng thái hiện tại
    elif tool_name == "fetch_actual_state":
        resource_type = tool_args.get("resource_type", "ec2")
        print(f"[Dispatcher] Đang quét trạng thái tài nguyên: {resource_type.upper()}...")
        result = fetch_actual_state(resource_type=resource_type)

        if result["status"] == "success":
            state_json_str = json.dumps(result.get("actual_state"), indent=2, ensure_ascii=False)
            return {
                "status": "success",
                "status_code": 0,
                "raw_log": f"KẾT QUẢ QUÉT HẠ TẦNG:\n{state_json_str}",
                "execution_time": 0
            }
        else:
            return {
                "status": "error",
                "status_code": 500,
                "raw_log": result.get("message", "Lỗi không xác định khi quét hạ tầng.")
            }

    # Tool khác chưa thêm
    else:
        return {
            "status": "error",
            "status_code": 404,
            "raw_log": f"Tool '{tool_name}' không tồn tại trong hệ thống."
        }
