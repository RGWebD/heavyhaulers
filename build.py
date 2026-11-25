#!/usr/bin/env python3
"""Heavy Haulers & Junk Removal — static site generator (RGWebD).
Facts come from site.json (sourced in notes_gbp.md). Output: docs/ (GitHub Pages)."""
import json, os, shutil, html, sys
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs')
D = json.load(open(os.path.join(ROOT, 'site.json')))
BASE = os.environ.get('BASE_URL', D['base_url'])
TEL = 'tel:' + D['phone_e164']
SMS = 'sms:' + D['phone_e164']
E = html.escape
YEAR = 2026

def isize(name):
    with Image.open(os.path.join(ROOT, 'img', name + '.webp')) as im:
        return im.size

def img(name, alt, cls='', lazy=True, extra=''):
    w, h = isize(name)
    la = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high" decoding="async"'
    c = f' class="{cls}"' if cls else ''
    return f'<img src="img/{name}.webp" width="{w}" height="{h}" alt="{E(alt)}"{c}{la}{extra}>'

I_PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>'
I_SMS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'
I_ARROW = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.6" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

PAGES = [('index.html', 'Home'), ('services.html', 'Services'), ('fleet.html', 'The Fleet'),
         ('crew.html', 'The Crew'), ('reviews.html', 'Reviews'), ('contact.html', 'Contact')]

ADDR = f"{D['street']}, {D['city']}, {D['region']} {D['zip']}"
HOURS_LINE = 'Mon–Sat 8 AM–5 PM · Sun closed'
DAYS = [('Mo', 'Monday'), ('Tu', 'Tuesday'), ('We', 'Wednesday'), ('Th', 'Thursday'), ('Fr', 'Friday'), ('Sa', 'Saturday'), ('Su', 'Sunday')]

def fmt_t(t):
    h, m = int(t[:2]), t[3:]
    ap = 'PM' if h >= 12 else 'AM'; h = h % 12 or 12
    return f"{h}{'' if m == '00' else ':' + m} {ap}"

def business_ld(full=True):
    ld = {
        "@context": "https://schema.org", "@type": "HomeAndConstructionBusiness", "@id": BASE + "#business",
        "name": D['name'], "url": BASE, "telephone": D['phone'], "image": BASE + "img/crew.webp",
        "logo": BASE + "brand/logo-stacked.png",
        "description": "Junk removal, demolition, house and garage cleanouts, construction and yard debris removal, appliance, furniture and hot tub removal in Orange Park and the Jacksonville area. Black-owned. Call or text (904) 576-1110 for a free quote.",
        "address": {"@type": "PostalAddress", "streetAddress": D['street'], "addressLocality": D['city'], "addressRegion": D['region'], "postalCode": D['zip'], "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": D['lat'], "longitude": D['lng']},
        "hasMap": D['maps_url'],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": full_day, "opens": D['hours'][k][0], "closes": D['hours'][k][1]} for k, full_day in DAYS if D['hours'][k]],
        "sameAs": [D['maps_url'], D['instagram']],
        "areaServed": [{"@type": "City", "name": "Orange Park, FL"}, {"@type": "City", "name": "Jacksonville, FL"}],
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": "5.0", "bestRating": "5", "reviewCount": str(D['review_count'])},
        "knowsAbout": ["Junk removal", "Demolition", "House cleanouts", "Garage cleanouts", "Construction debris removal", "Yard debris removal", "Appliance removal", "Furniture removal", "Hot tub removal"],
    }
    if full:
        ld["review"] = [{"@type": "Review", "author": {"@type": "Person", "name": r['name']},
                         "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                         "reviewBody": r['text'], "publisher": {"@type": "Organization", "name": "Google"}} for r in D['reviews']]
    return ld

def crumbs_ld(title, href):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
        {"@type": "ListItem", "position": 2, "name": title, "item": BASE + href}]}

def head(href, title, desc, ld, og='og.jpg'):
    can = BASE + ('' if href == 'index.html' else href)
    lds = '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{can}">
<meta name="theme-color" content="#0b0b0d">
<meta property="og:type" content="website"><meta property="og:site_name" content="{E(D['name'])}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{can}"><meta property="og:image" content="{BASE}{og}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{BASE}{og}">
<link rel="icon" href="brand/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="brand/emblem.svg">
<link rel="icon" type="image/png" sizes="32x32" href="brand/favicon-32.png">
<link rel="apple-touch-icon" href="brand/favicon-180.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700;800&family=Smokum&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css?v=3">
{lds}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"></div>
'''

def nav(href):
    items = ''.join(f'<li><a href="{h}"{" aria-current=\"page\"" if h == href else ""}>{t}</a></li>' for h, t in PAGES[1:])
    mitems = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if h == href else ""}>{t}</a>' for h, t in PAGES)
    return f'''<header class="nav" role="banner">
  <a class="brand" href="index.html" aria-label="{E(D['name'])} home"><img src="brand/logo-horizontal-dark.svg" width="200" height="48" alt="{E(D['name'])}"></a>
  <nav aria-label="Main"><ul>{items}</ul></nav>
  <div class="ctas"><a class="btn sm ghost" href="{SMS}">{I_SMS}Text</a><a class="btn sm" href="{TEL}" data-magnet>{I_PHONE}{D['phone']}</a></div>
  <button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="mmenu"><span></span><span></span><span></span></button>
</header>
<div class="mmenu" id="mmenu" aria-hidden="true">{mitems}
  <div class="mm-meta"><a class="btn" href="{TEL}" style="font-family:var(--body);font-size:16px;margin-bottom:12px">{I_PHONE}Call {D['phone']}</a><br>{E(ADDR)}<br>{HOURS_LINE}</div>
</div>
'''

def footer():
    links = ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in PAGES)
    hrs = ''.join(f'<li>{full[:3]}: {(fmt_t(D["hours"][k][0]) + "–" + fmt_t(D["hours"][k][1])) if D["hours"][k] else "Closed"}</li>' for k, full in DAYS)
    return f'''<footer>
  <div class="wrap">
    <div class="fgrid">
      <div><img class="flogo" src="brand/logo-stacked-dark.svg" width="230" height="191" alt="{E(D['name'])} logo" loading="lazy">
        <p>Junk removal, demolition and cleanouts for Orange Park, Jacksonville and the surrounding area. Black-owned. 5.0 stars from {D['review_count']} Google reviews.</p></div>
      <div><h4>Pages</h4><ul>{links}</ul></div>
      <div><h4>Find us</h4><ul><li>{E(D['street'])}<br>{D['city']}, {D['region']} {D['zip']}</li>
        <li><a href="{TEL}">{D['phone']}</a> (call or text)</li>
        <li><a href="{E(D['maps_url'])}" target="_blank" rel="noopener">Google Maps &amp; reviews</a></li>
        <li><a href="{D['instagram']}" target="_blank" rel="noopener">Instagram</a></li></ul></div>
      <div><h4>Hours</h4><ul>{hrs}</ul></div>
    </div>
    <div class="fbase"><span>© {YEAR} {E(D['name'])} · {E(ADDR)}</span><span>Design preview by <a href="https://rgwebd.github.io/rgwebd/" target="_blank" rel="noopener">RGWebD</a></span></div>
  </div>
