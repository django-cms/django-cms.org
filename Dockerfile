FROM python:3.12

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y purge --auto-remove && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

RUN python manage.py collectstatic --noinput

CMD uwsgi --http=0.0.0.0:80 --module=backend.wsgi
