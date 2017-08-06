FROM python:3.5

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

WORKDIR /dashboard

CMD python3 run.py --sonos-api gateway

ADD . /dashboard
