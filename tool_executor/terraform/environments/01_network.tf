# Tạo VPC không

resource "aws_vpc" "main_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "Test_alone-VPC"
    Environment = "dev"
  }
}

# Tạo VPC đầy đủ 


# Tạo Public Subnet
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true 
  tags = { Name = "Test_alone-Public-Subnet" }
}

# Tạo Private Subnet
resource "aws_subnet" "private_subnet" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = false 
  tags = { Name = "Test_alone-Private-Subnet" }
}

# Tạo Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main_vpc.id
}

# Tạo Route Table & Route ra Internet
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public_rta" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

# Tạo một IP tĩnh (Elastic IP) cho NAT
resource "aws_eip" "nat_eip" {
  domain = "vpc"
}

# Tạo NAT Gateway và đặt nó ở Public Subnet
resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnet.id
  tags = { Name = "Test_alone-NAT" }
  depends_on = [aws_internet_gateway.igw]
}

# Tạo Private Route Table
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.main_vpc.id
    # Dạy máy Private nếu muốn ra Internet (0.0.0.0/0) thì đi qua NAT Gateway
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }
}

# Gắn Private Route Table vào Private Subnet
resource "aws_route_table_association" "private_rta" {
  subnet_id      = aws_subnet.private_subnet.id
  route_table_id = aws_route_table.private_rt.id
}

# Security Group cho máy public 
resource "aws_security_group" "public_sg" {
  name        = "Test_alone-Public-SG"
  description = "Security Group for Bastion Host & Public Web"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security Group cho máy private
resource "aws_security_group" "private_sg" {
  name        = "Test_alone-Private-SG"
  description = "Security Group for Internal Servers"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.public_sg.id]
  }

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.public_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}



# OUTPUTS
output "vpc_id" { value = aws_vpc.main_vpc.id }


output "public_subnet_id" { value = aws_subnet.public_subnet.id }
output "private_subnet_id" { value = aws_subnet.private_subnet.id }
output "public_security_group_id" { value = aws_security_group.public_sg.id }
output "private_security_group_id" { value = aws_security_group.private_sg.id }
output "security_group_id" { value = aws_security_group.public_sg.id }
