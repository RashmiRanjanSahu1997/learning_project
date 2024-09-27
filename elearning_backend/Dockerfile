# FROM python:3.8.10
# ENV PYTHONUNBUFFERED 1
# WORKDIR /app
# ADD . /app
# COPY requirements.txt /app/requirements.txt

# RUN pip install -r requirements.txt
# COPY . /app

FROM python:3.8.10

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/
