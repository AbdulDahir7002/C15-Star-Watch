aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com

docker build --platform linux/amd64 --provenance=false -t c15-star-watch-daily-lambda-repo .

docker tag c15-star-watch-daily-lambda-repo:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c15-star-watch-daily-lambda-repo:latest

docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c15-star-watch-daily-lambda-repo:latest 