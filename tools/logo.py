"""Heavy Haulers & Junk Removal — tightened vector logo (text converted to paths)."""
import os, io
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'brand')
os.makedirs(OUT, exist_ok=True)
FONT = os.path.join(ROOT, 'brand', 'Smokum-Regular.ttf')
FONT_B = os.path.join(ROOT, 'brand', 'Anton-Regular.ttf')

BLACK = '#0d0d0f'; RED = '#d7261e'; STEEL = '#8a9097'; WHITE = '#ffffff'; DARK = '#1b1c1f'

def text_path(fontfile, text, cx, base, size, tracking=0, sx=1.0):
    f = TTFont(fontfile); gs = f.getGlyphSet(); cmap = f.getBestCmap()
    upm = f['head'].unitsPerEm; s = size / upm
    names = [cmap[ord(c)] for c in text]
    widths = [f['hmtx'][n][0] * s * sx + tracking for n in names]
    total = sum(widths) - tracking
    x = cx - total / 2
    out = []
    for n, w in zip(names, widths):
        pen = SVGPathPen(gs)
        tp = TransformPen(pen, (s * sx, 0, 0, -s, x, base))
        gs[n].draw(tp)
        d = pen.getCommands()
        if d: out.append(d)
        x += w
    return ' '.join(out), total

def star(cx, cy, r, ri=None):
    import math
    ri = ri or r * 0.42
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else ri
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return 'M' + ' L'.join(pts) + 'Z'

def block_h(x, y, w, h):
    """Chunky block H as a single path."""
    t = w * 0.34; mid = h * 0.40; mh = h * 0.22
    return (f"M{x},{y} h{t} v{mid} h{w-2*t} v{-mid} h{t} v{h} h{-t} v{-(h-mid-mh)} "
            f"h{-(w-2*t)} v{h-mid-mh} h{-t} Z")

