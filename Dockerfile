FROM python:3.9-alpine

WORKDIR /home/

COPY main.py .
COPY ../token.txt .

RUN apk update && pip install pyTelegramBotAPI && pip install bs4

CMD ["python3", "main.py"]
