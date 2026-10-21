import json,re,pathlib,zipfile,xml.sax.saxutils as sx
from collections import defaultdict
D=pathlib.Path(__file__).parent; data=json.loads((D/'estructura.json').read_text(encoding='utf-8')); O=data['objects']
tables=[x for x in O if x['kind']=='table']; views=[x for x in O if x['kind']=='view']; trigs=[x for x in O if x['kind']=='trigger']; procs=[x for x in O if x['kind']=='procedure']
def split_def(s):
 return [x.strip().rstrip(',') for x in s.splitlines() if x.strip() and not x.strip().startswith(('CREATE TABLE','/*','*/')) and x.strip() not in (') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci','(')]
def parse_table(t):
 s=t['sql']; cols=[]; cons=[]
 for ln in split_def(s):
  if ln.startswith(')'): continue
  m=re.match(r'`([^`]+)`\s+(.+)',ln)
  if m and not m.group(1).upper() in ('PRIMARY','UNIQUE','KEY','CONSTRAINT','FOREIGN','CHECK'):
   name=m.group(1); rest=m.group(2); typ=re.match(r'(\w+(?:\s*\([^)]*\))?)',rest).group(1); null='NO' if re.search(r'\bNOT NULL\b',rest,re.I) else 'Sí'; default=(re.search(r'\bDEFAULT\s+((?:\'[^\']*\')|(?:[^\s,]+))',rest,re.I) or [None,'No especificado'])[1]; extra='; '.join(x for x in ('AUTO_INCREMENT' if 'AUTO_INCREMENT' in rest else '', 'GENERATED STORED' if 'STORED' in rest else '', 'ON UPDATE CURRENT_TIMESTAMP' if 'ON UPDATE' in rest else '') if x) or '—'; cols.append({'name':name,'type':typ,'nullable':null,'default':default,'extra':extra,'key':''})
  elif re.match(r'(PRIMARY KEY|UNIQUE KEY|KEY|CONSTRAINT|CHECK)',ln,re.I): cons.append(ln)
 for c in cons:
  for col in re.findall(r'`([^`]+)`',c):
   for x in cols:
    if x['name']==col:
     x['key']+=('PK' if c.startswith('PRIMARY') else 'UK' if c.startswith('UNIQUE') else 'FK' if 'FOREIGN KEY' in c else 'IDX')+' '
 return cols,cons
parsed={t['name']:parse_table(t) for t in tables}
def purpose(name):
 known={'tb_buyer_orders':'Órdenes asociadas al flujo de compra por comprador/vendedor (la estructura solo incluye seller_ID).','tb_carts':'Carritos de usuarios.','tb_logs':'Bitácora de operaciones de las tablas auditadas.','tb_orders':'Órdenes del modelo principal.','tb_payments':'Pagos asociados a órdenes y métodos de pago.','tb_products':'Catálogo principal de productos.','tb_user_addresses':'Direcciones registradas por usuarios.','tb_users':'Cuentas y perfiles de usuarios.','tbc_categories':'Catálogo jerárquico de categorías.','tbc_payment_methods':'Catálogo de métodos de pago.','tbc_payment_methods_types':'Catálogo de tipos de métodos de pago.','tbd_address_components':'Componentes estructurados de direcciones.','tbd_carts_items':'Productos incluidos en carritos.','tbd_order_details':'Detalle de las órdenes principales.','tbd_order_items':'Productos incluidos en órdenes de comprador.','tbd_products_categories':'Relación de productos con categorías.','tbd_products_users_providers':'Relación entre productos y proveedores usuarios.','tbd_user_payment_methods':'Métodos de pago de usuarios.','tbd_users_wishlist_products':'Relación usuario/producto para wishlist.','tbd_wishlist':'Wishlist asociada a usuarios/productos.'}
 return known.get(name,'Propósito no especificado en el SQL.')
# relation info
fks=[]
for t in tables:
 for c in parsed[t['name']][1]:
  m=re.search(r'CONSTRAINT\s+`([^`]+)`\s+FOREIGN KEY\s*\(([^)]*)\)\s+REFERENCES\s+`([^`]+)`\s*\(([^)]*)\)(.*)',c,re.I)
  if m: fks.append({'name':m.group(1),'table':t['name'],'cols':m.group(2),'ref':m.group(3),'refcols':m.group(4),'actions':m.group(5)})
# markdown
md=['# Diccionario de datos — db_test','', '**Motor objetivo:** MySQL 8.0.36. Fuente: `BD13.sql`; datos INSERT excluidos del proceso.','', '## Índice','', '- [Tablas](#tablas)','- [Vistas](#vistas)','- [Triggers](#triggers)','- [Procedimientos](#procedimientos)','- [Catálogo de dominios](#catálogo-de-dominios)','- [Convenciones](#convenciones-de-nombres)','- [Observaciones de calidad](#observaciones-de-calidad-del-diseño)','- [Pendientes por confirmar](#pendientes-por-confirmar)','']
md += ['## Tablas','']
for t in tables:
 n=t['name']; cols,cons=parsed[n]; md += [f'### `{n}`','',f'- **Prefijo/tipo:** {"principal (tb_)" if n.startswith("tb_") else "catálogo (tbc_)" if n.startswith("tbc_") else "detalle (tbd_)"}.','- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci (según opciones explícitas; revisar excepciones en DDL).',f'- **Propósito:** {purpose(n)}','', '| # | Columna | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |','|---:|---|---|---|:---:|---|---|---|---|']
 for i,c in enumerate(cols,1):
  typ=c['type']; length=typ[typ.find('(')+1:-1] if '(' in typ else '—'; desc='1 = activo; 0 = inactivo (borrado lógico).' if c['name'].lower()=='status' and 'bit' in typ.lower() else 'No especificado en SQL.'
  md.append(f"| {i} | `{c['name']}` | `{typ}` | {length} | {c['nullable']} | {c['default']} | {c['extra']} | {c['key'].strip() or '—'} | {desc} |")
 md += ['', '**Restricciones e índices:**','']
 for c in cons: md.append(f'- `{c}`')
 if not cons: md.append('- No se declaran restricciones adicionales en el DDL.')
 outgoing=[f for f in fks if f['table']==n]; incoming=[f for f in fks if f['ref']==n]
 md += ['', '**Relaciones:**']
 for f in outgoing: md.append(f"- Referencia: `{f['cols'].replace('`','')}` → `{f['ref']}.{f['refcols'].replace('`','')}` ({f['actions'].strip() or 'sin acción referencial explícita'}). Cardinalidad estimada: N:1.")
 for f in incoming: md.append(f"- Referenciada por `{f['table']}` mediante `{f['cols'].replace('`','')}`; cardinalidad estimada 1:N.")
 if not outgoing and not incoming: md.append('- Sin FK declaradas.')
 tt=[x['name'] for x in trigs if re.search(r'ON\s+`?'+re.escape(n)+r'`?\s+FOR EACH ROW',x['sql'],re.I)]
