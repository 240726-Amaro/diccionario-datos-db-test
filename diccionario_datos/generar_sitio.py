from __future__ import annotations
import collections, html, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent
OUT = ROOT / 'docs'
DOWNLOADS = OUT / 'descargas'
ASSETS = OUT / 'assets'
DATA = json.loads((SRC / 'estructura.json').read_text(encoding='utf-8'))
OBJECTS = DATA['objects']
TABLES = [o for o in OBJECTS if o['kind'] == 'table']
VIEWS = [o for o in OBJECTS if o['kind'] == 'view']
TRIGGERS = [o for o in OBJECTS if o['kind'] == 'trigger']
PROCEDURES = [o for o in OBJECTS if o['kind'] == 'procedure']

def esc(value): return html.escape(str(value if value is not None else ''), quote=True)
def slug(value): return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
def split_defs(sql):
    cols, cons = [], []
    for line in sql.splitlines():
        line = line.strip().rstrip(',')
        m = re.match(r'`([^`]+)`\s+(.+)', line)
        if m and m.group(1).upper() not in ('PRIMARY','UNIQUE','KEY','CONSTRAINT','FOREIGN','CHECK'):
            cols.append((m.group(1), re.match(r'(\w+(?:\s*\([^)]*\))?)', m.group(2)).group(1)))
        elif re.match(r'(PRIMARY KEY|UNIQUE KEY|KEY|CONSTRAINT|CHECK)', line, re.I): cons.append(line)
    return cols, cons

def er_name(value):
    return re.sub(r'[^A-Za-z0-9_]', '_', value)

def er_type(value):
    return re.sub(r'[^A-Za-z0-9_]', '', value.split('(', 1)[0].split()[0]).lower()

def obj_group(name):
    if 'order' in name or 'payment' in name: return 'Órdenes y pagos'
    if 'product' in name or 'categor' in name: return 'Productos y categorías'
    if 'cart' in name or 'wishlist' in name: return 'Carritos y wishlist'
    if 'address' in name or 'user' in name or 'buyer' in name: return 'Usuarios y direcciones'
    return 'Auditoría'

def render_table(t):
    technical = []
    for i,c in enumerate(t.get('columns', []),1):
        typ=c['type']; length=typ[typ.find('(')+1:-1] if '(' in typ else '—'
        default='Sin default' if c.get('default') == 'No especificado' else c.get('default','Sin default')
        technical.append(f'<tr><td>{i}</td><th scope="row">{esc(c["name"])}</th><td><code>{esc(typ)}</code></td><td>{esc(length)}</td><td>{esc(c["nullable"])}</td><td>{esc(default)}</td><td>{esc(c.get("extra","—"))}</td><td>{esc(c.get("key","No"))}</td><td>{esc(c["classification"]["descripcion_detallada"])}</td></tr>')
    classified=[]
    for c in t.get('columns', []):
        q=c['classification']
        classified.append(f'<tr class="column-row" data-nature="{esc(q["naturaleza"])}" data-obligation="{esc("Obligatorio" if q["obligatoriedad"].startswith("Obligatorio") else "Opcional")}" data-origin="{esc("Derivado" if q["origen"].startswith("Derivado") else "Almacenado")}" data-column="{esc((t["name"]+" "+c["name"]).lower())}"><th scope="row">{esc(c["name"])}</th><td>{esc(q["valor"])}</td><td>{esc(q["origen"])}</td><td>{esc(q["obligatoriedad"])}</td><td>{esc(q["llave"])}</td><td>{esc(q["naturaleza"])}</td><td><code>{esc(q["composicion_formal"])}</code></td><td>{esc(q["dominio"])}</td><td>{esc(q["descripcion_detallada"])}</td></tr>')
    return f'''<article class="table-card" id="{slug(t['name'])}" data-table="{esc(t['name'].lower())}" data-search="{esc(t['name'].lower())}">
      <details open><summary><h3>{esc(t['name'])}</h3><span class="table-module">{esc(obj_group(t['name']))}</span></summary>
      <div class="table-content"><p>{esc(t.get('description_detailed','Descripción del objeto según estructura.json.'))}</p>
      <h4>Notación formal</h4><pre class="formal">{esc(t.get('formal_notation','No disponible'))}</pre>
      <h4>Tabla técnica de columnas</h4><div class="table-wrap"><table><thead><tr><th>#</th><th>Nombre</th><th>Tipo</th><th>Longitud/precisión</th><th>NULL</th><th>Default</th><th>Extras</th><th>Llave</th><th>Descripción</th></tr></thead><tbody>{''.join(technical)}</tbody></table></div>
      <h4>Tabla de clasificación</h4><div class="table-wrap"><table><thead><tr><th>Nombre</th><th>Valor</th><th>Origen</th><th>Obligatoriedad</th><th>Llave</th><th>Naturaleza</th><th>Composición formal</th><th>Dominio</th><th>Descripción detallada</th></tr></thead><tbody>{''.join(classified)}</tbody></table></div></div></details></article>'''

