from flask import Flask, render_template, request, jsonify, send_file, abort
import io
import uuid
import time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# In-memory store: job_id -> {'gif': bytes, 'png': bytes, 'created': float}
JOBS = {}
JOB_TTL_SECONDS = 15 * 60  # evict old jobs after 15 min


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def evict_stale_jobs():
    cutoff = time.time() - JOB_TTL_SECONDS
    stale = [jid for jid, j in JOBS.items() if j['created'] < cutoff]
    for jid in stale:
        JOBS.pop(jid, None)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
@limiter.limit("5 per minute")
def process():
    if 'substance' not in request.files or 'template' not in request.files:
        return jsonify({'error': 'Both images are required'}), 400

    substance = request.files['substance']
    template = request.files['template']
    mode = request.form.get('mode', 'travel')

    if not allowed_file(substance.filename) or not allowed_file(template.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    evict_stale_jobs()

    try:
        from utils import load_image, save_image
        from remap import remap_pixels

        # Read uploads straight into memory buffers
        substance_bytes = io.BytesIO(substance.read())
        template_bytes = io.BytesIO(template.read())

        source = load_image(substance_bytes)
        target = load_image(template_bytes)
        result, frames = remap_pixels(source, target, mode)

        # PNG to memory
        png_buffer = io.BytesIO()
        save_image(result, png_buffer)
        png_buffer.seek(0)

        # GIF to memory
        gif_buffer = io.BytesIO()
        frames[0].save(
            gif_buffer,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )
        gif_buffer.seek(0)

        job_id = str(uuid.uuid4())[:8]
        JOBS[job_id] = {
            'gif': gif_buffer.getvalue(),
            'png': png_buffer.getvalue(),
            'created': time.time(),
        }

        return jsonify({
            'success': True,
            'gif_url': f'/outputs/{job_id}/gif',
            'png_url': f'/outputs/{job_id}/png',
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/outputs/<job_id>/<kind>')
@limiter.exempt
def output_file(job_id, kind):
    job = JOBS.get(job_id)
    if not job or kind not in ('gif', 'png'):
        abort(404)

    mimetype = 'image/gif' if kind == 'gif' else 'image/png'
    return send_file(
        io.BytesIO(job[kind]),
        mimetype=mimetype,
        download_name=f'{job_id}_output.{kind}',
    )


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=False)