from celery import Celery
from app import json_to_csv

celery = Celery('tasks', broker=os.environ.get('CLOUDAMQP_URL', 'pyamqp://guest:guest@localhost//'))

@celery.task
def process_json(json_data, csv_path):
    json_to_csv(json_data, csv_path)