</footer>
<div class="mbar" role="region" aria-label="Quick contact"><a class="btn" href="{TEL}">{I_PHONE}Call</a><a class="btn ghost" href="{SMS}">{I_SMS}Text a photo</a></div>
<div class="pill" role="note">Design preview by <a href="https://rgwebd.github.io/rgwebd/" target="_blank" rel="noopener">RGWebD</a><button type="button" aria-label="Dismiss preview note">×</button></div>
<script>window.HH_HOURS={json.dumps({k: v for k, v in D['hours'].items() if v})};</script>
<script src="assets/site.js?v=3" defer></script>
</body></html>
'''

def stars(n=5): return '★' * n

def chip_row():
    return f'''<a class="chip" href="reviews.html"><span class="stars" aria-hidden="true">★★★★★</span> 5.0 · {D['review_count']} Google reviews</a>
      <span class="chip open-badge"><span class="dot" aria-hidden="true"></span><span class="t">{HOURS_LINE}</span></span>'''

def cta_band(title='Got junk?<br>Call the crew.', sub=None):
    sub = sub or 'Call or text (904) 576-1110 — snap a photo of the pile and get a free quote.'
    return f'''<section class="cta-band pad" aria-label="Get a free quote">
  <div class="bigtype" aria-hidden="true">HAUL IT</div>
  <div class="wrap"><h2 class="rv-up">{title}</h2><p class="rv-up">{sub}</p>
  <div class="acts rv-up"><a class="btn xl" href="{TEL}" data-magnet>{I_PHONE}{D['phone']}</a><a class="btn xl ghost" href="{SMS}">{I_SMS}Text for a free quote</a></div></div>
</section>'''

def phero(href, title, kicker, h1, lead, media, bigtype):
    return f'''<section class="phero">
  <div class="bigtype" aria-hidden="true" data-speed="-0.08">{bigtype}</div>
  <div class="wrap phero-grid">
    <div>
      <div class="crumbs"><a href="index.html">Home</a> / <span aria-current="page">{E(title)}</span></div>
      <p class="kicker">{kicker}</p>
      <h1 data-split>{h1}</h1>
      <p class="lead rv-up">{lead}</p>
      <div class="acts rv-up"><a class="btn" href="{TEL}" data-magnet>{I_PHONE}Call {D['phone']}</a><a class="btn ghost" href="{SMS}">{I_SMS}Text a photo</a></div>
    </div>
    <div class="pframe rv-up">{media}</div>
  </div>
</section>'''

def short_reviews():
    pick = ['David Jasper', 'Miranda Lowe', 'Steve Jones', 'Samuel Sobrino', 'Wayne Smith', 'Alice Conte', 'Carrie Fernandez']
    by = {r['name']: r for r in D['reviews']}
    out = []
    for n in pick:
        r = by[n]
        out.append(f'''<div class="rcard" role="group" aria-roledescription="slide"><div class="in"><div class="qmark" aria-hidden="true">“</div><div>
<p>{E(r['text'])}</p><div class="who"><span class="stars" aria-label="5 stars">★★★★★</span>{E(r['name'])} · Google · {E(r['age'])}</div></div></div></div>''')
    return ''.join(out)

def gauge(frac, val, dec, label, suffix=''):
    import math
    # 240° arc, radius 100, centre 130,130
    L = 2 * math.pi * 100 * 240 / 360
    def pt(a):
        r = math.radians(a - 90); return 130 + 100 * math.cos(r), 130 + 100 * math.sin(r)
    x1, y1 = pt(-120); x2, y2 = pt(120)
    arc = f'M{x1:.1f},{y1:.1f} A100,100 0 1 1 {x2:.1f},{y2:.1f}'
    ticks = ''
    for i in range(13):
        a = -120 + i * 20; r1 = 86 if i % 3 == 0 else 92
        rad = math.radians(a - 90)
        ticks += f'<line x1="{130 + r1 * math.cos(rad):.1f}" y1="{130 + r1 * math.sin(rad):.1f}" x2="{130 + 100 * math.cos(rad):.1f}" y2="{130 + 100 * math.sin(rad):.1f}" stroke="#555a61" stroke-width="{3 if i % 3 == 0 else 2}"/>'
    return f'''<div class="gauge rv-up" data-frac="{frac:.4f}">
  <svg viewBox="0 0 260 190" aria-hidden="true">
    <path d="{arc}" fill="none" stroke="#24262b" stroke-width="16" stroke-linecap="round"/>
    <path class="arc-fill" d="{arc}" fill="none" stroke="url(#gr)" stroke-width="16" stroke-linecap="round" stroke-dasharray="{L:.1f}" stroke-dashoffset="{L:.1f}" data-len="{L:.1f}"/>
    <defs><linearGradient id="gr" x1="0" x2="1"><stop offset="0" stop-color="#9e1a14"/><stop offset="1" stop-color="#ff3d31"/></linearGradient></defs>
    {ticks}
    <g class="needle"><path d="M127,130 L130,46 L133,130 Z" fill="#fff"/><circle cx="130" cy="130" r="11" fill="#d7261e" stroke="#fff" stroke-width="3"/></g>
  </svg>
  <div class="val"><span data-count="{val}" data-dec="{dec}">{val:.{dec}f}</span>{suffix}</div>
  <div class="lbl">{label}</div>
