import subprocess
import os
import json

# Chạy terraform show -json để lấy Actual State
def fetch_actual_state(resource_type: str = "ec2") -> dict:
    try:
        # Xác định đường dẫn thư mục environments chứa file tfstate
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        target_dir = os.path.join(base_dir, 'tool_executor', 'terraform', 'environments')

        if not os.path.exists(target_dir):
             return {"status": "error", "message": "Thư mục môi trường không tồn tại. Hạ tầng chưa được cấp phát."}

        # Gọi API AWS để cập nhật tfstate cho khớp với thực tế
        subprocess.run(
            "terraform apply -refresh-only -auto-approve",
            cwd=target_dir,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Chạy lệnh terraform show -json
        result = subprocess.run(
            "terraform show -json",
            cwd=target_dir,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            return {"status": "error", "message": f"Lỗi khi lấy state: {result.stderr}"}

        # Parse JSON từ Terraform
        tf_state = json.loads(result.stdout)

        # Trích xuất thông tin cần thiết dựa trên resource_type
        extracted_state = {"resources": []}

        # Đảm bảo file state có chứa dữ liệu tài nguyên
        if "values" in tf_state and "root_module" in tf_state["values"] and "resources" in tf_state["values"]["root_module"]:
            resources = tf_state["values"]["root_module"]["resources"]

            if resource_type == "ec2":
                for res in resources:
                    if res["type"] == "aws_instance":
                        values = res.get("values", {})
                        extracted_state["resources"].append({
                            "type": "ec2",
                            "name": res.get("name"),
                            "instance_id": values.get("id"),
                            "instance_state": values.get("instance_state"),
                            "public_ip": values.get("public_ip"),
                            "private_ip": values.get("private_ip"),
                            "tags": values.get("tags", {})
                        })

        return {
            "status": "success",
            "message": "Đã lấy Actual State thành công",
            "actual_state": extracted_state
        }

    except Exception as e:
        return {"status": "error", "message": f"Lỗi hệ thống khi fetch state: {str(e)}"}
