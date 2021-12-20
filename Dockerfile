FROM python:3.7-buster
COPY ./requirements.txt /requirements.txt
COPY titanic.csv .
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
CMD ["python","api.py"]



