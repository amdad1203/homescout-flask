// static/js/app.js  (append or replace small parts)
(function(){
  // floating badges parallax on mouse move
  const hero = document.querySelector('.hero-right');
  if(hero){
    const badges = document.querySelectorAll('.badge');
    hero.addEventListener('mousemove', (e)=>{
      const r = hero.getBoundingClientRect();
      const cx = (e.clientX - r.left) / r.width - 0.5;
      const cy = (e.clientY - r.top) / r.height - 0.5;
      badges.forEach((b,i)=>{
        const factor = (i+1) * 6;
        b.style.transform = `translate3d(${cx * factor}px, ${cy * factor}px, 0)`;
      });
    });
    hero.addEventListener('mouseleave', ()=> badges.forEach(b=>b.style.transform='translate3d(0,0,0)'));
  }

  // simple toast
  window.hsToast = function(msg, opts={}){
    const t = document.createElement('div');
    t.className='hs-toast';
    t.style.position='fixed';
    t.style.right='18px';
    t.style.top='18px';
    t.style.zIndex=99999;
    t.style.background='linear-gradient(90deg,var(--accent),var(--accent-2))';
    t.style.color='#fff';
    t.style.padding='10px 14px';
    t.style.borderRadius='10px';
    t.style.boxShadow='0 10px 30px rgba(2,8,30,0.5)';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(()=> t.style.opacity='0', 2600);
    setTimeout(()=> t.remove(), 3000);
    return t;
  };
})();