def render_views():
 rows=[]
 for v in VIEWS:
  s=v['sql']; bases=list(dict.fromkeys(re.findall(r'\b(?:FROM|JOIN)\s+`([^`]+)`',s,re.I))); aliases=re.findall(r'\bAS\s+`([^`]+)`',s,re.I)
  rows.append(f'<article class="object-card"><h3>{esc(v["name"])}</h3><p>Consulta de trazabilidad definida en la vista.</p><p><b>Tablas base:</b> {esc(", ".join(bases) or "No inferidas del SQL")}</p><p><b>Columnas expuestas:</b> {esc(", ".join(aliases) or "Alias no inferidos del SQL")}</p></article>')
 return ''.join(rows)

def render_triggers():
 rows=[]
 for x in TRIGGERS:
  s=x['sql']; tab=re.search(r'ON\s+`([^`]+)`',s); ev=re.search(r'AFTER\s+(INSERT|UPDATE|DELETE)',s,re.I); cols=re.search(r'INSERT\s+INTO\s+`?tb_logs`?\s*\(([^)]*)\)',s,re.I); concat=re.search(r'CONCAT\s*\((.*?)\)\s*\)',s,re.S|re.I); fmt=' '.join(re.findall(r"'((?:[^']|'')*)'",concat.group(1))) if concat else 'Formato de description definido en el trigger.'
  rows.append(f'<tr><td><code>{esc(x["name"])}</code></td><td>{esc(tab.group(1) if tab else "No especificada")}</td><td>{esc(ev.group(1) if ev else "No especificado")}</td><td>AFTER</td><td>{esc(cols.group(1).replace("`","") if cols else "Ver definición")}</td><td>{esc(fmt)}</td></tr>')
 return ''.join(rows)

def render_procedures():
 rows=[]
 for p in PROCEDURES:
  s=p['sql']; params=re.search(r'PROCEDURE\s+`[^`]+`\s*\((.*?)\)\s*(?:BEGIN|begin)',s,re.S); affects=sorted(set(re.findall(r'\b(?:UPDATE|INSERT\s+INTO|DELETE\s+FROM)\s+`?([\w]+)',s,re.I)))
  rows.append(f'<article class="object-card"><h3>{esc(p["name"])}</h3><p><b>Parámetros:</b> <code>{esc(re.sub(r"\s+"," ",params.group(1)).strip() if params else "No especificados")}</code></p><p><b>Tablas afectadas:</b> {esc(", ".join(affects) or "Consultar el cuerpo SQL")}</p><pre><code>CALL {esc(p["name"])}(...);</code></pre><details><summary>Definición SQL</summary><pre><code>{esc(s)}</code></pre></details></article>')
 return ''.join(rows)

