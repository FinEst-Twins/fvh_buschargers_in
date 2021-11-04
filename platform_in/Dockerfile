# pull official base image
FROM python:3.8-slim-buster

# set working directory
WORKDIR /project

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# add and install requirements
COPY requirements.txt .

## install dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat-openbsd gcc && \
    apt-get clean && \
    python3 -m pip install -r requirements.txt


COPY $ca .
COPY $key .
COPY $cert .

COPY . /project/
ENV CERT_FOLDER /project

COPY $ca /usr/local/share/ca-certificates/chain.crt
RUN update-ca-certificates

