FROM python:3.8-slim

ARG DEV_CHAT
ARG BOT_TOKEN
ARG MONGO_KEY
ARG ADMIN_ID
ARG SWAGGER_URL
ARG SWAGGER_KEY

ENV DEV_CHAT=${DEV_CHAT}
ENV BOT_TOKEN=${BOT_TOKEN}
ENV MONGO_KEY=${MONGO_KEY}
ENV ADMIN_ID=${ADMIN_ID}
ENV SWAGGER_URL=${SWAGGER_URL}
ENV SWAGGER_KEY=${SWAGGER_KEY}

WORKDIR /app

COPY . /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]