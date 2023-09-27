import os
from flask import Flask, render_template, request, flash, redirect
from werkzeug.utils import secure_filename
from io import StringIO
import json
from celery import Celery
from worker import process_json
import csv

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'

app.config['CELERY_BROKER_URL'] = os.environ.get('CLOUDAMQP_URL', 'pyamqp://guest:guest@localhost//')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('CLOUDAMQP_URL', 'rpc://')

celery = Celery(
    app.import_name,
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL']
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def flatten_json(json_obj, parent_key='', sep='_'):
    flat_dict = {}
    for k, v in json_obj.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            flat_dict.update(flatten_json(v, new_key, sep=sep))
        else:
            flat_dict[new_key] = v
    return flat_dict

def json_to_csv(json_data, csv_path):
    data = json.loads(json_data)
    flattened_data = [flatten_json(record) for record in data]

    csv_data = StringIO()
    csv_writer = csv.DictWriter(csv_data, fieldnames=flattened_data[0].keys())

    csv_writer.writeheader()
    csv_writer.writerows(flattened_data)

    with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_file.write(csv_data.getvalue())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        if 'json_file' not in request.files:
            flash('No se seleccionó un archivo JSON.')
            return redirect(request.url)

        file = request.files['json_file']

        if file.filename == '':
            flash('No se seleccionó un archivo.')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            json_data = file.read().decode('utf-8')

            if not json_data.strip():
                flash('El archivo JSON está vacío.')
                return redirect(request.url)

            # Generar un nombre único para el archivo CSV
            csv_filename = secure_filename('output.csv')
            csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)

            # Enviar la tarea al worker
            process_json.delay(json_data, csv_path)

            flash('Procesamiento en curso. El archivo CSV estará disponible para descarga en breve.')
            return redirect(request.url)
        else:
            flash('El archivo seleccionado no es un archivo JSON válido.')
            return redirect(request.url)

    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
