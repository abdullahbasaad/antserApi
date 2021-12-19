FROM python:3.9.7-alpine3.14
COPY ./requirements.txt /requirements.txt
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt   
CMD ["python","api.py"]
