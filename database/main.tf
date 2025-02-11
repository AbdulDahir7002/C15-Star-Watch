provider "aws" {
  region     = var.REGION
  secret_key = var.AWS_SECRET_ACCESS_KEY
  access_key = var.AWS_ACCESS_KEY
}

resource "aws_security_group" "rds_sec_grp" {
  name   = "c15-star-watch-rds-sg"
  vpc_id = "vpc-065136f1afd6b0658"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  
  }

  egress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  

  }
}

resource "aws_db_subnet_group" "db_subnet_grp" {
  name       = "c15-star-watch-subnet-grp"
  subnet_ids = [ "subnet-09963d73cb3483abe", "subnet-0a007e7162fab0ba2", "subnet-08b00202ae83c58a8"]
}

resource "aws_db_instance" "star_watch_db" {
  identifier             = "c15-star-watch-db"
  allocated_storage      = 20
  db_name                = var.DB_NAME
  engine                 = "postgres"
  engine_version         = "16.3"
  instance_class         = "db.t3.micro"
  username               = var.DB_USERNAME
  password               = var.DB_PASSWORD
  skip_final_snapshot    = true
  db_subnet_group_name   = aws_db_subnet_group.db_subnet_grp.name
  vpc_security_group_ids = [ aws_security_group.rds_sec_grp.id ]
  publicly_accessible    = true
}