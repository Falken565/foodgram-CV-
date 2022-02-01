FROM python:3.8

LABEL maintainer='falken'

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000