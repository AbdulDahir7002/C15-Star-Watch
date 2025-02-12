provider "aws" {
    region = "eu-west-2"
}

resource "awscc_ecr_repository" "c15-star-watch-lambdas-repo" {
  repository_name      = "c15-star-watch-lambdas-repo"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration = {
    scan_on_push = true
  }

}