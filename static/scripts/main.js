let selectedMode = 'travel';
const files = { substance: null, template: null };

function setMode(mode, btn) {
    selectedMode = mode;
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
}

function setupDropZone(role) {
    const zone = document.getElementById(`zone-${role}`);
    const input = document.getElementById(`input-${role}`);
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', e => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        if (e.dataTransfer.files[0]) handleFile(role, e.dataTransfer.files[0]);
    });
    input.addEventListener('change', () => {
        if (input.files[0]) handleFile(role, input.files[0]);
    });
}

function handleFile(role, file) {
    files[role] = file;
    const zone = document.getElementById(`zone-${role}`);
    const prev = document.getElementById(`prev-${role}`);
    prev.src = URL.createObjectURL(file);
    prev.style.display = 'block';
    zone.classList.add('has-file');
    updateUI();
}

function clearZone(role) {
    files[role] = null;
    const zone = document.getElementById(`zone-${role}`);
    const prev = document.getElementById(`prev-${role}`);
    prev.src = ''; prev.style.display = 'none';
    zone.classList.remove('has-file');
    document.getElementById(`input-${role}`).value = '';
    updateUI();
}

function updateUI() {
    document.getElementById('submit-btn').disabled = !(files.substance && files.template);
}

function setStatus(msg, type) {
    const el = document.getElementById('status-msg');
    el.textContent = msg;
    el.className = `status-msg ${type}`;
}

function fakeProgress() {
    const track = document.getElementById('progress-track');
    const fill = document.getElementById('progress-fill');
    track.classList.add('active');
    let pct = 0;
    const iv = setInterval(() => { pct = Math.min(pct + Math.random() * 8, 88); fill.style.width = pct + '%'; }, 300);
    return { stop: () => { clearInterval(iv); fill.style.width = '100%'; setTimeout(() => { track.classList.remove('active'); fill.style.width = '0%'; }, 600); }};
}

async function runRemap() {
    const btn = document.getElementById('submit-btn');
    btn.disabled = true;
    btn.classList.add('loading');
    setStatus('Processing…', 'info');
    const progress = fakeProgress();

    const form = new FormData();
    form.append('substance', files.substance);
    form.append('template', files.template);
    form.append('mode', selectedMode);

    try {
        const res = await fetch('/process', { method: 'POST', body: form });
        const data = await res.json();
        progress.stop();

        if (data.error) {
        setStatus(`Error: ${data.error}`, 'error');
        } else {
        setStatus('', '');
        const ts = '?t=' + Date.now();
        const gifImg = document.getElementById('output-gif');
        const pngImg = document.getElementById('output-png');
        gifImg.src = data.gif_url + ts; gifImg.style.display = 'block';
        pngImg.src = data.png_url + ts; pngImg.style.display = 'block';
        const dlGif = document.getElementById('dl-gif');
        const dlPng = document.getElementById('dl-png');
        dlGif.href = data.gif_url; dlGif.style.display = 'block';
        dlPng.href = data.png_url; dlPng.style.display = 'block';
        document.querySelectorAll('.output-empty').forEach(el => el.style.display = 'none');
        }
    } catch (err) {
        progress.stop();
        setStatus('Network error — is the server running?', 'error');
    }

    btn.classList.remove('loading');
    btn.disabled = false;
}

setupDropZone('substance');
setupDropZone('template');