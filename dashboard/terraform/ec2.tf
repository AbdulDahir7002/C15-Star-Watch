provider "aws" {
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_ACCESS_KEY
    region = var.AWS_REGION
}


resource "aws_security_group" "ec2_security_group" {
  name = "c15-star-watch-ec2-sg"
  vpc_id = var.AWS_VPC_ID
}


resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 22 
  to_port = 22 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "receive_db" {
  security_group_id = aws_security_group.ec2_security_group.id 
  from_port = 5432 
  to_port = 5432 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "send_db" {
  security_group_id = aws_security_group.ec2_security_group.id 
  from_port = 5432 
  to_port = 5432 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "receive_http" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 80 
  to_port = 80 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "send_http" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 80 
  to_port = 80 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "receive_https" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 443 
  to_port = 443 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "send_https" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 443 
  to_port = 443 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "receive_streamlit" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 8501 
  to_port = 8501 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "send_streamlit" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 8501 
  to_port = 8501 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}


resource "aws_instance" "c15-star-watch-ec2" {
  ami                          = "ami-0cbf43fd299e3a464"
  instance_type                = "t2.micro"
  key_name                     = var.EC2_KEY_NAME
  associate_public_ip_address  = true
  subnet_id                    = var.EC2_SUBNET_ID
  vpc_security_group_ids       = [
    aws_security_group.ec2_security_group.id
  ]


  tags = {
    Name = "c15-star-watch"
  }
}