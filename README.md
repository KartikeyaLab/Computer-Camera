# ASCII Camera

> Your face. Rendered in characters.

A real-time camera feed converted into ASCII art — live, in your terminal window. Switch character sets, toggle color, detect edges, record videos, and take screenshots. All from your keyboard.

---

## What it looks like

```
 . . : : ; ; = = x x X X $ $ @ @
: . . : ; = x X $ @ @ $ X x = ; :
; : . ; = x X $ @ . . @ $ X x = ;
= ; : = x X $ @ .     . @ $ X x =
```

*(except it's your actual face)*

---

## Requirements

- Python 3.8+
- A webcam

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Run

```bash
python ascii_camera.py
```

That's it. Your camera opens instantly.

---

## Controls

### Drawing & Modes

| Key | Action |
|-----|--------|
| `C` | Toggle **color mode** — characters take on the real color of what the camera sees |
| `E` | Toggle **edge detection** — outlines your features sharply |
| `I` | Toggle **invert** — flip light and dark characters |

### Character Sets

| Key | Style | Preview |
|-----|-------|---------|
| `1` | Simple | ` .:;+=xX$@` |
| `2` | Detailed | Full ASCII density range |
| `3` | Blocks | ` ░▒▓█` |
| `4` | Custom | ` .:/\|!@#$%^&*` |
| `5` | Binary | ` █` — stark black and white |
| `6` | Minimal | ` .-+*#@` |

### Resolution

| Key | Action |
|-----|--------|
| `+` or `=` | Increase resolution (more characters, more detail) |
| `-` or `_` | Decrease resolution (fewer characters, faster) |

### Capture

| Key | Action |
|-----|--------|
| `S` | Save a **screenshot** — saved as `ascii_screenshot_TIMESTAMP.png` |
| `R` | Start / stop **recording** — saved as `ascii_recording_TIMESTAMP.mp4` |

A red dot appears in the top-left corner while recording is active, with a live timer.

### Exit

| Key | Action |
|-----|--------|
| `Q` or `Esc` | Quit |

---

## Tips

- **Best results** in good lighting facing a plain background
- **Edge mode + binary** (`E` then `5`) gives a striking silhouette effect
- **Color mode** (`C`) is slower — drop resolution with `-` if FPS dips
- **Detailed charset** (`2`) gives the most depth and shadow on faces
- FPS counter is shown live in the top-left corner

---

## File Structure

```
ascii_camera.py       ← main program
requirements.txt      ← dependencies
README.md             ← you are here
```

---

## How it works

Each frame from your camera is:
1. Converted to grayscale
2. Resized to a small grid (default 120×60 characters)
3. Each pixel's brightness maps to a character — bright = dense, dark = sparse
4. Characters are drawn onto a blank canvas at their grid position
5. The canvas is shown as the live window

The smoothness of the output is controlled by the character set density and grid resolution.

---

*Made with euphoria.*
