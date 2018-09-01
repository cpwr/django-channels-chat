FROM python:3.7

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=core.settings

RUN mkdir /src
WORKDIR /src
ADD . /src

RUN pip install -r requirements.txt && pip install --upgrade https://github.com/celery/celery/tarball/master
