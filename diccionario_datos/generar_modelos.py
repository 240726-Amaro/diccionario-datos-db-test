# Generate model files and XLSX directly from estructura.json
import json,re,pathlib,zipfile,xml.sax.saxutils as sx
from collections import defaultdict
D=pathlib.Path(__file__).parent; O=json.loads((D/'estructura.json').read_text(encoding='utf-8'))['objects']; ts=[x for x in O if x['kind']=='table']; vs=[x for x in O if x['kind']=='view']; gs=[x for x in O if x['kind']=='trigger']; ps=[x for x in O if x['kind']=='procedure']
def tablecols(t):
 cols=[]; cons=[]
 for ln in t['sql'].splitlines():
  z=ln.strip().rstrip(','); m=re.match(r'`([^`]+)`\s+(.+)',z)
  if m and m.group(1).upper() not in ('PRIMARY','UNIQUE','KEY','CONSTRAINT','FOREIGN','CHECK'):
   cols.append((m.group(1),re.match(r'(\w+(?:\s*\([^)]*\))?)',m.group(2)).group(1)))
  elif re.match(r'(PRIMARY KEY|UNIQUE KEY|KEY|CONSTRAINT|CHECK)',z,re.I): cons.append(z)
 return cols,cons
fks=[]
for t in ts:
 for z in tablecols(t)[1]:
  m=re.search(r'CONSTRAINT\s+`([^`]+)`\s+FOREIGN KEY\s*\(([^)]*)\)\s+REFERENCES\s+`([^`]+)`\s*\(([^)]*)\)(.*)',z,re.I)
  if m: fks.append((t['name'],m.group(1),m.group(2),m.group(3),m.group(4),m.group(5).strip()))
# ER Mermaid
mmd=['erDiagram']
for t in ts:
 cols,cons=tablecols(t); pkcols=[]
 for z in cons:
  if z.startswith('PRIMARY KEY'): pkcols=re.findall(r'`([^`]+)`',z)
 mmd.append('  '+t['name']+' {')
 for c,typ in cols:
  flag=' PK' if c in pkcols else ''
  if any(a==t['name'] and c in re.findall(r'`([^`]+)`',cc) for a,_,cc,_,_,_ in fks): flag+=' FK'
  mmd.append(f'    {typ.replace(" ","_")} {c}{flag}')
 mmd.append('  }')
for a,n,c,b,bc,act in fks: mmd.append(f'  {b} ||--o{{ {a} : "{n}"')
(D/'diagrama_er.mmd').write_text('\n'.join(mmd)+'\n',encoding='utf-8')
# DBML
bml=[]
for t in ts:
 cols,cons=tablecols(t); bml += [f'Table {t["name"]} {{']
 pkcols=[]
 for z in cons:
  if z.startswith('PRIMARY KEY'): pkcols=re.findall(r'`([^`]+)`',z)
 for c,typ in cols: bml.append(f'  {c} {typ}'+(' [pk]' if c in pkcols else ''))
 bml.append('}')
for a,n,c,b,bc,act in fks:
 ca=re.findall(r'`([^`]+)`',c); cb=re.findall(r'`([^`]+)`',bc); left=f'{a}.{ca[0]}' if len(ca)==1 else f'({", ".join(a+"."+q for q in ca)})'; right=f'{b}.{cb[0]}' if len(cb)==1 else f'({", ".join(b+"."+q for q in cb)})'; bml.append(f'Ref: {left} > {right} // {n} {act}')
