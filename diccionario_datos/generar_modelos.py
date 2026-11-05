# Generate model files and XLSX directly from estructura.json
import json,re,pathlib,zipfile,xml.sax.saxutils as sx
from collections import defaultdict
D=pathlib.Path(__file__).parent; DATA=json.loads((D/'estructura.json').read_text(encoding='utf-8')); O=DATA['objects']; selected=DATA.get('dictionary_tables', [x['name'] for x in O if x['kind']=='table'][:25]); ts=sorted((x for x in O if x['kind']=='table' and x['name'] in selected),key=lambda x:selected.index(x['name'])); vs=[x for x in O if x['kind']=='view']; gs=[x for x in O if x['kind']=='trigger']; ps=[x for x in O if x['kind']=='procedure']; fs=[x for x in O if x['kind']=='function']
SOURCE_NOTE=f"Estructura y totales de registros obtenidos del respaldo BD19.sql (fecha del archivo: {DATA.get('source_modified')}). Conteo de registros realizado el: {DATA.get('row_counted_at')}. Los totales corresponden al respaldo, no a la instancia en vivo."
def tablecols(t):
 cols=[]; cons=[]
 for ln in t['sql'].splitlines():
  z=ln.strip().rstrip(','); m=re.match(r'`([^`]+)`\s+(.+)',z)
  if m and m.group(1).upper() not in ('PRIMARY','UNIQUE','KEY','CONSTRAINT','FOREIGN','CHECK'):
   cols.append((m.group(1),re.match(r'(\w+(?:\s*\([^)]*\))?(?:\s+unsigned)?(?:\s+zerofill)?)',m.group(2),re.I).group(1)))
  elif re.match(r'(PRIMARY KEY|UNIQUE KEY|KEY|CONSTRAINT|CHECK)',z,re.I): cons.append(z)
 return cols,cons
fks=[]
for t in ts:
 for z in tablecols(t)[1]:
  m=re.search(r'CONSTRAINT\s+`([^`]+)`\s+FOREIGN KEY\s*\(([^)]*)\)\s+REFERENCES\s+`([^`]+)`\s*\(([^)]*)\)(.*)',z,re.I)
  if m: fks.append((t['name'],m.group(1),m.group(2),m.group(3),m.group(4),m.group(5).strip()))
# ER Mermaid. A single valid ER diagram uses comments as module separators.
def er_module(name):
 if any(k in name for k in ('shipment','return','refund','cancellation')): return 'Envíos, devoluciones y cancelaciones'
 if 'people' in name or 'user' in name or 'address' in name: return 'Usuarios y direcciones'
 if any(k in name for k in ('product','categor')): return 'Productos y categorías'
 if any(k in name for k in ('cart','wishlist')): return 'Carritos y wishlist'
 if any(k in name for k in ('order','payment')): return 'Órdenes y pagos'
 return 'Auditoría'
mmd=['erDiagram']
for module in dict.fromkeys(er_module(t['name']) for t in ts):
 mmd.append('  %% Módulo: '+module)
 for t in ts:
  if er_module(t['name'])!=module: continue
  cols,cons=tablecols(t); pkcols=[]
  for z in cons:
   if z.startswith('PRIMARY KEY'): pkcols=re.findall(r'`([^`]+)`',z)
  mmd.append('  '+t['name']+' {')
  for c,typ in cols:
   flag=' PK' if c in pkcols else ''
   if any(a==t['name'] and c in re.findall(r'`([^`]+)`',cc) for a,_,cc,_,_,_ in fks): flag+=' FK'
   base_type=typ.lower().split('(',1)[0].split()[0] if typ.strip() else 'string'
   safe_type=base_type+('_unsigned' if 'unsigned' in typ.lower() else '')+('_zerofill' if 'zerofill' in typ.lower() else '')
   mmd.append(f'    {safe_type} {c}{", " + flag.strip().replace(" ", ", ") if flag else ""}')
  mmd.append('  }')
for module in dict.fromkeys(er_module(a) for a,_,_,_,_,_ in fks):
 mmd.append('  %% Relaciones: '+module)
 for a,n,c,b,bc,act in fks:
  if er_module(a)==module: mmd.append(f'  {b} ||--o{{ {a} : "{n}"')
