from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = '/app/uploads'
TEMP_FOLDER = '/app/temp'
GIF_FOLDER = '/app/gifs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(GIF_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    file = request.files['file']
    operation = request.form['operation']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    if operation == 'gif':
        resolution = request.form.get('resolution', '320:-1')
        fps = request.form.get('fps', '10')
        palette_path = os.path.join(TEMP_FOLDER, 'palette.png')
        output_filename = f"{os.path.splitext(file.filename)[0]}_converted.gif"
        output_path = os.path.join(GIF_FOLDER, output_filename)
        
        try:
            # Generowanie palety
            subprocess.run([
                'ffmpeg', '-i', input_path, '-vf', f'fps={fps},scale={resolution}:flags=lanczos,palettegen', '-y', palette_path
            ], check=True)
            # Tworzenie GIFa z paletą
            subprocess.run([
                'ffmpeg', '-i', input_path, '-i', palette_path, '-lavfi', f'fps={fps},scale={resolution}:flags=lanczos [x]; [x][1:v] paletteuse', '-y', output_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({'success': False, 'error': str(e)})

        return jsonify({'success': True, 'filename': output_filename})

    elif operation == 'convert':
        output_filename = f"{os.path.splitext(file.filename)[0]}_converted.mp4"
        output_path = os.path.join(TEMP_FOLDER, output_filename)
        
        try:
            subprocess.run([
                'ffmpeg', '-i', input_path, output_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({'success': False, 'error': str(e)})

        return jsonify({'success': True, 'filename': output_filename})

    return jsonify({'success': False, 'error': 'Invalid operation'})

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_from_directory(GIF_FOLDER if filename.endswith('.gif') else TEMP_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
