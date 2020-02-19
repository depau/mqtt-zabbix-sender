FROM python:3.8-buster

MAINTAINER "Davide Depau <davide@depau.eu>"

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

VOLUME /etc/zabbix
VOLUME /conf

CMD [ "python", "./mqtt_zabbix_sender.py", "/conf/config.yml"]