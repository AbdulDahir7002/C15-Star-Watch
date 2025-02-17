FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt 

COPY first_week.py .

COPY daily_etl.py .

CMD ["daily_etl.handler"]