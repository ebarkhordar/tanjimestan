FROM python:3.8.3-slim

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
RUN pip install pipenv

COPY Pipfile /code/
RUN pipenv install --system --deploy

COPY . .

CMD [ "python", "main.py" ]