def truck(c_body=BLACK, c_detail=WHITE, junk=True, c_h=RED, c_h2=STEEL, c_junk=DARK, ox=0, oy=0):
    """Side-profile lifted crew-cab pickup hauling a load, with the red/gray H behind the bed."""
    g = [f'<g transform="translate({ox},{oy})">']
    if c_h:
        g.append(f'<path d="{block_h(640,10,210,250)}" fill="{c_h2}" transform="translate(34,14)"/>')
        g.append(f'<path d="{block_h(640,10,210,250)}" fill="{c_h}"/>')
    if junk:
        # load piled in the bed: bags + planks
        g.append(f'<path d="M640,232 C640,190 668,170 700,176 C716,150 752,150 764,178 C792,172 816,194 812,232 Z" fill="{c_junk}" stroke="{c_detail}" stroke-width="6"/>')
        g.append(f'<path d="M598,216 L742,150 L750,166 L606,232 Z" fill="{c_detail}" stroke="{c_body}" stroke-width="5"/>')
        g.append(f'<path d="M760,232 L800,128 L818,136 L780,236 Z" fill="{c_detail}" stroke="{c_body}" stroke-width="5"/>')
        g.append(f'<path d="M700,182 q10,-6 18,4" fill="none" stroke="{c_detail}" stroke-width="5" stroke-linecap="round"/>')
    # body
    body = ("M176,318 L178,262 Q180,246 198,242 L372,226 L432,152 Q438,146 450,146 L604,144 Q616,144 618,156 "
            "L624,222 L846,222 Q856,222 856,232 L858,322 Q858,336 844,336 L775,336 A86,86 0 0 0 603,336 "
            "L387,336 A86,86 0 0 0 215,336 L188,336 Q176,336 176,318 Z")
    g.append(f'<path d="{body}" fill="{c_body}"/>')
    # windows
    g.append(f'<path d="M392,224 L442,162 L516,160 L516,224 Z" fill="{c_detail}"/>')
    g.append(f'<path d="M530,160 L596,158 L604,224 L530,224 Z" fill="{c_detail}"/>')
    # body crease, door seams, handles, bed rail
    g.append(f'<path d="M190,276 L846,264" stroke="{c_detail}" stroke-width="5" fill="none"/>')
    g.append(f'<path d="M523,232 L523,330 M392,232 L398,330" stroke="{c_detail}" stroke-width="4" fill="none"/>')
    g.append(f'<rect x="470" y="244" width="30" height="7" rx="3" fill="{c_detail}"/><rect x="580" y="244" width="30" height="7" rx="3" fill="{c_detail}"/>')
    g.append(f'<path d="M634,236 L846,236" stroke="{c_detail}" stroke-width="4"/>')
    # grille + headlight + bumper
    g.append(f'<path d="M180,254 L222,250 L222,292 L180,296 Z" fill="{c_detail}"/>')
    g.append(f'<path d="M186,262 h30 M186,272 h30 M186,282 h30" stroke="{c_body}" stroke-width="4"/>')
    g.append(f'<rect x="226" y="252" width="34" height="16" rx="4" fill="{c_detail}"/>')
    g.append(f'<path d="M168,306 L232,304 L232,322 L168,324 Z" fill="{c_body}" stroke="{c_detail}" stroke-width="4"/>')
    # lift kit shadow under body
    for cx in (301, 689):
        g.append(f'<circle cx="{cx}" cy="368" r="70" fill="{c_body}" stroke="{c_detail}" stroke-width="8"/>')
        g.append(f'<circle cx="{cx}" cy="368" r="40" fill="{c_detail}"/>')
        g.append(f'<circle cx="{cx}" cy="368" r="27" fill="{c_body}"/>')
        g.append(f'<circle cx="{cx}" cy="368" r="9" fill="{c_detail}"/>')
        # tread blocks
        import math
        for i in range(16):
            a = i * math.pi / 8
            x1 = cx + 62 * math.cos(a); y1 = 368 + 62 * math.sin(a)
            x2 = cx + 52 * math.cos(a); y2 = 368 + 52 * math.sin(a)
            g.append(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" stroke="{c_detail}" stroke-width="5"/>')
    g.append('</g>')
    return '\n'.join(g)

def wordmark(cx, base, size, color, sx=1.0, tracking=8, stroke=7):
    d, w = text_path(FONT, 'HEAVY HAULERS', cx, base, size, tracking, sx)
    return f'<path d="{d}" fill="{color}" stroke="{color}" stroke-width="{stroke}" stroke-linejoin="round"/>', w

def banner(cx, top, w, color_red=RED, color_black=BLACK, color_text=WHITE, size=66):
    """Red '& JUNK REMOVAL' chevron banner with stars inside a black shield."""
    l = cx - w / 2; r = cx + w / 2
    h1 = 92  # straight part height
    pt = 76  # chevron depth
    pad = 22
    outer = (f"M{l-pad-60},{top-pad} L{r+pad+60},{top-pad} L{r+pad},{top+18} L{r+pad},{top+h1} L{cx},{top+h1+pt+pad*1.6} "
             f"L{l-pad},{top+h1} L{l-pad},{top+18} Z")
    inner = f"M{l},{top} L{r},{top} L{r},{top+h1-6} L{cx},{top+h1+pt-6} L{l},{top+h1-6} Z"
    d, tw = text_path(FONT, '& JUNK REMOVAL', cx, top + 70, size, 8, 1.0)
    parts = [f'<path d="{outer}" fill="{color_black}"/>', f'<path d="{inner}" fill="{color_red}"/>',
             f'<path d="{d}" fill="{color_text}" stroke="{color_text}" stroke-width="3" stroke-linejoin="round"/>']
    sy = top + h1 + 12
    for i, (dx, rr) in enumerate([(-130, 11), (-66, 13), (0, 17), (66, 13), (130, 11)]):
        parts.append(f'<path d="{star(cx+dx, sy + (0 if dx==0 else -4), rr)}" fill="{color_text}"/>')
    return '\n'.join(parts)

def svg(w, h, body, bg=None):
    b = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{b}{body}</svg>'

def stacked(dark=False, mono=None):
    body_c = WHITE if dark else BLACK
    det = BLACK if dark else WHITE
    red, steel, txt = RED, STEEL, WHITE
    if mono:
        body_c, det, red, steel = mono, ('#fff' if mono != '#fff' else '#000'), mono, mono
    parts = [truck(c_body=body_c, c_detail=det, c_h=red, c_h2=(steel if not mono else None) or None, c_junk=(DARK if not dark else '#e9e9ea') if not mono else mono, ox=-12, oy=6)]
    wm, _ = wordmark(500, 556, 156, body_c, sx=0.96)
    parts.append(wm)
    if mono:
        parts.append(banner(500, 612, 520, color_red=mono, color_black=mono, color_text=det))
    else:
        parts.append(banner(500, 612, 520, color_red=RED, color_black=(BLACK if not dark else WHITE), color_text=WHITE))
    return svg(1000, 830, '\n'.join(parts))

def horizontal(dark=False):
    fg = WHITE if dark else BLACK; det = BLACK if dark else WHITE
    t = truck(c_body=fg, c_detail=det, c_junk=(DARK if not dark else '#e9e9ea'))
    parts = [f'<g transform="translate(-70,8) scale(0.56)">{t}</g>']
    _, w = text_path(FONT, 'HEAVY HAULERS', 0, 0, 150, 8, 0.96)
    cx = 470 + w / 2
    wm, w = wordmark(cx, 168, 150, fg, sx=0.96)
    parts.append(wm)
    d, _ = text_path(FONT, '& JUNK REMOVAL', cx, 262, 62, 9)
    l = cx - w / 2; r = cx + w / 2
    parts.append(f'<path d="M{l},200 L{r},200 L{r-22},282 L{l+22},282 Z" fill="{RED}"/>')
    parts.append(f'<path d="{d}" fill="#fff" stroke="#fff" stroke-width="2.5"/>')
    for x in (l + 52, r - 52):
        parts.append(f'<path d="{star(x, 241, 13)}" fill="#fff"/>')
    return svg(int(r + 20), 300, '\n'.join(parts))

def emblem(bg=BLACK, fg=RED, star_c=WHITE, size=512, rounded=True):
    # shield (chevron) with block H and star — reads at 16-32px
    p = []
    if rounded:
        p.append(f'<rect width="512" height="512" rx="96" fill="{bg}"/>')
        shield = "M64,72 L448,72 L448,318 L256,470 L64,318 Z"
        p.append(f'<path d="{shield}" fill="{fg}"/>')
        p.append(f'<path d="{block_h(150,118,212,232)}" fill="{star_c}"/>')
        p.append(f'<path d="{star(256,402,30)}" fill="{star_c}"/>')
    return svg(512, 512, '\n'.join(p))

def write(name, s):
    open(os.path.join(OUT, name), 'w').write(s)

def png(svgstr, path, w=None, h=None):
    cairosvg.svg2png(bytestring=svgstr.encode(), write_to=path, output_width=w, output_height=h)

if __name__ == '__main__':
    files = {
        'logo-stacked.svg': stacked(), 'logo-stacked-dark.svg': stacked(dark=True),
        'logo-stacked-black.svg': stacked(mono=BLACK), 'logo-stacked-white.svg': stacked(mono='#fff'),
        'logo-horizontal.svg': horizontal(), 'logo-horizontal-dark.svg': horizontal(dark=True),
        'emblem.svg': emblem(), 'emblem-red.svg': emblem(bg=RED, fg=BLACK),
        'truck-mark.svg': svg(900, 450, truck()),
    }
    for k, v in files.items(): write(k, v)
    png(files['logo-stacked.svg'], os.path.join(OUT, 'logo-stacked.png'), 1400)
    png(files['logo-stacked-dark.svg'], os.path.join(OUT, 'logo-stacked-dark.png'), 1400)
    png(files['logo-horizontal.svg'], os.path.join(OUT, 'logo-horizontal.png'), 1600)
    for s in (16, 32, 48, 180, 192, 512):
        png(files['emblem.svg'], os.path.join(OUT, f'favicon-{s}.png'), s, s)
    ims = [Image.open(os.path.join(OUT, f'favicon-{s}.png')) for s in (16, 32, 48)]
    ims[2].save(os.path.join(OUT, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
    print('ok')
