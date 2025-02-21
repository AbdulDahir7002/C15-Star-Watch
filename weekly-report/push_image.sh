aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com
docker build --platform linux/amd64 --provenance=false -t "$WEEKLY_ECR_NAME" .
docker tag $WEEKLY_ECR_NAME:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/$WEEKLY_ECR_NAME:latest
docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/$WEEKLY_ECR_NAME:latest 
aws lambda update-function-code \
           --function-name $WEEKLY_LAMBDA_NAME \
           --image-uri 129033205317.dkr.ecr.eu-west-2.amazonaws.com/$WEEKLY_ECR_NAME:latest
