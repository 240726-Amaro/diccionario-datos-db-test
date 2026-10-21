import re,json,pathlib
src=pathlib.Path('Practica03/backups/BD13.sql'); out=pathlib.Path('diccionario_datos')
lines=src.open(encoding='utf-8',errors='replace')
objs=[]; active=None; kind=None
for line in lines:
 if line.lstrip().upper().startswith('INSERT INTO '):
  continue
 s=line.strip()
 if active is None:
  if re.search(r'CREATE TABLE\b',s,re.I): kind='table'
  elif re.search(r'CREATE\*/.*TRIGGER\b',s,re.I): kind='trigger'
  elif re.search(r'CREATE VIEW\b',s,re.I): kind='view'
  elif re.search(r'CREATE DEFINER=.* PROCEDURE\b',s,re.I): kind='procedure'
  else: continue
  active=[line]
 else: active.append(line)
 if active:
  blob=''.join(active)
  done=(kind=='table' and s.endswith(';')) or (kind=='trigger' and 'END */;;' in s) or (kind=='view' and s.endswith('*/;')) or (kind=='procedure' and s.endswith(';;'))
  if done:
   name=None
   if kind=='table': m=re.search(r'CREATE TABLE\s+`([^`]+)',blob,re.I)
   elif kind=='trigger': m=re.search(r'TRIGGER\s+`([^`]+)',blob,re.I)
   elif kind=='view': m=re.search(r'VIEW\s+`([^`]+)',blob,re.I)
   else: m=re.search(r'PROCEDURE\s+`([^`]+)',blob,re.I)
   name=m.group(1) if m else '?'; objs.append({'kind':kind,'name':name,'sql':blob}); active=None
(out/'estructura.json').write_text(json.dumps({'database':'db_test','mysql_version':'8.0.36','extraction_scope':'Solo CREATE TABLE/VIEW/TRIGGER/PROCEDURE; se omiten INSERT INTO. Los metadatos de clasificación se agregan al ejecutar generar.py.','objects':objs},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:sum(x['kind']==k for x in objs) for k in ('table','view','trigger','procedure')}))
