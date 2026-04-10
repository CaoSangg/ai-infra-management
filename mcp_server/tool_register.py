import mcp.types as types

# Khai báo các tool của MCP Server
def get_available_tools() -> list[types.Tool]:

    return [
	# Ansible
        types.Tool(
            name="run_ansible_playbook",
            description="Dùng để thực thi cấu hình hệ thống trên Linux bằng Ansible.",
            inputSchema={
                "type": "object",
                "properties": {
                    "playbook_name": {
                        "type": "string",
                        "description": "Tên file playbook .yml tĩnh nằm trên máy ảo Layer 5"
                    },
                    "extra_vars": {
                        "type": "object",
                        "description": "Các biến cấu hình bổ sung (vars)"
                    }
                },
                "required": ["playbook_name"]
            }
        )

	# Terraform
	types.Tool(
            name="provision_aws_infrastructure",
            description="Dùng để tạo, cập nhật hoặc quản lý tài nguyên hạ tầng AWS (ví dụ: EC2). Hệ thống sẽ tự động dùng Terraform để thực thi. Cần truyền vào resource_type và config.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "Loại tài nguyên muốn tạo (hiện tại hỗ trợ: 'ec2')",
                        "enum": ["ec2"]
                    },
                    "config": {
                        "type": "object",
                        "description": "Cấu hình chi tiết cho tài nguyên",
                        "properties": {
                            "region": {"type": "string", "default": "ap-southeast-1"},
                            "ami_id": {"type": "string", "description": "Amazon Machine Image ID"},
                            "instance_type": {"type": "string", "description": "Loại máy ảo, ví dụ t2.micro, t3.medium"},
                            "instance_name": {"type": "string", "description": "Tên định danh cho máy ảo"},
                            "environment": {"type": "string", "enum": ["dev", "staging", "production"]}
                        },
                        "required": ["ami_id", "instance_type"]
                    }
                },
                "required": ["resource_type", "config"]
            }
        )

        # Monitor
        types.Tool(
            name="fetch_actual_state",
            description="Dùng để lấy trạng thái thực tế (Actual State) của các tài nguyên hạ tầng đang chạy (ví dụ: lấy IP public, ID, trạng thái running của máy ảo EC2). Rất hữu ích để AI tự động kiểm chứng xem máy đã thực sự được tạo/xóa thành công chưa.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "Loại tài nguyên muốn quét (hiện tại hỗ trợ: 'ec2')",
                        "default": "ec2"
                    }
                }
            }
        )

    ]