</div>'''

FLEET = [
    dict(id='dumpster', no='01', name='Dumpster Trailer', tag='Heavy Haulers branded',
         img='dumpster-trailer', alt='Heavy Haulers black dumpster trailer loaded with old lumber, lettered 904.576.1110',
         inset='dumpster-decal', inset_alt='Heavy Haulers & Junk Removal logo decal on the dumpster door',
         blurb='The big black box with the red lettering. It rolls up to the curb, swallows a whole house worth of junk, and leaves with it.',
         role='Hauling loads off site: cleanouts, construction debris, yard debris', look='Black roll-off box, red & white reflective tape, "904.576.1110" on the side',
         lettered='Junk Removal · Demolition · House Clean Outs · Construction · Yard Debris Removal'),
    dict(id='bobcat', no='02', name='Bobcat Track Loader', tag='Grapple bucket',
         img='bobcat-grapple', alt='White Bobcat compact track loader with a grapple bucket loading debris into a black dump trailer',
         inset='bobcat-clearing', inset_alt='Bobcat track loader grabbing a pile of cleared palm debris',
         blurb='Grapple jaws up front, tracks underneath. This is the machine that grabs a whole brush pile and drops it in the trailer in a few bites.',
         role='Brush and debris piles, land clearing, loading trailers', look='White compact track loader with a grapple attachment', lettered=None),
    dict(id='kubota', no='03', name='Kubota Track Loader', tag='Site work',
         img='kubota-track-loader', alt='Orange Kubota compact track loader with bucket next to a pile of sand on a job site',
         inset=None, inset_alt=None,
         blurb='A second set of tracks for bigger jobs: pushing dirt, moving material and keeping the site moving.',
         role='Moving material, grading and site cleanup', look='Orange Kubota compact track loader with a bucket', lettered=None),
    dict(id='jlg', no='04', name='JLG Telehandler', tag='Reach + lift',
         img='jlg-telehandler', alt='Orange JLG telehandler with pallet forks on a sandy job site beside concrete pipe',
         inset=None, inset_alt=None,
         blurb='When it is too heavy to carry and too high to reach, the telehandler does the lifting.',
         role='Lifting and placing heavy material on job sites', look='Orange JLG telescopic handler with pallet forks', lettered=None),
    dict(id='excavator', no='05', name='Volvo Excavator', tag='Demolition muscle',
         img='volvo-excavator', alt='Volvo excavator digging out a roadside strip, operator in an orange safety shirt', portrait=True,
         inset=None, inset_alt=None,
         blurb='The heavy end of the fleet photos. Buckets of dirt and concrete gone in one swing.',
         role='Digging, demolition and breaking out ground', look='Volvo tracked excavator with a dig bucket', lettered=None),
]

def page_home():
    href = 'index.html'
    title = 'Heavy Haulers & Junk Removal | Junk Removal & Demolition, Orange Park FL'
    desc = 'Orange Park junk removal, demolition and cleanouts. 5.0 stars from 216 Google reviews. Call or text (904) 576-1110 for a free quote — Mon–Sat 8–5.'
    h = head(href, title, desc, [business_ld(True)])
    units = ''.join(f'''<a class="unit" href="fleet.html#{u['id']}" data-tilt>
  <span class="tag">{u['tag']}</span>
  <div class="ph">{img(u['img'], u['alt'])}</div>
  <div class="meta"><div class="no">Unit {u['no']}</div><h3>{u['name']}</h3><p>{u['role']}</p></div></a>''' for u in FLEET)
    marquee_items = ['Junk Removal', 'Demolition', 'House Clean Outs', 'Construction Debris', 'Yard Debris', 'Hot Tub Removal', 'Appliances & Furniture', 'Garage Cleanouts']
    mq = ''.join(f'<span class="{"o" if i % 2 else ""}">{E(t)}</span><b aria-hidden="true">★</b>' for i, t in enumerate(marquee_items))
    body = f'''
<div class="loader" aria-hidden="true"><div class="door l"></div><div class="door r"></div>
  <div class="core"><img src="brand/logo-stacked-dark.svg" width="340" height="282" alt=""><div class="bar"><i></i></div></div></div>
{nav(href)}
<main id="main">
<section class="hero" aria-label="Intro">
  <div class="bg">{img('crew', 'The Heavy Haulers crew — nine guys in matching camo and red team jerseys, arms crossed, in front of white work trucks under a moss-draped live oak', lazy=False)}</div>
  <div class="inner wrap">
    <p class="kicker">Orange Park · Jacksonville</p>
    <h1 data-split><span class="ln">These guys</span> <span class="ln"><em>mean</em> business.</span></h1>
  </div>
  <div class="hero-chip">{chip_row()}</div>
</section>
<div class="wrap tailgate">
  <div class="plate"><div class="tape" aria-hidden="true"></div>
    <div class="grid rivets">
      <p><strong style="color:#fff">Junk removal, demolition and cleanouts</strong> for Orange Park and the Jacksonville area. Send a photo of the pile, get a quote, and the crew shows up ready to work.</p>
      <div class="acts"><a class="btn" href="{TEL}" data-magnet>{I_PHONE}Call {D['phone']}</a><a class="btn ghost" href="{SMS}">{I_SMS}Text for a free quote</a></div>
    </div>
  </div>
</div>

<div class="marquee" aria-label="Services"><div class="track">{mq}{mq}</div></div>

<section class="crew-moment pad" aria-labelledby="crew-h">
  <div class="bigtype" aria-hidden="true" style="left:-3vw;top:40px" data-speed="0.12">THE CREW</div>
  <div class="wrap crew-grid">
    <div class="collage">
      <div class="frame f1" data-speed="-0.05">{img('demo-sledgehammers', 'Two Heavy Haulers crew members swinging sledgehammers to break down a concrete block structure in a backyard')}</div>
      <div class="frame f2" data-speed="0.06">{img('demo-cutting-sparks', 'Crew member cutting steel bollards at ground level, sparks flying')}</div>
      <div class="frame f3" data-speed="-0.02">{img('crew-four', 'Four Heavy Haulers crew members standing in a cleared backyard')}</div>
      <div class="sticker s1">“Made it look easy!”<small>David Jasper · Google review</small></div>
    </div>
    <div>
      <p class="kicker">Hard workers, every job</p>
      <h2 id="crew-h" data-split>Built for the heavy stuff.</h2>
      <p class="lead rv-up" style="margin-top:22px">Sledgehammers, saws, trailers and track loaders. When Heavy Haulers rolls up, a real crew gets out — and they don't leave until the pile is gone and the ground is swept.</p>
      <div class="quote-list rv-up">
        <blockquote>“They never complained—not once. They just rolled up their sleeves, worked together, and got the mission accomplished.”<cite>mark smith · Google</cite></blockquote>
        <blockquote>“What would have taken me at least a half days work … took them 30 minutes.”<cite>Lisa Coe · Google</cite></blockquote>
      </div>
      <p style="margin-top:28px" class="rv-up"><a class="btn ghost" href="crew.html">Meet the crew {I_ARROW}</a></p>
    </div>
  </div>
</section>

