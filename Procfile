web: python manage.py distributed_migrate --noinput && gunicorn conf.wsgi:application --config conf/gunicorn.py --bind 0.0.0.0:$PORT --worker-connections 1000
celery_worker: celery -A conf worker -l info
celery_beat: celery -A conf beat -l info -S django
