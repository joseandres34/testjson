import os
from flask import Flask, render_template, request, flash, redirect, send_file, url_for
from werkzeug.utils import secure_filename
import json
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def json_to_csv(json_data):
    data = json.loads(json_data)
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)

    if data:
        header = data[0].keys()
        csv_writer.writerow(header)

        for row in data:
            csv_writer.writerow(row.values())

    return csv_data.getvalue()

def process_json_and_generate_csv(json_file, csv_path):
    with open(json_file, 'r', encoding='utf-8') as f_json, open(csv_path, 'w', newline='', encoding='utf-8') as f_csv:
        # Lee el archivo JSON en bloques de líneas
        for line in f_json:
            json_data = json.loads(line)
            csv_data = json_to_csv(json.dumps(json_data))  # Vuelve a convertir a JSON y luego a CSV
            f_csv.write(csv_data)

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
            # Generar un nombre único para el archivo CSV
            csv_filename = secure_filename('output.csv')
            csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)

            # Inicia el proceso de procesamiento en bloques
            process_json_and_generate_csv(file, csv_path)

            flash('Procesamiento en curso. El archivo CSV estará disponible para descarga en breve.')
            return redirect(url_for('index'))  # Redirige a la página principal después del procesamiento

        else:
            flash('El archivo seleccionado no es un archivo JSON válido.')
            return redirect(request.url)

    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(request.url)

@app.route('/download/<filename>', methods=['POST'])
def download(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    except Exception as e:
        flash(f'Error al descargar el archivo: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
