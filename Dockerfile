FROM python:3.10.8-slim-buster
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD gunicorn app:app --bind 0.0.0.0:8080 & python3 bot.py
