from celery import Celery
from app import json_to_csv

app = Celery('tasks', broker='pyamqp://guest:guest@localhost//')

@app.task
def process_json(json_data, csv_path):
    json_to_csv(json_data, csv_path)
