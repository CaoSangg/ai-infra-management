import ansible_runner
import os
import glob

def execute_ansible_playbook(playbook_name: str, public_ip: str, instance_name: str, bastion_ip: str = None, extra_vars: dict = None) -> dict:
    """
    Thực thi file playbook bằng ansible-runner với cấu hình Dynamic Inventory.
    Hỗ trợ SSH ProxyJump xuyên qua Bastion Host nếu được cung cấp bastion_ip.
    """
    if extra_vars is None:
        extra_vars = {}

    # Xác định các thư mục làm việc 
    current_file = os.path.abspath(__file__)                  
    tools_dir = os.path.dirname(current_file)                   
    mcp_server_dir = os.path.dirname(tools_dir)                 
    root_dir = os.path.dirname(mcp_server_dir)                  

    work_dir = os.path.join(root_dir, 'tool_executor', 'ansible')
    terraform_env_dir = os.path.join(root_dir, 'tool_executor', 'terraform', 'environments')

    # Đường dẫn tới file khóa .pem của máy đích (Target Server) do Terraform vừa tạo
    target_key_path = os.path.join(terraform_env_dir, f"{instance_name}.pem")

    if not os.path.exists(target_key_path):
        return {
            "status": "error",
            "status_code": 1,
            "raw_log": f"Không tìm thấy file khóa SSH tại: {target_key_path}. Vui lòng kiểm tra lại Terraform."
        }

    # Xử lý Bastion host và đi qua Security Group
    # Mặc định chỉ tắt check Fingerprint
    ssh_common_args = "'-o StrictHostKeyChecking=no'"
    
    if bastion_ip and bastion_ip not in ["", "AUTO_FILL_BASTION"]:
        # Quét tất cả file .pem trong thư mục hạ tầng và đưa tất cả cho lệnh ProxyCommand. SSH sẽ tự động thử và dùng đúng chìa của máy Bastion.
        all_pem_files = glob.glob(os.path.join(terraform_env_dir, "*.pem"))
        identity_flags = " ".join([f"-i {pem}" for pem in all_pem_files])
        
        # Tạo đường hầm ẩn qua Bastion (-W %h:%p)
        proxy_cmd = f"ssh -W %h:%p -q ubuntu@{bastion_ip} -o StrictHostKeyChecking=no {identity_flags}"
        
        # Bọc lại thành chuỗi argument hoàn chỉnh cho Ansible
        ssh_common_args = f"'-o StrictHostKeyChecking=no -o ProxyCommand=\"{proxy_cmd}\"'"
        print(f"[Ansible Executor] Đã kích hoạt chế độ Xuyên Tường Lửa (ProxyJump) qua Bastion: {bastion_ip}")

    # Sinh file Inventory động 
    inventory_filename = f"inventory_{instance_name}.ini"
    inventory_path = os.path.join(work_dir, inventory_filename)
    
    # Nếu chạy qua Bastion thì 'public_ip' do AI truyền xuống chính là Private IP của máy đích.
    target_ip = public_ip 

    inventory_content = f"""[all]
{target_ip} ansible_user=ubuntu ansible_ssh_private_key_file={target_key_path} ansible_ssh_common_args={ssh_common_args}
"""
    
    try:
        # Ghi file inventory tạm ra đĩa
        with open(inventory_path, "w") as f:
            f.write(inventory_content)

        print(f"[Ansible Executor] Đang kết nối tới máy đích {target_ip} để chạy Playbook '{playbook_name}'...")

        # Kích hoạt ansible_runner với file inventory
        r = ansible_runner.run(
            private_data_dir=work_dir,
            playbook=playbook_name,
            inventory=inventory_path, 
            extravars=extra_vars,
            quiet=True
        )

        # Lấy log chuẩn từ ansible_runner
        try:
            with open(r.stdout.name, 'r') as f:
                out = f.read()
        except:
            out = "Không lấy được log từ quá trình thực thi."

        return {
            "status": "success" if r.rc == 0 else "error",
            "status_code": r.rc,
            "raw_log": out
        }

    except Exception as e:
        return {
            "status": "error",
            "status_code": 1,
            "raw_log": f"Lỗi thực thi Ansible: {str(e)}"
        }
    finally:
        # Dọn dẹp: Xóa file inventory tạm
        if os.path.exists(inventory_path):
            os.remove(inventory_path)