<section class="gauges pad-s" aria-labelledby="g-h">
  <div class="wrap">
    <p class="kicker">By the numbers (Google)</p>
    <h2 id="g-h" data-split>The gauges don't lie.</h2>
    <div class="gauge-row">
      {gauge(1.0, 5.0, 1, 'Star rating on Google', '<span class="red">★</span>')}
      {gauge(216/250, 216, 0, 'Google reviews')}
      {gauge(55/216, 55, 0, 'Reviews tagged “friendly staff”')}
    </div>
  </div>
</section>

<section class="pad" aria-labelledby="fleet-h" style="overflow:hidden">
  <div class="wrap">
    <div class="rail-head"><div><p class="kicker">The fleet</p><h2 id="fleet-h" data-split>Heavy iron. Real jobs.</h2></div>
      <a class="btn ghost" href="fleet.html">See the whole fleet {I_ARROW}</a></div>
    <div class="rail" tabindex="0" aria-label="Fleet — drag or scroll sideways">{units}</div>
  </div>
</section>

<section class="pad-s" aria-labelledby="why-h">
  <div class="wrap">
    <p class="kicker">Why folks call Heavy Haulers</p>
    <h2 id="why-h" data-split>No runaround.</h2>
    <div class="why-grid">
      <div class="why rv-up"><div class="ic"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Fast turnaround</h3><p>Plenty of reviews say the crew came the same day — sometimes within the hour.</p><span class="q">“Immediately came out within an hour.” — Jordan S.</span></div>
      <div class="why rv-up"><div class="ic"><svg viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="14" rx="2"/><circle cx="12" cy="13" r="3.5"/><path d="M8 6l1.5-2h5L16 6"/></svg></div><h3>Quote from a photo</h3><p>Text a picture of the pile and get a quote back. No waiting around for an estimate visit.</p><span class="q">“I sent pictures of the pile and quickly received a quote.” — Lisa C.</span></div>
      <div class="why rv-up"><div class="ic"><svg viewBox="0 0 24 24"><path d="M3 21h18M5 21V10l7-6 7 6v11"/><path d="M9 21v-6h6v6"/></svg></div><h3>Left clean</h3><p>They load it, haul it and sweep up after themselves. Your yard and floors look better than before.</p><span class="q">“The area … was clean after job was completed.” — Wayne S.</span></div>
      <div class="why rv-up"><div class="ic"><svg viewBox="0 0 24 24"><path d="M12 21s-7-4.4-9.3-9A5.4 5.4 0 0 1 12 6a5.4 5.4 0 0 1 9.3 6C19 16.6 12 21 12 21z"/></svg></div><h3>Careful handling</h3><p>Sleeper sofas through tight doorways, hot tubs out of screened porches. Done without wrecking the house.</p><span class="q">“Took extra care to get the sofa through the doorway.” — Steve J.</span></div>
    </div>
  </div>
</section>

<section class="reviews-band pad" aria-labelledby="rv-h">
  <div class="wrap">
    <p class="kicker">5.0 ★ on Google</p>
    <h2 id="rv-h" data-split>{D['review_count']} reviews. All talk the same.</h2>
    <div class="carousel" aria-roledescription="carousel" aria-label="Customer reviews">
      <div style="overflow:hidden"><div class="car-track" aria-live="polite">{short_reviews()}</div></div>
      <div class="car-ctl"><button class="prev" type="button" aria-label="Previous review">←</button><button class="next" type="button" aria-label="Next review">→</button><div class="dots"></div>
        <a href="reviews.html" style="margin-left:auto;font-weight:800;text-transform:uppercase;letter-spacing:.06em;font-size:14px;color:#111">All reviews →</a></div>
    </div>
  </div>
</section>

<section class="pad-s" aria-labelledby="t-h">
  <div class="wrap">
    <p class="kicker">Pick your job</p>
    <h2 id="t-h" data-split>What we haul.</h2>
    <div class="teasers">
      <a class="teaser rv-up" href="services.html#junk">{img('dumpster-loaded', 'Heavy Haulers dumpster trailer piled high with bagged junk', extra=' style="object-position:50% 22%"')}<div class="t"><h3>Junk removal</h3><span>Services {I_ARROW}</span></div></a>
      <a class="teaser rv-up" href="services.html#demolition">{img('rooftop-before', 'Old rooftop deck structure on a downtown building before demolition')}<div class="t"><h3>Demolition</h3><span>Services {I_ARROW}</span></div></a>
      <a class="teaser rv-up" href="services.html#hot-tubs">{img('hot-tub-removal', 'Two crew members tipping a hot tub on its side on a pool deck')}<div class="t"><h3>Hot tubs &amp; heavy items</h3><span>Services {I_ARROW}</span></div></a>
    </div>
  </div>
