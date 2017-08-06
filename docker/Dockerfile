FROM python:3.5

RUN useradd -m user

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

USER user
WORKDIR /home/user/dashboard

CMD python3 run.py --sonos-api gateway

ADD . /home/user/dashboard
