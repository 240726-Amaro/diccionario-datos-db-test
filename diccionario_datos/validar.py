import json, re, zipfile, pathlib, xml.etree.ElementTree as ET, sys

BASE = pathlib.Path(__file__).parent
MD = (BASE / 'diccionario_datos.md').read_text(encoding='utf-8')
SCHEMA = json.loads((BASE / 'estructura.json').read_text(encoding='utf-8'))
TABLES = [o['name'] for o in SCHEMA['objects'] if o['kind'] == 'table']
EXPECTED_COLUMNS = sum(len(o.get('columns', [])) for o in SCHEMA['objects'] if o['kind'] == 'table')
TABLE_OBJECTS = [o for o in SCHEMA['objects'] if o['kind'] == 'table']

# Markdown: each table needs description, notation, technical and classification tables.
sections = {}
for i, name in enumerate(TABLES):
    marker = f'### `{name}`'
    start = MD.find(marker)
    if start < 0:
        sections[name] = ''
        continue
    next_starts = [MD.find(f'### `{other}`', start + len(marker)) for other in TABLES]
    next_starts = [p for p in next_starts if p >= 0]
    end = min(next_starts) if next_starts else MD.find('\n## Vistas', start)
    if end < 0:
        end = len(MD)
    sections[name] = MD[start:end]

md_missing_sections = []
md_bad_descriptions = []
md_class_rows = 0
for name, section in sections.items():
    has_desc = '**Descripción general detallada:**' in section and len(re.findall(r'^  - ', section, re.M)) >= 5
    has_notation = '**Notación formal:**' in section
    has_technical = '**Tabla técnica de columnas**' in section
    has_classification = '**Tabla de clasificación de columnas**' in section
    if not all((has_desc, has_notation, has_technical, has_classification)):
        md_missing_sections.append(name)
    if has_classification:
        block = section.split('**Tabla de clasificación de columnas**', 1)[1]
        rows = [line for line in block.splitlines() if line.startswith('| `')]
        md_class_rows += len(rows)
        for row in rows:
            cells = [x.strip() for x in row.strip('|').split('|')]
            if len(cells) < 9 or 'No especificado' in cells[-1]:
                md_bad_descriptions.append(name)
    tech_block = section.split('**Tabla técnica de columnas**', 1)[1].split('**Restricciones e índices del DDL**', 1)[0] if has_technical else ''
    for row in [line for line in tech_block.splitlines() if line.startswith('| ') and not line.startswith('|---') and not line.startswith('| #')]:
        cells = [x.strip() for x in row.strip('|').split('|')]
        if len(cells) >= 9 and 'No especificado' in cells[-1]:
            md_bad_descriptions.append(name)

# XLSX: read workbook names and worksheet XML without third-party dependencies.
with zipfile.ZipFile(BASE / 'diccionario_datos.xlsx') as book:
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    workbook = ET.fromstring(book.read('xl/workbook.xml'))
    names = [s.attrib['name'] for s in workbook.find('m:sheets', ns)]
    sheet_xml = [ET.fromstring(book.read(f'xl/worksheets/sheet{i}.xml')) for i in range(1, len(names) + 1)]
    def sheet_rows(root):
        result = []
        for row in root.findall('.//m:sheetData/m:row', ns):
            vals = []
            for cell in row.findall('m:c', ns):
                text = ''.join((x.text or '') for x in cell.findall('.//m:t', ns))
                vals.append(text)
            result.append(vals)
        return result
    rows_by_name = {n: sheet_rows(x) for n, x in zip(names, sheet_xml)}
    tab_rows = rows_by_name.get('Tablas', [])
    col_rows = rows_by_name.get('Columnas', [])

xlsx_missing_tables = [name for name in TABLES if not any(row and row[0] == name for row in tab_rows[1:])]
xlsx_bad_table_rows = []
for row in tab_rows[1:]:
    if row and row[0] in TABLES:
        # Table sheet columns: name, prefix, module, engine, charset, collation, detailed description, formal notation.
        if len(row) < 8 or not row[6].strip() or not row[7].strip() or 'No especificado' in row[6]:
            xlsx_bad_table_rows.append(row[0])
xlsx_column_count = max(0, len(col_rows) - 1)
xlsx_bad_column_descriptions = []
for row in col_rows[1:]:
    if len(row) < 17 or not row[16].strip() or 'No especificado' in row[16]:
        xlsx_bad_column_descriptions.append(row[0] + '.' + row[2] if len(row) > 2 else 'fila sin identificador')

