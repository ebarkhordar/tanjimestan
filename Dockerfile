FROM python:3.9.0-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get install -y tzdata

ENV TZ Asia/Tehran

# set work directory
RUN mkdir /code
WORKDIR /code

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]