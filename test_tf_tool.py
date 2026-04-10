import os
from mcp_server.tools.terraform_tool import provision_aws_infrastructure
from tool_executor.wrapper import SanitizationWrapper

# Giả lập tham số mà Node 4 sẽ truyền xuống để tạo main tf
fake_ai_params = {
    "resource_type": "ec2",
    "config": {
        "region": "ap-southeast-1",
        "ami_id": "ami-0e7ff22101b84bcff", 
        "instance_type": "t2.micro",
        "instance_name": "Test-Terraform-EC2",
        "environment": "staging"
    }
}

print("Đang gọi hàm tạo resource...")
result = provision_aws_infrastructure(
    resource_type=fake_ai_params["resource_type"], 
    config=fake_ai_params["config"]
)

print(result "\n")

# Thực thi Terraform
if result["status"] == "success":
    print("2. Đang kích hoạt Wrapper để chạy Terraform...")
    # Xác định đường dẫn thư mục environments
    base_dir = os.path.dirname(os.path.abspath(__file__))
    environments_dir = os.path.join(base_dir, 'tool_executor', 'terraform', 'environments')
    
    # Khởi tạo Wrapper và chạy
    wrapper = SanitizationWrapper(target_dir=environments_dir)
    execution_result = wrapper.execute_terraform()
    
    print("\n KẾT QUẢ THỰC THI")
    print(f"Status Code: {execution_result['status_code']}")
    print(f"Thời gian: {execution_result['execution_time']} giây")
    print(f"Log (đã mask): \n{execution_result['clean_log'][:500]}...\n[LOG ĐÃ ĐƯỢC CẮT BỚT ĐỂ HIỂN THỊ]")


