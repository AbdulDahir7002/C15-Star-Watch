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


resource "aws_scheduler_schedule" "daily_scheduler" {
  name       = "c15-starwatch-daily-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 0 * * ? *)"

  target {
    arn      = aws_lambda_function.pipeline-lambda.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}

