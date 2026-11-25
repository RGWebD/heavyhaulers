"""Logo presentation sheet -> brand/logo-presentation.png (rendered with Chrome)."""
import os, asyncio, base64
from playwright.async_api import async_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(R, 'brand')
def u(f):
    data = open(os.path.join(B, f), 'rb').read()
    mt = 'image/svg+xml' if f.endswith('.svg') else 'image/png'
    return f'data:{mt};base64,' + base64.b64encode(data).decode()
orig = 'data:image/png;base64,' + base64.b64encode(open('/workspace/heavyhaulers/uploads/logo.png', 'rb').read()).decode()
font = lambda f: 'data:font/ttf;base64,' + base64.b64encode(open(os.path.join(B, f), 'rb').read()).decode()
HTML = f'''<html><head><style>
@font-face{{font-family:Anton;src:url({font('Anton-Regular.ttf')})}}
@font-face{{font-family:Smokum;src:url({font('Smokum-Regular.ttf')})}}
*{{margin:0;box-sizing:border-box}} body{{width:2400px;background:#e9e7e2;font-family:Inter,Arial,sans-serif;color:#111;padding:70px}}
h1{{font-family:Anton;font-size:96px;text-transform:uppercase;line-height:1}} .k{{font-family:Smokum;color:#d7261e;font-size:34px;letter-spacing:2px}}
.g{{display:grid;gap:30px;margin-top:40px}} .c{{border-radius:22px;padding:40px;display:flex;align-items:center;justify-content:center;position:relative}}
.c span{{position:absolute;left:22px;top:16px;font-size:16px;font-weight:700;letter-spacing:2px;text-transform:uppercase;opacity:.6}}
.w{{background:#fff}} .d{{background:#0b0b0d;color:#fff}} .r{{background:#d7261e;color:#fff}} .s{{background:#8a9097}}
.sw{{display:flex;gap:20px;margin-top:30px}} .sw div{{flex:1;height:170px;border-radius:18px;padding:18px;display:flex;flex-direction:column;justify-content:flex-end;font-weight:800;font-size:22px}}
.sw small{{font-weight:500;font-size:17px;opacity:.85}}
.fav{{display:flex;gap:40px;align-items:flex-end}} .fav figure{{text-align:center;font-size:15px;font-weight:700}}
.ty{{display:flex;gap:40px;margin-top:30px}} .ty div{{flex:1;background:#fff;border-radius:18px;padding:28px}}
</style></head><body>
<div class="k">— RGWebD brand refresh</div><h1>Heavy Haulers &amp; Junk Removal · Logo</h1>
<p style="font-size:22px;margin-top:14px;max-width:1500px">Tightened from the original mark: same lifted pickup, red &amp; steel “H”, western slab wordmark and the red “&amp; Junk Removal” banner with stars. Redrawn as clean vector shapes (text converted to paths), simplified so it holds up on a truck door, a shirt and a 16-pixel browser tab.</p>
<div class="g" style="grid-template-columns:1fr 1.25fr 1.25fr">
 <div class="c w" style="flex-direction:column"><span>Before (original)</span><img src="{orig}" style="width:100%;max-width:520px"></div>
 <div class="c w"><span>After · primary stacked</span><img src="{u('logo-stacked.svg')}" style="width:88%"></div>
 <div class="c d"><span>Reversed · dark</span><img src="{u('logo-stacked-dark.svg')}" style="width:88%"></div>
</div>
<div class="g" style="grid-template-columns:1.6fr 1fr">
 <div class="c w" style="height:330px"><span>Horizontal lockup</span><img src="{u('logo-horizontal.svg')}" style="width:92%"></div>
 <div class="c d" style="height:330px"><span>Horizontal · dark</span><img src="{u('logo-horizontal-dark.svg')}" style="width:92%"></div>
</div>
<div class="g" style="grid-template-columns:1fr 1fr 1fr 1.4fr">
 <div class="c w"><span>One-color black</span><img src="{u('logo-stacked-black.svg')}" style="width:80%"></div>
 <div class="c r"><span>One-color white</span><img src="{u('logo-stacked-white.svg')}" style="width:80%"></div>
 <div class="c s"><span>Truck mark</span><img src="{u('truck-mark.svg')}" style="width:92%"></div>
 <div class="c w"><span>Emblem + favicons</span><div class="fav">
   <figure><img src="{u('emblem.svg')}" width="200"><br>512</figure><figure><img src="{u('emblem-red.svg')}" width="120"><br>alt</figure>
   <figure><img src="{u('favicon-180.png')}" width="64"><br>180</figure><figure><img src="{u('favicon-32.png')}" width="32"><br>32</figure><figure><img src="{u('favicon-16.png')}" width="16"><br>16</figure></div></div>
</div>
<div class="sw">
 <div style="background:#0b0b0d;color:#fff">Haul Black<small>#0B0B0D</small></div>
 <div style="background:#d7261e;color:#fff">Racing Red<small>#D7261E</small></div>
 <div style="background:#ff3d31;color:#fff">Signal Red<small>#FF3D31 (screen accent)</small></div>
 <div style="background:#8a9097;color:#fff">Steel Gray<small>#8A9097</small></div>
 <div style="background:#fff;color:#111;border:2px solid #ccc">White<small>#FFFFFF</small></div>
</div>
<div class="ty">
 <div><div style="font-family:Smokum;font-size:64px">HEAVY HAULERS</div><b>Smokum</b> — western slab wordmark &amp; accent labels</div>
 <div><div style="font-family:Anton;font-size:64px;text-transform:uppercase">These guys mean business</div><b>Anton</b> — website headlines</div>
 <div><div style="font-size:40px;font-weight:600;padding:12px 0">Inter — body copy</div><b>Inter</b> — paragraphs, buttons, forms</div>
</div>
</body></html>'''
async def m():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 2400, 'height': 1000})
        await pg.set_content(HTML); await pg.wait_for_timeout(800)
        await pg.screenshot(path=os.path.join(B, 'logo-presentation.png'), full_page=True)
        await b.close()
asyncio.run(m())
print('ok')
