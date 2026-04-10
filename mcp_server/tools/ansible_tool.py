import ansible_runner
import os

def execute_ansible_playbook(playbook_name: str, extra_vars: dict) -> dict:
    """
    Thực thi file playbook cục bộ bằng ansible-runner
    """
    # Xác định thư mục làm việc
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    work_dir = os.path.join(base_dir, 'tool_executor', 'ansible')

    try:
        r = ansible_runner.run(
            private_data_dir=work_dir,
            playbook=playbook_name,
            inventory='inventory.ini',
            extravars=extra_vars,
            quiet=True
        )

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

