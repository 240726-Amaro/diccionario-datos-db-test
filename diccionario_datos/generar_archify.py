"""Genera el candidato Archify (ERD) de DB Test a partir de estructura.json (BD23).

Uso, desde la raíz del repositorio:
    python Practica04/diccionario_datos/generar_archify.py <ruta/candidate.json>
    node <archify>/bin/archify.mjs finalize erd <ruta/candidate.json> Practica04/diagrama/db-test-archify.html --quality standard --json
"""
import json
import pathlib
import re
import sys

D = pathlib.Path(__file__).resolve().parent
DATA = json.loads((D / 'estructura.json').read_text(encoding='utf-8'))
TABLES = {o['name']: o for o in DATA['objects'] if o['kind'] == 'table'}

# Un dominio funcional por columna del lienzo (lectura de izquierda a derecha);
# tb_logs (sin FK) ocupa la celda libre bajo 'Carrito y órdenes' para no añadir otra columna.
PLACE = {'Auditoría': (2, 5)}
DOMAINS = [
    ('Usuarios', ['tb_users', 'tb_people', 'tb_user_addresses', 'tbd_address_components']),
    ('Productos', ['tb_products', 'tbc_categories', 'tbd_products_categories', 'tbd_products_users_providers', 'tbd_users_wishlist_products']),
    ('Carrito y órdenes', ['tb_carts', 'tbd_carts_items', 'tb_orders', 'tb_buyer_orders', 'tbd_order_items']),
    ('Pagos', ['tbc_payment_methods_types', 'tbd_user_payment_methods', 'tbc_payment_methods', 'tb_payments', 'tb_payment_transaction']),
    ('Postventa', ['tb_shipments', 'tb_returns', 'tbd_return_items', 'tb_order_cancellations', 'tbd_cancellation_items', 'tb_refunds']),
    ('Auditoría', ['tb_logs']),
]
COLS = {'Usuarios': 0, 'Productos': 1, 'Carrito y órdenes': 2, 'Pagos': 3, 'Postventa': 4}
assert sorted(n for _, ns in DOMAINS for n in ns) == sorted(TABLES), 'Cada tabla de BD23 debe tener dominio'

LABELS = {
    ('tb_orders', 'tb_carts'): '1:1 se genera de',
    ('tb_buyer_orders', 'tb_orders'): 'suborden por vendedor',
}


def ident(name):
    return re.sub(r'[^A-Za-z0-9_]', '_', name)


def parse(table):
    cols, cons = [], []
    for raw in table['sql'].splitlines():
        line = raw.strip().rstrip(',')
        m = re.match(r'`([^`]+)`\s+(.+)', line)
        if m:
            typ = re.match(r'(\w+(?:\s*\([^)]*\))?(?:\s+unsigned)?)', m.group(2), re.I).group(1)
            cols.append((m.group(1), typ, 'NOT NULL' not in m.group(2).upper()))
        elif re.match(r'(PRIMARY KEY|UNIQUE KEY|KEY|CONSTRAINT)', line, re.I):
            cons.append(line)
    return cols, cons


def short_type(typ):
    # Los ENUM se resumen como enum(n) para que la tabla siga legible; sus valores
    # completos están en la tarjeta "Dominios ENUM" y en el diccionario.
    if typ.lower().startswith('enum'):
        return 'enum(%d)' % len(re.findall(r"'([^']*)'", typ))
    return typ


entities, relationships, self_refs = [], [], []
for domain, names in DOMAINS:
    col_idx, row0 = PLACE.get(domain, (COLS.get(domain), 0))
    for row_idx, name in enumerate(names, row0):
        cols, cons = parse(TABLES[name])
        pk = next((re.findall(r'`([^`]+)`', z) for z in cons if z.startswith('PRIMARY KEY')), [])
        uks = [re.findall(r'`([^`]+)`', z)[1:] for z in cons if z.startswith('UNIQUE KEY')]
        fks = []
        for z in cons:
            m = re.search(r'CONSTRAINT\s+`([^`]+)`\s+FOREIGN KEY\s*\(([^)]*)\)\s+REFERENCES\s+`([^`]+)`\s*\(([^)]*)\)', z, re.I)
            if m:
                fks.append((m.group(1), re.findall(r'`([^`]+)`', m.group(2)), m.group(3), re.findall(r'`([^`]+)`', m.group(4))))
        attrs, widest = [], len(name) + 4
        for cname, typ, nullable in cols:
            keys = []
            if cname in pk:
                keys.append('pk')
            ref = next((f'{ident(parent)}.{pcols[lcols.index(cname)]}' for _, lcols, parent, pcols in fks if cname in lcols), None)
            if ref:
                keys.append('fk')
            if any(cname in u for u in uks):
                keys.append('uk')
            attr = {'name': cname, 'type': short_type(typ)}
            if keys:
                attr['key'] = keys[0] if len(keys) == 1 else keys
            if ref:
                attr['references'] = ref
            attrs.append(attr)
            widest = max(widest, len(cname) + len(attr['type']))
        entities.append({'id': ident(name), 'label': name, 'tag': domain, 'row': row_idx, 'col': col_idx,
                         'width': max(200, int(widest * 6.9) + 28 + (50 if any(isinstance(a.get('key'), list) for a in attrs) else 30)), 'attributes': attrs})
        nullable = {c: n for c, _, n in cols}
        for fk_name, lcols, parent, _ in fks:
            if parent == name:  # Archify no dibuja autorreferencias; se explican en una tarjeta.
                self_refs.append(f"{name}.{', '.join(lcols)} → {name} ({fk_name}): jerarquía en la misma tabla.")
                continue
            unique_fk = sorted(lcols) == sorted(pk) or any(sorted(lcols) == sorted(u) for u in uks)
            rel = {'id': ident(fk_name), 'from': ident(name), 'to': ident(parent),
                   'fromCardinality': 'one' if unique_fk else 'many', 'fromOptional': True,
                   'toCardinality': 'one'}
            if any(nullable[c] for c in lcols):
                rel['toOptional'] = True
            if set(lcols) <= set(pk):
                rel['identifying'] = True
            if (name, parent) in LABELS:
                rel['label'] = LABELS[(name, parent)]
            relationships.append(rel)

