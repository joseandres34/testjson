web: gunicorn app:app
worker: celery -A worker worker --loglevel=info