md += ['', '**Triggers asociados:** '+(', '.join(f'`{x}`' for x in tt) if tt else 'Ninguno.'), '']
md += ['## Vistas','']
for v in views:
 s=v['sql']; sel=re.sub(r'^.*?AS\s+','',s,flags=re.S|re.I); names=re.findall(r'\bAS\s+`([^`]+)`',sel,re.I); bases=list(dict.fromkeys(re.findall(r'\b(?:FROM|JOIN)\s+`([^`]+)`',sel,re.I))); md += [f"### `{v['name']}`",'',f"- **Propósito:** trazabilidad/consulta derivada según su SELECT.",f"- **Tablas base:** {', '.join('`'+x+'`' for x in bases) or 'No especificado'}.",'- **Columnas expuestas:** '+(', '.join('`'+x+'` (tipo derivado de expresión; origen en SELECT)' for x in names) or 'No inferibles del alias SQL.')+'.','']
md += ['## Triggers','', '| Nombre | Tabla | Evento | Momento | Registro en tb_logs |','|---|---|---|---|---|']
for x in trigs:
 s=x['sql']; tab=re.search(r'ON\s+`([^`]+)`',s); ev=re.search(r'\b(AFTER)\s+(INSERT|UPDATE|DELETE)',s); cols=re.search(r'INSERT\s+INTO\s+`?tb_logs`?\s*\(([^)]*)\)',s,re.I); concat=re.search(r'CONCAT\s*\((.*?)\)\s*\)',s,re.S|re.I); fmt=' '.join(re.findall(r"'((?:[^']|'')*)'",concat.group(1))) if concat else 'description sin plantilla CONCAT identificable'
 md.append(f"| `{x['name']}` | `{tab.group(1) if tab else 'No especificado'}` | {ev.group(2) if ev else 'No especificado'} | {ev.group(1) if ev else 'AFTER'} | {cols.group(1).replace('`','') if cols else 'No especificado'}; description: `{fmt}` (valores dinámicos NEW/OLD según operación). |")
md += ['','## Procedimientos','']
for x in procs:
 s=x['sql']; pars=re.search(r'PROCEDURE\s+`[^`]+`\s*\((.*?)\)\s*(?:BEGIN|begin)',s,re.S); params=re.sub(r'\s+',' ',pars.group(1)).strip() if pars else 'No especificado'; affects=sorted(set(re.findall(r'\b(?:UPDATE|INSERT\s+INTO|DELETE\s+FROM)\s+`?([\w]+)',s,re.I))); md += [f"### `{x['name']}`",'',f'- **Parámetros:** `{params}` (dirección/tipo conforme a la firma; si no tiene modo explícito, MySQL lo considera IN).', '- **Pasos:** valida parámetros/estado y actualiza el status para borrado lógico, según cuerpo; pasos específicos no inferibles de la firma.',f"- **Tablas afectadas:** {', '.join('`'+a+'`' for a in affects) or 'No especificado'}.",f"- **Ejemplo:** `CALL {x['name']}({', '.join('/* '+p+' */' for p in re.findall(r'(?:IN|OUT|INOUT)\s+(\w+)',params))});`",'']
md += ['## Catálogo de dominios','', '### ENUM','']
enums=defaultdict(list)
for t in tables:
 for c in parsed[t['name']][0]:
  if c['type'].lower().startswith('enum'): enums[c['type']].append(t['name']+'.'+c['name'])
for typ,loc in enums.items(): md.append(f"- `{typ}` — {', '.join('`'+x+'`' for x in loc)}")
if not enums: md.append('- No hay columnas ENUM detectadas.')
md += ['', '### status','']
for kind in ('bit','tinyint'):
 loc=[f"{t['name']}.{c['name']} ({c['type']})" for t in tables for c in parsed[t['name']][0] if c['name'].lower()=='status' and c['type'].lower().startswith(kind)]
 md.append(f"- `{kind}`: {', '.join('`'+x+'`' for x in loc) or 'ninguno'}.")
md += ['', '## Convenciones de nombres','', '- `tb_`: tabla principal; `tbc_`: catálogo; `tbd_`: detalle/relación; `vw_`: vista; `trg_`: trigger; `sp_`: procedimiento; `fk_`: restricción FK; `uk_`: restricción UNIQUE; `chk_`: CHECK.', '- `creation_date`, `last_update` y `status` son columnas de auditoría/estado cuando aparecen; el SQL define defaults y comportamiento concretos en cada tabla. `status` no se asume equivalente entre tipos.', '', '## Observaciones de calidad del diseño','']
obs=['**Alta —** `tbd_products_categories.category_ID` carece de FK a `tbc_categories`. Recomendación: declarar FK y decidir acciones referenciales.','**Alta —** existen dos posibles modelos paralelos de órdenes: `tb_orders`/`tbd_order_details` y `tb_buyer_orders`/`tbd_order_items`. Recomendación: confirmar si cubren flujos distintos y documentar el límite funcional.','**Alta —** `tb_buyer_orders` solo guarda `seller_ID`; no identifica comprador. Recomendación: agregar vínculo al comprador si el proceso lo requiere.','**Media —** `tbd_carts_items` y `tbd_order_items` separan referencias `user_ID` y `product_ID` hacia `tbd_products_users_providers` en vez de una FK compuesta. Recomendación: usar FK compuesta o validar consistencia en otro mecanismo.','**Media —** las llaves relacionadas usan tipos INT, INT UNSIGNED y BIGINT; `status` combina bit(1) y tinyint. Recomendación: normalizar tipos/signo y dominio documentando migración.','**Baja —** se detectaron variaciones en nombres de triggers (por ejemplo, prefijos omitidos). Recomendación: adoptar convención uniforme.']
for x in obs: md.append('- '+x)
legacy=' '.join(x['sql'] for x in O)
md += ['', '**Verificación de nombres obsoletos:** '+('Verificado: sin referencias huérfanas' if not re.search(r'tbd_shopping_cart|tbd_users_offer_products',legacy,re.I) else 'Se encontraron referencias en las definiciones extraídas; revisar estructura.json.'),'', '## Pendientes por confirmar','', '- Propósito de negocio de tablas/vistas que no esté expresado en nombres o relaciones SQL.','- Semántica de cardinalidad 1:1/N:M cuando no existe restricción única/FK que la garantice.','- En vistas, algunos tipos de columnas dependen de expresiones SQL y no están declarados explícitamente; deben confirmarse mediante DESCRIBE en una instancia.','- Valores exactos de `description` se deben interpretar junto con el SQL de cada trigger; no representan necesariamente formatos uniformes.','']
(D/'diccionario_datos.md').write_text('\n'.join(md),encoding='utf-8')