</section>
{cta_band()}
</main>
'''
    return h + body + footer()

SERVICES = [
    dict(id='junk', n='01', t='Junk removal', img='dumpster-loaded', tall=True,
         alt='Heavy Haulers dumpster trailer piled high with bags and boxes of junk, lettered 904.576.1110',
         p='Old furniture, boxes, bagged trash, moving leftovers, rental turnovers — if you want it gone, the crew loads it and hauls it away. You point, they lift.',
         ex=['A pile of cardboard after a move — broken down and gone within an hour (Jordan S.)', 'A rental property cleared out the same day, in about an hour (Samuel S.)', '“A fast pickup of a ton of junk” — same day (Carrie F.)']),
    dict(id='demolition', n='02', t='Demolition', img='demo-sledgehammers', img2='demo-cutting-sparks',
         alt='Two crew members swinging sledgehammers to break down a concrete block structure', alt2='Crew member cutting steel bollards at ground level, sparks flying',
         p='Their Facebook page calls them “Jacksonville\'s Trusted Demolition Experts.” Full homes, mobile homes, interiors and backyard demos — they break it down, load the rubble and haul it off.',
         ex=['Full home and mobile home demos (from their Facebook page)', 'Interior tear-outs', 'Backyard demo: block walls, slabs, old structures', 'Cutting out steel posts and bollards']),
    dict(id='cleanouts', n='03', t='House & garage cleanouts', img='cleanout-empty-room',
         alt='Empty living room with brick fireplace after a cleanout',
         p='Estates, move-outs, rentals and garages packed to the rafters. They clear the whole place room by room and leave it empty and broom-clean.',
         ex=['A multigenerational house and property, cleared under a tight deadline (mark smith)', 'Old furniture and trash out of a garage in about 10 minutes (Jaiden W.)']),
    dict(id='construction', n='04', t='Construction debris', img='decking-debris', img2='lumber-pile',
         alt='Pile of old decking boards and lumber waiting for pickup', alt2='Heap of torn-out lumber and boards in a backyard',
         p='Old decking, lumber, drywall and job-site leftovers. Skip the truck rental and the landfill run — they load it and take it.',
         ex=['A pile of old decking hauled off in 30 minutes (Lisa C.)', 'Debris off site within 24 hours of calling (Samantha M.)']),
    dict(id='yard', n='05', t='Yard debris', img='yard-cleared',
         alt='Backyard cleared of brush and debris down to bare ground',
         p='Tree brush, limbs, palm fronds and overgrowth. If you bit off more than you could chew with the yard work, call the guys with the grapple.',
         ex=['“A mountain of tree brush we could never bag up” — gone within a few hours (Felipe W.)', 'Everything removed from a back yard, yard cleaned before the owners got home (dwayne richie)']),
    dict(id='hot-tubs', n='06', t='Hot tubs, appliances & furniture', img='hot-tub-removal', tall=True,
         alt='Two crew members tipping a hot tub on its side on a concrete pool deck',
         p='The heavy, awkward stuff: hot tubs, appliances, sleeper sofas and big furniture. Carried out carefully, without tearing up the doorway on the way out.',
         ex=['Hot tub out of an enclosed screened porch, handled professionally (Alice C.)', '“2 guys removed a hot tub for me in under an hour” (David J.)', 'A heavy sleeper sofa and side chair, same-day pickup (Steve J.)']),
]

def page_services():
    href = 'services.html'
    title = 'Services | Junk Removal, Demolition & Cleanouts — Heavy Haulers, Orange Park FL'
    desc = 'Junk removal, demolition, house & garage cleanouts, construction and yard debris, hot tubs, appliances and furniture. Orange Park & Jacksonville. Call (904) 576-1110.'
    svc_ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "Heavy Haulers services", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "item": {"@type": "Service", "name": s['t'], "description": s['p'], "provider": {"@id": BASE + "#business"}, "areaServed": "Orange Park & Jacksonville, FL"}} for i, s in enumerate(SERVICES)]}
    h = head(href, title, desc, [business_ld(False), crumbs_ld('Services', href), svc_ld])
    secs = ''
    for s in SERVICES:
        if s.get('img2'):
            media = f'''<div class="duo"><div class="svc-ph rv-up"><span class="num">{s['n']}</span>{img(s['img'], s['alt'])}</div><div class="svc-ph rv-up">{img(s['img2'], s['alt2'])}</div></div>'''
        else:
            media = f'''<div class="svc-ph rv-up{' tall' if s.get('tall') else ''}"><span class="num">{s['n']}</span>{img(s['img'], s['alt'])}</div>'''
        exs = ''.join(f'<li>{E(x)}</li>' for x in s['ex'])
        secs += f'''<article class="svc" id="{s['id']}">{media}<div><p class="kicker">Service {s['n']}</p><h2 style="font-size:clamp(44px,5vw,78px)">{E(s['t'])}</h2>
<p class="lead rv-up" style="margin-top:18px">{E(s['p'])}</p><ul class="rv-up">{exs}</ul><p class="src">Examples come from real Google reviews and the company's own pages.</p></div></article>'''
    body = f'''{nav(href)}<main id="main">
{phero(href, 'Services', 'What we do', 'Junk out. <span class="red">Demo</span> done.', 'Six kinds of jobs, one crew. Junk removal, demolition, cleanouts, construction and yard debris, plus the heavy stuff nobody else wants to lift.', img('dumpster-downtown-crop', 'Heavy Haulers dumpster trailer parked at a downtown Jacksonville job with the hauling truck behind it', lazy=False), 'SERVICES')}
<section class="pad-s"><div class="wrap">{secs}</div></section>

<section class="pad" aria-labelledby="ba-h" style="background:#0f1012;border-block:1px solid #1f2024">
  <div class="wrap"><p class="kicker">Before / after</p><h2 id="ba-h" data-split>One rooftop deck. Gone.</h2>
    <p class="lead rv-up" style="margin-top:16px">A wooden rooftop deck structure on a downtown building, torn out and hauled away. Drag the handle.</p>
    <div class="ba rv-up">
      {img('rooftop-before', 'Before: wooden deck structure on a downtown rooftop')}
      {img('rooftop-after', 'After: the same rooftop cleared, building wall exposed', 'after')}
      <span class="lab b">Before</span><span class="lab a">After</span><span class="handle" aria-hidden="true"></span>
      <input type="range" min="0" max="100" value="50" aria-label="Before and after comparison slider">
    </div>
  </div>
</section>

<section class="pad" aria-labelledby="how-h">
  <div class="wrap"><p class="kicker">How it works</p><h2 id="how-h" data-split>Four steps. Zero hassle.</h2>
    <div class="timeline"><div class="rail-line" aria-hidden="true"><i></i></div>
      <div class="step rv-up"><span class="n">1</span><h3>Call or text</h3><p>Reach the crew at {D['phone']}. Reviewers say someone actually picks up.</p></div>
      <div class="step rv-up"><span class="n">2</span><h3>Send a photo</h3><p>Snap the pile, the shed, the hot tub. You get a free quote back.</p></div>
      <div class="step rv-up"><span class="n">3</span><h3>Crew rolls up</h3><p>Trucks, trailers and the right machine for the job — often the same day if the schedule allows.</p></div>
      <div class="step rv-up"><span class="n">4</span><h3>Loaded, hauled, swept</h3><p>Everything goes on the trailer and the area gets cleaned before they leave.</p></div>
    </div>
  </div>
</section>
{cta_band('Point at it.<br>It\'s gone.')}
</main>'''
    return h + body + footer()

