import mcp.types as types

# Khai báo các tool của MCP Server
def get_available_tools() -> list[types.Tool]:

    return [
	# Ansible
        types.Tool(
            name="execute_ansible_playbook",
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
        ),

	# Terraform
        types.Tool(
            name="provision_aws_infrastructure",
            description="Dùng để tạo, cập nhật hoặc quản lý tài nguyên AWS. QUAN TRỌNG: Phải tạo 'network' trước, sau đó lấy Output ID truyền vào 'ec2'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "Loại tài nguyên muốn tạo.",
                        "enum": ["network", "iam", "ec2", "s3"] 
                    },
                    "config": {
                        "type": "object",
                        "description": "Cấu hình chi tiết cho tài nguyên. \n- Với 'network': có thể truyền vpc_cidr, public_subnet_cidr, private_subnet_cidr.\n- Với 'ec2': BẮT BUỘC có ami_id, instance_type. Nếu muốn gắn vào mạng riêng, truyền thêm target_subnet_id và security_group_id.",
                        "properties": {
                            "region": {"type": "string", "default": "ap-southeast-1"},
                            "ami_id": {"type": "string", "description": "ID của hệ điều hành (Chỉ dùng cho ec2)"},
                            "instance_type": {"type": "string", "description": "Loại máy ảo (Chỉ dùng cho ec2)"},
                            "instance_name": {"type": "string", "description": "Tên tài nguyên"},
                            "environment": {"type": "string", "enum": ["dev", "staging", "production"]},
                            "vpc_cidr": {"type": "string", "description": "Dải IP cho VPC (Chỉ dùng cho network)"},
                            "public_subnet_cidr": {"type": "string", "description": "Dải IP cho Public Subnet (Chỉ dùng cho network)"},
                            "private_subnet_cidr": {"type": "string", "description": "Dải IP cho Private Subnet (Chỉ dùng cho network)"},
                            "target_subnet_id": {"type": "string", "description": "ID của Subnet (Public hoặc Private) để gắn tài nguyên vào"},
                            "security_group_id": {"type": "string", "description": "ID của Security Group để gắn tài nguyên vào"}
                        }
                    }
                },
                "required": ["resource_type", "config"]
            }
        ),

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