# Enriquecimiento estructurado de tabla y columna desde el DDL ya aislado.
def detailed_table(t, cols, cons, trig_names):
 name=t['name']; module='órdenes' if 'order' in name else 'usuarios' if 'user' in name else 'productos' if any(k in name for k in ('product','categor')) else 'carritos' if any(k in name for k in ('cart','wishlist')) else 'pagos' if 'payment' in name else 'auditoría' if name=='tb_logs' else 'direcciones'
 refs=[f['ref'] for f in fks if f['table']==name]; incoming=[f['table'] for f in fks if f['ref']==name]
 tr=[x['name'] for x in trigs if re.search(r'ON\s+`?'+re.escape(name)+r'`?\s+FOR EACH ROW',x['sql'],re.I)]
 related=', '.join('`'+r+'`' for r in dict.fromkeys(refs+incoming)) or 'no declara relaciones FK'
 checks=[x.split('CHECK',1)[1].strip().rstrip(',') for x in cons if 'CHECK' in x.upper()]
 uniques=[x for x in cons if 'UNIQUE' in x.upper()]
 actions=[f"{f['name']} {f['actions'].strip()}" for f in fks if f['table']==name and f['actions'].strip()]
 generated=[c['name'] for c in cols if 'GENERATED' in c['extra'].upper()]
 return ' '.join((
  f"`{name}` representa la entidad o relación sugerida por sus atributos (inferido).",
  f"Pertenece al módulo de {module} (inferido por el nombre).",
  f"Se relaciona con {related}; las FK entrantes y salientes están enumeradas en Relaciones.",
  f"Reglas de negocio declaradas: CHECK {('; '.join(checks) if checks else 'ninguno')}; UNIQUE {('; '.join(uniques) if uniques else 'ninguno')}; acciones referenciales {('; '.join(actions) if actions else 'sin acción explícita')}; columnas generadas {(', '.join(generated) if generated else 'ninguna')}.",
  f"Triggers asociados: {(', '.join(tr) if tr else 'ninguno')}; la función se deriva de los eventos y mensajes de auditoría visibles (inferido)."))
def nature(c,typ):
 low=c.lower(); t=typ.lower()
 if low=='id' or low.endswith('_id') or low.startswith('id_'): return 'Cualitativa nominal'
 if re.search(r'(^|_)(date|time|datetime|timestamp|created|creation|updated|update|login)(_|$)',low) or t in ('date','datetime','timestamp','time','year'): return 'Cuantitativa (temporal)'
 if t.startswith('enum'):
  vals=re.findall(r"'([^']*)'",typ); ordkeys=('status','state','fulfillment','payment_status')
  return 'Cualitativa ordinal' if any(k in low for k in ordkeys) else 'Cualitativa nominal'
 if low in ('status','operation_status','is_default','active','is_active','enabled','is_enabled') or t.startswith('bit(1)'): return 'Cualitativa nominal'
 if any(w in low for w in ('quantity','count','units','stock')) and re.match(r'(tinyint|smallint|mediumint|int|bigint)',t): return 'Cuantitativa discreta'
 if any(w in low for w in ('price','amount','subtotal','total','cost','latitude','longitude','weight')) or t.startswith(('decimal','float','double')): return 'Cuantitativa continua'
 return 'Cualitativa nominal'
def domain(c,typ,raw,table,cons):
 t=typ.lower(); name=c.lower()
 if t.startswith('enum'):
  vals=', '.join(re.findall("'([^']*)'",typ)); return f"{c} ∈ {{{vals}}}; tipo {typ}"
 if t.startswith('bit(1)') and name=='status': return 'status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1)'
 if t.startswith('bit(1)'): return f'{c} ∈ {{0,1}}; bit(1)'
 if 'int' in t:
  if 'AUTO_INCREMENT' in raw.upper(): return f'{c} ∈ ℤ⁺; tipo {typ}; AUTO_INCREMENT'
  unsigned='unsigned' in raw.lower() or 'unsigned' in t
  return f'{c} ∈ ℤ'+('⁺ ∪ {0}' if unsigned else '')+f'; tipo {typ}'
 m=re.search(r'\((\d+)(?:,(\d+))?\)',typ)
 if t.startswith('decimal') or t.startswith(('float','double')):
  prec=m.group(1)+(','+m.group(2) if m and m.group(2) else '') if m else 'precisión del tipo'; return f'{c} ∈ ℝ, precisión {prec}; {typ}; sin rango adicional salvo CHECK explícito'
 if t.startswith(('char','varchar','binary','varbinary')): return f'{c} ∈ cadena(≤{m.group(1) if m else "No especificado"}); tipo {typ}'
 if t in ('date','datetime','timestamp','time','year'): return f'{c} ∈ fecha/hora válida según {typ}'
 if t in ('text','tinytext','mediumtext','longtext','json'): return f'{c} ∈ texto ({typ}); formato no restringido por CHECK'
 return f'{c} ∈ dominio del tipo {typ}; rango/formato adicional no especificado'
def domain_checked(c,typ,raw,table,cons):
 base=domain(c,typ,raw,table,cons); checks=[]
 for z in cons:
  if z.startswith('CONSTRAINT') and 'CHECK' in z.upper() and f'`{c}`' in z:
   checks.append(z.split('CHECK',1)[1].strip().rstrip(','))
 if re.match(r'(tinyint|smallint|mediumint|int|bigint)',typ.lower()) and any(re.search(r'>\s*0',check) for check in checks):
  base=f'{c} ∈ ℤ⁺; tipo {typ}'
 if typ.lower() in ('date','datetime','timestamp','time','year'):
  dm=re.search(r'\bDEFAULT\s+((?:\'[^\']*\')|(?:[^\s,]+))',raw,re.I)
  default=dm.group(1) if dm else 'sin default'
  base=f'{c} ∈ {typ.upper()}; default {default}'
 return base+('; CHECK '+ ' y '.join(checks) if checks else '')