def page_fleet():
    href = 'fleet.html'
    title = 'The Fleet | Trucks, Track Loaders & Dumpster Trailer — Heavy Haulers'
    desc = 'Meet the Heavy Haulers fleet: branded dumpster trailer, Bobcat and Kubota track loaders, JLG telehandler and Volvo excavator. Orange Park junk removal & demolition.'
    h = head(href, title, desc, [business_ld(False), crumbs_ld('The Fleet', href)])
    units = ''
    for u in FLEET:
        inset = f'<div class="inset{" tall" if isize(u["inset"])[1] > isize(u["inset"])[0] else ""}">{img(u["inset"], u["inset_alt"])}</div>' if u.get('inset') else ''
        lettered = f'<dt>Lettered</dt><dd>{E(u["lettered"])}</dd>' if u.get('lettered') else ''
        units += f'''<article class="fleet-unit" id="{u['id']}">
  <div class="fu-media rv-up"><div class="main{' portrait' if u.get('portrait') else ''}">{img(u['img'], u['alt'])}</div>{inset}</div>
  <div><span class="unitno" aria-hidden="true">{u['no']}</span><p class="kicker">Unit {u['no']} · {E(u['tag'])}</p><h2 style="font-size:clamp(46px,5.4vw,84px)">{E(u['name'])}</h2>
    <p class="lead rv-up" style="margin-top:16px">{E(u['blurb'])}</p>
    <div class="specplate rv-up"><dl><dt>On the job</dt><dd>{E(u['role'])}</dd><dt>Look for</dt><dd>{E(u['look'])}</dd>{lettered}</dl></div>
  </div>
</article>'''
    body = f'''{nav(href)}<main id="main">
{phero(href, 'The Fleet', 'Equipment that means business', 'The <span class="red">fleet.</span>', 'A crew is only as good as what it brings. Here is the iron that shows up on Heavy Haulers jobs — from the branded dumpster trailer to track loaders, a telehandler and an excavator.', img('dumpster-downtown-crop', 'Heavy Haulers dumpster trailer and hauling truck at a downtown Jacksonville job', lazy=False), 'IRON')}
<section class="pad-s"><div class="wrap">{units}</div></section>
<section class="pad-s"><div class="wrap" style="text-align:center"><p class="lead" style="margin:0 auto">Photos are from real Heavy Haulers jobs posted on their Google profile. Ask about the right machine for your job when you call.</p></div></section>
{cta_band('Need the<br>big iron?', 'Call or text (904) 576-1110 and tell us what you are moving.')}
</main>'''
    return h + body + footer()

def page_crew():
    href = 'crew.html'
    title = 'The Crew | Black-Owned Junk Removal & Demolition Team — Heavy Haulers, Orange Park'
    desc = 'Meet the Heavy Haulers crew: a Black-owned Orange Park junk removal and demolition team with 5.0 stars from 216 Google reviews. Call (904) 576-1110.'
    h = head(href, title, desc, [business_ld(False), crumbs_ld('The Crew', href)])
    gal = [('demo-cutting-sparks', 'Cutting steel bollards, sparks flying'), ('hot-tub-trailer', 'Loading an old hot tub onto the trailer in a driveway'),
           ('decking-debris', 'Old decking stacked for haul-off'), ('yard-cleared', 'Backyard cleared down to bare ground'),
           ('lumber-pile', 'Torn-out lumber ready to load'), ('cleanout-empty-room', 'Living room after a full cleanout'),
           ('demo-sledgehammers', 'Busting up a block structure with sledgehammers'), ('dumpster-loaded', 'Dumpster trailer loaded to the top')]
    galhtml = ''.join(f'<button type="button" data-lb="img/{n}.webp" aria-label="Open photo: {E(a)}">{img(n, a)}</button>' for n, a in gal)
    body = f'''{nav(href)}<main id="main">
<section class="phero">
  <div class="bigtype" aria-hidden="true" data-speed="-0.08">CREW</div>
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Home</a> / <span aria-current="page">The Crew</span></div>
    <p class="kicker">Meet the team</p>
    <h1 data-split>The crew that <span class="red">shows up.</span></h1>
    <p class="lead rv-up" style="margin-top:20px">Matching jerseys, arms crossed, trucks behind them. This is who shows up at your door. Tap the pins.</p>
    <div class="hotspots rv-up" style="margin-top:40px">
      {img('crew-wide', 'The Heavy Haulers crew in matching camo and red jerseys in front of white work trucks under a live oak', lazy=False)}
      <div class="pin" style="left:39%;top:46%"><button type="button" aria-expanded="false" aria-label="About the jerseys">+</button><div class="tip" role="tooltip">Matching team jerseys, so you know exactly who's on your property.</div></div>
      <div class="pin" style="left:87%;top:31%"><button type="button" aria-expanded="false" aria-label="About the trucks">+</button><div class="tip" role="tooltip">Pickups that tow the trailers, the dumpster and the machines to your job.</div></div>
      <div class="pin" style="left:12%;top:52%"><button type="button" aria-expanded="false" aria-label="About the crew">+</button><div class="tip" role="tooltip">A full crew, so the big jobs go quick. Reviewers keep saying “fast.”</div></div>
    </div>
  </div>
</section>

<section class="pad-s"><div class="wrap">
  <p class="kicker">What we stand for</p><h2 data-split>Work hard. Be respectful. Leave it clean.</h2>
  <p class="lead rv-up" style="margin-top:20px">Heavy Haulers & Junk Removal is a Black-owned crew based on Park Ave in Orange Park, working jobs around Orange Park and Jacksonville. The reviews keep coming back to the same three things:</p>
  <div class="values">
    <div class="value rv-up"><h3>Hustle</h3><p>“Quick, professional, respectful, and worked extremely hard from the moment they arrived.” — mark smith</p></div>
    <div class="value rv-up"><h3>Respect</h3><p>“If you need a crew that works hard, gets the job done, and treats you with respect, I HIGHLY recommend Juan and his crew!” — mark smith</p></div>
    <div class="value rv-up"><h3>Follow-through</h3><p>“Came by before and after the job to provide quality assurance checks and make sure that we were satisfied.” — dwayne richie</p></div>
  </div>
</div></section>

<section class="pad-s" style="overflow:hidden"><div class="wrap">
  <div class="rail-head"><div><p class="kicker">On the job</p><h2 data-split>Real jobs. Real photos.</h2></div><p style="color:#9a9da3">Drag or swipe · tap to enlarge</p></div>
  <div class="gallery" tabindex="0" aria-label="Job photo gallery">{galhtml}</div>
</div></section>

<section class="pad"><div class="wrap brandstrip">
  <div class="decal rv-up">{img('dumpster-decal', 'Heavy Haulers & Junk Removal logo decal on the back of the dumpster trailer')}</div>
  <div><p class="kicker">You'll know us when you see us</p><h2 data-split>Look for the red banner.</h2>
    <p class="lead rv-up" style="margin-top:18px">The black dumpster trailer, the truck with the chain-pulling strongman and the red “& Junk Removal” banner. If it says {D['phone']} on the side, that's the crew.</p>
    <p class="rv-up" style="margin-top:26px"><a class="btn ghost" href="fleet.html">See the fleet {I_ARROW}</a></p></div>
</div></section>
{cta_band('Put this crew<br>on your job.')}
</main>
<div class="lb" role="dialog" aria-modal="true" aria-label="Photo viewer" aria-hidden="true"><img src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" alt=""><button class="x" type="button" aria-label="Close">×</button><button class="pv" type="button" aria-label="Previous photo">←</button><button class="nx" type="button" aria-label="Next photo">→</button><div class="cap"></div></div>'''
    return h + body + footer()

