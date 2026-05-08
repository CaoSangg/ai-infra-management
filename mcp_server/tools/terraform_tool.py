import os
from jinja2 import Environment, FileSystemLoader

# Nhận input, sinh file .tf hoặc xóa file .tf
def provision_aws_infrastructure(resource_type: str, config: dict, action: str = "apply") -> dict:
    try:
        # Patch lỗi phổ biến của AI khi sinh JSON cho EC2
        if "ami" in config and "ami_id" not in config:
            config["ami_id"] = config["ami"]

        # Xác định đường dẫn thư mục
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        template_dir = os.path.join(base_dir, 'tool_executor', 'terraform', 'templates')
        output_dir = os.path.join(base_dir, 'tool_executor', 'terraform', 'environments')

        # Check để đảm bảo thư mục environments tồn tại
        os.makedirs(output_dir, exist_ok=True)

        # Setup Jinja2 Environment
        env = Environment(loader=FileSystemLoader(template_dir))

        # Khai báo Map
        resource_map = {
            "network": {
                "template": "vpc.tf.j2",
                "output_file": "01_network.tf" 
            },
            "iam": {
                "template": "iam.tf.j2",
                "output_file": "02_iam.tf"
            },
            "ec2": {
                "template": "ec2.tf.j2",
                "output_file": "03_ec2.tf"
            },
            "s3": {
                "template": "s3.tf.j2",
                "output_file": "04_s3.tf"
            }
        }

        # 1. Kiểm tra xem resource_type do AI chọn có hợp lệ không
        if resource_type not in resource_map:
            return {"status": "error", "message": f"Unsupported resource_type: {resource_type}. Available types: {list(resource_map.keys())}"}

        # Lấy thông tin cấu hình cho resource_type tương ứng
        mapping_info = resource_map[resource_type]
        template_file = mapping_info["template"]
        output_filename = mapping_info["output_file"]

        # Định tuyến tên file động
        if resource_type == "iam":
            safe_name = config.get("iam_name", "default_iam").replace("-", "_")
            output_filename = f"02_iam_{safe_name}.tf"
        elif resource_type == "ec2":
            safe_name = config.get("instance_name", "default_server").replace("-", "_")
            output_filename = f"03_ec2_{safe_name}.tf"
        elif resource_type == "s3":
            safe_name = config.get("bucket_name", "default_bucket").replace("-", "_")
            output_filename = f"04_s3_{safe_name}.tf"

        output_path = os.path.join(output_dir, output_filename)

        # ==================================================
        # XÓA TÀI NGUYÊN (DESTROY)
        # ==================================================
        if action == "destroy":
            if os.path.exists(output_path):
                os.remove(output_path)
                return {
                    "status": "success",
                    "message": f"Đã xóa file cấu hình {output_filename}. Hệ thống sẽ Apply để gỡ bỏ tài nguyên trên AWS.",
                    "file_path": output_path
                }
            else:
                return {
                    "status": "error",
                    "message": f"Không tìm thấy tài nguyên {output_filename} để xóa. Có thể nó chưa từng được tạo."
                }

        # ==================================================
        # TẠO / CẬP NHẬT TÀI NGUYÊN (APPLY)
        # ==================================================
        # Đọc và Render template bằng Jinja2
        template = env.get_template(template_file)
        
        # Truyền toàn bộ biến từ dict 'config' vào Jinja2 context
        rendered_terraform_code = template.render(**config)

        # Ghi ra file .tf riêng biệt
        with open(output_path, 'w') as f:
            f.write(rendered_terraform_code)

        return {
            "status": "success",
            "message": f"Đã render thành công cấu hình Terraform cho {resource_type}",
            "file_path": output_path
        }

    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi xử lý Terraform: {str(e)}"}
