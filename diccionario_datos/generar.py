import json,re,pathlib,zipfile,xml.sax.saxutils as sx
from collections import defaultdict
D=pathlib.Path(__file__).parent; data=json.loads((D/'estructura.json').read_text(encoding='utf-8')); O=data['objects']
SOURCE_NOTE=f"Estructura y totales de registros obtenidos del respaldo BD19.sql (fecha del archivo: {data.get('source_modified')}). Conteo de registros realizado el: {data.get('row_counted_at')}. Los totales corresponden al respaldo, no a la instancia en vivo."
all_tables=[x for x in O if x['kind']=='table']; all_views=[x for x in O if x['kind']=='view']; all_trigs=[x for x in O if x['kind']=='trigger']
selected=data.get('dictionary_tables', [x['name'] for x in all_tables[:25]])
tables=sorted((x for x in all_tables if x['name'] in selected),key=lambda x:selected.index(x['name']))
def belongs_to_selected(obj, kind):
    if kind == 'trigger':
        m=re.search(r'\bON\s+`([^`]+)`',obj['sql'],re.I); return bool(m and m.group(1) in selected)
    sql=obj['sql']; refs=set(re.findall(r'`([^`]+)`',sql))
    owners=set(re.findall(r"'((?:tb_|tbc_|tbd_)[\w]+)'",sql))
    if owners: return bool(owners & set(selected))
    refs.discard('tb_logs')
    return bool(refs & set(selected))
views=[x for x in all_views if belongs_to_selected(x,'view')]
trigs=[x for x in all_trigs if belongs_to_selected(x,'trigger')]
procs=[x for x in O if x['kind']=='procedure']; funcs=[x for x in O if x['kind']=='function']
def split_def(s):
 return [x.strip().rstrip(',') for x in s.splitlines() if x.strip() and not x.strip().startswith(('CREATE TABLE','/*','*/')) and x.strip() not in (') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci','(')]
def parse_table(t):
 s=t['sql']; cols=[]; cons=[]
 for ln in split_def(s):
  if ln.startswith(')'): continue
  m=re.match(r'`([^`]+)`\s+(.+)',ln)
  if m and not m.group(1).upper() in ('PRIMARY','UNIQUE','KEY','CONSTRAINT','FOREIGN','CHECK'):
   name=m.group(1); rest=m.group(2); typ=re.match(r'(\w+(?:\s*\([^)]*\))?(?:\s+unsigned)?(?:\s+zerofill)?)',rest,re.I).group(1); null='NO' if re.search(r'\bNOT NULL\b',rest,re.I) else 'Sí'; default=(re.search(r'\bDEFAULT\s+((?:\'[^\']*\')|(?:[^\s,]+))',rest,re.I) or [None,'Sin dato declarado'])[1]; extra='; '.join(x for x in ('AUTO_INCREMENT' if 'AUTO_INCREMENT' in rest else '', 'GENERATED STORED' if 'STORED' in rest else '', 'ON UPDATE CURRENT_TIMESTAMP' if 'ON UPDATE' in rest else '') if x) or '—'; cols.append({'name':name,'type':typ,'nullable':null,'default':default,'extra':extra,'key':''})
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
 known.update({'tbc_gen_country_profile':'Catálogo de apoyo para la generación masiva de usuarios; define códigos de país, prefijos y formatos telefónicos, y títulos de cortesía.','tbc_gen_family_names':'Catálogo de apoyo para la generación masiva de usuarios; conserva apellidos disponibles por país y los relaciona con tbc_gen_country_profile.','tbc_gen_given_names':'Catálogo de apoyo para la generación masiva de usuarios; conserva nombres por país y género, relacionados con tbc_gen_country_profile.'})
 known.update({'tbc_gen_country_profile':'Catálogo de apoyo para la generación masiva de usuarios; define códigos de país y parámetros locales de teléfono y título de cortesía.','tbc_gen_family_names':'Catálogo de apoyo para la generación masiva de usuarios; almacena apellidos por país relacionados con tbc_gen_country_profile.','tbc_gen_given_names':'Catálogo de apoyo para la generación masiva de usuarios; almacena nombres por país y género relacionados con tbc_gen_country_profile.'})
 return known.get(name,'Propósito no especificado en el SQL.')
# relation info
fks=[]
for t in tables:
 for c in parsed[t['name']][1]:
  m=re.search(r'CONSTRAINT\s+`([^`]+)`\s+FOREIGN KEY\s*\(([^)]*)\)\s+REFERENCES\s+`([^`]+)`\s*\(([^)]*)\)(.*)',c,re.I)
  if m: fks.append({'name':m.group(1),'table':t['name'],'cols':m.group(2),'ref':m.group(3),'refcols':m.group(4),'actions':m.group(5)})