# No reescribir diagramas en esta actualización de solo diccionario.
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
# El ER y DBML que acompañan al diccionario reflejan el mismo subconjunto de 25 tablas.
(D/'diagrama_er.mmd').write_text('\n'.join(mmd)+'\n',encoding='utf-8')
(D/'schema.dbml').write_text('\n'.join(bml)+'\n',encoding='utf-8')
# workbook rows from schema (inline strings, no optional packages)
sheets={}
sheets['Tablas']=[['Tabla','Registros BD19','Prefijo/tipo','Módulo','Motor','Charset','Collation','Descripción detallada','Notación formal']]+[[t['name'],DATA.get('row_counts',{}).get(t['name'],0), 'principal tb_' if t['name'].startswith('tb_') else 'catálogo tbc_' if t['name'].startswith('tbc_') else 'detalle tbd_','Según descripción inferida','InnoDB','utf8mb4','utf8mb4_0900_ai_ci',t.get('description_detailed','Descripción derivada del esquema.'),t.get('formal_notation','')] for t in ts]
sheets['Columnas']=[['Tabla','#','Columna','Tipo','Longitud/precisión','NULL','Default','Extras','Llave técnica','Valor','Origen','Obligatoriedad','Llave','Naturaleza','Composición formal','Dominio','Descripción detallada']]
for t in ts:
 cs,co=tablecols(t)
 for i,(c,typ) in enumerate(cs,1):
  full=next((z.strip().rstrip(',') for z in t['sql'].splitlines() if re.match(r'\s*`'+re.escape(c)+r'`\s+',z)), ''); null='NO' if 'NOT NULL' in full.upper() else 'Sí'; default=(re.search(r'\bDEFAULT\s+((?:\'[^\']*\')|(?:[^\s,]+))',full,re.I) or [None,'Sin dato declarado'])[1]; extra='AUTO_INCREMENT' if 'AUTO_INCREMENT' in full else 'GENERATED STORED' if 'STORED' in full else 'ON UPDATE CURRENT_TIMESTAMP' if 'ON UPDATE' in full else '—'; key='PK' if any(z.startswith('PRIMARY KEY') and f'`{c}`' in z for z in co) else 'FK' if any(a==t['name'] and f'`{c}`' in cc for a,_,cc,_,_,_ in fks) else 'UK/INDEX' if any(('UNIQUE' in z or z.startswith('KEY')) and f'`{c}`' in z for z in co) else '—'; length=typ[typ.find('(')+1:-1] if '(' in typ else '—'; desc='1 activo / 0 inactivo' if c.lower()=='status' and typ.lower().startswith('bit') else 'Sin dato declarado'
  rich=next((x for x in t.get('columns',[]) if x['name']==c),None); q=rich.get('classification',{}) if rich else {}; sheets['Columnas'].append([t['name'],i,c,typ,length,null,default,extra,key,q.get('valor','Sin dato declarado'),q.get('origen','Sin dato declarado'),q.get('obligatoriedad','Sin dato declarado'),q.get('llave','Sin dato declarado'),q.get('naturaleza','Sin dato declarado'),q.get('composicion_formal','Sin dato declarado'),q.get('dominio','Sin dato declarado'),q.get('descripcion_detallada','Sin dato declarado')])
sheets['Relaciones']=[['Nombre FK','Tabla','Columna(s)','Tabla referenciada','Columna(s) ref.','Acciones']]+[list(x) for x in fks]
sheets['Indices_restricciones']=[['Tabla','Tipo','Nombre/definición']]
for table in ts:
 for definition in tablecols(table)[1]:
  upper=definition.upper()
  kind='PK' if upper.startswith('PRIMARY KEY') else 'UNIQUE' if upper.startswith('UNIQUE') else 'INDEX' if upper.startswith('KEY') else 'FK' if 'FOREIGN KEY' in upper else 'CHECK' if 'CHECK' in upper else 'CONSTRAINT'
  sheets['Indices_restricciones'].append([table['name'],kind,definition])
