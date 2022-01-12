FROM python:3.9-slim

RUN mkdir /app

RUN pip3 install mysql-connector-python apscheduler slack-sdk

ADD bot.py /app
ADD db.py /app
ADD strings.py /app
ADD tasks.py /app
ADD config.py /app

CMD ["python3", "-u", "/app/bot.py"]