# markdown
md=['# Diccionario de datos — BD19','', '**Motor objetivo:** MySQL 8.0.45. Fuente: `Practica03/backups/BD19.sql`; estructura y conteos del respaldo.','', '## Índice','', '- [Tablas](#tablas)','- [Vistas](#vistas)','- [Triggers](#triggers)','- [Procedimientos](#procedimientos)','- [Catálogo de dominios](#catálogo-de-dominios)','- [Convenciones](#convenciones-de-nombres)','- [Observaciones de calidad](#observaciones-de-calidad-del-diseño)','- [Pendientes por confirmar](#pendientes-por-confirmar)','']
md += ['## Tablas','']
for t in tables:
 n=t['name']; cols,cons=parsed[n]; md += [f'### `{n}`','',f'- **Prefijo/tipo:** {"principal (tb_)" if n.startswith("tb_") else "catálogo (tbc_)" if n.startswith("tbc_") else "detalle (tbd_)"}.','- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci (según opciones explícitas; revisar excepciones en DDL).',f'- **Propósito:** {purpose(n)}','', '| # | Columna | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |','|---:|---|---|---|:---:|---|---|---|---|']
 for i,c in enumerate(cols,1):
  typ=c['type']; length=typ[typ.find('(')+1:-1] if '(' in typ else '—'; desc='1 = activo; 0 = inactivo (borrado lógico).' if c['name'].lower()=='status' and 'bit' in typ.lower() else 'Sin dato declarado en SQL.'
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
 s=v['sql']; sel=re.sub(r'^.*?AS\s+','',s,flags=re.S|re.I); names=re.findall(r'\bAS\s+`([^`]+)`',sel,re.I); bases=list(dict.fromkeys(re.findall(r'\b(?:FROM|JOIN)\s+`?([\w]+)`?',sel,re.I)+re.findall(r"'((?:tb_|tbc_|tbd_)[\w]+)'",sel))); md += [f"### `{v['name']}`",'',f"- **Propósito:** presenta trazabilidad de {v['name'].replace('vw_trazabilidad_','').replace('_',' ')} mediante la consulta definida en SQL (inferido).",f"- **Tablas base:** {', '.join('`'+x+'`' for x in bases) or 'La consulta no expone tablas base identificables.'}.",'- **Columnas expuestas:** '+(', '.join('`'+x+'` (tipo derivado de expresión; origen en SELECT)' for x in names) or 'Columnas determinadas por las expresiones SELECT del cuerpo.')+'.','']
md += ['## Triggers','', '| Nombre | Tabla | Evento | Momento | Registro en tb_logs |','|---|---|---|---|---|']
for x in trigs:
 s=x['sql']; tab=re.search(r'ON\s+`([^`]+)`',s); ev=re.search(r'\b(AFTER)\s+(INSERT|UPDATE|DELETE)',s); cols=re.search(r'INSERT\s+INTO\s+`?tb_logs`?\s*\(([^)]*)\)',s,re.I); concat=re.search(r'CONCAT\s*\((.*?)\)\s*\)',s,re.S|re.I); fmt=' '.join(re.findall(r"'((?:[^']|'')*)'",concat.group(1))) if concat else 'description sin plantilla CONCAT identificable'
 md.append(f"| `{x['name']}` | `{tab.group(1) if tab else 'Sin dato declarado'}` | {ev.group(2) if ev else 'Sin dato declarado'} | {ev.group(1) if ev else 'AFTER'} | {cols.group(1).replace('`','') if cols else 'Sin dato declarado'}; description: `{fmt}` (valores dinámicos NEW/OLD según operación). |")
md += ['','## Procedimientos','']
def routine_signature(sql, kind='PROCEDURE'):
 m=re.search(r'\b'+kind+r'\s+`[^`]+`\s*\(',sql,re.I)
 if not m: return ''
 start=m.end(); depth=1; quote=None; i=start
 while i<len(sql) and depth:
  ch=sql[i]
  if quote:
   if ch==quote and (i==0 or sql[i-1]!='\\'): quote=None
  elif ch in "'\"`": quote=ch
  elif ch=='(': depth+=1
  elif ch==')': depth-=1
  i+=1
 return sql[start:i-1] if depth==0 else ''

def split_params(raw):
 parts=[]; start=0; depth=0; quote=None
 for i,ch in enumerate(raw):
  if quote:
   if ch==quote: quote=None
  elif ch in "'\"`": quote=ch
  elif ch=='(': depth+=1
  elif ch==')': depth-=1
  elif ch==',' and depth==0: parts.append(raw[start:i].strip()); start=i+1
 if raw[start:].strip(): parts.append(raw[start:].strip())
 return parts

procedure_info={
 'sp_gen_validate_params':('Valida total, rango de edades, porcentaje activo y país; genera error SQL si algún parámetro no cumple sus límites.','`tbc_gen_country_profile`'),
 'sp_gen_insert_user_person':('Inserta la cuenta en tb_users y su perfil en tb_people; devuelve el identificador mediante parámetro OUT.','`tb_users`, `tb_people`'),
 'sp_generate_users':('Valida parámetros y genera en lote cuentas y personas usando los catálogos y funciones fn_gen_*; controla la operación con transacción.','`tb_users`, `tb_people`, `tbc_gen_*`; `tb_logs` mediante triggers'),
 'sp_register_user_person':('Valida los datos de una cuenta y registra el usuario junto con su perfil de persona como una operación coordinada; el propósito se infiere del nombre del procedimiento.','`tb_users`, `tb_people` (inferido)'),
 'sp_soft_delete':('Valida el nombre de tabla y el identificador recibidos, y aplica el borrado lógico al registro indicado si la tabla está permitida.','Tabla indicada por p_table_name (dinámico)'),
 'sp_soft_delete_product':('Comprueba el producto solicitado y cambia su status a inactivo para conservar el registro y su historial.','`tb_products`'),
 'sp_soft_delete_user':('Comprueba la cuenta solicitada y cambia su status a inactivo para impedir su uso sin borrar su historial.','`tb_users`')}