def render_domains():
 enums=collections.defaultdict(list); statuses=collections.defaultdict(list)
 for t in TABLES:
  for c in t.get('columns',[]):
   if c['type'].lower().startswith('enum'): enums[c['type']].append(t['name']+'.'+c['name'])
   if c['name'].lower()=='status': statuses[c['type']].append(t['name']+'.status')
 enum_rows=''.join(f'<tr><td><code>{esc(typ)}</code></td><td>{esc(", ".join(re.findall(r"\'([^\']*)\'",typ)))}</td><td>{esc(", ".join(uses))}</td></tr>' for typ,uses in enums.items())
 status_rows=''.join(f'<tr><td><code>{esc(typ)}</code></td><td>{"1 = activo; 0 = inactivo" if typ.lower().startswith("bit") else "Dominio entero definido por SQL"}</td><td>{esc(", ".join(uses))}</td></tr>' for typ,uses in statuses.items())
 return f'<h3>ENUM</h3><div class="table-wrap"><table><thead><tr><th>Tipo</th><th>Valores</th><th>Usos</th></tr></thead><tbody>{enum_rows}</tbody></table></div><h3>status</h3><div class="table-wrap"><table><thead><tr><th>Tipo</th><th>Significado/dominio</th><th>Usos</th></tr></thead><tbody>{status_rows}</tbody></table></div>'

def render_stats():
 nature=collections.Counter(); oblig=collections.Counter(); origin=collections.Counter(); keys=collections.Counter()
 for t in TABLES:
  for c in t.get('columns',[]):
   q=c['classification']; nature[q['naturaleza']]+=1; oblig['Obligatorio' if q['obligatoriedad'].startswith('Obligatorio') else 'Opcional']+=1; origin['Derivado' if q['origen'].startswith('Derivado') else 'Almacenado']+=1
   if q['llave'].startswith('PK'): keys['PK']+=1
   if 'FK →' in q['llave']: keys['FK']+=1
   if 'UK' in q['llave']: keys['UK']+=1
 groups=[('Naturaleza',nature),('Obligatoriedad',oblig),('Origen',origin),('Llaves',keys)]
 return ''.join(f'<h3>{title}</h3><ul>'+''.join(f'<li>{esc(k)}: {v}</li>' for k,v in counts.items())+'</ul>' for title,counts in groups)

def md_section(text, heading):
 match=re.search(r'^## '+re.escape(heading)+r'\s*$',text,re.M)
 if not match: return '<p>Sección no encontrada en el documento fuente.</p>'
 end=re.search(r'^## ',text[match.end():],re.M); body=text[match.end():match.end()+end.start()] if end else text[match.end():]
 out=[]
 for line in body.splitlines():
  line=line.strip()
  if not line: continue
  if line.startswith('### '): out.append('<h3>'+esc(line[4:])+'</h3>')
  elif line.startswith('- '): out.append('<li>'+esc(line[2:])+'</li>')
  elif line.startswith('|'):
   continue
  else: out.append('<p>'+esc(line)+'</p>')
 # Group adjacent list items into lists.
 result=[]; listing=False
 for item in out:
  if item.startswith('<li>'):
   if not listing: result.append('<ul>'); listing=True
   result.append(item)
  else:
   if listing: result.append('</ul>'); listing=False
   result.append(item)
 if listing: result.append('</ul>')
 return ''.join(result)

md_text=(SRC/'diccionario_datos.md').read_text(encoding='utf-8')
observations=md_section(md_text,'Observaciones de calidad del diseño')
conventions=md_section(md_text,'Convenciones de nombres')
legend=md_section(md_text,'Leyenda de la notación')+md_section(md_text,'Criterios de clasificación')
notes=''.join(f'<li>{esc(x)}</li>' for x in DATA.get('pending_confirmations',[]))
# Build modular ER diagrams from JSON constraints, keeping all local table/column definitions.
fk_list=[]
for t in TABLES:
 for line in split_defs(t['sql'])[1]:
  m=re.search(r'CONSTRAINT\s+`([^`]+)`\s+FOREIGN KEY\s*\(([^)]*)\)\s+REFERENCES\s+`([^`]+)`\s*\(([^)]*)\)',line,re.I)
  if m: fk_list.append((t['name'],m.group(1),m.group(2),m.group(3),m.group(4)))
