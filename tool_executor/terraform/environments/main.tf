# Khai báo provider
provider "aws" {
  region = "ap-southeast-1"
}

# Khai báo template EC2
resource "aws_instance" "app_server" {
  ami = "ami-0e7ff22101b84bcff"
  instance_type = "t2.micro"

  tags = {
    Name = "AI-Generated-EC2"
    Environment = "dev"
  }
}