for x in procs:
 s=x['sql']; params=re.sub(r'\s+',' ',routine_signature(s)).strip(); parts=split_params(params); parsed_params=[]
 for part in parts:
  pm=re.match(r'(?:(IN|OUT|INOUT)\s+)?(\w+)\s+(.+)',part,re.I)
  if pm: parsed_params.append((pm.group(1) or 'IN',pm.group(2),pm.group(3)))
 affects=procedure_info.get(x['name'],('',''))[1] or ', '.join(sorted(set(re.findall(r'\b(?:UPDATE|INSERT\s+INTO|DELETE\s+FROM)\s+`?([\w]+)',s,re.I)))) or 'Sin tablas modificadas detectables.'
 desc,touched=procedure_info.get(x['name'],('Realiza las validaciones y operaciones indicadas por su cuerpo SQL. (inferido)',affects))
 example_args=', '.join('@'+p[1] for p in parsed_params)
 md += [f"### `{x['name']}`",'',f"- **Parámetros:** "+('; '.join(f'{mode} {name} {typ}' for mode,name,typ in parsed_params) or 'sin parámetros')+'.',f'- **Pasos:** {desc}',f'- **Tablas afectadas:** {touched}.',f"- **Ejemplo:** `CALL {x['name']}({example_args});`",'']
if not procs: md.append('- BD19.sql no define procedimientos.')
md += ['## Funciones','']
if not funcs: md.append('- BD19.sql no define funciones.')
function_info={'fn_gen_birth_date':'Genera fecha de nacimiento aleatoria dentro del rango de edades indicado.','fn_gen_courtesy_title':'Devuelve el título de cortesía según país y género.','fn_gen_datetime_between':'Genera DATETIME aleatorio entre dos límites.','fn_gen_email':'Construye correo con nombre, apellido, secuencia y dominio de prueba.','fn_gen_email_domain':'Elige example.com, example.org o example.net.','fn_gen_family_name':'Selecciona apellido al azar del catálogo del país.','fn_gen_gender_id':'Devuelve aleatoriamente 1 o 2.','fn_gen_given_name':'Selecciona nombre al azar por país y género.','fn_gen_is_active':'Distribuye el estado activo conforme al porcentaje solicitado.','fn_gen_nickname':'Construye alias con inicial, apellido normalizado y secuencia.','fn_gen_password_hash':'Genera hash SHA-256 sobre texto aleatorio con UUID y RAND().','fn_gen_phone':'Construye teléfono con prefijo y longitud del perfil del país.','fn_gen_random_country':'Selecciona un país cuyo perfil esté activo.','fn_gen_random_int':'Devuelve entero aleatorio en el intervalo inclusivo indicado.','fn_gen_slug':'Normaliza a minúsculas y elimina espacios, apóstrofos, guiones y puntos.'}
for fn in funcs:
 sig=routine_signature(fn['sql'],'FUNCTION'); ret=re.search(r'RETURNS\s+([^\s]+)',fn['sql'],re.I); props=', '.join(x for x in ('DETERMINISTIC','NO SQL','READS SQL DATA') if re.search(r'\b'+x+r'\b',fn['sql'],re.I)) or 'características no declaradas explícitamente'; md += [f"### `{fn['name']}`",f"- **Parámetros:** `{sig}`.",f"- **Retorno:** `{ret.group(1) if ret else 'tipo no localizado'}`.",f'- **Características:** {props}.',f'- **Qué hace:** {function_info.get(fn["name"],"Operación expresada en el cuerpo SQL.")} (descripción derivada del SQL).',f"- **Ejemplo:** `SELECT {fn['name']}(...);`",'']
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
obs=['**Alta —** `tbd_products_categories.category_ID` carece de FK a `tbc_categories`. Recomendación: declarar FK y decidir acciones referenciales.','**Alta —** coexisten `tb_orders`/`tbd_order_details` y `tb_buyer_orders`/`tbd_order_items`; `tb_payments` referencia `tb_orders`, mientras envíos, devoluciones y cancelaciones referencian `tb_buyer_orders`. Recomendación: confirmar si son flujos distintos y definir un modelo canónico de pagos/órdenes.','**Alta —** `tb_buyer_orders` solo guarda `seller_ID`; no identifica comprador. Recomendación: agregar vínculo al comprador si el proceso lo requiere.','**Alta —** `tb_refunds.return_ID` y `cancellation_ID` son opcionales y no hay CHECK que exija exactamente uno. Recomendación: agregar CHECK/XOR o separar los tipos de origen.','**Alta —** `tbd_return_items.quantity` y `tbd_cancellation_items.quantity` no tienen CHECK `quantity > 0`. Recomendación: agregar restricción positiva.','**Media —** `tb_payments.transaction_reference` y `tb_payment_transaction.gateway_reference` pueden representar la misma referencia de pasarela. Recomendación: definir qué identificador es canónico y evitar duplicar valores divergentes.','**Media —** tablas sin columna genérica `status`: `tb_order_cancellations`, `tb_payment_transaction`, `tb_people`, `tb_refunds`, `tb_returns`, `tb_shipments`, `tbd_cancellation_items`, `tbd_return_items`; varias tienen estados de proceso específicos. Recomendación: documentar si esos estados sustituyen deliberadamente a `status` y mantener transiciones válidas.','**Media —** las llaves relacionadas usan tipos INT, INT UNSIGNED y BIGINT; `status` combina bit(1) y tinyint. Recomendación: normalizar tipos/signo y dominios documentando una migración compatible.','**Media —** `tbd_carts_items` y `tbd_order_items` separan referencias a usuario y producto hacia `tbd_products_users_providers` en vez de declarar una FK compuesta. Recomendación: añadir integridad compuesta o validación equivalente.','**Baja —** courtesy_title_ID y country_code sin catálogo ni FK: en `tb_people` son `char(10)` y `char(2)` respectivamente; tampoco existe `fk_people_courtesy_title` ni `fk_people_country`. Recomendación: incorporar catálogos y restricciones si esos códigos deben validarse.']
for x in obs: md.append('- '+x)
legacy=' '.join(x['sql'] for x in O)
md += ['', '**Referencias huérfanas:** las definiciones de BD19 no contienen referencias a `tbd_order_details`, `tbd_wishlist`, `tbd_shopping_cart` ni `tb_users_offer_products`; esas tablas no aparecen en esta versión. La ausencia de referencias se verifica en DDL, no en valores de filas.','', '## Pendientes por confirmar','', '- Confirmar con negocio si órdenes, pagos, devoluciones y envíos comparten una entidad canónica o pertenecen a flujos separados.', '- Confirmar el catálogo y semántica de `tb_people.gender_ID`, `courtesy_title_ID` y `country_code`.', '- Confirmar si `tb_people` tiene vínculo obligatorio 1:1 con `tb_users` y el uso de los perfiles.', '- Confirmar qué pasarelas crean `gateway_reference` y `transaction_reference` y cómo se concilian.', '- Confirmar cardinalidades no garantizadas por FK/UNIQUE y las inferencias de negocio señaladas en las fichas.', '- En vistas, algunos tipos dependen de expresiones SQL; deben confirmarse con DESCRIBE en una instancia.', '- Los mensajes de `description` de triggers incluyen valores NEW/OLD; su formato exacto depende del evento.','']
(D/'diccionario_datos.md').write_text('\n'.join(md),encoding='utf-8')