def page_reviews():
    href = 'reviews.html'
    title = 'Reviews | 5.0 Stars from 216 Google Reviews — Heavy Haulers & Junk Removal'
    desc = 'Read what Orange Park and Jacksonville customers say about Heavy Haulers: 5.0 stars from 216 Google reviews. Junk removal, hot tubs, cleanouts and demolition.'
    h = head(href, title, desc, [business_ld(True), crumbs_ld('Reviews', href)])
    cards = ''.join(f'''<article class="rv rv-up"><div class="stars" aria-label="5 out of 5 stars">★★★★★</div><p>{E(r['text'])}</p>
<div class="who">{E(r['name'])}<small>Google review · {E(r['age'])}</small></div></article>''' for r in D['reviews'])
    topics = ['friendly crew', 'hot tub removal', 'house clearing', 'online quote', 'easy scheduling', 'no hidden fees', 'cleanliness', 'upfront pricing', 'careful handling']
    tops = '<span>friendly staff <b>55</b></span>' + ''.join(f'<span>{t}</span>' for t in topics)
    body = f'''{nav(href)}<main id="main">
<section class="phero"><div class="bigtype" aria-hidden="true" data-speed="-0.08">5.0</div>
  <div class="wrap"><div class="crumbs"><a href="index.html">Home</a> / <span aria-current="page">Reviews</span></div>
    <p class="kicker">Straight from Google</p><h1 data-split>Don't take <span class="red">our</span> word.</h1>
    <div class="rsum rv-up"><div class="big">5.0</div><div><div class="stars" aria-hidden="true">★★★★★</div><div style="font-weight:700">{D['review_count']} Google reviews</div>
      <a href="{E(D['maps_url'])}" target="_blank" rel="noopener" style="color:var(--red2);font-weight:700">Read them all on Google →</a></div></div>
    <p style="margin-top:28px;color:#9a9da3;font-size:14px;letter-spacing:.06em;text-transform:uppercase;font-weight:700">What reviewers mention most</p>
    <div class="topics rv-up">{tops}</div>
  </div></section>
<section class="pad-s"><div class="wrap"><p class="kicker">A few of the {D['review_count']}</p><div class="masonry">{cards}</div>
  <p class="note">Reviews are quoted word for word from the company's Google Business Profile, November 2026.</p></div></section>
{cta_band('Be the next<br>5-star job.')}
</main>'''
    return h + body + footer()

FAQ = [
    ('How do I get a quote?', f'Call or text {D["phone"]}. Texting a photo of the job is the fastest way. Quotes are free.'),
    ('Where are you located?', f'Heavy Haulers & Junk Removal is at {ADDR}, and works jobs around Orange Park and the Jacksonville area.'),
    ('What are your hours?', 'Monday through Saturday, 8 AM to 5 PM. Closed Sunday.'),
    ('Can you come the same day?', 'Often, yes. Many Google reviews mention same-day pickups. Call or text to check today\'s schedule.'),
    ('What do you haul?', 'Household junk, furniture, appliances, hot tubs, construction debris, old decking and lumber, yard debris and tree brush, plus full house and garage cleanouts.'),
    ('Do you do demolition?', 'Yes. Full home, mobile home, interior and backyard demolition, plus haul-off of the debris.'),
]