sheets['Vistas']=[['Vista','Tablas base','Columnas expuestas','Origen/tipo']]
for v in vs:
 s=v['sql']; bases=', '.join(dict.fromkeys(re.findall(r'\b(?:FROM|JOIN)\s+`([^`]+)`',s,re.I))); aliases=', '.join(re.findall(r'\bAS\s+`([^`]+)`',s,re.I)); sheets['Vistas'].append([v['name'],bases,aliases,'Derivado de expresión SQL; tipo inferido'])
sheets['Triggers']=[['Nombre','Tabla','Evento','Momento','Columnas log','Formato description']]
for g in gs:
 s=g['sql']; tb=re.search(r'ON\s+`([^`]+)`',s); ev=re.search(r'AFTER\s+(INSERT|UPDATE|DELETE)',s); cc=re.search(r'INSERT\s+INTO\s+`?tb_logs`?\s*\(([^)]*)\)',s,re.I); concat=re.search(r'CONCAT\s*\((.*?)\)\s*\)',s,re.S|re.I); fmt=' '.join(re.findall(r"'((?:[^']|'')*)'",concat.group(1))) if concat else 'description sin plantilla CONCAT identificable'; sheets['Triggers'].append([g['name'],tb.group(1) if tb else '',ev.group(1) if ev else '', 'AFTER',cc.group(1).replace('`','') if cc else 'Sin dato declarado',fmt+' (valores dinámicos NEW/OLD)'])
sheets['Procedimientos']=[['Nombre','Parámetros','Tablas afectadas','Descripción','Ejemplo']]
def routine_signature(sql, kind='PROCEDURE'):
 m=re.search(r'\b'+kind+r'\s+`[^`]+`\s*\(',sql,re.I)
 if not m: return ''
 start=m.end(); depth=1; i=start
 while i<len(sql) and depth:
  if sql[i]=='(': depth+=1
  elif sql[i]==')': depth-=1
  i+=1
 return sql[start:i-1] if depth==0 else ''
proc_descriptions={
 'sp_gen_validate_params':('Valida total (1–100000), edades (18–100), porcentaje activo (0–100) y país existente; señala error si falla.', 'tbc_gen_country_profile'),
 'sp_gen_insert_user_person':('Inserta la cuenta y su perfil personal, y devuelve el ID mediante parámetro OUT.', 'tb_users, tb_people'),
 'sp_generate_users':('Valida los argumentos y genera en lote usuarios/personas usando los catálogos y funciones fn_gen_* dentro de una transacción.', 'tb_users, tb_people, tbc_gen_*; tb_logs por triggers'),
 'sp_register_user_person':('Valida y registra conjuntamente una cuenta y su perfil personal (inferido).','tb_users, tb_people (inferido)'),
 'sp_soft_delete':('Valida la tabla e identificador indicados y aplica borrado lógico al registro permitido.','tabla indicada por parámetro'),
 'sp_soft_delete_product':('Comprueba el producto y marca su status como inactivo, conservando el historial.','tb_products'),
 'sp_soft_delete_user':('Comprueba la cuenta y marca su status como inactivo, conservando el historial.','tb_users')}
for p in ps:
 s=p['sql']; params=re.sub(r'\s+',' ',routine_signature(s)).strip(); desc,affects=proc_descriptions.get(p['name'],('Operaciones definidas en el cuerpo SQL.', 'tablas declaradas por el cuerpo SQL')); args=re.findall(r'(?:IN|OUT|INOUT)\s+(\w+)',params,re.I); sheets['Procedimientos'].append([p['name'],params,affects,desc,f"CALL {p['name']}({', '.join('@'+a for a in args)});"])
