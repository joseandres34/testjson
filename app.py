import os
from flask import Flask, render_template, request, send_from_directory, flash, redirect
from werkzeug.utils import secure_filename
from io import StringIO
import json
import csv

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'

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

            csv_data = json_to_csv(json_data)

            # Guarda el archivo CSV temporalmente
            csv_filename = 'output.csv'
            csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)

            with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_file.write(csv_data)

            # Envia el archivo para descarga
            return send_from_directory(app.config['UPLOAD_FOLDER'], csv_filename, as_attachment=True)
        else:
            flash('El archivo seleccionado no es un archivo JSON válido.')
            return redirect(request.url)

    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
