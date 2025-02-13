
provider "aws" {
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
    region = var.AWS_REGION
}

resource "aws_sns_topic" "c15_star_watch_city_sns_topic" {
  for_each = toset(var.CITIES)

  name = "c15-star-watch-${each.key}"
}

output "sns-topic-arns" {
  value = [for topic in aws_sns_topic.c15_star_watch_city_sns_topic : topic.arn]
}
