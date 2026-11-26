"""Client's ORIGINAL logo -> transparent web versions (edge flood-fill, not a global white key).
No redraw: pixels are the client's artwork; only the outside white background is removed."""
import os, numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage as ndi
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = '/workspace/heavyhaulers/uploads/logo-official.jpg'
OUT = os.path.join(R, 'brand', 'official'); os.makedirs(OUT, exist_ok=True)

im = Image.open(SRC).convert('RGB'); a = np.asarray(im).astype(np.float32)
dist = 255 - a.min(axis=2)                       # 0 = pure white
T_BG, T_SOFT = 28, 70
near = dist < T_BG
lab, n = ndi.label(near)
edge_labels = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(edge_labels))
# soft anti-aliased edge: a 2px band next to the background gets alpha from its distance to white
band = ndi.binary_dilation(bg, iterations=2) & ~bg
alpha = np.full(dist.shape, 255.0); alpha[bg] = 0
soft = band & (dist < T_SOFT)
alpha[soft] = np.clip((dist[soft] - T_BG * 0.5) / (T_SOFT - T_BG * 0.5), 0, 1) * 255
# un-matte the band from white so edges don't keep a white fringe
al = (alpha / 255.0)[..., None]
rgb = a.copy()
m = soft & (alpha > 0)
rgb[m] = np.clip((a[m] - 255 * (1 - al[m])) / np.maximum(al[m], 1e-3), 0, 255)
rgba = np.dstack([rgb, alpha]).astype(np.uint8)
logo = Image.fromarray(rgba, 'RGBA')
bbox = logo.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
pad = 6
bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(logo.width, bbox[2] + pad), min(logo.height, bbox[3] + pad))
logo = logo.crop(bbox)
print('trimmed', logo.size, 'bg comps', len(edge_labels))

def save(img, name, w=None):
    if w and img.width > w:
        img = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
    img.save(os.path.join(OUT, name + '.png'), optimize=True)
    img.save(os.path.join(OUT, name + '.webp'), 'WEBP', quality=92, method=6)
    return img

save(logo, 'logo-full')
save(logo, 'logo-512', 512)
save(logo, 'logo-256', 256)

# light rounded plate version for dark header/footer
def plate(img, w, padx=0.035, pady=0.035, radius=0.08, color=(246, 244, 239, 255)):
    img = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
    px, py = round(w * padx), round(w * pady)
    W, H = w + 2 * px, img.height + 2 * py
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    mask = Image.new('L', (W * 4, H * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W * 4 - 1, H * 4 - 1], radius=round(W * radius * 4), fill=255)
    mask = mask.resize((W, H), Image.LANCZOS)
    base.paste(Image.new('RGBA', (W, H), color), (0, 0), mask)
    base.alpha_composite(img, (px, py))
    return base
save(plate(logo, 1000), 'logo-plate')
save(plate(logo, 480), 'logo-plate-480')

# check composites on dark + checker for QA
for nm, bgc in [('qa-on-dark', (11, 11, 13)), ('qa-on-red', (215, 38, 30))]:
    c = Image.new('RGBA', logo.size, bgc + (255,)); c.alpha_composite(logo); c.convert('RGB').save(f'/workspace/heavyhaulers/qa/{nm}.png')

# favicon / touch icon: the full logo on a white rounded square (the client's art, unmodified)
def icon(size, full=True):
    W = 1024
    can = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    mask = Image.new('L', (W, W), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, W - 1], radius=180, fill=255)
    can.paste(Image.new('RGBA', (W, W), (255, 255, 255, 255)), (0, 0), mask)
    src = logo if full else mark
    s = min(W * 0.9 / src.width, W * 0.9 / src.height)
    r = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
    can.alpha_composite(r, ((W - r.width) // 2, (W - r.height) // 2))
    return can.resize((size, size), Image.LANCZOS)
# truck + HV crop (reads better small than the full lockup); coords on the trimmed logo
lw, lh = logo.size
mark = logo.crop((round(lw * 0.245), 0, round(lw * 0.99), round(lh * 0.565)))
mark.save(os.path.join(OUT, 'mark-truck-hv.png'))
for s in (16, 32, 48, 64):
    icon(s, full=False).save(os.path.join(OUT, f'favicon-{s}.png'))
for s in (180, 192, 512):
    icon(s, full=True).save(os.path.join(OUT, f'icon-{s}.png'))
ims = [Image.open(os.path.join(OUT, f'favicon-{s}.png')) for s in (16, 32, 48)]
ims[2].save(os.path.join(OUT, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
print('ok')
