document.addEventListener('DOMContentLoaded',()=>{
 const body=document.body, theme=document.getElementById('theme-toggle');
 const saved=localStorage.getItem('dbtest-theme'); if(saved==='dark')body.classList.add('dark');
 function labelTheme(){theme.textContent=body.classList.contains('dark')?'Modo claro':'Modo oscuro'} labelTheme();
 theme.addEventListener('click',()=>{body.classList.toggle('dark');localStorage.setItem('dbtest-theme',body.classList.contains('dark')?'dark':'light');labelTheme()});
 const nature=document.getElementById('filter-nature'), obligation=document.getElementById('filter-obligation'), origin=document.getElementById('filter-origin');
 const natureValues=[...new Set([...document.querySelectorAll('.column-row')].map(r=>r.dataset.nature))].sort(); for(const v of natureValues){const o=document.createElement('option');o.value=v;o.textContent=v;nature.appendChild(o)}
 const search=document.getElementById('site-search');
 function apply(){const q=search.value.trim().toLowerCase();document.querySelectorAll('.table-card').forEach(card=>{const cardMatch=!q||card.dataset.table.includes(q)||[...card.querySelectorAll('.column-row')].some(r=>r.dataset.column.includes(q));let visible=0;card.querySelectorAll('.column-row').forEach(r=>{const ok=(!nature.value||r.dataset.nature===nature.value)&&(!obligation.value||r.dataset.obligation===obligation.value)&&(!origin.value||r.dataset.origin===origin.value)&&(!q||r.dataset.column.includes(q)||card.dataset.table.includes(q));r.classList.toggle('hidden',!ok);if(ok)visible++});card.classList.toggle('hidden',!cardMatch||visible===0);if(q&&cardMatch)card.querySelector('details').open=true});}
 [search,nature,obligation,origin].forEach(el=>el.addEventListener(el===search?'input':'change',apply));document.getElementById('clear-filters').addEventListener('click',()=>{nature.value='';obligation.value='';origin.value='';search.value='';apply()});
let scale=1;function setZoom(){document.querySelectorAll('.diagram-scale').forEach(p=>p.style.transform=`scale(${scale})`)}document.querySelectorAll('[data-zoom]').forEach(b=>b.addEventListener('click',()=>{const z=b.dataset.zoom;if(z==='in')scale=Math.min(2.5,scale+.15);else if(z==='out')scale=Math.max(.5,scale-.15);else scale=1;setZoom()}));
 if(window.mermaid){mermaid.initialize({startOnLoad:true,theme:body.classList.contains('dark')?'dark':'default',securityLevel:'strict'});}
});
