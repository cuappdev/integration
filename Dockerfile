FROM python:3.9

RUN apt-get update && apt-get -y install cron && apt-get -y install vim
RUN mkdir /usr/app
WORKDIR /usr/app
COPY ./src .
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./src/scheduled_run.txt /etc/cron.d/scheduled_run
RUN crontab /etc/cron.d/scheduled_run