MODULES={
 'Usuarios y direcciones':['tb_users','tb_user_addresses','tbd_address_components'],
 'Productos y categorías':['tb_products','tbc_categories','tbd_products_categories','tbd_products_users_providers'],
 'Carritos y wishlist':['tb_carts','tbd_carts_items','tbd_wishlist','tbd_users_wishlist_products'],
 'Órdenes y pagos':['tb_orders','tbd_order_details','tb_buyer_orders','tbd_order_items','tb_payments','tbc_payment_methods','tbc_payment_methods_types','tbd_user_payment_methods'],
 'Auditoría':['tb_logs']}
diagrams=[]
for module,names in MODULES.items():
 diagrams.append(f'<div class="diagram-panel"><h3>{esc(module)}</h3><div class="diagram-viewport"><div class="diagram-scale"><pre class="mermaid">erDiagram')
 for t in TABLES:
  if t['name'] not in names: continue
  cols,cons=split_defs(t['sql']); pk=[]
  for con in cons:
   if con.startswith('PRIMARY KEY'): pk=re.findall(r'`([^`]+)`',con)
  diagrams.append(f'{er_name(t["name"])} {{')
  for col,typ in cols:
   flags=[]
   if col in pk: flags.append('PK')
   if any(a==t['name'] and col in re.findall(r'`([^`]+)`',raw) for a,_,raw,_,_ in fk_list): flags.append('FK')
   diagrams.append(f'{er_type(typ)} {er_name(col)}'+(' '+', '.join(flags) if flags else ''))
  diagrams.append('}')
 for child,fk,raw,parent,raw_ref in fk_list:
  if child in names and parent in names:
   diagrams.append(f'{er_name(parent)} ||--o{{ {er_name(child)} : "{er_name(fk)}"')
 diagrams.append('</pre></div></div></div>')
diagram_html='\n'.join(diagrams)

nav=[('inicio','Inicio'),('tablas','Tablas'),('vistas','Vistas'),('triggers','Triggers'),('procedimientos','Procedimientos'),('dominios','Dominios y ENUM'),('convenciones','Convenciones'),('leyenda','Notación y criterios'),('resumen','Resumen estadístico'),('observaciones','Observaciones de calidad'),('diagrama','Diagrama ER')]
sidebar=''.join(f'<a href="#{i}">{esc(label)}</a>' for i,label in nav)
sections=[]
sections.append(f'<section id="tablas"><h2>Tablas</h2><div class="filters"><label>Filtrar naturaleza<select id="filter-nature"><option value="">Todas</option></select></label><label>Obligatoriedad<select id="filter-obligation"><option value="">Todas</option><option>Obligatorio</option><option>Opcional</option></select></label><label>Origen<select id="filter-origin"><option value="">Todos</option><option>Derivado</option><option>Almacenado</option></select></label><button id="clear-filters" type="button">Limpiar filtros</button></div><div id="table-list">'+''.join(render_table(t) for t in TABLES)+'</div></section>')
sections.append('<section id="vistas"><h2>Vistas</h2>'+render_views()+'</section>')
sections.append('<section id="triggers"><h2>Triggers</h2><div class="table-wrap"><table><thead><tr><th>Nombre</th><th>Tabla</th><th>Evento</th><th>Momento</th><th>Columnas escritas en tb_logs</th><th>Formato de description</th></tr></thead><tbody>'+render_triggers()+'</tbody></table></div></section>')
sections.append('<section id="procedimientos"><h2>Procedimientos</h2>'+render_procedures()+'</section>')
sections.append('<section id="dominios"><h2>Dominios y ENUM</h2>'+render_domains()+'</section>')
sections.append('<section id="convenciones"><h2>Convenciones de nombres</h2>'+conventions+'</section>')
sections.append('<section id="leyenda"><h2>Leyenda de la notación y criterios de clasificación</h2>'+legend+'</section>')
sections.append('<section id="resumen"><h2>Resumen estadístico</h2>'+render_stats()+'</section>')
sections.append('<section id="observaciones"><h2>Observaciones de calidad</h2>'+observations+'</section>')
sections.append('<section id="diagrama"><h2>Diagrama ER</h2><p>Diagramas generados a partir de las PK y FK del esquema. Usa los controles para ampliar o reducir; también puedes desplazarte dentro de cada módulo.</p><div class="zoom"><button type="button" data-zoom="out">−</button><button type="button" data-zoom="in">+</button><button type="button" data-zoom="reset">Restablecer</button></div>'+diagram_html+'</section>')
sections.append('<section id="pendientes"><h2>Pendientes por confirmar</h2><ul>'+notes+'</ul></section>')

