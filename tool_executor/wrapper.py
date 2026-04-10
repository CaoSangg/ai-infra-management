import subprocess
import time
import re
import os

class SanitizationWrapper:
    def __init__(self, target_dir):
        # Thư mục chứa file main.tf (environments)
        self.target_dir = target_dir

    # Lọc và che giấu các thông tin nhạy cảm (Ví dụ: AWS Access Key, Password)
    def sanitize_log(self, raw_log):
        # Giấu chuỗi trông giống AWS Access Key
        sanitized = re.sub(r'(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])', '[REDACTED_AWS_KEY]', raw_log)
        # Giấu chuỗi trông giống Secret Key
        sanitized = re.sub(r'(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])', '[REDACTED_SECRET]', sanitized)
        return sanitized

    # Chạy một lệnh shell và bắt stdout/stderr
    def _run_command(self, command):
        try:
            result = subprocess.run(
                command,
                cwd=self.target_dir, # Trỏ thư mục thực thi vào environments
                shell=True,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.returncode, result.stdout + result.stderr
        except Exception as e:
            return 1, str(e)

    # Thực thi Terraform init và apply/destroy
    def execute_terraform(self, action="apply"):
        start_time = time.time()

        # Kiểm tra xem đã có provider chưa
        terraform_dir = os.path.join(self.target_dir, ".terraform")

        if not os.path.exists(terraform_dir):
            print("[Wrapper] Phát hiện thư mục mới, đang chạy 'terraform init'...")
            init_code, init_log = self._run_command("terraform init -no-color")
            if init_code != 0:
                execution_time = time.time() - start_time
                return {
                    "status_code": init_code,
                    "execution_time": round(execution_time, 2),
                    "clean_log": self.sanitize_log(init_log),
                    "error": "Lỗi ở bước init"
                }
        else:
            print("[Wrapper] Thư mục đã được init, bỏ qua bước 'terraform init'.")

        # Chạy Terraform dựa trên action
        print(f"[Wrapper] Đang chạy 'terraform {action}'...")

        # Tạo câu lệnh linh hoạt dựa trên action
        command = f"terraform {action} -auto-approve -no-color"

        action_code, action_log = self._run_command(command)

        execution_time = time.time() - start_time

        return {
            "status_code": action_code, # Trả về 0 nếu thành công
            "execution_time": round(execution_time, 2),
            "clean_log": self.sanitize_log(action_log),
            "error": None if action_code == 0 else f"Lỗi ở bước {action}"
        }

    # Clean Log (Đang chỉ với Terraform)
    def sanitize_log(self, raw_log: str) -> str:
        if not raw_log:
           return ""

        # Loại bỏ các mã màu ANSI (như \x1b[0m, \033[31m)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_escape.sub('', raw_log)

        # Loại bỏ các dòng log thừa thãi (như Refreshing state)
        # Giữ lại các dòng Plan, Apply complete, Error
        important_lines = []
        for line in clean_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Lọc bỏ các dòng đang trong quá trình chờ đợi
            if "Refreshing state..." in line or "Still creating..." in line or "Still destroying..." in line:
                continue

            important_lines.append(line)

        # Gom gọn log nếu quá dài để tránh tốn token và ngợp
        if len(important_lines) > 100:
            summary = important_lines[:50] + ["\n... [ĐÃ RÚT GỌN LOG Ở GIỮA] ...\n"] + important_lines[-50:]
            return "\n".join(summary)

        return "\n".join(important_lines)
