/* Heavy Haulers — site interactions. No libraries. */
(function(){
  var d=document, w=window, root=d.documentElement;
  var RM = w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var HOURS = w.HH_HOURS || {};

  /* loader (home only, once per session) */
  var ld=d.querySelector('.loader');
  if(ld){
    var seen=false; try{seen=sessionStorage.getItem('hh-intro')}catch(e){}
    if(RM||seen){ld.classList.add('gone')}
    else{
      try{sessionStorage.setItem('hh-intro','1')}catch(e){}
      setTimeout(function(){ld.classList.add('done')},1050);
      setTimeout(function(){ld.classList.add('gone')},2050);
    }
  }

  /* nav scroll state + progress */
  var nav=d.querySelector('.nav'), prog=d.querySelector('.progress');
  function onScroll(){
    var y=w.scrollY; if(nav) nav.classList.toggle('scrolled',y>40);
    if(prog){var h=root.scrollHeight-w.innerHeight; prog.style.transform='scaleX('+(h>0?Math.min(1,y/h):0)+')'}
    parallax();
  }
  /* mobile menu */
  var burger=d.querySelector('.burger'), mm=d.querySelector('.mmenu');
  if(burger){
    burger.addEventListener('click',function(){
      var open=!root.classList.contains('menu-open');
      root.classList.toggle('menu-open',open); burger.setAttribute('aria-expanded',open);
      if(mm) mm.setAttribute('aria-hidden',!open);
      if(open&&mm){var a=mm.querySelector('a'); a&&a.focus()}
    });
    d.addEventListener('keydown',function(e){if(e.key==='Escape'&&root.classList.contains('menu-open')){burger.click();burger.focus()}});
    mm&&mm.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){root.classList.remove('menu-open')})});
  }

  /* split text */
  d.querySelectorAll('[data-split]').forEach(function(el){
    var i=0;
    (function walk(node){
      Array.prototype.slice.call(node.childNodes).forEach(function(n){
        if(n.nodeType===3){
          var frag=d.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function(t){
            if(!t) return;
            if(/^\s+$/.test(t)){frag.appendChild(d.createTextNode(' '));return}
            var o=d.createElement('span');o.className='w';var s=d.createElement('span');s.textContent=t;
            s.style.transitionDelay=(i++*0.07)+'s';o.appendChild(s);frag.appendChild(o);
          });
          n.parentNode.replaceChild(frag,n);
        } else if(n.nodeType===1 && !n.classList.contains('w')) walk(n);
      });
    })(el);
    el.classList.add('split');
  });

  /* reveal on scroll */
  var io=('IntersectionObserver' in w)? new IntersectionObserver(function(es){
    es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})
  },{rootMargin:'0px 0px -8% 0px',threshold:.12}):null;
  d.querySelectorAll('.rv-up,.split').forEach(function(el){ if(io&&!RM) io.observe(el); else el.classList.add('in') });
  /* hero split fires after loader */
  d.querySelectorAll('.hero .split').forEach(function(el){
    var delay=(ld&&!ld.classList.contains('gone'))?1250:150;
    setTimeout(function(){el.classList.add('in')},RM?0:delay);
  });

  /* parallax */
  var px=[].slice.call(d.querySelectorAll('[data-speed]'));
  function parallax(){
    if(RM) return;
    var vh=w.innerHeight;
    px.forEach(function(el){
      var r=el.getBoundingClientRect(); if(r.bottom<-200||r.top>vh+200) return;
      var c=(r.top+r.height/2-vh/2); var s=parseFloat(el.dataset.speed);
      el.style.translate='0 '+(c*s).toFixed(1)+'px';
    });
  }
  w.addEventListener('scroll',onScroll,{passive:true}); onScroll();

  /* counters + gauges */
  function animateNum(el){
    var to=parseFloat(el.dataset.count), dec=(el.dataset.dec|0), dur=1800, t0=null;
    if(RM){el.textContent=to.toFixed(dec);return}
    function f(t){t0=t0||t;var p=Math.min(1,(t-t0)/dur);var e=1-Math.pow(1-p,3);
      el.textContent=(to*e).toFixed(dec); if(p<1) requestAnimationFrame(f); else el.textContent=to.toFixed(dec)}
    requestAnimationFrame(f);
  }
  var gio=('IntersectionObserver' in w)? new IntersectionObserver(function(es){
    es.forEach(function(e){ if(!e.isIntersecting) return; gio.unobserve(e.target); fire(e.target) })
  },{threshold:.35}):null;
  function fire(g){
    var frac=parseFloat(g.dataset.frac||'1');
    var n=g.querySelector('.needle'); if(n) n.style.transform='rotate('+(-120+240*frac)+'deg)';
    var a=g.querySelector('.arc-fill'); if(a){var L=parseFloat(a.getAttribute('data-len')); a.style.strokeDashoffset=(L*(1-frac)).toFixed(1)}
    g.querySelectorAll('[data-count]').forEach(animateNum);
  }
  d.querySelectorAll('.gauge,[data-counter-wrap]').forEach(function(g){ if(gio&&!RM) gio.observe(g); else fire(g) });

  /* open / closed badge (business time zone) */
  function nowNY(){
    var p=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',weekday:'short',hour:'2-digit',minute:'2-digit',hour12:false}).formatToParts(new Date());
    var o={};p.forEach(function(x){o[x.type]=x.value});return {day:o.weekday.slice(0,2),min:(parseInt(o.hour,10)%24)*60+parseInt(o.minute,10)};
  }
  function fmt(t){var h=parseInt(t.slice(0,2),10),m=t.slice(3);var ap=h>=12?'PM':'AM';h=h%12||12;return h+(m!=='00'?':'+m:'')+' '+ap}
  var order=['Su','Mo','Tu','We','Th','Fr','Sa'];
  function status(){
    var n=nowNY(), today=HOURS[n.day];
    if(today){var o=+today[0].slice(0,2)*60+ +today[0].slice(3), c=+today[1].slice(0,2)*60+ +today[1].slice(3);
      if(n.min>=o&&n.min<c) return {open:true,text:'Open now · until '+fmt(today[1])};
      if(n.min<o) return {open:false,text:'Closed · opens '+fmt(today[0])+' today'};}
    var i=order.indexOf(n.day);
    for(var k=1;k<=7;k++){var dd=order[(i+k)%7]; if(HOURS[dd]){return {open:false,text:'Closed · opens '+({Su:'Sun',Mo:'Mon',Tu:'Tue',We:'Wed',Th:'Thu',Fr:'Fri',Sa:'Sat'})[dd]+' '+fmt(HOURS[dd][0])}}}
    return {open:false,text:'Closed'};
  }
  var st=status();
  d.querySelectorAll('.open-badge').forEach(function(b){b.classList.add(st.open?'is-open':'is-closed');var t=b.querySelector('.t');if(t)t.textContent=st.text});
  var td=nowNY().day; d.querySelectorAll('.hours tr[data-d="'+td+'"]').forEach(function(r){r.classList.add('today')});

  /* drag-to-scroll rails */
  d.querySelectorAll('.rail,.gallery').forEach(function(r){
    var down=false,sx=0,sl=0,moved=0;
    r.addEventListener('pointerdown',function(e){if(e.pointerType!=='mouse')return;down=true;moved=0;sx=e.clientX;sl=r.scrollLeft});
    w.addEventListener('pointermove',function(e){if(!down)return;var dx=e.clientX-sx;moved=Math.max(moved,Math.abs(dx));if(moved>4)r.classList.add('drag');r.scrollLeft=sl-dx});
    w.addEventListener('pointerup',function(){down=false;setTimeout(function(){r.classList.remove('drag')},0)});
    r.addEventListener('click',function(e){if(moved>6){e.preventDefault();e.stopPropagation();moved=0}},true);
  });

  /* tilt cards */
  if(!RM && w.matchMedia('(hover:hover)').matches){
    d.querySelectorAll('[data-tilt]').forEach(function(c){
      c.addEventListener('pointermove',function(e){var r=c.getBoundingClientRect();var x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
        c.style.transform='perspective(900px) rotateY('+(x*8)+'deg) rotateX('+(-y*8)+'deg) translateY(-4px)'});
      c.addEventListener('pointerleave',function(){c.style.transform=''});
    });
    /* magnetic buttons */
    d.querySelectorAll('[data-magnet]').forEach(function(b){
      b.addEventListener('pointermove',function(e){var r=b.getBoundingClientRect();b.style.transform='translate('+((e.clientX-r.left-r.width/2)*.22)+'px,'+((e.clientY-r.top-r.height/2)*.3)+'px)'});
      b.addEventListener('pointerleave',function(){b.style.transform=''});
    });
  }

  /* reviews carousel */
  d.querySelectorAll('.carousel').forEach(function(cr){
    var tr=cr.querySelector('.car-track'), slides=tr.children, n=slides.length, i=0, timer=null;
    var dots=cr.querySelector('.dots');
    for(var k=0;k<n;k++){(function(k){var b=d.createElement('button');b.type='button';b.setAttribute('aria-label','Review '+(k+1));b.addEventListener('click',function(){go(k)});dots.appendChild(b)})(k)}
    function go(k){i=(k+n)%n;tr.style.transform='translateX('+(-100*i)+'%)';
      [].forEach.call(slides,function(s,j){s.setAttribute('aria-hidden',j!==i); s.querySelectorAll('a,button').forEach(function(x){x.tabIndex=j===i?0:-1})});
      [].forEach.call(dots.children,function(b,j){b.setAttribute('aria-current',j===i)})}
    cr.querySelector('.prev').addEventListener('click',function(){go(i-1)});
    cr.querySelector('.next').addEventListener('click',function(){go(i+1)});
    function play(){if(RM)return;stop();timer=setInterval(function(){go(i+1)},6500)}
    function stop(){clearInterval(timer)}
    cr.addEventListener('mouseenter',stop);cr.addEventListener('mouseleave',play);
    cr.addEventListener('focusin',stop);cr.addEventListener('focusout',play);
    var tx=null;cr.addEventListener('touchstart',function(e){tx=e.touches[0].clientX},{passive:true});
    cr.addEventListener('touchend',function(e){if(tx===null)return;var dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>40)go(i+(dx<0?1:-1));tx=null});
    go(0);play();
  });

  /* before / after */
  d.querySelectorAll('.ba').forEach(function(b){
    var inp=b.querySelector('input'),a=b.querySelector('.after'),h=b.querySelector('.handle');
    function set(v){a.style.clipPath='inset(0 0 0 '+v+'%)';h.style.left=v+'%'}
    inp.addEventListener('input',function(){set(inp.value)}); set(inp.value);
  });

  /* scroll-drawn timeline */
  var tl=d.querySelector('.timeline');
  if(tl&&!RM){var bar=tl.querySelector('.rail-line i');
    function tlu(){var r=tl.getBoundingClientRect();var p=(w.innerHeight*.7-r.top)/r.height;bar.style.transform='scaleY('+Math.max(0,Math.min(1,p))+')'}
    w.addEventListener('scroll',tlu,{passive:true});tlu();}

  /* hotspots */
  d.querySelectorAll('.pin button').forEach(function(b){
    b.addEventListener('click',function(){var p=b.parentNode;var on=!p.classList.contains('on');d.querySelectorAll('.pin').forEach(function(x){x.classList.remove('on')});p.classList.toggle('on',on);b.setAttribute('aria-expanded',on)});
  });

  /* lightbox */
  var lb=d.querySelector('.lb');
  if(lb){
    var items=[].slice.call(d.querySelectorAll('[data-lb]')), cur=0, last=null;
    var img=lb.querySelector('img'), cap=lb.querySelector('.cap');
    function show(k){cur=(k+items.length)%items.length;var it=items[cur];img.src=it.dataset.lb;img.alt=it.querySelector('img').alt;cap.textContent=it.querySelector('img').alt}
    function open(k){last=d.activeElement;show(k);lb.classList.add('on');lb.setAttribute('aria-hidden','false');lb.querySelector('.x').focus();d.body.style.overflow='hidden'}
    function close(){lb.classList.remove('on');lb.setAttribute('aria-hidden','true');d.body.style.overflow='';last&&last.focus()}
    items.forEach(function(it,k){it.addEventListener('click',function(){open(k)})});
    lb.querySelector('.x').addEventListener('click',close);
    lb.querySelector('.pv').addEventListener('click',function(){show(cur-1)});
    lb.querySelector('.nx').addEventListener('click',function(){show(cur+1)});
    lb.addEventListener('click',function(e){if(e.target===lb)close()});
    d.addEventListener('keydown',function(e){if(!lb.classList.contains('on'))return;
      if(e.key==='Escape')close(); if(e.key==='ArrowLeft')show(cur-1); if(e.key==='ArrowRight')show(cur+1);
      if(e.key==='Tab'){var f=[].slice.call(lb.querySelectorAll('button'));var i=f.indexOf(d.activeElement);e.preventDefault();f[(i+(e.shiftKey?-1:1)+f.length)%f.length].focus()}});
    var sx=null;lb.addEventListener('touchstart',function(e){sx=e.touches[0].clientX},{passive:true});
    lb.addEventListener('touchend',function(e){if(sx===null)return;var dx=e.changedTouches[0].clientX-sx;if(Math.abs(dx)>40)show(cur+(dx<0?1:-1));sx=null});
  }

  /* quote form -> SMS / call (nothing is submitted anywhere) */
  var qf=d.querySelector('form.quote');
  if(qf){
    function body(){var f=new FormData(qf);var s='Hi Heavy Haulers! Free quote request.';
      ['name','job','where','when','details'].forEach(function(k){var v=(f.get(k)||'').toString().trim();if(v)s+='\n'+({name:'Name',job:'Job',where:'Location',when:'When',details:'Details'})[k]+': '+v});
      return s+'\n(I can text photos of the job.)'}
    qf.addEventListener('submit',function(e){e.preventDefault();var ua=navigator.userAgent;var sep=/iPhone|iPad|Mac/.test(ua)?'&':'?';
      w.location.href='sms:'+qf.dataset.phone+sep+'body='+encodeURIComponent(body())});
  }

  /* preview pill */
  var pill=d.querySelector('.pill');
  if(pill){try{if(localStorage.getItem('hh-pill'))pill.remove()}catch(e){}
    var pb=pill.querySelector('button');pb&&pb.addEventListener('click',function(){pill.remove();try{localStorage.setItem('hh-pill','1')}catch(e){}})}
})();
