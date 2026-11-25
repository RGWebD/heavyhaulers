"""Curate + export real Heavy Haulers photos to WebP. Sources: GBP (g##) and Reese's uploads."""
import os
from PIL import Image, ImageFilter, ImageDraw
SRC = '/workspace/heavyhaulers'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')

def load(p):
    return Image.open(os.path.join(SRC, p)).convert('RGB')

def blur_box(im, box, r=18):
    reg = im.crop(box).filter(ImageFilter.GaussianBlur(r))
    im.paste(reg, box); return im

def save(im, name, maxw=1600, q=80):
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(os.path.join(OUT, name + '.webp'), 'WEBP', quality=q, method=6)
    print(name, im.size)

PLAN = [
    # (source, out-name, crop or None, blur boxes, maxw)
    ('gbp/g18.jpg', 'crew', None, [], 2000),
    ('gbp/g14.jpg', 'crew-four', None, [], 1400),
    ('gbp/g18.jpg', 'crew-wide', (0, 330, 2000, 1333), [], 2000),
    ('gbp/g30.jpg', 'dumpster-downtown-crop', (0, 230, 1350, 1010), [], 1350),
    ('gbp/g11.jpg', 'demo-sledgehammers', None, [], 1600),
    ('gbp/g29.jpg', 'demo-cutting-sparks', None, [], 1080),
    ('gbp/g13.jpg', 'dumpster-loaded', None, [], 1200),
    ('gbp/g27.jpg', 'dumpster-trailer', None, [], 1024),
    ('gbp/g30.jpg', 'dumpster-downtown', None, [], 1600),
    ('gbp/g15.jpg', 'dumpster-decal', None, [], 1080),
    ('gbp/g10.jpg', 'bobcat-grapple', None, [(965, 745, 1060, 812)], 1080),
    ('uploads/bobcat-clearing.png', 'bobcat-clearing', None, [], 1218),
    ('uploads/kubota-track-loader.png', 'kubota-track-loader', None, [], 968),
    ('gbp/g09.jpg', 'jlg-telehandler', None, [], 1600),
    ('gbp/g20.jpg', 'volvo-excavator', None, [], 1200),
    ('gbp/g28.jpg', 'hot-tub-removal', None, [], 1200),
    ('gbp/g08.jpg', 'hot-tub-trailer', None, [], 1200),
    ('gbp/g06.jpg', 'decking-debris', None, [], 1600),
    ('gbp/g26.jpg', 'lumber-pile', None, [], 1200),
    ('gbp/g31.jpg', 'cleanout-empty-room', None, [], 1600),
    ('gbp/g01.jpg', 'yard-cleared', None, [], 1600),
]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for src, name, crop, blurs, mw in PLAN:
        im = load(src)
        for b in blurs: blur_box(im, b)
        if crop: im = im.crop(crop)
        save(im, name, mw)
    # rooftop deck demolition before/after (g02 before; g24 after, cropped clear of its inset + label)
    after = load('gbp/g24.jpg').crop((0, 0, 642, 364))
    after = after.resize((1280, round(364 * 1280 / 642)), Image.LANCZOS)
    before = load('gbp/g02.jpg')
    h = round(before.width * after.height / after.width)
    before = before.crop((0, 1500 - h - 40, 2000, 1500 - 40)).resize(after.size, Image.LANCZOS)
    save(before, 'rooftop-before', 1280); save(after, 'rooftop-after', 1280)
