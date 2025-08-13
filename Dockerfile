FROM python:3.11

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

RUN python manage.py migrate djangocms_blog
RUN python manage.py collectstatic --noinput

CMD uwsgi --http=0.0.0.0:80 --module=backend.wsgi
