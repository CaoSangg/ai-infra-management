# Tự động sinh khóa SSH RSA
resource "tls_private_key" "ssh_key_ec2_instance_default" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Đăng ký Public Key lên AWS
resource "aws_key_pair" "keypair_ec2_instance_default" {
  key_name   = "key-ec2-instance-default"
  public_key = tls_private_key.ssh_key_ec2_instance_default.public_key_openssh
}

# Lưu Private Key xuống máy local thành file .pem để Ansible sử dụng
resource "local_file" "private_key_ec2_instance_default" {
  content         = tls_private_key.ssh_key_ec2_instance_default.private_key_pem
  filename        = "${path.module}/ec2-instance-default.pem"
  file_permission = "0400" # Ansible yêu cầu quyền 0400 cho file key
}

# Khai báo EC2
resource "aws_instance" "ec2_ec2_instance_default" {
  ami           = "ami-0e7ff22101b84bcff"
  instance_type = "t2.micro"
  
  # Gắn Key Pair vừa tạo vào máy ảo
  key_name      = aws_key_pair.keypair_ec2_instance_default.key_name

  # If/else xử lý Subnet
  
  subnet_id = aws_subnet.public_subnet.id 
  

  # If/else xử lý Security Group
  
  vpc_security_group_ids = [aws_security_group.public_sg.id] 
  
  
  # Quyền lấy IP public
  
  associate_public_ip_address = true
  
  
  tags = {
    Name        = "ec2-instance-default"
    Environment = "dev"
    ManagedBy   = "AI-Agent"
    # Tag thêm để dễ nhận biết trên giao diện AWS
    NetworkType = "Public/Bastion"
  }
}

# Outputs cho Ansible vs State Fetcher

output "public_ip_ec2_instance_default" {
  description = "Public IP để Ansible SSH vào cấu hình"
  value       = aws_instance.ec2_ec2_instance_default.public_ip
}


output "private_ip_ec2_instance_default" {
  description = "Private IP dùng để kết nối nội bộ hoặc ProxyJump"
  value       = aws_instance.ec2_ec2_instance_default.private_ip
}