if fs:
 sheets['Funciones']=[['Nombre','Parámetros','Retorno','Características','Descripción','Ejemplo']]
 for f in fs:
  sig=re.search(r'FUNCTION\s+`[^`]+`\s*\((.*?)\)\s*RETURNS\s+([^\n]+)',f['sql'],re.S|re.I)
  descriptions={'fn_gen_birth_date':'Fecha aleatoria dentro de edades mínima/máxima.','fn_gen_courtesy_title':'Título de cortesía por país y género.','fn_gen_datetime_between':'Fecha y hora aleatoria entre dos límites.','fn_gen_email':'Construye correo de prueba desde nombre, apellido y secuencia.','fn_gen_email_domain':'Elige dominio example.com, example.org o example.net.','fn_gen_family_name':'Selecciona apellido aleatorio del catálogo del país.','fn_gen_gender_id':'Devuelve género aleatorio 1 o 2.','fn_gen_given_name':'Selecciona nombre por país y género.','fn_gen_is_active':'Distribuye estado activo según porcentaje solicitado.','fn_gen_nickname':'Construye alias con inicial, apellido y secuencia.','fn_gen_password_hash':'Genera SHA-256 de texto aleatorio basado en UUID/RAND.','fn_gen_phone':'Construye teléfono según perfil del país.','fn_gen_random_country':'Elige un perfil de país activo.','fn_gen_random_int':'Devuelve entero aleatorio en rango inclusivo.','fn_gen_slug':'Normaliza texto eliminando espacios y signos indicados.'}
  sheets['Funciones'].append([f['name'],re.sub(r'\s+',' ',sig.group(1)).strip() if sig else '',sig.group(2).strip() if sig else '',', '.join(x for x in ('DETERMINISTIC','NO SQL','READS SQL DATA') if re.search(r'\b'+x+r'\b',f['sql'],re.I)),descriptions.get(f['name'],'Descripción derivada del SQL.'),f"SELECT {f['name']}( ... );"])
row_counts=DATA.get('row_counts',{})
for table in ts: row_counts.setdefault(table['name'],'No verificable en el respaldo')
row_total=sum(v for v in row_counts.values() if isinstance(v,int)); verified=sum(isinstance(row_counts.get(t['name']),int) for t in ts)
sheets['Volumen_datos']=[['Tabla','Registros','Porcentaje del total']]
for table in sorted(ts,key=lambda t:(-(row_counts[t['name']] if isinstance(row_counts[t['name']],int) else -1),t['name'])):
 n=row_counts[table['name']]; sheets['Volumen_datos'].append([table['name'],n,f'{100*n/row_total:.2f}%' if isinstance(n,int) and row_total else '—'])
sheets['Volumen_datos'].append(['TOTAL verificable',row_total,'100.00%'])
sheets['Volumen_datos'] += [['Tablas sin INSERT verificable',len(ts)-verified,''],['Fuente',SOURCE_NOTE,'Conteo de filas INSERT; no es un conteo en vivo.'],['Nota','tb_logs crece con INSERT/UPDATE/DELETE auditados; tb_users y tb_people contienen gran parte de datos de prueba generados.','']]
sheets['Convenciones']=[['Elemento','Convención'],['tb_','Tabla principal'],['tbc_','Catálogo'],['tbd_','Detalle o relación'],['vw_','Vista'],['trg_','Trigger'],['sp_','Procedimiento'],['fk_','Llave foránea'],['uk_','Restricción UNIQUE'],['chk_','Restricción CHECK'],['creation_date / last_update','Fechas de ciclo de vida; ver default por columna'],['status','Dominio depende del tipo SQL; bit(1) y tinyint no se presumen equivalentes']]
sheets['Historial_cambios']=[['Versión','Objeto','Cantidad','Detalle'],
 ['BD19','Esquema completo',DATA.get('counts',{}).get('tables',0),'Fuente: Practica03/backups/BD19.sql.'],
 ['BD19','Vistas',DATA.get('counts',{}).get('views',0),'Definiciones finales del respaldo.'],
 ['BD19','Triggers',DATA.get('counts',{}).get('triggers',0),'Definiciones del respaldo.'],
 ['BD19','Procedimientos',DATA.get('counts',{}).get('procedures',0),'Definiciones del respaldo.'],
 ['BD19','Funciones',DATA.get('counts',{}).get('functions',0),'Definiciones del respaldo.'],
 ['BD19','Tablas en este diccionario',len(ts),'25 tablas: primero las pobladas y después las que no tienen filas verificables.']]
