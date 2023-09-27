# app.py
import os
import json
import csv
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from io import StringIO

app = Flask(__name__)

# Configuración de subida de archivos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def json_to_csv(json_data):
    data = json.loads(json_data)
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Escribir el encabezado
    if data:
        header = data[0].keys()
        csv_writer.writerow(header)
        
        # Escribir los datos
        for row in data:
            csv_writer.writerow(row.values())
    
    return csv_data.getvalue()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'json_file' not in request.files:
        flash('No se seleccionó un archivo JSON.')
        return redirect(request.url)
    
    file = request.files['json_file']
    
    if file.filename == '':
        flash('No se seleccionó un archivo.')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            json_data = file.read().decode('utf-8')
            csv_data = json_to_csv(json_data)
            return send_file(
                StringIO(csv_data),
                mimetype='text/csv',
                as_attachment=True,
                download_name='output.csv'
            )
        except Exception as e:
            flash(f'Error al procesar el archivo JSON: {str(e)}')
            return redirect(request.url)
    else:
        flash('El archivo seleccionado no es un archivo JSON válido.')
        return redirect(request.url)

if __name__ == '__main__':
    app.secret_key = 'supersecretkey'  # Cambia esto a una clave secreta más segura en un entorno de producción
    app.run(debug=True)
