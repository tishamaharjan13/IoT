FROM python:3.10.12-bullseye

WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN  pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "server.py"]