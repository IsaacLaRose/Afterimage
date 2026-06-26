from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
# @limiter.limit("4 per minute")
def process():
    if 'substance' not in request.files or 'template' not in request.files:
        return jsonify({'error': 'Both images are required'}), 400

    substance = request.files['substance']
    template = request.files['template']
    mode = request.form.get('mode', 'travel')

    if not allowed_file(substance.filename) or not allowed_file(template.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    job_id = str(uuid.uuid4())[:8]
    substance_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{job_id}_substance.png')
    template_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{job_id}_template.png')
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'{job_id}_output.png')
    gif_path = os.path.join(app.config['OUTPUT_FOLDER'], f'{job_id}_output.gif')

    substance.save(substance_path)
    template.save(template_path)

    try:
        from utils import load_image, save_image
        from remap import remap_pixels

        source = load_image(substance_path)
        target = load_image(template_path)
        result, frames = remap_pixels(source, target, mode)
        save_image(result, output_path)

        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )

        return jsonify({
            'success': True,
            'gif_url': f'/outputs/{job_id}_output.gif',
            'png_url': f'/outputs/{job_id}_output.png',
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/outputs/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)