sheets['Dominios_ENUM']=[['Tipo/dominio','Valores','Usos']]
enums=defaultdict(list); stats=defaultdict(list)
for t in ts:
 for c,typ in tablecols(t)[0]:
  if typ.lower().startswith('enum'): enums[typ].append(t['name']+'.'+c)
  if c.lower()=='status': stats[typ].append(t['name']+'.'+c)
for typ,uses in enums.items(): sheets['Dominios_ENUM'].append([typ,typ[5:-1],', '.join(uses)])
for typ,uses in stats.items(): sheets['Dominios_ENUM'].append(['status '+typ,'1 activo / 0 inactivo si bit; tinyint sin dominio declarado',', '.join(uses)])
observations=[
 ('Alta','tbd_products_categories.category_ID carece de FK a tbc_categories.','Declarar FK y definir acciones referenciales.'),
 ('Alta','Coexisten tb_orders/tbd_order_details y tb_buyer_orders/tbd_order_items; pagos apuntan a tb_orders y envíos, devoluciones y cancelaciones a tb_buyer_orders.','Confirmar flujos y definir un modelo canónico para órdenes y pagos.'),
 ('Alta','tb_buyer_orders solo guarda seller_ID.','Agregar la referencia al comprador si el flujo lo requiere.'),
 ('Alta','tb_refunds.return_ID y cancellation_ID son opcionales sin CHECK de exactamente uno.','Agregar CHECK XOR o separar el origen del reembolso.'),
 ('Alta','tbd_return_items.quantity y tbd_cancellation_items.quantity no tienen CHECK quantity > 0.','Agregar restricción positiva.'),
 ('Media','tb_payments.transaction_reference y tb_payment_transaction.gateway_reference pueden duplicar la referencia de pasarela.','Definir el campo canónico y reconciliar su uso.'),
 ('Media','Varias tablas de cancelación, transacción, personas, reembolso, devolución, envío y sus detalles no tienen columna status genérica.','Documentar estados específicos y sus transiciones.'),
 ('Media','Llaves mezclan INT, INT UNSIGNED y BIGINT; status mezcla bit(1) y tinyint.','Normalizar tipos y dominios con migración compatible.'),
 ('Media','tb_people.courtesy_title_ID char(10) y country_code char(2) sin catálogo ni FK; faltan fk_people_courtesy_title y fk_people_country.','Crear catálogos y restricciones o documentar el origen de esos códigos.'),
]
sheets['Observaciones']=[['Severidad','Hallazgo','Recomendación']]+[list(x) for x in observations]
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
(D/'README.md').write_text('# Diccionario de datos de BD19\n\nEntregables generados desde el DDL extraído de `Practica03/backups/BD19.sql`: `diccionario_datos.md`, `diccionario_datos.xlsx`, `estructura.json`, `diagrama_er.mmd`, `schema.dbml` y el sitio estático `Practica03/docs`. El diccionario presenta 25 tablas (primero las 11 con filas en el respaldo y después 14 sin filas verificables), con sus vistas y triggers asociados. `estructura.json` conserva el esquema completo de 29 tablas para regenerar el diagrama Archify. No se guardan valores de filas del volcado.\n\n## Regeneración segura\n\nDesde la raíz del repositorio, con Python 3:\n\n```powershell\npython Practica03\\diccionario_datos\\extraer.py\npython Practica03\\diccionario_datos\\contar_filas.py\npython Practica03\\diccionario_datos\\generar.py\npython Practica03\\diccionario_datos\\generar_modelos.py\npython Practica03\\diccionario_datos\\generar_sitio.py\n```\n\n`extraer.py` conserva exclusivamente DDL. `contar_filas.py` procesa las tuplas INSERT en streaming y persiste solo conteos agregados. Los conteos pertenecen al respaldo BD19, no a una instancia en vivo.\n',encoding='utf-8')
# validation
counts={k:sum(x['kind']==k for x in O) for k in ('table','view','trigger','procedure')}; missing=[x[1] for x in fks if x[1] not in (D/'diccionario_datos.md').read_text(encoding='utf-8')]
print(json.dumps({'conteos':counts,'FK_SQL':len(fks),'FK_nombres_ausentes_en_diccionario':missing,'hojas_XLSX':names},ensure_ascii=False))
