FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY aurora_status.py .

COPY weather_extract.py .

COPY hourly_etl.py .

CMD ["hourly_etl.lambda_handler"]