(D/'schema.dbml').write_text('\n'.join(bml)+'\n',encoding='utf-8')
# workbook rows from schema (inline strings, no optional packages)
sheets={}
sheets['Tablas']=[['Tabla','Prefijo/tipo','Módulo','Motor','Charset','Collation','Descripción detallada','Notación formal']]+[[t['name'], 'principal tb_' if t['name'].startswith('tb_') else 'catálogo tbc_' if t['name'].startswith('tbc_') else 'detalle tbd_','Según descripción inferida','InnoDB','utf8mb4','utf8mb4_0900_ai_ci',t.get('description_detailed','No especificado'),t.get('formal_notation','No especificado')] for t in ts]
sheets['Columnas']=[['Tabla','#','Columna','Tipo','Longitud/precisión','NULL','Default','Extras','Llave técnica','Valor','Origen','Obligatoriedad','Llave','Naturaleza','Composición formal','Dominio','Descripción detallada']]
for t in ts:
 cs,co=tablecols(t)
 for i,(c,typ) in enumerate(cs,1):
  full=next((z.strip().rstrip(',') for z in t['sql'].splitlines() if re.match(r'\s*`'+re.escape(c)+r'`\s+',z)), ''); null='NO' if 'NOT NULL' in full.upper() else 'Sí'; default=(re.search(r'\bDEFAULT\s+((?:\'[^\']*\')|(?:[^\s,]+))',full,re.I) or [None,'No especificado'])[1]; extra='AUTO_INCREMENT' if 'AUTO_INCREMENT' in full else 'GENERATED STORED' if 'STORED' in full else 'ON UPDATE CURRENT_TIMESTAMP' if 'ON UPDATE' in full else '—'; key='PK' if any(z.startswith('PRIMARY KEY') and f'`{c}`' in z for z in co) else 'FK' if any(a==t['name'] and f'`{c}`' in cc for a,_,cc,_,_,_ in fks) else 'UK/INDEX' if any(('UNIQUE' in z or z.startswith('KEY')) and f'`{c}`' in z for z in co) else '—'; length=typ[typ.find('(')+1:-1] if '(' in typ else '—'; desc='1 activo / 0 inactivo' if c.lower()=='status' and typ.lower().startswith('bit') else 'No especificado'
  rich=next((x for x in t.get('columns',[]) if x['name']==c),None); q=rich.get('classification',{}) if rich else {}; sheets['Columnas'].append([t['name'],i,c,typ,length,null,default,extra,key,q.get('valor','No especificado'),q.get('origen','No especificado'),q.get('obligatoriedad','No especificado'),q.get('llave','No especificado'),q.get('naturaleza','No especificado'),q.get('composicion_formal','No especificado'),q.get('dominio','No especificado'),q.get('descripcion_detallada','No especificado')])
sheets['Relaciones']=[['Nombre FK','Tabla','Columna(s)','Tabla referenciada','Columna(s) ref.','Acciones']]+[list(x) for x in fks]
sheets['Vistas']=[['Vista','Tablas base','Columnas expuestas','Origen/tipo']]
for v in vs:
 s=v['sql']; bases=', '.join(dict.fromkeys(re.findall(r'\b(?:FROM|JOIN)\s+`([^`]+)`',s,re.I))); aliases=', '.join(re.findall(r'\bAS\s+`([^`]+)`',s,re.I)); sheets['Vistas'].append([v['name'],bases,aliases,'Derivado de expresión SQL; tipo inferido'])
sheets['Triggers']=[['Nombre','Tabla','Evento','Momento','Columnas log','Formato description']]
for g in gs:
 s=g['sql']; tb=re.search(r'ON\s+`([^`]+)`',s); ev=re.search(r'AFTER\s+(INSERT|UPDATE|DELETE)',s); cc=re.search(r'INSERT\s+INTO\s+`?tb_logs`?\s*\(([^)]*)\)',s,re.I); concat=re.search(r'CONCAT\s*\((.*?)\)\s*\)',s,re.S|re.I); fmt=' '.join(re.findall(r"'((?:[^']|'')*)'",concat.group(1))) if concat else 'description sin plantilla CONCAT identificable'; sheets['Triggers'].append([g['name'],tb.group(1) if tb else '',ev.group(1) if ev else '', 'AFTER',cc.group(1).replace('`','') if cc else 'No especificado',fmt+' (valores dinámicos NEW/OLD)'])
sheets['Procedimientos']=[['Nombre','Parámetros','Tablas afectadas','Descripción','Ejemplo']]
for p in ps:
 s=p['sql']; pa=re.search(r'PROCEDURE\s+`[^`]+`\s*\((.*?)\)\s*(?:BEGIN|begin)',s,re.S); affects=', '.join(sorted(set(re.findall(r'\b(?:UPDATE|INSERT\s+INTO|DELETE\s+FROM)\s+`?([\w]+)',s,re.I)))); params=re.sub(r'\s+',' ',pa.group(1)).strip() if pa else 'No especificado'; sheets['Procedimientos'].append([p['name'],params,affects,'Borrado lógico; consultar cuerpo del procedimiento',f'CALL {p["name"]}(...);'])
sheets['Dominios_ENUM']=[['Tipo/dominio','Valores','Usos']]
enums=defaultdict(list); stats=defaultdict(list)
for t in ts:
 for c,typ in tablecols(t)[0]:
  if typ.lower().startswith('enum'): enums[typ].append(t['name']+'.'+c)
  if c.lower()=='status': stats[typ].append(t['name']+'.'+c)
