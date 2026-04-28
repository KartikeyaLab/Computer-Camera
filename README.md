# Computer Camera

> Your face, in the language of computers.

<img src="https://raw.githubusercontent.com/KartikeyaLab/The-Archive/main/Pictures/vid_001.gif" width="100%" />

It was an inspiration from a [YouTube video](https://youtube.com/shorts/FIZI3k7mTvA?si=vDPck3tcL50K4xzT) I watched years ago as a kid, and it stayed in my mind. I wanted to create something close to it, something that could capture the world in the language of computers. It is beautiful!! More than that, the most beautiful thing was people enjoying looking at themselves through the lens of characters… and it was a good time, exhibiting this program.

---


## How to run it

**Requirements** — Python 3.8+ and a webcam.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python ascii_camera.py
```

Your camera opens. That's it.

---

## Controls

### Modes

| Key | What it does |
|-----|-------------|
| `C` | Color mode — characters take on the real colors the camera sees |
| `E` | Edge detection — outlines and sharpens everything |
| `I` | Invert — flips light and dark |

### Character sets

| Key | Style |
|-----|-------|
| `1` | Simple — ` .:;+=xX$@` |
| `2` | Detailed — full density range |
| `3` | Blocks — ` ░▒▓█` |
| `4` | Custom — ` .:/\|!@#$%^&*` |
| `5` | Binary — ` █` |
| `6` | Minimal — ` .-+*#@` |

### Resolution

| Key | What it does |
|-----|-------------|
| `+` | More characters, more detail |
| `-` | Fewer characters, faster |

### Capture

| Key | What it does |
|-----|-------------|
| `S` | Screenshot — saves as `ascii_screenshot_TIMESTAMP.png` |
| `R` | Start / stop recording — saves as `ascii_recording_TIMESTAMP.mp4` |

A red dot appears in the corner while recording, with a live timer.

### Exit

| Key | What it does |
|-----|-------------|
| `Q` or `Esc` | Quit |

---

## How it actually works

Each frame from your camera is converted to grayscale, then resized down to a small grid — 120 columns by 60 rows by default. Every pixel in that grid has a brightness value, and that brightness maps to a character. Bright areas get dense characters like `@` or `#`, dark areas get light ones like `.` or just a space. Those characters are drawn onto a blank canvas, one by one, and that canvas becomes your live window.

The result is your world, rendered in text.

---

## File structure

```
ascii_camera.py       ← the program
requirements.txt      ← dependencies
README.md             ← you are here
```

---

*Made with euphoria.*
