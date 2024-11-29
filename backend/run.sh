#!/bin/sh

while ! nc -z db 5432;
    do sleep .5;
    echo "Wait Database";
done;
    echo "Connected to the Database";

python3 manage.py migrate;
python3 manage.py collectstatic --noinput;

gunicorn -w 2 -b 0:8000 sayfood.wsgi;