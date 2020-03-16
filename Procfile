web: python manage.py collectstatic --noinput && python manage.py distributed_migrate --noinput && waitress-serve --port=$PORT conf.wsgi:application
celery_worker: celery -A conf worker -l info
