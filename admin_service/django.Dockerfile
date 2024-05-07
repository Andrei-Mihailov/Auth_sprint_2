FROM python:3.9-slim

ENV HOME_APP=/app

RUN addgroup --system app && adduser --system --group app
RUN mkdir $HOME_APP
RUN mkdir $HOME_APP/static

WORKDIR $HOME_APP

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY ./admin_service/requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./admin_service/ $HOME_APP
COPY ./envs.env /app/config/.env

RUN chown -R app:app $HOME_APP

USER app