for typ,uses in enums.items(): sheets['Dominios_ENUM'].append([typ,typ[5:-1],', '.join(uses)])
for typ,uses in stats.items(): sheets['Dominios_ENUM'].append(['status '+typ,'1 activo / 0 inactivo si bit; tinyint sin dominio declarado',', '.join(uses)])
obs=['Se reporta en diccionario_datos.md con severidad y recomendación.']
sheets['Observaciones']=[['Severidad','Hallazgo','Recomendación']]+[['Alta',x,'Consultar sección Observaciones de calidad del diseño en diccionario_datos.md.'] for x in ['category_ID sin FK','Modelos de orden potencialmente duplicados','tb_buyer_orders no identifica comprador']]+[['Media',x,'Consultar sección de observaciones.'] for x in ['Referencias parciales al proveedor-producto','Tipos relacionados y status inconsistentes']]
counts=defaultdict(int)
for t in ts:
 for c in t.get('columns',[]):
  q=c['classification']; counts['Naturaleza: '+q['naturaleza']]+=1; counts['Obligatoriedad: '+('Obligatorio' if q['obligatoriedad'].startswith('Obligatorio') else 'Opcional')]+=1; counts['Origen: '+('Derivado' if q['origen'].startswith('Derivado') else 'Almacenado')]+=1
  for key in ('PK','FK','UK'):
   if q['llave'].startswith(key) if key=='PK' else (key=='FK' and 'FK →' in q['llave']) or (key=='UK' and 'UK' in q['llave']): counts['Llave: '+key]+=1
sheets['Resumen estadístico']=[['Métrica','Cantidad']]+[[k,v] for k,v in sorted(counts.items())]
# xlsx minimal OOXML
names=list(sheets); esc=lambda v:sx.escape(str(v if v is not None else ''))
def colname(n):
 s=''
 while n: n,r=divmod(n-1,26); s=chr(65+r)+s
 return s
with zipfile.ZipFile(D/'diccionario_datos.xlsx','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'+''.join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1,len(names)+1))+'</Types>')
 z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
 z.writestr('xl/workbook.xml','<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'+''.join(f'<sheet name="{sx.escape(n)}" sheetId="{i}" r:id="rId{i}"/>' for i,n in enumerate(names,1))+'</sheets></workbook>')
 z.writestr('xl/_rels/workbook.xml.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,len(names)+1))+f'<Relationship Id="rId{len(names)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
 for i,n in enumerate(names,1):
  rows=[]
  for ri,row in enumerate(sheets[n],1): rows.append('<row r="%d">'%ri+''.join(f'<c r="{colname(ci)}{ri}" s="{2 if ri==1 else 1}" t="inlineStr"><is><t>{esc(val)}</t></is></c>' for ci,val in enumerate(row,1))+'</row>')
  end=colname(max(len(r) for r in sheets[n])); z.writestr(f'xl/worksheets/sheet{i}.xml','<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><sheetFormatPr defaultRowHeight="30"/><sheetData>'+''.join(rows)+f'</sheetData><autoFilter ref="A1:{end}{len(sheets[n])}"/></worksheet>')
 z.writestr('xl/styles.xml','<?xml version="1.0" encoding="UTF-8"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFD9EAF7"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf><xf numFmtId="0" fontId="1" fillId="1" borderId="0" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf><xf numFmtId="0" fontId="0" fillId="0" borderId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf></cellXfs></styleSheet>')
# README
(D/'README.md').write_text('# Diccionario de datos de db_test\n\nSe generaron `diccionario_datos.md`, `diccionario_datos.xlsx`, `diagrama_er.mmd` y `schema.dbml`. `estructura.json` contiene exclusivamente definiciones CREATE y metadatos derivados de columnas, restricciones y triggers; no contiene INSERT.\n\n## Regeneración\n\nDesde la raíz del repositorio, con Python 3:\n\n```powershell\npython diccionario_datos\\extraer.py\npython diccionario_datos\\generar.py\npython diccionario_datos\\generar_modelos.py\npython diccionario_datos\\validar.py\n```\n\nEl XLSX incluye autofiltros, encabezado congelado y ajuste de texto. `Resumen estadístico` consolida las clasificaciones por naturaleza, obligatoriedad, origen y llaves. `validar.py` revisa secciones por tabla, descripciones y el total de filas de clasificación en Markdown y XLSX. No se requiere instalar librerías externas.\n',encoding='utf-8')
# validation
counts={k:sum(x['kind']==k for x in O) for k in ('table','view','trigger','procedure')}; missing=[x[1] for x in fks if x[1] not in (D/'diccionario_datos.md').read_text(encoding='utf-8')]
print(json.dumps({'conteos':counts,'FK_SQL':len(fks),'FK_nombres_ausentes_en_diccionario':missing,'hojas_XLSX':names},ensure_ascii=False))