html_doc=f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Diccionario de datos de db_test, MySQL 8.0.36"><title>Diccionario de datos · db_test</title><link rel="stylesheet" href="assets/site.css"><script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script><script defer src="assets/site.js"></script></head><body>
<aside class="sidebar"><a class="brand" href="#inicio">db_test</a><label class="search-label" for="site-search">Buscar tablas y columnas</label><input id="site-search" type="search" placeholder="Nombre de tabla o columna"><nav>{sidebar}</nav><div class="sidebar-actions"><button id="theme-toggle" type="button">Modo oscuro</button><a href="descargas/diccionario_datos.xlsx" download>Descargar XLSX</a><a href="descargas/diccionario_datos.md" download>Descargar Markdown</a><a href="descargas/schema.dbml" download>Descargar DBML</a></div></aside>
<main><section id="inicio" class="hero"><p class="eyebrow">Diccionario de datos</p><h1>db_test</h1><p>Esquema relacional documentado para <b>MySQL {esc(DATA['mysql_version'])}</b>.</p><div class="counts"><span><b>{len(TABLES)}</b> tablas</span><span><b>{len(VIEWS)}</b> vistas</span><span><b>{len(TRIGGERS)}</b> triggers</span><span><b>{len(PROCEDURES)}</b> procedimientos</span></div><p>Consulta el modelo, los dominios, la auditoría y las reglas del esquema. El sitio se genera desde <code>estructura.json</code>.</p></section>{''.join(sections)}<footer>Generado localmente con HTML, CSS y JavaScript. Mermaid.js 11.4.1 se carga desde jsDelivr.</footer></main></body></html>'''

OUT.mkdir(exist_ok=True); DOWNLOADS.mkdir(parents=True,exist_ok=True); ASSETS.mkdir(parents=True,exist_ok=True)
(OUT/'index.html').write_text(html_doc,encoding='utf-8')
for name in ('diccionario_datos.xlsx','diccionario_datos.md','schema.dbml'):
 shutil.copy2(SRC/name,DOWNLOADS/name)
(OUT/'.nojekyll').write_text('',encoding='utf-8')

css=r'''/* Static, responsive, accessible styles */
:root{color-scheme:light;--bg:#f4f7fb;--surface:#fff;--text:#172334;--muted:#58677a;--line:#d5deea;--accent:#1459a6;--accent-soft:#e5f0ff;--shadow:0 8px 28px #19324d12}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:1rem}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}.sidebar{position:fixed;inset:0 auto 0 0;width:270px;padding:1.1rem;background:var(--surface);border-right:1px solid var(--line);overflow-y:auto;z-index:5}.brand{display:block;font-size:1.5rem;font-weight:800;color:var(--accent);text-decoration:none;margin-bottom:1rem}.search-label,.filters label{display:block;color:var(--muted);font-size:.84rem;font-weight:650}.sidebar input,.filters select{width:100%;padding:.6rem;border:1px solid var(--line);border-radius:.5rem;background:var(--surface);color:var(--text);margin:.3rem 0 .9rem}.sidebar nav{display:grid;gap:.15rem;margin:.5rem 0 1.2rem}.sidebar nav a,.sidebar-actions a{display:block;padding:.4rem .55rem;color:var(--text);text-decoration:none;border-radius:.4rem}.sidebar nav a:hover,.sidebar-actions a:hover{background:var(--accent-soft);color:var(--accent)}.sidebar-actions{border-top:1px solid var(--line);padding-top:.8rem}.sidebar button,.zoom button,.filters button{padding:.5rem .75rem;border:1px solid var(--line);border-radius:.45rem;background:var(--surface);color:var(--text);cursor:pointer}.sidebar button{width:100%;margin-bottom:.4rem}main{margin-left:270px;padding:2.2rem clamp(1rem,3vw,3rem);max-width:1800px}.hero{padding:2.5rem;border-radius:1.2rem;background:linear-gradient(130deg,#113f75,#1d75ba);color:white;box-shadow:var(--shadow)}.hero h1{font-size:clamp(2.3rem,5vw,4.3rem);line-height:1.1;margin:.1rem 0}.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-weight:700;opacity:.8}.counts{display:flex;flex-wrap:wrap;gap:.65rem;margin:1.5rem 0}.counts span{padding:.6rem .9rem;border:1px solid #ffffff66;border-radius:.7rem;background:#ffffff16}.counts b{font-size:1.35rem;margin-right:.25rem}section:not(.hero){margin:2rem 0;padding:1.3rem;background:var(--surface);border:1px solid var(--line);border-radius:1rem;box-shadow:var(--shadow)}h2{margin:.1rem 0 1rem;font-size:1.7rem}h3{font-size:1.18rem;margin:.4rem 0}h4{margin:1.1rem 0 .5rem}.filters{display:flex;flex-wrap:wrap;align-items:end;gap:.8rem;margin:1rem 0}.filters label{min-width:175px}.filters select{display:block;margin:.3rem 0 0}.table-card,.object-card,.diagram-panel{margin:1rem 0;border:1px solid var(--line);border-radius:.75rem;background:var(--surface)}.table-card summary{display:flex;align-items:center;gap:1rem;cursor:pointer;padding:.5rem 1rem}.table-card summary h3{margin:.4rem 0}.table-module{margin-left:auto;color:var(--muted);font-size:.9rem}.table-content,.object-card{padding:1rem}.formal,pre{max-width:100%;overflow:auto;padding:.8rem;border-radius:.5rem;background:var(--accent-soft);white-space:pre-wrap;overflow-wrap:anywhere}.table-wrap{max-width:100%;overflow:auto;border:1px solid var(--line);border-radius:.5rem;margin:.65rem 0 1rem}table{border-collapse:collapse;width:100%;min-width:950px;font-size:.88rem}th,td{padding:.55rem .65rem;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}thead{position:sticky;top:0;background:var(--accent-soft);z-index:1}th{font-weight:700}tbody tr:nth-child(even){background:color-mix(in srgb,var(--surface) 88%,var(--accent-soft))}.object-card h3{margin-top:0}.diagram-panel{padding:.8rem}.diagram-viewport{max-width:100%;max-height:650px;overflow:auto;border:1px solid var(--line);border-radius:.5rem;padding:1rem}.diagram-scale{transform-origin:top left;width:max-content;min-width:100%}.diagram-scale pre{background:transparent}.zoom{display:flex;gap:.5rem;margin:.6rem 0}.zoom button{font-size:1.1rem}footer{padding:2rem;color:var(--muted);text-align:center}.hidden{display:none!important}body.dark{color-scheme:dark;--bg:#111923;--surface:#192432;--text:#e4edf7;--muted:#a9b8c9;--line:#35465a;--accent:#8ec5ff;--accent-soft:#20364e;--shadow:0 8px 28px #0004}body.dark .hero{background:linear-gradient(130deg,#101f32,#183b59)}
@media(max-width:900px){.sidebar{position:sticky;inset:0;width:auto;max-height:48vh;border-right:0;border-bottom:1px solid var(--line)}.sidebar nav{grid-template-columns:repeat(auto-fit,minmax(130px,1fr));max-height:120px;overflow:auto}.sidebar-actions{display:flex;flex-wrap:wrap;gap:.2rem}.sidebar-actions button,.sidebar-actions a{width:auto;margin:0}main{margin-left:0;padding:1rem}.hero{padding:1.5rem}section:not(.hero){padding:1rem}}
'''
(ASSETS/'site.css').write_text(css,encoding='utf-8')
js=r'''document.addEventListener('DOMContentLoaded',()=>{
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
'''
(ASSETS/'site.js').write_text(js,encoding='utf-8')
print(f'Generated {OUT} with {len(TABLES)} tables, {len(VIEWS)} views, {len(TRIGGERS)} triggers, {len(PROCEDURES)} procedures.')

