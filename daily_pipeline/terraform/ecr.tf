provider "aws" {
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_ACCESS_KEY
    region = var.AWS_REGION
}

resource "awscc_ecr_repository" "c15-star-watch-lambdas-repo" {
  repository_name      = "c15-star-watch-daily-lambda-repo"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration = {
    scan_on_push = true
  }

}