import os
from flask import Flask, request, send_from_directory, render_template

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
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Pobranie opcji z formularza
        resolution = request.form.get('resolution')
        custom_resolution = request.form.get('custom_resolution')
        fps = request.form.get('fps')

        scale_option = resolve_scale_option(resolution, custom_resolution)
        print(f"Received: resolution={resolution}, custom_resolution={custom_resolution}, fps={fps}, scale_option={scale_option}")

        # Konwersja na GIF
        output_filename = os.path.splitext(filename)[0] + '.gif'
        output_path = os.path.join(app.config['GIF_FOLDER'], output_filename)
        palette_path = os.path.join(app.config['TEMP_FOLDER'], 'palette.png')
        
        command_palette = f"ffmpeg -i {file_path} -vf fps={fps},scale={scale_option}:flags=lanczos,palettegen {palette_path}"
        command_gif = f"ffmpeg -i {file_path} -i {palette_path} -lavfi \"fps={fps},scale={scale_option}:flags=lanczos [x]; [x][1:v] paletteuse\" {output_path}"

        print("Executing:", command_palette)
        os.system(command_palette)
        print("Executing:", command_gif)
        os.system(command_gif)

        if os.path.exists(palette_path):
            os.remove(palette_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        return render_template('index.html', file_processed=True, output_filename=output_filename)
    return "Error processing file", 500

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['GIF_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