def domain_fk(c,table):
 domains=[]
 for fk in fks:
  if fk['table']!=table: continue
  local=re.findall(r'`([^`]+)`',fk['cols']); remote=re.findall(r'`([^`]+)`',fk['refcols'])
  if c in local:
   target=fk['ref']+'.'+remote[local.index(c)]
   delete=re.search(r'ON\s+DELETE\s+(CASCADE|RESTRICT|NO ACTION|SET NULL|SET DEFAULT)',fk['actions'],re.I)
   rule=delete.group(1).lower() if delete else 'sin acción'
   domains.append(f'{c} ∈ {{{target}}}; ON DELETE {rule}')
 return '; '.join(domains) if domains else None
def describe_col(table,c,typ,raw,cons,pkcols,fkcol,uk):
 low=c.lower(); gen='GENERATED' in raw.upper(); default=(re.search(r'\bDEFAULT\s+((?:\'[^\']*\')|(?:[^\s,]+))',raw,re.I) or [None,None])[1]
 if gen:
  formula=re.search(r'AS\s*(\(.*\))\s+(?:VIRTUAL|STORED)',raw,re.I); return f"Almacena un valor calculado por la base de datos; fórmula `{formula.group(1) if formula else 'No especificada'}` y columna generada según DDL. Restricciones: {raw.strip()}."
 if 'AUTO_INCREMENT' in raw.upper(): return f"Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. Restricciones: NOT NULL y AUTO_INCREMENT."
 if c in fkcol: return f"Identifica o enlaza el registro con `{fkcol[c]}`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. Restricciones: FK y {('NOT NULL' if 'NOT NULL' in raw.upper() else 'NULL permitido')}."
 if low in ('creation_date','last_update','operation_date','last_login'): return f"Registra una fecha u hora del ciclo de vida/auditoría (inferido); {('se asigna por defecto '+str(default) if default else 'se captura al guardar')}. Restricciones: tipo {typ}, {('NOT NULL' if 'NOT NULL' in raw.upper() else 'NULL permitido')}."
 if low=='status': return f"Indica el estado lógico del registro (inferido); {('usa DEFAULT '+str(default) if default else 'se asigna según la operación')}. Restricciones: {typ} y {'NOT NULL' if 'NOT NULL' in raw.upper() else 'NULL permitido'}."
 if table=='tb_logs' and low=='table_name': return f"Identifica el nombre de la tabla cuya operación se registra; lo asignan los triggers de auditoría. Restricciones: {typ}, NOT NULL."
 if table=='tb_logs' and low=='operation': return f"Clasifica la operación registrada; el dominio ENUM limita el valor a Create, Read, Update o Delete. Los triggers asignan Create, Update o Delete según el evento."
 if table=='tb_logs' and low=='db_user': return f"Guarda la identidad de base de datos devuelta por USER() al generar el registro de auditoría. Restricciones: {typ}, NOT NULL."
 if table=='tb_logs' and low=='description': return f"Contiene el mensaje de auditoría con atributos relevantes del registro afectado; los triggers lo construyen con CONCAT y valores NEW u OLD. Restricciones: texto NOT NULL."
 if table=='tb_logs' and low=='operation_status': return f"Marca el resultado/estado de la entrada de auditoría; el SQL permite los valores de bit(1) y declara DEFAULT {default}."
 specific={
  ('tb_payments','transaction_reference'): 'Guarda la referencia externa de la transacción para localizar el pago en el procesador o institución financiera (inferido). Es opcional y puede quedar NULL cuando el proveedor todavía no devuelve una referencia o el medio de pago no la proporciona (inferido).',
  ('tb_payments','payment_date'): 'Registra la fecha y hora en que se registra el pago; si no se proporciona, el sistema asigna CURRENT_TIMESTAMP. El valor obligatorio permite ordenar y conciliar los pagos.',
  ('tb_products','sku'): 'Guarda el código SKU que distingue el producto en el catálogo; se captura al dar de alta o importar el producto (inferido). Es obligatorio y único para localizar y controlar ese producto.',
  ('tb_products','current_price'): 'Guarda el precio vigente del producto y se usa para calcular el importe de venta (inferido). Es obligatorio; si no se informa al insertar, comienza en 0.00 y luego se actualiza con el precio autorizado (inferido).',
  ('tb_products','current_stock'): 'Guarda las unidades disponibles del producto y sirve para consultar y actualizar inventario (inferido). Es obligatorio; el sistema inicializa el valor en cero y el proceso de venta o reposición lo modifica (inferido).',
  ('tb_user_addresses','address_label'): 'Guarda la etiqueta que permite al usuario distinguir esta dirección, por ejemplo casa o trabajo (inferido). Es obligatoria y la aporta el usuario al registrar la dirección.',
  ('tb_user_addresses','recipient_name'): 'Guarda el nombre de quien recibirá el envío (inferido). Es opcional y se captura cuando el destinatario difiere del titular o se necesita identificarlo para la entrega (inferido).',
  ('tb_user_addresses','recipient_phone'): 'Guarda un teléfono de contacto para coordinar la entrega (inferido). Es opcional y se captura cuando hace falta contactar al destinatario (inferido).',
  ('tb_user_addresses','delivery_instructions'): 'Guarda indicaciones para localizar el domicilio o completar la entrega (inferido). Es opcional porque la dirección puede registrarse sin instrucciones adicionales; el usuario las aporta cuando son necesarias (inferido).',
  ('tbc_payment_methods_types','code'): 'Guarda el código estable que identifica cada tipo de método de pago en el catálogo (inferido). Es obligatorio, único y se asigna al configurar el catálogo para que otras filas puedan distinguir el tipo.',
  ('tbd_address_components','value'): 'Guarda el contenido de un componente individual de la dirección, como una calle o localidad (inferido). Es obligatorio y se captura al desglosar la dirección para poder consultar cada componente junto con su tipo.',
  ('tbd_address_components','component_type'): 'Indica qué clase de dato contiene `value`, por ejemplo calle, ciudad o código postal (inferido). Es obligatorio y se captura al estructurar la dirección para interpretar cada componente.',
  ('tbd_order_items','product_name'): 'Guarda el nombre del producto mostrado en esta línea de la orden; probablemente se copia del catálogo al crearla para conservar el detalle histórico (inferido). Es obligatorio y permite identificar el artículo en el comprobante aunque cambie su nombre en el catálogo.',
  ('tbd_products_users_providers','type_ownership'): 'Clasifica la relación del usuario con el producto mediante Owner, Reseller o Distributor. Es opcional porque DEFAULT NULL permite registrar la relación sin asignar todavía un tipo; se usa para distinguir la función del proveedor (inferido).',
  ('tbd_products_users_providers','avalaible_date'): 'Registra desde cuándo está disponible el producto del proveedor (inferido); el valor se captura al registrar su disponibilidad. Es obligatorio y permite determinar desde qué fecha ofrecerlo.',
  ('tbd_user_payment_methods','provider'): 'Guarda el nombre del proveedor o servicio que administra el método de pago (inferido). Es obligatorio y se aporta al vincular el método para identificar qué sistema debe procesar o consultar la referencia externa.',
  ('tbd_user_payment_methods','provider_method_ref'): 'Guarda el identificador que el proveedor asigna al método de pago del usuario (inferido), sin implicar que sea el número completo de tarjeta. Es obligatorio y se usa junto con `provider` para localizar ese método; ambos campos tienen unicidad conjunta.'
 }
 if (table,low) in specific: return specific[(table,low)]
 semantic={
  'email': 'Guarda el correo de contacto o acceso asociado a la cuenta (inferido); el SQL fija su longitud y cualquier restricción UNIQUE detectada.',
  'nickname': 'Guarda el alias visible del usuario para identificar su perfil en la aplicación (inferido).',
  'password': 'Almacena el hash de la contraseña de la cuenta para verificarla durante la autenticación; el algoritmo de hash no está declarado en el esquema (inferido).',
  'quantity': 'Indica cuántas unidades del producto contiene esta línea; los CHECK aplicables definen el mínimo permitido.',
  'unit_price': 'Guarda el precio unitario aplicado a la línea; el SQL determina su precisión y puede imponer un límite mediante CHECK.',
  'subtotal': 'Guarda o calcula el importe de esta línea de orden; si es GENERATED, su fórmula es la declarada en la expresión SQL.',
  'total_amount': 'Guarda el importe total de la orden; puede derivarse de sus líneas de detalle, pero el DDL no declara una fórmula de actualización (inferido).',
  'amount': 'Guarda el importe asociado al pago; su precisión procede del tipo decimal y la moneda no está especificada (inferido).',
  'shipping_cost': 'Guarda el costo de envío de la orden; se sujeta al CHECK de no negatividad declarado en el DDL.',
  'fulfillment_status': 'Representa la etapa del cumplimiento de la orden dentro del conjunto ENUM ordenado del flujo.',
  'payment_status': 'Representa la etapa del pago dentro del conjunto ENUM declarado.',
  'operation': 'Clasifica la operación registrada; el dominio ENUM limita los valores válidos.',
  'table_name': 'Identifica el nombre de la tabla cuya operación se registra en la bitácora.',
  'category_id': 'Guarda el identificador lógico de categoría asociado al producto o relación; esta columna no declara FK en el DDL.',
  'seller_id': 'Identifica al vendedor asociado a la orden; el DDL no incluye un identificador de comprador en esta tabla (inferido).',
  'is_default': 'Indica si el método de pago se marca como preferido para el usuario, según el nombre de la columna (inferido).',
  'last_four': 'Conserva los últimos cuatro caracteres de una referencia de pago para mostrarla parcialmente (inferido).',
  'label': 'Guarda una etiqueta legible para distinguir este método de pago del usuario (inferido).',
  'latitude': 'Guarda la latitud geográfica; CHECK limita el valor al intervalo de −90 a 90 y chk_coordinates exige pareja con longitude.',
  'longitude': 'Guarda la longitud geográfica; CHECK limita el valor al intervalo de −180 a 180 y chk_coordinates exige pareja con latitude.',
  'shipping_address': 'Conserva la dirección de envío en texto libre; el formato interno no está normalizado por el DDL (inferido).',
  'description': 'Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers.',
  'name': 'Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido).',
  'title': 'Guarda el título legible asociado al elemento (inferido).',
  'operation_status': 'Marca el estado binario de la entrada de auditoría y toma el DEFAULT declarado por el SQL.'
 }
 if low in semantic:
  return semantic[low]+f" Restricciones: {typ}, {'NOT NULL' if 'NOT NULL' in raw.upper() else 'NULL permitido'}"+('; UNIQUE.' if uk else '.')
 friendly=c.replace('_',' ')
 applied=('; valor por defecto '+str(default) if default is not None else '; se captura al insertar (inferido)')
 return f"Almacena {friendly} de `{table}` para describir o relacionar ese registro (inferido){applied}. Restricciones: tipo {typ}, {'NOT NULL' if 'NOT NULL' in raw.upper() else 'NULL permitido'}"+('; UNIQUE' if uk else '')+'.'
