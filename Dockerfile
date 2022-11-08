FROM python:3.9-alpine

WORKDIR /usr/src/tg_autoreply

COPY notification_bot.py .

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python3", "notification_bot.py"]
