#!/usr/bin/env python3
"""
Prepare a photo or avatar for clean ASCII conversion:
  1. remove the background (rembg) so the subject is isolated
  2. bilateral-smooth away the texture/noise while keeping edges sharp
  3. stretch tones with CLAHE/adaptive contrast so highlights pop and lines stay dark
  4. darken line work (difference-of-gaussians ridges) for glasses, eyes, and smile
  5. composite onto white and crop square around the subject

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.

Usage:
    python scripts/prep_photo.py [input.png] [output.png]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INP = os.path.join(HERE, "..", "avatar-github.png")
if not os.path.exists(DEFAULT_INP):
    DEFAULT_INP = os.path.join(HERE, "..", "source-photo.png")

INP = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INP
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

LINE_WEIGHT = 0.65     # how hard drawn lines are pushed toward black

print(f"Prepping photo: {INP} -> {OUT}")
img_in = Image.open(INP).convert("RGBA")

# 1. cut out the subject using rembg (u2net model)
try:
    import rembg
    session = rembg.new_session("u2net")
    cut = rembg.remove(img_in, session=session)
except Exception as e:
    print(f"Warning: rembg failed ({e}), proceeding with original image")
    cut = img_in

rgb = np.array(cut.convert("RGB"))
alpha = np.array(cut.split()[-1])                 # 0 = background
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

# 2. smooth texture, keep edges
smooth = gray
for _ in range(3):
    smooth = cv2.bilateralFilter(smooth, 9, 40, 9)

# 3. tone stretch over the subject only
subject_mask = alpha > 128
if np.sum(subject_mask) > 100:
    lo, hi = np.percentile(smooth[subject_mask], [2, 92])
    hi = max(hi, lo + 1.0)
    tone = np.clip((smooth.astype(np.float32) - lo) / (hi - lo), 0, 1)
else:
    tone = smooth.astype(np.float32) / 255.0

# Boost local contrast with CLAHE
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
tone_u8 = (tone * 255).astype(np.uint8)
tone = clahe.apply(tone_u8).astype(np.float32) / 255.0

# 4. dark-on-light ridges -> darken line work
fine = cv2.GaussianBlur(smooth, (0, 0), 1.5).astype(np.float32)
coarse = cv2.GaussianBlur(smooth, (0, 0), 6.0).astype(np.float32)
lines = np.clip((coarse - fine) / 40.0, 0, 1)
out = np.clip(tone - LINE_WEIGHT * lines, 0, 1) * 255

# 5. paste onto white, square crop
mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
out = out * mask + 255.0 * (1.0 - mask)

ys, xs = np.where(alpha > 20)
if len(xs) > 0 and len(ys) > 0:
    side = max(xs.max() - xs.min(), ys.max() - ys.min()) + 40
    cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
else:
    side = max(out.shape[0], out.shape[1])
    cx, cy = out.shape[1] // 2, out.shape[0] // 2

canvas = np.full((side, side), 255, np.uint8)
x0, y0 = cx - side // 2, cy - side // 2
sx0, sy0 = max(x0, 0), max(y0, 0)
sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out[sy0:sy1, sx0:sx1].astype(np.uint8)

Image.fromarray(canvas, mode="L").save(OUT)
print("Successfully wrote prepped image to:", OUT, f"shape: {canvas.shape}")
