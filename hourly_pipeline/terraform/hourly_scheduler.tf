resource "aws_iam_role" "scheduler_role" {
    name = "EventBridgeSchedulerRole"
    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = "sts:AssumeRole"
                Effect = "Allow"
                Principal = {
                    Service = "scheduler.amazonaws.com"
                }
            }
        ]
    })
}

resource "aws_iam_role_policy" "scheduler_lambda_invoke" {
    name = "EventBridgeInvokeLambdaPolicy"
    role = aws_iam_role.scheduler_role.id
    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
            Effect = "Allow"
            Action = "lambda:InvokeFunction"
            Resource = aws_lambda_function.pipeline-lambda.arn
        }
        ]
    })
}

# maybe the above should be data blocks instead since these have already been made in the daily schedule


resource "aws_scheduler_schedule" "hourly_scheduler" {
  name       = "c15-starwatch-hourly-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 * * * ? *)"

  target {
    arn      = aws_lambda_function.pipeline-lambda.arn # possibly may need to change since both etl lambdas are called "pipeline-lambda"
    role_arn = aws_iam_role.scheduler_role.arn
  }
}