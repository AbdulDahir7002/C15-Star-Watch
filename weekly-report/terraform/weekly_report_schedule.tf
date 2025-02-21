resource "aws_iam_role" "scheduler_role" {
    name = "EventBridgeWeeklySchedulerRole"
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
            Resource = aws_lambda_function.email-lambda.arn
        }
        ]
    })
}


resource "aws_scheduler_schedule" "weekly_scheduler" {
  name       = "c15-starwatch-weekly-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 0 ? * 2 *)"

  target {
    arn      = aws_lambda_function.email-lambda.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}