cd hourly_pipeline/hourly_etl_script
source .env
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com
docker build --platform linux/amd64 --provenance=false -t "$HOURLY_ECR_NAME" .
docker tag $HOURLY_ECR_NAME:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/$HOURLY_ECR_NAME:latest
docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/$HOURLY_ECR_NAME:latest 
aws lambda update-function-code \
           --function-name $HOURLY_LAMBDA_NAME \
           --image-uri 129033205317.dkr.ecr.eu-west-2.amazonaws.com/$HOURLY_ECR_NAME:latest
