# Afterimage
A command-line tool that takes the pixels from one image and remaps them onto the structure of another — using brightness-based pixel sorting to make one image "become" another.

---

## Example
![Travel mode demo](examples/tigertofrog/output_travel.gif)
![Band mode demo](examples/tigertofrog/output_band.gif)

---

## Modes
- **Travel** — Pixels physically move from their origin positions to their destination, creating a flowing, liquid animation
- **Band** — Pixels are remapped incrementally from darkest to brightest, building the target image band by band

---

## Usage
```bash
python main.py <image1> <image2> [--output OUTPUT] [--mode {travel,band}]
```

| Argument | Description |
|---|---|
| `image1` | Source image — provides the pixels |
| `image2` | Template image — provides the structure |
| `--output`, `-o` | Output file path (default: `output.png`) |
| `--mode`, `-m` | Animation mode: `travel` or `band` (default: `travel`) |

### Examples
```bash
# Travel mode (default)
python main.py tiger.jpg frog.jpg -o result.png

# Band mode
python main.py tiger.jpg frog.jpg -o result.png -m band
```

Both commands produce a `.png` of the final frame and a `.gif` of the full animation.

---

## How It Works
1. Image 1 is resized to match Image 2's dimensions
2. Both images are flattened into pixel arrays
3. Each pixel is assigned a brightness value (average of R, G, B)
4. Both arrays are sorted by brightness — darkest to brightest
5. Pixels from Image 1 are mapped to the positions of brightness-matched pixels in Image 2
6. The transformation is animated either by pixel travel (lerping positions) or by brightness band

---

## Tech Stack
- **[Pillow](https://python-pillow.org/)** — Image loading, saving, and GIF export
- **[NumPy](https://numpy.org/)** — Pixel manipulation and brightness sorting

---

## Setup
### Prerequisites
- Python 3.10+
- pip

### 1. Clone the repo
```bash
git clone https://github.com/IsaacLaRose/Afterimage.git
cd Afterimage
```

### 2. Install dependencies
```bash
pip install Pillow numpy
```

### 3. Run
```bash
python main.py image1.jpg image2.jpg
```

---

## Project Structure
```
Afterimage/
├── main.py        # CLI entry point (runs image remap from terminal)
├── remap.py       # Core pixel remapping algorithm (heart of the project)
├── anim.py        # Animation modes (e.g., travel, band transitions → GIF frames)
├── utils.py       # Helper functions (image I/O, resizing, normalization)
├── examples/      # Sample inputs and generated outputs for demos
│
├── static/        # Frontend assets (served by web app)
│   ├── scripts/
│   │   └── main.js   # Frontend logic (file upload, UI interaction, requests)
│   ├── styles/
│   │   └── style.css # UI styling for web interface
│   └── favicon.ico   # Browser tab icon
│
├── templates/     # HTML templates
│   └── index.html  # Main web UI page
│
└── README.md      # Project overview, usage, and setup instructions
```

---

## License
MIT
