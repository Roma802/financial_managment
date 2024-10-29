FROM python:3.8.3-alpine

WORKDIR /financial_managment

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    build-base


RUN pip install --upgrade pip setuptools
COPY ./requirements.txt ./requirements.txt
COPY . .


RUN pip install --only-binary cryptography -r ./requirements.txt

RUN adduser --disabled-password financial_app_user
RUN chown -R financial_app_user:financial_app_user /financial_managment
USER financial_app_user



