import os
from jinja2 import Environment, FileSystemLoader

# Nhận input và sinh file main.tf từ templates
def provision_aws_infrastructure(resource_type: str, config: dict) -> dict:
    try:

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

        # Chọn template cho từng resource
        if resource_type == "ec2":
            template_file = 'ec2.tf.j2'
        else:
            return {"status": "error", "message": f"Unsupported resource_type: {resource_type}"}

        # Đọc template
        template = env.get_template(template_file)

        # Render template với dữ liệu config
        rendered_terraform_code = template.render(**config)

        # Ghi ra file main.tf
        output_path = os.path.join(output_dir, 'main.tf')
        with open(output_path, 'w') as f:
            f.write(rendered_terraform_code)

        return {
            "status": "success",
            "message": f"Đã render thành công file main.tf cho {resource_type}",
            "file_path": output_path
        }

    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi render Terraform: {str(e)}"}
