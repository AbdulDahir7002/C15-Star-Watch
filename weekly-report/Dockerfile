FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip3 install -r requirements.txt 

COPY report_frame.html .

COPY stylesheet.css .

COPY weekly_report_generator.py .

COPY send_email.py .

CMD ["send_email.handler"]