def page_contact():
    href = 'contact.html'
    title = 'Contact | Call or Text (904) 576-1110 — Heavy Haulers & Junk Removal, Orange Park'
    desc = 'Call or text Heavy Haulers at (904) 576-1110 for a free junk removal or demolition quote. 1120 Park Ave #D, Orange Park FL. Mon–Sat 8 AM–5 PM.'
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    h = head(href, title, desc, [business_ld(False), crumbs_ld('Contact', href), faq_ld])
    rows = ''.join(f'<tr data-d="{k}"><td>{full}</td><td>{(fmt_t(D["hours"][k][0]) + " – " + fmt_t(D["hours"][k][1])) if D["hours"][k] else "Closed"}</td></tr>' for k, full in DAYS)
    faqs = ''.join(f'<details class="rv-up"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in FAQ)
    mapsrc = 'https://www.google.com/maps?q=' + 'Heavy+Haulers+%26+Junk+Removal,+1120+Park+Ave+%23D,+Orange+Park,+FL+32073' + '&output=embed'
    body = f'''{nav(href)}<main id="main">
<section class="phero"><div class="bigtype" aria-hidden="true" data-speed="-0.08">CALL</div>
  <div class="wrap"><div class="crumbs"><a href="index.html">Home</a> / <span aria-current="page">Contact</span></div>
    <p class="kicker">Free quotes</p><h1 data-split>Let's move <span class="red">some junk.</span></h1>
    <p class="lead rv-up" style="margin-top:20px">Call or text. Send a photo of the job and get a free quote.</p>
    <div class="contact-grid" style="margin-top:44px">
      <div class="card rv-up"><h3>Call or text</h3><a class="bigphone" href="{TEL}">{D['phone']}</a>
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:22px"><a class="btn" href="{TEL}" data-magnet>{I_PHONE}Call now</a><a class="btn ghost" href="{SMS}">{I_SMS}Text a photo</a></div>
        <p style="margin-top:26px;color:#cfccc6"><strong style="color:#fff">{E(D['name'])}</strong><br>{E(D['street'])}<br>{D['city']}, {D['region']} {D['zip']}</p>
        <p style="margin-top:12px"><a href="{E(D['maps_url'])}" target="_blank" rel="noopener" style="color:var(--red2);font-weight:700">Directions on Google Maps →</a></p>
        <h3 style="margin-top:30px;font-size:28px">Hours <span class="chip open-badge" style="font-family:var(--body);font-size:13px;vertical-align:middle;margin-left:8px"><span class="dot"></span><span class="t">{HOURS_LINE}</span></span></h3>
        <table class="hours"><tbody>{rows}</tbody></table></div>
      <div class="card rv-up"><h3>Text us your job</h3><p style="color:#b8bac0;margin-bottom:18px">Fill this in and it opens a pre-written text to {D['phone']} on your phone. Attach photos of the job before you hit send. Nothing is sent from this site.</p>
        <form class="quote" data-phone="{D['phone_e164']}">
          <div class="row"><label>Your name<input name="name" autocomplete="name" placeholder="First name"></label>
          <label>Job type<select name="job"><option>Junk removal</option><option>Demolition</option><option>House / garage cleanout</option><option>Construction debris</option><option>Yard debris</option><option>Hot tub / appliance / furniture</option><option>Something else</option></select></label></div>
          <div class="row"><label>Where<input name="where" placeholder="Neighborhood or city"></label><label>When<input name="when" placeholder="ASAP, this week…"></label></div>
          <label>What needs to go?<textarea name="details" rows="4" placeholder="e.g. old couch, washer and a pile of boards in the backyard"></textarea></label>
          <div class="acts"><button class="btn" type="submit">{I_SMS}Open text message</button><a class="btn ghost" href="{TEL}">{I_PHONE}Or just call</a></div>
        </form></div>
    </div>
    <div class="map rv-up"><iframe title="Map to Heavy Haulers & Junk Removal, 1120 Park Ave, Orange Park FL" src="{mapsrc}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
  </div></section>
<section class="pad-s"><div class="wrap"><p class="kicker">FAQ</p><h2 data-split>Quick answers.</h2><div class="faq">{faqs}</div></div></section>
{cta_band()}
</main>'''
    return h + body + footer()

def page_404():
    h = head('404.html', 'Page not found | Heavy Haulers & Junk Removal', 'That page got hauled away. Head back to Heavy Haulers & Junk Removal.', [])
    body = f'''{nav('')}<main id="main"><section class="phero" style="min-height:80vh;display:grid;align-items:center"><div class="bigtype" aria-hidden="true">404</div>
<div class="wrap"><p class="kicker">Error 404</p><h1 data-split>This page got <span class="red">hauled off.</span></h1>
<p class="lead rv-up" style="margin-top:20px">The page you wanted isn't here. The crew probably took it to the dump.</p>
<div class="acts rv-up" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:30px"><a class="btn" href="index.html">Back home</a><a class="btn ghost" href="{TEL}">{I_PHONE}{D['phone']}</a></div></div></section></main>'''
    return h + body + footer()

def llms():
    rv = '\n'.join(f'- "{r["text"][:220]}{"…" if len(r["text"]) > 220 else ""}" — {r["name"]} (Google, {r["age"]})' for r in D['reviews'][:8])
    return f'''# {D['name']}

> Black-owned junk removal and demolition company in Orange Park, Florida, serving Orange Park and the Jacksonville area. 5.0 stars from {D['review_count']} Google reviews. Call or text {D['phone']} for a free quote.

## Key facts
- Name: {D['name']}
- Google category: {D['category']}
- Address: {ADDR}
- Phone (call or text): {D['phone']}
- Hours: Monday–Saturday 8 AM–5 PM; Sunday closed
- Rating: 5.0 stars, {D['review_count']} Google reviews
- Google Maps: {D['maps_url']}
- Instagram: {D['instagram']}
- Attributes: Black-owned; onsite services
- Quotes: free; customers can text a photo of the job

## Services
- Junk removal (furniture, boxes, bagged trash, moving leftovers, rental turnovers)
- Demolition (full home, mobile home, interior and backyard demos)
- House and garage cleanouts
- Construction debris removal (old decking, lumber, job-site waste)
- Yard debris removal (tree brush, limbs, overgrowth)
- Hot tub, appliance and furniture removal

## Equipment (from their job photos)
- Heavy Haulers branded black dumpster trailer (lettered: Junk Removal, Demolition, House Clean Outs, Construction, Yard Debris Removal)
- Bobcat compact track loader with grapple
- Kubota compact track loader
- JLG telehandler
- Volvo excavator

## Pages
- Home: {BASE}
- Services: {BASE}services.html
- The Fleet: {BASE}fleet.html
- The Crew: {BASE}crew.html
- Reviews: {BASE}reviews.html
- Contact & FAQ: {BASE}contact.html

## What customers say
{rv}
'''

def og_image():
    from PIL import ImageDraw, ImageFilter
    im = Image.open(os.path.join(ROOT, 'img', 'crew.webp')).convert('RGB')
    W, H = 1200, 630
    s = max(W / im.width, H / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - W) // 2; y = int((im.height - H) * 0.55); im = im.crop((x, y, x + W, y + H))
    grad = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(grad)
    for i in range(W):
        dr.line([(i, 0), (i, H)], fill=int(max(0, 215 - i * 0.42)))
    im.paste(Image.new('RGB', (W, H), (11, 11, 13)), (0, 0), grad)
    logo = Image.open(os.path.join(ROOT, 'brand', 'logo-stacked-dark.png')).convert('RGBA')
    logo.thumbnail((440, 440)); im.paste(logo, (40, (H - logo.height) // 2), logo)
    tape = Image.new('RGB', (W, 12)); td = ImageDraw.Draw(tape)
    for k in range(0, W, 108):
        td.rectangle([k, 0, k + 53, 12], fill=(215, 38, 30)); td.rectangle([k + 54, 0, k + 107, 12], fill=(242, 242, 242))
    im.paste(tape, (0, H - 12))
    im.save(os.path.join(OUT, 'og.jpg'), quality=86)

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, 'assets'))
    shutil.copytree(os.path.join(ROOT, 'img'), os.path.join(OUT, 'img'))
    os.makedirs(os.path.join(OUT, 'brand'))
    for f in os.listdir(os.path.join(ROOT, 'brand')):
        if f.endswith(('.svg', '.png', '.ico')):
            shutil.copy(os.path.join(ROOT, 'brand', f), os.path.join(OUT, 'brand', f))
    shutil.copy(os.path.join(ROOT, 'src', 'site.css'), os.path.join(OUT, 'assets', 'site.css'))
    shutil.copy(os.path.join(ROOT, 'src', 'site.js'), os.path.join(OUT, 'assets', 'site.js'))
    pages = {'index.html': page_home(), 'services.html': page_services(), 'fleet.html': page_fleet(), 'crew.html': page_crew(),
             'reviews.html': page_reviews(), 'contact.html': page_contact(), '404.html': page_404()}
    for k, v in pages.items():
        open(os.path.join(OUT, k), 'w').write(v)
    open(os.path.join(OUT, 'llms.txt'), 'w').write(llms())
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
    urls = ''.join(f'<url><loc>{BASE}{"" if h == "index.html" else h}</loc><lastmod>2026-11-25</lastmod></url>' for h, _ in PAGES)
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    open(os.path.join(OUT, 'site.webmanifest'), 'w').write(json.dumps({"name": D['name'], "short_name": "Heavy Haulers", "icons": [
        {"src": "brand/favicon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "brand/favicon-512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": "#0b0b0d", "background_color": "#0b0b0d", "display": "standalone"}))
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    og_image()
    print('built', len(pages), 'pages ->', OUT)

if __name__ == '__main__':
    main()
