let selectedMode = 'travel';
const files = { substance: null, template: null };

const MAX_DIMENSION = 1600; // longest side, in px — triggers the warning
const MIN_DOWNSIZE = 400;   // slider floor

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
    input.addEventListener('click', () => { input.value = ''; }); // allow re-selecting the same file
    input.addEventListener('change', () => {
        if (input.files[0]) handleFile(role, input.files[0]);
    });
}

function getImageDimensions(file) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve({ width: img.width, height: img.height });
        img.onerror = reject;
        img.src = URL.createObjectURL(file);
    });
}

function downsizeImage(file, maxDim) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
            const scale = Math.min(1, maxDim / Math.max(img.width, img.height));
            const canvas = document.createElement('canvas');
            canvas.width = Math.round(img.width * scale);
            canvas.height = Math.round(img.height * scale);
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            canvas.toBlob(blob => {
                resolve(new File([blob], file.name, { type: 'image/png' }));
            }, 'image/png');
        };
        img.onerror = reject;
        img.src = URL.createObjectURL(file);
    });
}

// Shows a banner with a size slider + wait option. Resolves { action: 'downsize', target } or { action: 'wait' }
function askSizeChoice(roleLabel, width, height) {
    return new Promise(resolve => {
        const longest = Math.max(width, height);
        const defaultTarget = Math.round(longest * 0.75);
        const el = document.getElementById('status-msg');
        el.className = 'status-msg info';
        el.innerHTML = `
            <div>The ${roleLabel} image is ${width}×${height} and may be slow to generate.</div>
            <div style="margin-top:0.6rem;">
                <div style="display:flex; justify-content:space-between; font-size:0.68rem; color:var(--text-muted);">
                    <span>Resize longest side to</span>
                    <span id="size-choice-readout">${defaultTarget}px</span>
                </div>
                <input type="range" id="size-choice-slider"
                       min="${MIN_DOWNSIZE}" max="${longest}" value="${defaultTarget}"
                       style="width:100%; margin-top:0.35rem;">
            </div>
            <div style="display:flex; gap:0.5rem; margin-top:0.6rem;">
                <button type="button" id="size-choice-downsize" class="mode-btn" style="flex:1; padding:0.4rem 0.6rem; font-size:0.72rem;">Downsize it</button>
                <button type="button" id="size-choice-wait" class="mode-btn" style="flex:1; padding:0.4rem 0.6rem; font-size:0.72rem;">No, I'll wait</button>
            </div>
        `;

        const slider = document.getElementById('size-choice-slider');
        const readout = document.getElementById('size-choice-readout');
        slider.addEventListener('input', () => {
            readout.textContent = `${slider.value}px`;
        });

        document.getElementById('size-choice-downsize').addEventListener('click', () => {
            setStatus('', '');
            resolve({ action: 'downsize', target: parseInt(slider.value, 10) });
        });
        document.getElementById('size-choice-wait').addEventListener('click', () => {
            setStatus('', '');
            resolve({ action: 'wait' });
        });
    });
}

async function handleFile(role, file) {
    const { width, height } = await getImageDimensions(file);
    const longest = Math.max(width, height);

    if (longest > MAX_DIMENSION) {
        const roleLabel = role === 'substance' ? 'source' : 'template';
        const choice = await askSizeChoice(roleLabel, width, height);
        if (choice.action === 'downsize') {
            file = await downsizeImage(file, choice.target);
        }
        // choice.action === 'wait' just proceeds with the original file
    }

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