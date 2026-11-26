import asyncio, sys
from playwright.async_api import async_playwright
BASE='http://localhost:47219/'
OUT='/workspace/heavyhaulers/qa/shots/'
# spec: name page width selector(or 'top')
SPECS=[l.split() for l in sys.argv[1:]]
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for name,page,w,sel in SPECS:
      w=int(w); ctx=await b.new_context(viewport={'width':w,'height':900 if w>800 else 844})
      pg=await ctx.new_page(); await pg.goto(BASE+page,wait_until='load'); await pg.wait_for_timeout(2600)
      if sel!='top':
        await pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'start',behavior:'instant'}})"); await pg.evaluate('window.scrollBy({top:-90,behavior:"instant"})')
        await pg.wait_for_timeout(2600)
      await pg.screenshot(path=OUT+name+'.png'); await ctx.close()
    await b.close()
asyncio.run(m())
