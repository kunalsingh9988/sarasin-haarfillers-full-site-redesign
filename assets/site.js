const toggle=document.querySelector('.menu-toggle');
const mobile=document.querySelector('.mobile-nav');
if(toggle&&mobile){toggle.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')==='true';toggle.setAttribute('aria-expanded',String(!open));toggle.setAttribute('aria-label',open?'Open menu':'Sluit menu');mobile.hidden=open;});mobile.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{mobile.hidden=true;toggle.setAttribute('aria-expanded','false')}));}
const headings=[...document.querySelectorAll('.source-content h2[id]')];
if(headings.length&&'IntersectionObserver' in window){const links=[...document.querySelectorAll('.article-aside nav a')];const io=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){links.forEach(a=>a.style.color=a.hash==='#'+entry.target.id?'#18352d':'');}})},{rootMargin:'-20% 0px -70% 0px'});headings.forEach(h=>io.observe(h));}