def formal_table(t, cols, cons):
 pk=[]
 for z in cons:
  if z.startswith('PRIMARY KEY'): pk=re.findall(r'`([^`]+)`',z)
 parts=[]
 fkset={a for f in fks if f['table']==t for a in re.findall(r'`([^`]+)`',f['cols'])}
 for item in cols:
  c=item['name']; parts.append(('@' if c in pk else '')+('#' if c in fkset else '')+c)
 return t+' = '+' + '.join(parts)
def formal_column(table,c,typ,raw,cons):
 low=c.lower(); t=typ.lower()
 if low=='email': return 'email = usuario + "@" + dominio'
 if table=='tb_user_addresses' and low in ('latitude','longitude'): return 'coordenadas = latitude + longitude'
 if low=='subtotal' and 'GENERATED' in raw.upper(): return 'subtotal = quantity × unit_price'
 if low=='operation' and t.startswith('enum'):
  return 'operation = [ '+' | '.join(re.findall("'([^']*)'",typ))+' ]'
 if low=='status' and t.startswith('enum'):
  return 'status = [ '+' | '.join(re.findall("'([^']*)'",typ))+' ]'
 if t.startswith('enum'): return c+' = [ '+' | '.join(re.findall("'([^']*)'",typ))+' ]'
 if low=='status' or t.startswith('bit(1)'): return c+' = {0 | 1}'
 if low=='id' or low.endswith('_id') or low.startswith('id_'): return c+' = {dígito}'
 if low in ('quantity','count','units'): return c+' = {entero}'
 if low in ('latitude','longitude'): return c+' = {número real}'
 if re.search(r'(^|_)(date|time|datetime|timestamp|created|creation|updated|update|login)(_|$)',low) or t in ('date','datetime','timestamp','time','year'): return c+' = {fecha/hora}'
 if low in ('transaction_reference','reference','last_four'): return c+' = {carácter alfanumérico}'
 if t.startswith(('decimal','float','double')): return c+' = {número real}'
 if t.startswith(('int','tinyint','smallint','mediumint','bigint')): return c+' = {entero}'
 return c+' = {carácter}'