# Classification rules requested for identifiers, formal notation and hashes.
bad_identifier_nature = []
bad_formal_notation = []
bad_auto_increment_domain = []
password_hash_ok = False
bad_fk_domains = []
bad_date_domains = []
generic_descriptions = []
descriptions_with_restrictions = []
for table in TABLE_OBJECTS:
    colmap = {c['name']: c for c in table.get('columns', [])}
    for line in table['sql'].splitlines():
        fk = re.search(r'FOREIGN KEY\s*\(([^)]*)\)\s+REFERENCES\s+`([^`]+)`\s*\(([^)]*)\)(.*)', line, re.I)
        if fk:
            local = re.findall(r'`([^`]+)`', fk.group(1))
            remote = re.findall(r'`([^`]+)`', fk.group(3))
            delete = re.search(r'ON\s+DELETE\s+(CASCADE|RESTRICT|NO ACTION|SET NULL|SET DEFAULT)', fk.group(4), re.I)
            rule = delete.group(1).lower() if delete else 'sin acción'
            for lc, rc in zip(local, remote):
                expected = f"{lc} ∈ {{{fk.group(2)}.{rc}}}; ON DELETE {rule}"
                if lc not in colmap or expected not in colmap[lc]['classification']['dominio']:
                    bad_fk_domains.append(table['name'] + '.' + lc)
    for column in table.get('columns', []):
        name = column['name'].lower()
        q = column['classification']
        description = q['descripcion_detallada']
        if ' para describir o relacionar ese registro' in description:
            generic_descriptions.append(table['name'] + '.' + column['name'])
        if 'Restricciones:' in description:
            descriptions_with_restrictions.append(table['name'] + '.' + column['name'])
        if (name == 'id' or name.endswith('_id') or name.startswith('id_')) and q['naturaleza'] != 'Cualitativa nominal':
            bad_identifier_nature.append(table['name'] + '.' + column['name'])
        formal = q['composicion_formal']
        if '*' in formal or re.search(r'\b(int|varchar|char|enum|decimal|datetime|timestamp|text|bigint|tinyint)\b', formal, re.I):
            bad_formal_notation.append(table['name'] + '.' + column['name'])
        if 'AUTO_INCREMENT' in column.get('extra', '').upper() and ('ℤ⁺' not in q['dominio'] or '∪ {0}' in q['dominio']):
            bad_auto_increment_domain.append(table['name'] + '.' + column['name'])
        if table['name'] == 'tb_users' and name == 'password':
            password_hash_ok = 'hash' in q['descripcion_detallada'].lower()
        if column['type'].lower() in ('date', 'datetime', 'timestamp', 'time', 'year'):
            if f"∈ {column['type'].upper()}; default " not in q['dominio']:
                bad_date_domains.append(table['name'] + '.' + column['name'])

result = {
    'markdown': {
        'tablas': len(TABLES),
        'tablas_con_secciones_1_a_4': len(TABLES) - len(md_missing_sections),
        'tablas_faltantes_secciones': md_missing_sections,
        'filas_clasificacion': md_class_rows,
        'filas_esperadas': EXPECTED_COLUMNS,
        'celdas_descripcion_invalidas': sorted(set(md_bad_descriptions)),
    },
    'xlsx': {
        'hojas': names,
        'tablas_faltantes': xlsx_missing_tables,
        'filas_clasificacion': xlsx_column_count,
        'filas_esperadas': EXPECTED_COLUMNS,
        'tablas_con_descripcion_o_notacion_invalida': xlsx_bad_table_rows,
        'descripciones_columna_invalidas': xlsx_bad_column_descriptions,
    },
    'clasificacion_solicitada': {
        'identificadores_cualitativos_nominales': not bad_identifier_nature,
        'composicion_sin_tipos_sql_ni_asteriscos': not bad_formal_notation,
        'autoincrement_usa_Z_mas': not bad_auto_increment_domain,
        'tb_users_password_indica_hash': password_hash_ok,
        'dominios_FK_incluyen_destino_y_ON_DELETE': not bad_fk_domains,
        'dominios_fecha_incluyen_tipo_y_default': not bad_date_domains,
        'descripciones_sin_plantilla_generica': not generic_descriptions,
        'descripciones_sin_texto_de_restricciones': not descriptions_with_restrictions,
        'descripciones_genericas': generic_descriptions,
        'descripciones_con_restricciones': descriptions_with_restrictions,
        'errores_identificadores': bad_identifier_nature,
        'errores_composicion': bad_formal_notation,
        'errores_autoincrement': bad_auto_increment_domain,
        'errores_dominio_FK': bad_fk_domains,
        'errores_dominio_fecha': bad_date_domains,
    },
    'resultado': 'OK' if not (md_missing_sections or md_bad_descriptions or xlsx_missing_tables or xlsx_bad_table_rows or xlsx_bad_column_descriptions or md_class_rows != EXPECTED_COLUMNS or xlsx_column_count != EXPECTED_COLUMNS or bad_identifier_nature or bad_formal_notation or bad_auto_increment_domain or not password_hash_ok or bad_fk_domains or bad_date_domains or generic_descriptions or descriptions_with_restrictions) else 'FALLÓ'
}
print(json.dumps(result, ensure_ascii=False, indent=2))
if result['resultado'] != 'OK':
    sys.exit(1)
