FROM python:3.10.12-bullseye

WORKDIR /app

ENV PYTHONUNBUFFERED 1

RUN apt update && apk install \
    build-base \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    jpeg-dev \
    zlib-dev \
    musl-dev

COPY requirements.txt .
RUN  pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "server:app"]