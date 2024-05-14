import os
from flask import Flask, request, send_file, jsonify, after_this_request

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
TEMP_FOLDER = 'temp'

def clean_up_files(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    file = request.files['file']
    command = request.form['command']

    if file:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        output_filename = f"{os.path.splitext(filename)[0]}_converted.gif"
        palette_path = os.path.join(TEMP_FOLDER, 'palette.png')
        output_filepath = os.path.join(TEMP_FOLDER, output_filename)

        if command == 'gif':
            ffmpeg_command1 = f"ffmpeg -i {filepath} -vf 'fps=10,scale=320:-1:flags=lanczos,palettegen' -y {palette_path}"
            ffmpeg_command2 = f"ffmpeg -i {filepath} -i {palette_path} -lavfi 'fps=10,scale=320:-1:flags=lanczos [x]; [x][1:v] paletteuse' {output_filepath}"
            os.system(ffmpeg_command1)
            os.system(ffmpeg_command2)
        
        clean_up_files([filepath, palette_path])

        return jsonify({'status': 'success', 'output_file': output_filename})

    return jsonify({'status': 'error'}), 400

@app.route('/download/<filename>')
def download(filename):
    @after_this_request
    def remove_file(response):
        try:
            os.remove(os.path.join(TEMP_FOLDER, filename))
        except Exception as error:
            app.logger.error("Error removing or closing downloaded file handle", error)
        return response

    return send_file(os.path.join(TEMP_FOLDER, filename))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(TEMP_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=8080)
