# ECR

data "aws_ecr_repository" "lambda-image-repo" {
  name = "c15-star-watch-hourly-lambda-repo"
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

data "aws_iam_policy_document" "lambda-role-permissions-sns-doc" {
    statement {
        effect = "Allow"
        actions = [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:PutMetricFilter",
                "logs:PutRetentionPolicy"
        ]
        resources = [ "arn:aws:iam::aws:policy/service-role/AmazonSNSRole" ]
    }
}

data "aws_iam_policy_document" "lambda-role-permissions-ses-doc" {
    statement {
        effect = "Allow"
        actions = ["ses:*"]
        resources = [ "arn:aws:iam::aws:policy/AmazonSESFullAccess" ]
    }
}
# Role

resource "aws_iam_role" "lambda-role" {
  name ="c15-star-watch-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda-role-trust-policy-doc.json
}

resource "aws_iam_policy" "lambda-role-permissions-policy" {
  name = "c15-star-watch-email-report-policy"
  policy = data.aws_iam_policy_document.lambda-role-permissions-policy-doc.json
}

resource "aws_iam_policy" "lambda-sns-policy"{
    name = "c15-star-watch-sns"
    policy = data.aws_iam_policy_document.lambda-role-permissions-sns-doc.json
}

resource "aws_iam_policy" "lambda-ses-policy"{
    name = "c15-star-watch-ses"
    policy = data.aws_iam_policy_document.lambda-role-permissions-ses-doc.json
}

resource "aws_iam_role_policy_attachment" "lambda-role-policy-attachment" {
  role = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda-role-permissions-policy.arn
}

# Lambda

resource "aws_lambda_function" "pipeline-lambda" {
  function_name = "c15-star-email-report"
  role = aws_iam_role.lambda-role.arn
  package_type = "Image"
  image_uri = data.aws_ecr_image.lambda-image-version.image_uri
  timeout = 600
  environment { 
    variables = {
        DB_HOST = var.DB_HOST
        DB_NAME = var.DB_NAME
        DB_USER = var.DB_USER
        DB_PASSWORD = var.DB_PASSWORD
        DB_PORT = var.DB_PORT
        EMAIL = var.EMAIL
        }
    }
}