enum_lines = []
for name, t in TABLES.items():
    for cname, typ, _ in parse(t)[0]:
        if typ.lower().startswith('enum'):
            enum_lines.append(f"{name}.{cname}: " + ', '.join(re.findall(r"'([^']*)'", typ)))

candidate = {
    'schema_version': 1,
    'diagram_type': 'erd',
    'meta': {
        'title': 'DB Test · esquema relacional (BD23)',
        'locale': 'es',
        'output': 'Practica04/diagrama/db-test-archify.html',
        'quality_profile': 'standard',
        'views': [
            {'id': 'compra', 'label': 'Flujo de compra', 'focus': ['tb_carts', 'tbd_carts_items', 'tb_orders', 'tb_buyer_orders', 'tbd_order_items'],
             'note': 'Carrito → orden (1:1 por cart_ID UNIQUE) → subórdenes por vendedor (order_ID + seller_ID únicos) → líneas.'},
            {'id': 'pago', 'label': 'Pago de una orden', 'focus': ['tb_orders', 'tb_payments', 'tb_payment_transaction', 'tbc_payment_methods', 'tbd_user_payment_methods', 'tbc_payment_methods_types'],
             'note': 'sp_pay_order crea un pago y una transacción por cuota; meses solo con CREDIT_CARD.'},
            {'id': 'postventa', 'label': 'Envíos y postventa', 'focus': ['tb_buyer_orders', 'tb_shipments', 'tb_returns', 'tbd_return_items', 'tb_order_cancellations', 'tbd_cancellation_items', 'tb_refunds'],
             'note': 'Envíos, devoluciones y cancelaciones cuelgan de la suborden del vendedor.'},
            {'id': 'usuarios', 'label': 'Usuarios', 'focus': ['tb_users', 'tb_people', 'tb_user_addresses', 'tbd_address_components', 'tb_carts'],
             'note': 'Un usuario puede tener varios carritos (idx_cart_user ya no es único).'},
        ],
    },
    'layout': {'mode': 'grid', 'gapX': 64, 'gapY': 36},
    'entities': entities,
    'relationships': relationships,
    'cards': [
        {'dot': 'cyan', 'title': 'Cambios BD23', 'items': [
            'tb_orders.cart_ID: NOT NULL, UNIQUE, FK → tb_carts.ID (1:1 carrito-orden).',
            'tb_buyer_orders.order_ID: FK → tb_orders.ID; UNIQUE (order_ID, seller_ID).',
            'tb_carts: uk_cart_user pasa a índice idx_cart_user (varios carritos por usuario).',
            "tb_shipments: nueva columna notes; shipment_status agrega 'Failed attempt' y 'At pickup point'.",
            'Eliminados: tbc_gen_country_profile, tbc_gen_family_names, tbc_gen_given_names.']},
        {'dot': 'amber', 'title': 'Dominios ENUM', 'items': enum_lines},
        {'dot': 'emerald', 'title': 'Cómo leer', 'items': [
            'Cada columna del lienzo es un dominio funcional; tb_logs recibe las escrituras de los 75 triggers sin FK.',
            'tbd_products_categories.category_ID no declara FK a tbc_categories, por eso no hay línea entre ambas.',
            'Los ENUM se muestran como enum(n); sus valores están en la tarjeta Dominios ENUM.']},
        {'dot': 'violet', 'title': 'Autorreferencias (sin línea)', 'items': self_refs},
    ],
}
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'candidate.json')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'{out}: {len(entities)} tablas, {len(relationships)} relaciones')
