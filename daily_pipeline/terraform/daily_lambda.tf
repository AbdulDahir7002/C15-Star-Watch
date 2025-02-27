# ECR

data "aws_ecr_repository" "lambda-image-repo" {
  name = "c15-star-watch-daily-lambda-repo"
}

data "aws_ecr_image" "lambda-image-version" {
  repository_name = data.aws_ecr_repository.lambda-image-repo.name
  image_tag = "latest"
}

# Permissions for the lambda

data "aws_iam_policy_document" "lambda-role-trust-policy-doc" {
  statement {
    effect = "Allow"
    principals {
      type = "Service"
      identifiers = [ "lambda.amazonaws.com" ]
    }
    actions = [ 
        "sts:AssumeRole" 
    ]
  }
}

data "aws_iam_policy_document" "lambda-role-permissions-policy-doc" {
  statement {
    effect = "Allow"
    actions = [ 
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents" 
    ]
    resources = [ "arn:aws:logs:eu-west-2:129033205317:*" ]
  }
}

# Role

resource "aws_iam_role" "lambda-role" {
  name ="c15-star-watch-daily-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda-role-trust-policy-doc.json
}

resource "aws_iam_policy" "lambda-role-permissions-policy" {
  name = "c15-star-watch-daily-pipeline-policy"
  policy = data.aws_iam_policy_document.lambda-role-permissions-policy-doc.json
}

resource "aws_iam_role_policy_attachment" "lambda-role-policy-attachment" {
  role = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda-role-permissions-policy.arn
}

# Lambda

resource "aws_lambda_function" "pipeline-lambda" {
  function_name = "c15-star-watch-daily"
  role = aws_iam_role.lambda-role.arn
  package_type = "Image"
  image_uri = data.aws_ecr_image.lambda-image-version.image_uri
  timeout = 900
  environment { 
    variables = {
        DB_HOST = var.DB_HOST
        DB_NAME = var.DB_NAME
        DB_USERNAME = var.DB_USERNAME
        DB_PASSWORD = var.DB_PASSWORD
        DB_PORT = var.DB_PORT
        ASTRONOMY_BASIC_AUTH_KEY = var.ASTRONOMY_BASIC_AUTH_KEY
        }
    }
}