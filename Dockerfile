FROM python:3.8

ENV APP_HOME=/usr/app/src
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD . $APP_HOME
WORKDIR $APP_HOME

COPY pyproject.toml $APP_HOME

RUN pip install poetry
RUN poetry config virtualenvs.create false

RUN poetry install --no-dev && \
    poetry lock

COPY . $APP_HOME

