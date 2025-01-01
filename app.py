import os
from flask import Flask, request, send_from_directory, render_template
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
TEMP_FOLDER = 'temp/GIFY'
GIF_FOLDER = 'gifs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['GIF_FOLDER'] = GIF_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

def resolve_scale_option(resolution, custom_resolution):
    if custom_resolution:
        return custom_resolution
    width, height = resolution.split('x')
    if height.lower() == 'auto':
        return f"{width}:-1"
    return resolution

@app.route('/execute', methods=['POST'])
def execute():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file:
        # Zabezpiecz nazwę pliku
        filename = secure_filename(file.filename)
        
        # Upewnij się, że katalogi istnieją
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
        os.makedirs(app.config['GIF_FOLDER'], exist_ok=True)
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Pobranie opcji z formularza
        resolution = request.form.get('resolution', '320xAuto')
        custom_resolution = request.form.get('custom_resolution', '')
        fps = request.form.get('fps', '10')

        scale_option = resolve_scale_option(resolution, custom_resolution)
        print(f"Received: resolution={resolution}, custom_resolution={custom_resolution}, fps={fps}, scale_option={scale_option}")

        # Konwersja na GIF
        output_filename = os.path.splitext(filename)[0] + '.gif'
        output_path = os.path.join(app.config['GIF_FOLDER'], output_filename)
        palette_path = os.path.join(app.config['TEMP_FOLDER'], 'palette.png')
        
        # Użyj subprocess zamiast os.system dla lepszej kontroli błędów
        try:
            subprocess.run(['ffmpeg', '-i', file_path, '-vf', f'fps={fps},scale={scale_option}:flags=lanczos,palettegen', palette_path], check=True)
            subprocess.run(['ffmpeg', '-i', file_path, '-i', palette_path, '-lavfi', f'fps={fps},scale={scale_option}:flags=lanczos [x]; [x][1:v] paletteuse', output_path], check=True)
            
            # Wyczyść pliki tymczasowe
            if os.path.exists(palette_path):
                os.remove(palette_path)
            if os.path.exists(file_path):
                os.remove(file_path)
                
            if os.path.exists(output_path):
                return render_template('index.html', file_processed=True, output_filename=output_filename)
            else:
                return "Error: Output file was not created", 500
                
        except subprocess.CalledProcessError as e:
            return f"Error processing file: {str(e)}", 500
            
    return "Error processing file", 500

@app.route('/download/<filename>')
def download(filename):
    # Sprawdź czy plik istnieje
    if not os.path.exists(os.path.join(app.config['GIF_FOLDER'], filename)):
        return "File not found", 404
    return send_from_directory(app.config['GIF_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    # Upewnij się, że wszystkie wymagane katalogi istnieją
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(TEMP_FOLDER, exist_ok=True)
    os.makedirs(GIF_FOLDER, exist_ok=True)
    
    app.run(host='0.0.0.0', port=8080)