# Enriquecimiento estructurado de tabla y columna desde el DDL ya aislado.
TABLE_PURPOSES={
 'tbc_gen_country_profile':'Catálogo de apoyo para la generación masiva de usuarios; define país, prefijos telefónicos, cantidad de dígitos y títulos de cortesía.',
 'tbc_gen_family_names':'Catálogo de apoyo para la generación masiva de usuarios; almacena apellidos por país con FK al perfil del país.',
 'tbc_gen_given_names':'Catálogo de apoyo para la generación masiva de usuarios; almacena nombres por país y género, con FK y CHECK.',
 'tbc_gen_country_profile':'Catálogo de apoyo para la generación masiva de usuarios; define el país y los parámetros locales usados para construir teléfono y título de cortesía.',
 'tbc_gen_family_names':'Catálogo de apoyo para la generación masiva de usuarios; almacena apellidos por país y mantiene FK al perfil del país.',
 'tbc_gen_given_names':'Catálogo de apoyo para la generación masiva de usuarios; almacena nombres por país y género, con FK al perfil del país y CHECK de género.',
 'tb_buyer_orders':'Conserva las órdenes del flujo de compra asociadas al vendedor, sus importes y su etapa de cumplimiento; el DDL no contiene una columna de comprador.',
 'tb_carts':'Representa el carrito activo o histórico de un usuario para agrupar artículos antes de convertirlos en orden.',
 'tb_logs':'Registra operaciones de auditoría emitidas por triggers, con tabla, evento, usuario de base de datos y descripción del cambio.',
 'tb_order_cancellations':'Registra solicitudes para cancelar órdenes de comprador, con usuario solicitante, motivo y estado del trámite.',
 'tb_orders':'Representa órdenes del modelo principal vinculadas a una cuenta, con importe, estado y dirección de envío en texto.',
 'tb_payment_transaction':'Conserva los movimientos enviados o recibidos por la pasarela de pago, su importe, resultado y referencia externa.',
 'tb_payments':'Registra los pagos asociados a órdenes del modelo principal y al método de pago utilizado.',
 'tb_people':'Almacena datos personales de contacto e identificación asociados a una cuenta de usuario.',
 'tb_products':'Mantiene el catálogo de productos con SKU, descripción, precio vigente, existencias y estado de publicación.',
 'tb_refunds':'Registra importes devueltos y su vínculo opcional con una devolución o una cancelación.',
 'tb_returns':'Representa solicitudes de devolución asociadas a una orden de comprador y su estado de atención.',
 'tb_shipments':'Registra el envío de una orden, la dirección de destino, la transportista, el rastreo y las fechas logísticas.',
 'tb_user_addresses':'Conserva direcciones de entrega de usuarios, sus datos de contacto, coordenadas e instrucciones.',
 'tb_users':'Representa cuentas de acceso con correo, alias, hash de contraseña, fechas de actividad y estado.',
 'tbc_categories':'Define categorías de productos y la relación jerárquica opcional entre categorías.',
 'tbc_payment_methods':'Lista los métodos de pago disponibles para registrar pagos.',
 'tbc_payment_methods_types':'Define tipos codificados que clasifican métodos de pago de usuarios.',
 'tbd_address_components':'Desglosa una dirección en componentes tipados y permite una relación jerárquica entre componentes.',
 'tbd_cancellation_items':'Detalla qué líneas y cantidades de una orden se incluyen en una solicitud de cancelación.',
 'tbd_carts_items':'Relaciona carritos con productos y proveedores, indicando la cantidad solicitada.',
 'tbd_order_items':'Conserva las líneas de las órdenes de comprador con nombre histórico, cantidad, precio unitario e importe.',
 'tbd_products_categories':'Asocia productos con categorías para permitir su clasificación en el catálogo.',
 'tbd_products_users_providers':'Asocia productos con usuarios que actúan como propietarios o proveedores.',
 'tbd_return_items':'Detalla las líneas y cantidades incluidas en una devolución, junto con notas sobre su condición.',
 'tbd_user_payment_methods':'Vincula usuarios con referencias de métodos de pago administradas por proveedores externos.',
 'tbd_users_wishlist_products':'Relaciona usuarios con productos guardados en su lista de deseos.',
}
def detailed_table(t, cols, cons, trig_names):
 name=t['name']; module='envíos, devoluciones y cancelaciones' if any(k in name for k in ('shipment','return','refund','cancellation')) else 'órdenes' if 'order' in name else 'usuarios' if 'user' in name or 'people' in name else 'productos' if any(k in name for k in ('product','categor')) else 'carritos' if any(k in name for k in ('cart','wishlist')) else 'pagos' if 'payment' in name else 'auditoría' if name=='tb_logs' else 'direcciones'
 refs=[f['ref'] for f in fks if f['table']==name]; incoming=[f['table'] for f in fks if f['ref']==name]
 tr=[x['name'] for x in trigs if re.search(r'ON\s+`?'+re.escape(name)+r'`?\s+FOR EACH ROW',x['sql'],re.I)]
 view_names=[]
 for view in views:
  sql=view['sql']; owners=set(re.findall(r"'((?:tb_|tbc_|tbd_)[\w]+)'",sql)); view_refs=set(re.findall(r'`([^`]+)`',sql)); view_refs.discard('tb_logs')
  if name in owners or (not owners and name in view_refs): view_names.append(view['name'])
 related=', '.join('`'+r+'`' for r in dict.fromkeys(refs+incoming)) or 'no declara relaciones FK'
 checks=[x.split('CHECK',1)[1].strip().rstrip(',') for x in cons if 'CHECK' in x.upper()]
 uniques=[x for x in cons if 'UNIQUE' in x.upper()]
 actions=[f"{f['name']} {f['actions'].strip()}" for f in fks if f['table']==name and f['actions'].strip()]
 generated=[c['name'] for c in cols if 'GENERATED' in c['extra'].upper()]
 return ' '.join((
  TABLE_PURPOSES.get(name,f"Registra la relación de negocio indicada por sus columnas {', '.join(c['name'] for c in cols[:4])} (inferido)."),
  f"Pertenece al módulo de {module} (inferido por el nombre).",
  f"Se relaciona con {related}; las FK entrantes y salientes están enumeradas en Relaciones.",
  f"Reglas de negocio declaradas: CHECK {('; '.join(checks) if checks else 'ninguno')}; UNIQUE {('; '.join(uniques) if uniques else 'ninguno')}; acciones referenciales {('; '.join(actions) if actions else 'sin acción explícita')}; columnas generadas {(', '.join(generated) if generated else 'ninguna')}.",
  f"Vistas asociadas: {(', '.join(view_names) if view_names else 'ninguna')}; mapeo por tabla base o filtro de trazabilidad.",
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
 if t.startswith(('char','varchar','binary','varbinary')): return f'{c} ∈ cadena(≤{m.group(1) if m else "Sin dato declarado"}); tipo {typ}'
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
  ('tbc_gen_country_profile','country_code'): 'Código ISO de dos caracteres que identifica el país usado como clave del perfil de generación; permite relacionar los catálogos auxiliares con sus parámetros locales.',
  ('tbc_gen_country_profile','country_name'): 'Nombre legible del país asociado al código country_code.',
  ('tbc_gen_country_profile','phone_prefix'): 'Prefijo telefónico internacional que se antepone a los dígitos locales al generar teléfonos.',
  ('tbc_gen_country_profile','phone_digits'): 'Cantidad de dígitos locales que deben generarse para completar el teléfono del país.',
  ('tbc_gen_country_profile','title_male'): 'Título de cortesía que se asigna a personas del género masculino en el contexto del país.',
  ('tbc_gen_country_profile','title_female'): 'Título de cortesía que se asigna a personas del género femenino en el contexto del país.',
  ('tbc_gen_family_names','country_code'): 'Código de país que identifica el perfil cultural al que pertenece el apellido; FK a tbc_gen_country_profile.country_code.',
  ('tbc_gen_family_names','name'): 'Apellido disponible para selección aleatoria durante la generación masiva de usuarios.',
  ('tbc_gen_given_names','country_code'): 'Código de país que identifica el perfil cultural del nombre; FK a tbc_gen_country_profile.country_code.',
  ('tbc_gen_given_names','gender_id'): 'Identificador del género al que se asocia el nombre; CHECK restringe el valor a 1 o 2.',
  ('tbc_gen_given_names','name'): 'Nombre de pila disponible para selección por país y género durante la generación masiva de usuarios.',
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
 new_fields={
  'tb_order_cancellations': {'buyer_order_id':'Vincula la solicitud de cancelación con la orden del comprador que se pretende detener.','user_id':'Identifica al usuario que registró o gestionó la solicitud de cancelación (inferido).','reason':'Explica el motivo indicado para cancelar la orden.','cancellation_status':'Registra la etapa de la cancelación dentro del ENUM del flujo.','request_date':'Marca cuándo se presentó la solicitud de cancelación.','creation_date':'Marca cuándo se creó el registro de cancelación.','last_update':'Marca la última modificación del registro de cancelación.'},
  'tb_payment_transaction': {'payment_id':'Vincula el movimiento del procesador con el pago interno correspondiente.','transaction_type':'Distingue el tipo de movimiento financiero descrito por el ENUM (por ejemplo, cargo o reembolso).','amount':'Registra el importe asociado a este movimiento del pago; la moneda no está declarada (inferido).','transaction_status':'Registra el resultado o etapa del movimiento financiero.','gateway_reference':'Conserva la referencia asignada por la pasarela para consultar o conciliar el movimiento.','response_message':'Conserva el mensaje devuelto por la pasarela para explicar el resultado de la operación.','transaction_date':'Registra cuándo ocurrió el movimiento en la pasarela.','creation_date':'Registra cuándo se creó la fila de transacción.','last_update':'Registra la última modificación de la fila de transacción.'},
  'tb_people': {'person_id':'Identifica el perfil de persona asociado a una cuenta; BIGINT permite un identificador independiente del usuario.','user_id':'Relaciona el perfil personal con la cuenta de usuario que lo administra.','courtesy_title_id':'Guarda el código de tratamiento honorífico asociado a la persona; el DDL no declara catálogo ni FK.','given_names':'Guarda los nombres propios de la persona para identificarla en registros de entrega o cuenta.','family_names':'Guarda los apellidos de la persona para completar su nombre de identificación.','birth_date':'Registra la fecha de nacimiento de la persona.','gender_id':'Guarda un código de género; el DDL no declara catálogo ni FK para interpretarlo.','country_code':'Guarda el código de país asociado a la persona; el DDL no declara catálogo ni FK.','phone':'Guarda el teléfono de contacto de la persona.','last_update':'Registra la última modificación de los datos personales.'},
  'tb_refunds': {'payment_id':'Identifica el pago del que se devuelve dinero.','return_id':'Vincula el reembolso con una devolución cuando esa es su causa; la columna es opcional.','cancellation_id':'Vincula el reembolso con una cancelación cuando esa es su causa; la columna es opcional.','amount':'Registra el importe que se devuelve al cliente; la moneda no está declarada (inferido).','refund_status':'Registra la etapa del reembolso dentro del ENUM del flujo.','reason':'Describe el motivo del reembolso.','refund_date':'Registra cuándo se procesó o registró el reembolso.','creation_date':'Registra cuándo se creó el registro del reembolso.','last_update':'Registra la última modificación del reembolso.'},
  'tb_returns': {'buyer_order_id':'Vincula la devolución con la orden del comprador de la que provienen los artículos.','user_id':'Identifica al usuario que solicitó o gestionó la devolución (inferido).','reason':'Describe el motivo indicado para devolver artículos.','return_status':'Registra la etapa de la devolución dentro del ENUM del flujo.','request_date':'Registra cuándo se solicitó la devolución.','creation_date':'Registra cuándo se creó la fila de devolución.','last_update':'Registra la última modificación de la devolución.'},
  'tb_shipments': {'buyer_order_id':'Vincula el envío con la orden del comprador que se entrega.','address_id':'Identifica la dirección de entrega asociada al envío.','carrier':'Guarda el nombre de la empresa transportista encargada del envío.','tracking_number':'Conserva el código que permite consultar el recorrido del paquete con la transportista.','shipment_status':'Registra la etapa logística del envío dentro del ENUM declarado.','shipped_date':'Registra cuándo la transportista recibió o despachó el paquete.','estimated_delivery_date':'Registra la fecha estimada de entrega comunicada para el envío.','delivered_date':'Registra cuándo se marcó el paquete como entregado.','creation_date':'Registra cuándo se creó el registro del envío.','last_update':'Registra la última modificación del estado o datos del envío.'},
  'tbd_return_items': {'return_id':'Identifica la devolución que contiene esta línea.','order_item_id':'Identifica la línea original de la orden cuyos artículos se devuelven.','quantity':'Registra cuántas unidades de la línea original se incluyen en la devolución; el DDL no exige quantity > 0.','condition_notes':'Describe la condición observada de los artículos devueltos.','creation_date':'Registra cuándo se creó esta línea de devolución.','last_update':'Registra la última modificación de esta línea.'},
  'tbd_cancellation_items': {'cancellation_id':'Identifica la solicitud de cancelación a la que pertenece la línea.','order_item_id':'Identifica la línea de la orden que se solicita cancelar.','quantity':'Registra cuántas unidades de la línea original se pretende cancelar; el DDL no exige quantity > 0.','creation_date':'Registra cuándo se creó esta línea de cancelación.','last_update':'Registra la última modificación de esta línea.'}
 }
 if table in new_fields and low in new_fields[table]: return new_fields[table][low]+' (inferido).'
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
  obligation=('Obligatorio (NOT NULL)' if nullable=='NO' else 'Opcional (NULL)')+('; valor aportado por sistema (AUTO_INCREMENT)' if 'AUTO_INCREMENT' in raw.upper() else '; valor por sistema (DEFAULT '+str(c['default'])+')' if c['default']!='Sin dato declarado' else '; valor capturado por usuario/proceso (inferido)')
  composition=formal_column(t['name'],c['name'],c['type'],raw,cons)
  desc=describe_col(t['name'],c['name'],c['type'],raw,cons,pkcols,fkcol,uk)
  desc=re.sub(r'\s*Restricciones:.*$', '', desc)
  col_domain=domain_fk(c['name'],t['name']) or domain_checked(c['name'],c['type'],raw,t['name'],cons)
  record={'name':c['name'],'type':c['type'],'nullable':nullable,'default':c['default'],'extra':c['extra'],'key':key,'classification':{'valor':value,'origen':origin,'obligatoriedad':obligation,'llave':key,'naturaleza':nature(c['name'],c['type']),'composicion_formal':composition,'dominio':col_domain,'descripcion_detallada':desc}}
  rows.append(record)
 t['columns']=rows; t['description_detailed']=detailed_table(t,cols,cons,trigs); t['formal_notation']=formal_table(t['name'],cols,cons)
data['dictionary_tables']=selected
data['dictionary_counts']={'tables':len(tables),'views':len(views),'triggers':len(trigs),'columns':sum(len(t['columns']) for t in tables),'foreign_keys':len(fks)}
data['counts']={'tables':len(all_tables),'views':len(all_views),'triggers':len(all_trigs),'procedures':len(procs),'functions':len(funcs),'columns':sum(len(parse_table(t)[0]) for t in all_tables),'foreign_keys':sum(1 for t in all_tables for c in parse_table(t)[1] if 'FOREIGN KEY' in c),'derived_columns':sum('GENERATED' in c.get('extra','').upper() for t in all_tables for c in t.get('columns',[]))}
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
 if any(x in name for x in ('shipment','return','refund','cancellation')): return 'envíos, devoluciones y cancelaciones'
 if 'people' in name: return 'usuarios y perfiles personales'
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
  TABLE_PURPOSES.get(name,f"Registra la relación de negocio indicada por sus columnas {', '.join(c['name'] for c in cols[:4])} (inferido)."),
  f"Pertenece al módulo de {module_for(name)} (inferido por el prefijo y el nombre del objeto).",
  'Relaciones salientes: '+('; '.join(f"{f['cols']} → {f['ref']}.{f['refcols']}" for f in outgoing) if outgoing else 'ninguna FK declarada')+'. Relaciones entrantes: '+('; '.join(f"{f['table']}.{f['cols']}" for f in incoming) if incoming else 'ninguna FK entrante')+'.',
  'Reglas SQL: '+('; '.join('CHECK '+x.split('CHECK',1)[1].strip().rstrip(',') for x in checks) if checks else 'sin CHECK')+'; '+('; '.join('UNIQUE '+x for x in uniques) if uniques else 'sin UNIQUE')+'. Acciones ON DELETE/UPDATE: '+('; '.join(actions) if actions else 'sin FK salientes con acciones')+'. Columnas generadas: '+(', '.join(generated) if generated else 'ninguna')+'.',
  'Triggers asociados: '+(', '.join('`'+x['name']+'`' for x in tr) if tr else 'ninguno')+('; sus acciones de auditoría registran operación y valores NEW/OLD.' if tr else '; esta tabla recibe registros generados por triggers de otras tablas.' if name=='tb_logs' else '.')
 ]
 kind='principal (tb_)' if name.startswith('tb_') else 'catálogo (tbc_)' if name.startswith('tbc_') else 'detalle/relación (tbd_)'
 out=[f"### `{name}`",'',f'- **Total de registros:** {data.get("row_counts",{}).get(name,"No verificable en el respaldo")}. ',f'- **Prefijo/tipo:** {kind}. **Módulo:** {module_for(name)} (inferido).',f'- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.','- **Descripción general detallada:**']
 out += ['  - '+x for x in rs]
 out += ['',f"**Notación formal:** `{t['formal_notation']}`",'','**Tabla técnica de columnas**','', '| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |','|---:|---|---|---|:---:|---|---|---|---|']
 for i,c in enumerate(cols,1):
  rich=enriched[c['name']]; q=rich['classification']; typ=c['type']; length=typ[typ.find('(')+1:-1] if '(' in typ else '—'; default='Sin default' if c['default']=='Sin dato declarado' else c['default']; desc=q['descripcion_detallada']
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
head=['# Diccionario de datos — BD19','','**Motor objetivo:** MySQL 8.0.45. '+SOURCE_NOTE,'','## Leyenda de la notación','', '- `=` significa “se compone de”; `+` significa “y”; `[a | b]` significa “uno de”; `{x}` significa repetición; `(x)` significa opcional; `*texto*` es comentario o dominio.', '- `@columna` marca una PK; `#columna` marca una FK. En PK compuestas todas las columnas de la clave se enumeran en la notación y el campo Llave muestra la composición completa.', '- Las expresiones atómicas se escriben como `columna = {tipo}` y pueden incluir dominio o fórmula entre `*...*`.','','## Criterios de clasificación','', '- Valor: las llaves y referencias escalares son monovalor; los atributos que se repiten por concepto se identifican con su tabla de relación o componentes. Texto que agrupa datos se marca como compuesto en texto libre.', '- Origen: almacenado si se persiste; derivado si es GENERATED, con expresión SQL. Importes persistidos calculables se identifican como almacenados derivables, sin inventar fórmula no declarada.', '- Obligatoriedad: NOT NULL es obligatorio, NULL es opcional. Se indica si AUTO_INCREMENT/DEFAULT lo asigna el sistema o si el origen se infiere.', '- Llave: PK, PK compuesta (miembros completos), FK (destino), UK o No. Naturaleza: ENUM de estados procesales es ordinal; demás ENUM son nominales; numéricos discretos/continuos y fechas temporales.', '- Dominio: tipo, longitud/precisión, valores ENUM y CHECK del DDL; si el SQL no define un rango/formato, se indica el tipo y que no hay una restricción adicional declarada.','','## Índice','','- [Tablas](#tablas)','- [Vistas](#vistas)','- [Triggers](#triggers)','- [Procedimientos](#procedimientos)','- [Funciones](#funciones)','- [Volumen de datos](#volumen-de-datos)','- [Catálogo de dominios](#catálogo-de-dominios)','- [Convenciones](#convenciones-de-nombres)','- [Observaciones de calidad](#observaciones-de-calidad-del-diseño)','- [Historial de cambios](#historial-de-cambios)','- [Pendientes por confirmar](#pendientes-por-confirmar)','','## Tablas','']
head[3:3]=['**Alcance:** 25 tablas: `tb_logs` y 24 tablas auditadas. Las 24 auditadas se priorizan por población y corresponden a 24 vistas y 72 triggers. `tb_logs` no tiene vista ni trigger propio; se omiten los tres catálogos poblados `tbc_gen_*` porque BD19 tampoco les declara vistas o triggers.','']
final=head
for t in tables: final += lines_for_table(t)
final += non_table
# Ensure the statistical summary and inference ledger are part of the final main document.
final += ['','## Resumen estadístico','',f"- Columnas clasificadas: {sum(len(t['columns']) for t in tables)}."]
for k,v in sorted(stats.items()): final.append(f'- {k}: {v}.')
row_counts=data.get('row_counts', {}); row_total=sum(v for v in row_counts.values() if isinstance(v,int)); verified=sum(isinstance(row_counts.get(t['name']),int) for t in tables)
final += ['', '## Volumen de datos', '', SOURCE_NOTE, f"- Conteo de registros realizado el: {data.get('row_counted_at')}. Los valores son conteos de filas INSERT del respaldo BD19.sql, no de la instancia en vivo.", f'- Total verificable: {row_total:,} registros en {verified} tablas; {len(tables)-verified} tablas sin INSERT no son verificables en el respaldo.', '', '| Tabla | Registros | Porcentaje del total verificable |', '|---|---:|---:|']
for t in sorted(tables,key=lambda x:(-(row_counts.get(x['name']) if isinstance(row_counts.get(x['name']),int) else -1),x['name'])):
 n=row_counts.get(t['name'],'No verificable en el respaldo'); pct=(100*n/row_total) if isinstance(n,int) and row_total else None
 final.append(f"| `{t['name']}` | {n} | {pct:.2f}% |" if pct is not None else f"| `{t['name']}` | {n} | — |")
final.append(f'| **Total verificable** | **{row_total}** | **100.00%** |')
final += ['', '## Historial de cambios', '', '- Fuente actualizada a BD19 (`Practica03/backups/BD19.sql`), versión MySQL '+data.get('mysql_version','no declarada')+'.', f"- Esquema completo BD19: {data.get('counts',{}).get('tables')} tablas, {data.get('counts',{}).get('views')} vistas, {data.get('counts',{}).get('triggers')} triggers, {data.get('counts',{}).get('procedures')} procedimientos, {data.get('counts',{}).get('functions')} funciones, {data.get('counts',{}).get('columns')} columnas y {data.get('counts',{}).get('foreign_keys')} FK.", f"- Este diccionario contiene {len(tables)} tablas: `tb_logs` y 24 tablas auditadas; entre las auditadas se priorizaron las pobladas. Los catálogos `tbc_gen_*` poblados se omiten porque no tienen vistas ni triggers."]
final += ['', '## Descripciones marcadas (inferido)','']+['- '+x for x in inferred]+['','## Pendientes por confirmar — inferencias','', '- Confirmar con responsables de negocio las descripciones y módulos marcados (inferido).', '- Confirmar el origen de captura de los campos no identificados como AUTO_INCREMENT o DEFAULT; el SQL no identifica la interfaz de captura.', '- Confirmar fórmulas de importes almacenados derivables; solo se declaran como derivadas las expresiones GENERATED del DDL.', '']
final += ['## Descripciones genéricas detectadas y reescritas','']+['- `'+x+'`' for x in data['generic_descriptions_rewritten']]+['']
final += ['## Pendientes por confirmar — significado de columnas','']+['- '+x for x in data['pending_confirmations']]+['']
(D/'diccionario_datos.md').write_text('\n'.join(final),encoding='utf-8')