# Build the richer metadata in estructura.json for the website and workbook.
data['pending_confirmations']=[
 'tb_payments.transaction_reference: confirmar qué pasarelas o medios pueden dejar la referencia NULL y el momento en que se recibe.',
 'tb_products.SKU: confirmar el estándar del código y si se captura manualmente o se importa desde otro sistema.',
 'tb_products.current_price: confirmar qué proceso o rol autoriza y actualiza el precio vigente.',
 'tb_products.current_stock: confirmar si el inventario se actualiza automáticamente con ventas y reposiciones.',
 'tb_user_addresses.address_label: confirmar las etiquetas de dirección permitidas y su captura en la aplicación.',
 'tb_user_addresses.recipient_name, recipient_phone y delivery_instructions: confirmar en qué operaciones de entrega son necesarios.',
 'tbc_payment_methods_types.code: confirmar el sistema que asigna los códigos del catálogo.',
 'tbd_address_components.value y component_type: confirmar los tipos de componente y las reglas para dividir/validar direcciones.',
 'tbd_order_items.product_name: confirmar si se guarda como copia histórica del nombre al crear la orden.',
 'tbd_products_users_providers.type_ownership y avalaible_date: confirmar cuándo se asigna el rol y qué evento define la fecha de disponibilidad.',
 'tbd_user_payment_methods.provider y provider_method_ref: confirmar el formato y el origen exacto de la referencia externa; no se infiere que contenga datos completos de tarjeta.'
]
data['generic_descriptions_rewritten']=[
 'tb_payments.transaction_reference','tb_payments.payment_date','tb_products.SKU','tb_products.current_price','tb_products.current_stock',
 'tb_user_addresses.address_label','tb_user_addresses.recipient_name','tb_user_addresses.recipient_phone','tb_user_addresses.delivery_instructions',
 'tbc_payment_methods_types.code','tbd_address_components.value','tbd_address_components.component_type','tbd_order_items.product_name',
 'tbd_products_users_providers.type_ownership','tbd_products_users_providers.avalaible_date','tbd_user_payment_methods.provider',
 'tbd_user_payment_methods.provider_method_ref'
]
for t in tables:
 cols,cons=parsed[t['name']]; pkcols=[]
 for z in cons:
  if z.startswith('PRIMARY KEY'): pkcols=re.findall(r'`([^`]+)`',z)
 fkcol={}
 for f in fks:
  if f['table']==t['name']:
   lhs=re.findall(r'`([^`]+)`',f['cols']); rhs=re.findall(r'`([^`]+)`',f['refcols'])
   for a,b in zip(lhs,rhs): fkcol[a]=f['ref']+'.'+b
 rows=[]
 for c in cols:
  raw=next((ln.strip().rstrip(',') for ln in t['sql'].splitlines() if re.match(r'\s*`'+re.escape(c['name'])+r'`\s+',ln)), '')
  uk=any(z.startswith('UNIQUE') and f"`{c['name']}`" in z for z in cons)
  pk='PK compuesta ('+', '.join(pkcols)+')' if c['name'] in pkcols and len(pkcols)>1 else 'PK' if c['name'] in pkcols else ''
  keys=[]
  if pk: keys.append(pk)
  if c['name'] in fkcol: keys.append('FK → '+fkcol[c['name']])
  if uk: keys.append('UK')
  key='; '.join(keys) if keys else 'No'
  gen='GENERATED' in raw.upper(); nullable='NO' if re.search(r'\bNOT NULL\b',raw,re.I) else 'Sí'
  formula=re.search(r'AS\s*(\(.*\))\s+(?:VIRTUAL|STORED)',raw,re.I)
  origin=('Derivado: '+(formula.group(1) if formula else 'fórmula no especificada')) if gen else 'Almacenado'
  if c['name'].lower()=='subtotal' and t['name']=='tb_buyer_orders': origin='Almacenado (derivable de la suma de tbd_order_items.subtotal; fórmula no declarada, inferido)'
  elif c['name'].lower()=='total_amount' and t['name']=='tb_orders': origin='Almacenado (derivable de la suma de tbd_order_details.subtotal; fórmula no declarada, inferido)'
  elif c['name'].lower()=='subtotal' and t['name'] not in ('tbd_order_details','tbd_order_items'): origin='Almacenado (derivable de sus conceptos de orden; fórmula no declarada, inferido)'
  rel=bool(c['name'] in fkcol)
  value='Monovalor' if rel else 'Monovalor (contiene datos compuestos en texto libre)' if t['name']+'.'+c['name'] in ('tb_logs.description','tb_orders.shipping_address') else 'Multivalor resuelto mediante tabla '+('tbd_products_categories' if c['name'].lower() in ('category_id','product_id') and t['name'] in ('tb_products','tbd_products_categories') else 'tbd_address_components' if c['name'].lower().startswith(('address','component')) else t['name']) if 'category' in c['name'].lower() or 'component' in c['name'].lower() else 'Monovalor'
  obligation=('Obligatorio (NOT NULL)' if nullable=='NO' else 'Opcional (NULL)')+('; valor aportado por sistema (AUTO_INCREMENT)' if 'AUTO_INCREMENT' in raw.upper() else '; valor por sistema (DEFAULT '+str(c['default'])+')' if c['default']!='No especificado' else '; valor capturado por usuario/proceso (inferido)')
  composition=formal_column(t['name'],c['name'],c['type'],raw,cons)
  desc=describe_col(t['name'],c['name'],c['type'],raw,cons,pkcols,fkcol,uk)
  desc=re.sub(r'\s*Restricciones:.*$', '', desc)
  col_domain=domain_fk(c['name'],t['name']) or domain_checked(c['name'],c['type'],raw,t['name'],cons)
  record={'name':c['name'],'type':c['type'],'nullable':nullable,'default':c['default'],'extra':c['extra'],'key':key,'classification':{'valor':value,'origen':origin,'obligatoriedad':obligation,'llave':key,'naturaleza':nature(c['name'],c['type']),'composicion_formal':composition,'dominio':col_domain,'descripcion_detallada':desc}}
  rows.append(record)
 t['columns']=rows; t['description_detailed']=detailed_table(t,cols,cons,trigs); t['formal_notation']=formal_table(t['name'],cols,cons)
 (D/'estructura.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
# Add a navegable extension with formal notation, long descriptions, and every-column classification.
ext=['## Leyenda de la notación','', '- `=` se compone de; `+` y; `[a | b]` uno de; `{x}` repetición; `(x)` opcional; `*texto*` comentario/domino.', '- `@` identifica PK; `#` identifica FK. En PK compuestas, todos los miembros llevan `@` y la forma completa se indica explícitamente.', '- Atributos de texto, números, fechas y ENUM se representan como átomos con su tipo y dominio; pares de coordenadas solo se agrupan cuando existe CHECK que lo exige.', '', '## Criterios de clasificación','', '- Las columnas relacionales se clasifican como monovalor; atributos conceptuales repetibles se identifican con la tabla puente/componente correspondiente cuando el esquema lo evidencia.', '- Derivado se reserva para columnas GENERATED o fórmulas expresas. Valores almacenados calculables se marcan “Almacenado (derivable de …)”.', '- NOT NULL equivale a obligatorio; NULL equivale a opcional. Se distingue aporte del sistema por DEFAULT/AUTO_INCREMENT del aporte capturado (inferido).', '- ENUM de estados con progresión de proceso se clasifica ordinal; otros ENUM nominal. Números se clasifican discreto/continuo según tipo y significado; fechas como cuantitativa temporal.', '- Los dominios no declarados por CHECK se limitan al tipo, longitud y restricciones SQL observables; cualquier descripción no literal del esquema va marcada “(inferido)”.', '']
for t in tables:
 cols,cons=parsed[t['name']]
 ext += [f"### Ampliación de `{t['name']}`",'',f"**Descripción general detallada:** {t['description_detailed']}",f"**Composición formal:** `{t['formal_notation']}`",'','**Clasificación de columnas**','', '| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |','|---|---|---|---|---|---|---|---|---|']
 for c in t['columns']:
  q=c['classification']; ext.append('| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in [f"`{c['name']}`",q['valor'],q['origen'],q['obligatoriedad'],q['llave'],q['naturaleza'],q['composicion_formal'],q['dominio'],q['descripcion_detallada']])+' |')
 ext.append('')
# Inference tracking and summary
inferred=[]
for t in tables:
 if '(inferido)' in t['description_detailed']: inferred.append(f"Tabla `{t['name']}`: descripción de propósito/módulo inferida de nombres y relaciones.")
 for c in t['columns']:
  if '(inferido)' in c['classification']['descripcion_detallada'] or '(inferido)' in c['classification']['obligatoriedad']: inferred.append(f"Columna `{t['name']}.{c['name']}`: interpretación funcional o aporte inferido.")
stats=defaultdict(int)
for t in tables:
 for c in t['columns']:
  q=c['classification']; stats['naturaleza:'+q['naturaleza']]+=1; stats['obligatoriedad:'+('Obligatorio' if q['obligatoriedad'].startswith('Obligatorio') else 'Opcional')]+=1; stats['origen:'+('Derivado' if q['origen'].startswith('Derivado') else 'Almacenado')]+=1
  for label in ('PK','FK','UK'):
   if (label=='PK' and q['llave'].startswith('PK')) or (label=='FK' and 'FK →' in q['llave']) or (label=='UK' and 'UK' in q['llave']): stats['llave:'+label]+=1
ext += ['## Resumen estadístico','',f"- Total de columnas clasificadas: {sum(len(t['columns']) for t in tables)}."]
for k,v in sorted(stats.items()): ext.append(f'- {k}: {v}.')
ext += ['', '## Descripciones marcadas (inferido)','']+['- '+x for x in inferred]+['','## Pendientes por confirmar — inferencias','', '- Confirmar las descripciones funcionales y módulos marcados (inferido) con responsables de negocio.', '- Confirmar qué columnas capturadas por procesos externos son ingresadas por usuarios; el dump no identifica la aplicación cliente.', '- Confirmar fórmulas funcionales exactas de importes almacenados. Solo las columnas GENERATED y CHECK expresan reglas computables en el DDL.', '']
with (D/'diccionario_datos.md').open('a',encoding='utf-8') as f: f.write('\n'.join(ext))

# Render final Markdown with every table's required sections together.
def module_for(name):
 if 'order' in name: return 'órdenes'
 if 'buyer' in name or 'user' in name: return 'usuarios'
 if any(x in name for x in ('product','categor')): return 'productos'
 if any(x in name for x in ('cart','wishlist')): return 'carritos'
 if 'order' in name: return 'órdenes'
 if 'payment' in name: return 'pagos'
 if name=='tb_logs': return 'auditoría'
 return 'direcciones'
def lines_for_table(t):
 name=t['name']; cols,cons=parsed[name]; enriched={x['name']:x for x in t['columns']}
 outgoing=[f for f in fks if f['table']==name]; incoming=[f for f in fks if f['ref']==name]
 tr=[x for x in trigs if re.search(r'ON\s+`?'+re.escape(name)+r'`?\s+FOR EACH ROW',x['sql'],re.I)]
 checks=[x for x in cons if re.search(r'\bCHECK\b',x,re.I)]; uniques=[x for x in cons if re.search(r'\bUNIQUE\b',x,re.I)]
 actions=[f"{x['name']}: {x['actions'].strip() or 'sin acción referencial explícita'}" for x in outgoing]
 generated=[c['name']+' '+c['type'] for c in cols if 'GENERATED' in c['extra'].upper()]
 rs=[
  f"Representa la entidad o asociación `{name}` a partir de los nombres y tipos de sus atributos (inferido).",
  f"Pertenece al módulo de {module_for(name)} (inferido por el prefijo y el nombre del objeto).",
  'Relaciones salientes: '+('; '.join(f"{f['cols']} → {f['ref']}.{f['refcols']}" for f in outgoing) if outgoing else 'ninguna FK declarada')+'. Relaciones entrantes: '+('; '.join(f"{f['table']}.{f['cols']}" for f in incoming) if incoming else 'ninguna FK entrante')+'.',
  'Reglas SQL: '+('; '.join('CHECK '+x.split('CHECK',1)[1].strip().rstrip(',') for x in checks) if checks else 'sin CHECK')+'; '+('; '.join('UNIQUE '+x for x in uniques) if uniques else 'sin UNIQUE')+'. Acciones ON DELETE/UPDATE: '+('; '.join(actions) if actions else 'sin FK salientes con acciones')+'. Columnas generadas: '+(', '.join(generated) if generated else 'ninguna')+'.',
  'Triggers asociados: '+(', '.join('`'+x['name']+'`' for x in tr) if tr else 'ninguno')+('; sus acciones de auditoría registran operación y valores NEW/OLD.' if tr else '; esta tabla recibe registros generados por triggers de otras tablas.' if name=='tb_logs' else '.')
 ]
 kind='principal (tb_)' if name.startswith('tb_') else 'catálogo (tbc_)' if name.startswith('tbc_') else 'detalle/relación (tbd_)'
 out=[f"### `{name}`",'',f'- **Prefijo/tipo:** {kind}. **Módulo:** {module_for(name)} (inferido).',f'- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.','- **Descripción general detallada:**']
 out += ['  - '+x for x in rs]
 out += ['',f"**Notación formal:** `{t['formal_notation']}`",'','**Tabla técnica de columnas**','', '| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |','|---:|---|---|---|:---:|---|---|---|---|']
 for i,c in enumerate(cols,1):
  rich=enriched[c['name']]; q=rich['classification']; typ=c['type']; length=typ[typ.find('(')+1:-1] if '(' in typ else '—'; default='Sin default' if c['default']=='No especificado' else c['default']; desc=q['descripcion_detallada']
  techkey=rich['key'] if rich['key']!='No' else '—'
  out.append(f"| {i} | `{c['name']}` | `{typ}` | {length} | {c['nullable']} | {default} | {c['extra']} | {techkey} | {desc} |")
 out += ['', '**Restricciones e índices del DDL**','']
 out += ['- `'+x.replace('`','\\`')+'`' for x in cons] if cons else ['- Sin restricciones o índices declarados.']
 out += ['', '**Relaciones**','']
 out += [f"- `{f['cols'].replace('`','')}` → `{f['ref']}.{f['refcols'].replace('`','')}`; {f['actions'].strip() or 'sin acción referencial explícita'}" for f in outgoing] or ['- Sin FK salientes.']
 out += [f"- Referenciada por `{f['table']}` mediante `{f['cols'].replace('`','')}`." for f in incoming]
 out += ['', '**Triggers asociados:** '+(', '.join('`'+x['name']+'`' for x in tr) if tr else 'Ninguno.'),'','**Tabla de clasificación de columnas**','', '| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |','|---|---|---|---|---|---|---|---|---|']
 for c in t['columns']:
  q=c['classification']; vals=[f"`{c['name']}`",q['valor'],q['origen'],q['obligatoriedad'],q['llave'],q['naturaleza'],q['composicion_formal'],q['dominio'],q['descripcion_detallada']]
  out.append('| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in vals)+' |')
 out.append(''); return out
# Keep the existing generated non-table sections and replace the former shallow table section.
non_table=md[md.index('## Vistas'):]
head=['# Diccionario de datos — db_test','','**Motor objetivo:** MySQL 8.0.36. Fuente de esquema: `BD13.sql`; las sentencias INSERT no se procesan.','','## Leyenda de la notación','', '- `=` significa “se compone de”; `+` significa “y”; `[a | b]` significa “uno de”; `{x}` significa repetición; `(x)` significa opcional; `*texto*` es comentario o dominio.', '- `@columna` marca una PK; `#columna` marca una FK. En PK compuestas todas las columnas de la clave se enumeran en la notación y el campo Llave muestra la composición completa.', '- Las expresiones atómicas se escriben como `columna = {tipo}` y pueden incluir dominio o fórmula entre `*...*`.','','## Criterios de clasificación','', '- Valor: las llaves y referencias escalares son monovalor; los atributos que se repiten por concepto se identifican con su tabla de relación o componentes. Texto que agrupa datos se marca como compuesto en texto libre.', '- Origen: almacenado si se persiste; derivado si es GENERATED, con expresión SQL. Importes persistidos calculables se identifican como almacenados derivables, sin inventar fórmula no declarada.', '- Obligatoriedad: NOT NULL es obligatorio, NULL es opcional. Se indica si AUTO_INCREMENT/DEFAULT lo asigna el sistema o si el origen se infiere.', '- Llave: PK, PK compuesta (miembros completos), FK (destino), UK o No. Naturaleza: ENUM de estados procesales es ordinal; demás ENUM son nominales; numéricos discretos/continuos y fechas temporales.', '- Dominio: tipo, longitud/precisión, valores ENUM y CHECK del DDL; si el SQL no define un rango/formato, se indica el tipo y que no hay una restricción adicional declarada.','','## Índice','','- [Tablas](#tablas)','- [Vistas](#vistas)','- [Triggers](#triggers)','- [Procedimientos](#procedimientos)','- [Catálogo de dominios](#catálogo-de-dominios)','- [Convenciones](#convenciones-de-nombres)','- [Observaciones de calidad](#observaciones-de-calidad-del-diseño)','- [Pendientes por confirmar](#pendientes-por-confirmar)','','## Tablas','']
final=head
for t in tables: final += lines_for_table(t)
final += non_table
# Ensure the statistical summary and inference ledger are part of the final main document.
final += ['','## Resumen estadístico','',f"- Columnas clasificadas: {sum(len(t['columns']) for t in tables)}."]
for k,v in sorted(stats.items()): final.append(f'- {k}: {v}.')
final += ['', '## Descripciones marcadas (inferido)','']+['- '+x for x in inferred]+['','## Pendientes por confirmar — inferencias','', '- Confirmar con responsables de negocio las descripciones y módulos marcados (inferido).', '- Confirmar el origen de captura de los campos no identificados como AUTO_INCREMENT o DEFAULT; el SQL no identifica la interfaz de captura.', '- Confirmar fórmulas de importes almacenados derivables; solo se declaran como derivadas las expresiones GENERATED del DDL.', '']
final += ['## Descripciones genéricas detectadas y reescritas','']+['- `'+x+'`' for x in data['generic_descriptions_rewritten']]+['']
final += ['## Pendientes por confirmar — significado de columnas','']+['- '+x for x in data['pending_confirmations']]+['']
(D/'diccionario_datos.md').write_text('\n'.join(final),encoding='utf-8')
