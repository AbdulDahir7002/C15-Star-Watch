data "aws_iam_role" "scheduler_role" {
    name = "EventBridgeSchedulerRole"
}

data "aws_iam_role_policy" "scheduler_lambda_invoke" {
    name = "EventBridgeInvokeLambdaPolicy"
}


resource "aws_scheduler_schedule" "hourly_scheduler" {
  name       = "c15-starwatch-hourly-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 * * * ? *)"

  target {
    arn      = aws_lambda_function.pipeline-lambda.arn # possibly may need to change since both etl lambdas are called "pipeline-lambda"
    role_arn = data.aws_iam_role.scheduler_role.arn
  }
}