"""Extrae definiciones DDL de BD24.sql (respaldo de db_test); los bloques INSERT se descartan."""
import json
import pathlib
import re
from datetime import datetime

def local_stamp(value):
    offset = value.strftime("%z")
    return f"{value:%Y-%m-%d %H:%M:%S} {offset[:3]}:{offset[3:]}"

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "Practica04" / "backups" / "BD24.sql"
OUT = ROOT / "Practica04" / "diccionario_datos"

objects = []
active = None
kind = None

def begin_kind(line):
    s = line.strip()
    if re.search(r"\bCREATE\s+TABLE\b", s, re.I): return "table"
    if re.search(r"\bCREATE\s+VIEW\b", s, re.I): return "view"
    if re.search(r"\bCREATE\b.*?\bTRIGGER\b", s, re.I): return "trigger"
    if re.search(r"\bCREATE\b.*?\bPROCEDURE\b", s, re.I): return "procedure"
    if re.search(r"\bCREATE\b.*?\bFUNCTION\b", s, re.I): return "function"
    return None

def is_complete(k, text, stripped):
    if k == "table": return stripped.endswith(";")
    if k in ("procedure", "function", "trigger"):
        return bool(re.search(r"END\s*(?:\*/)?\s*;;?\s*$", text, re.I))
    return stripped.endswith(";") or stripped.endswith("*/;") or stripped.endswith("*/;;")

def add_object(k, text):
    patterns = {
        "table": r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`([^`]+)",
        "view": r"VIEW\s+`([^`]+)",
        "trigger": r"TRIGGER\s+`([^`]+)",
        "procedure": r"PROCEDURE\s+`([^`]+)",
        "function": r"FUNCTION\s+`([^`]+)",
    }
    match = re.search(patterns[k], text, re.I)
    if match:
        objects.append({"kind": k, "name": match.group(1), "sql": text})

with SRC.open("r", encoding="utf-8", errors="replace") as source:
    for line in source:
        # INSERT lines are deliberately discarded before any buffering or parsing.
        if active is None:
            if line.lstrip().upper().startswith("INSERT INTO "):
                continue
            candidate = begin_kind(line)
            if candidate is None:
                continue
            active, kind = [line], candidate
        else:
            active.append(line)
        blob = "".join(active)
        if is_complete(kind, blob, line.strip()):
            add_object(kind, blob)
            active, kind = None, None

# mysqldump writes temporary CREATE VIEW stubs (SELECT 1) and the real
# definitions later as /*!50001 VIEW ... */ statements. Prefer the final SQL.
source_text = SRC.read_text(encoding="utf-8", errors="replace")
# Las columnas reales de cada vista se toman del stub temporal (`1 AS `col``) antes
# de sustituirlo por la definición final; así las vistas con CTE no exponen alias internos.
stub_columns = {obj["name"]: re.findall(r"\b1\s+AS\s+`([^`]+)`", obj["sql"], re.I)
                for obj in objects if obj["kind"] == "view"}
final_views =re.findall(r"/\*!50001\s+VIEW\s+`([^`]+)`\s+AS\s+(.*?)\*/;", source_text, re.I | re.S)
for name, definition in final_views:
    sql = f"CREATE VIEW `{name}` AS {definition.strip()};"
    existing = next((obj for obj in objects if obj["kind"] == "view" and obj["name"] == name), None)
    if existing:
        existing["sql"] = sql
    else:
        objects.append({"kind": "view", "name": name, "sql": sql})

# Excepción documentada: solo los catálogos de pago se transcriben (ID, código/nombre y
# descripción) porque el diccionario documenta sus valores registrados. Ningún otro INSERT se conserva.
CATALOGS = {"tbc_payment_methods_types": ("ID", "code", "description"), "tbc_payment_methods": ("ID", "name", "description")}
def split_tuples(body):
    rows, row, field, quote, i = [], None, "", None, 0
    while i < len(body):
        ch = body[i]
        if quote:
            if ch == "\\" and i + 1 < len(body): field += body[i+1]; i += 2; continue
            if ch == quote: quote = None
            else: field += ch
        elif ch in "'\"": quote = ch
        elif ch == "(" and row is None: row, field = [], ""
        elif ch == "," and row is not None: row.append(field.strip()); field = ""
        elif ch == ")" and row is not None: row.append(field.strip()); rows.append(row); row = None; field = ""
        elif row is not None: field += ch
        i += 1
    return rows
catalog_values = {}
for name, labels in CATALOGS.items():
    m = re.search(r"^INSERT INTO `" + name + r"` VALUES (.*);\s*$", source_text, re.M)
    if m:
        catalog_values[name] = [dict(zip(labels, (int(r[0]),) + tuple(r[1:3]))) for r in split_tuples(m.group(1))]

# Metadatos de vistas: columnas (del stub), tablas/vistas base reales (sin nombres de CTE)
# y propósito redactado para las vistas de trazabilidad por caso de prueba agregadas en BD24.
VIEW_PURPOSES = {
    "vw_trazabilidad_compras": "Vista consolidada de trazabilidad por orden. Con CTE (`entidades`, `bitacora`, `movimientos`, `ventana`, `inventario`) relaciona cada orden (`tb_orders.ID`) con todas las entidades de su flujo de compra —carrito y sus artículos, usuario, persona, direcciones y sus componentes, subórdenes, artículos de orden, producto-proveedor, método de pago del usuario, pagos, transacciones, reembolsos, envíos, devoluciones y cancelaciones— y une esas claves con los registros de `tb_logs` extrayendo el ID de `description`. Agrega los movimientos de stock de `tb_products` (Update con 'stock') ocurridos dentro de la ventana de logs de la orden. Es la base de las cinco vistas por caso.",
    "vw_trazabilidad_caso1_compra_exitosa": "Caso de prueba 1 (compra exitosa, sin modificaciones): filtra `vw_trazabilidad_compras` a las órdenes con exactamente un pago y cuyo método es 'Tarjeta de débito'. Ordena por `order_ID` y `log_id`.",
    "vw_trazabilidad_caso2_pagos_reclamacion": "Caso de prueba 2 (pagos mensuales, último rechazado, reclamación y reenvío): filtra `vw_trazabilidad_compras` a las órdenes con más de un pago con 'Tarjeta de crédito' y que además tienen una devolución (`tb_returns`) en alguna de sus subórdenes. Ordena por `order_ID` y `log_id`.",
    "vw_trazabilidad_caso3_cancelacion_parcial": "Caso de prueba 3 (cancelación parcial, ajuste y reembolso parcial): filtra `vw_trazabilidad_compras` a las órdenes con una cancelación de suborden que generó reembolso (`tb_refunds.cancellation_ID`) y cuya orden principal no quedó en estado 'Cancelled'. Ordena por `order_ID` y `log_id`.",
    "vw_trazabilidad_caso4_punto_recoleccion": "Caso de prueba 4 (mismo proveedor, entrega en punto de recolección): filtra `vw_trazabilidad_compras` a las órdenes con un envío cuyo campo `notes` menciona 'punto de recolección'. Ordena por `order_ID` y `log_id`.",
    "vw_trazabilidad_caso5_falta_inventario": "Caso de prueba 5 (compra fallida por falta de inventario): filtra `vw_trazabilidad_compras` a las órdenes en estado 'Cancelled' con una cancelación cuyo motivo menciona 'inventario'. Ordena por `order_ID` y `log_id`.",
}
known_relations = {o["name"] for o in objects if o["kind"] in ("table", "view")}
view_meta = {}
for obj in objects:
    if obj["kind"] != "view":
        continue
    refs = re.findall(r"\b(?:from|join)\s+\(*`([^`]+)`", obj["sql"], re.I)
    refs += re.findall(r"'((?:tb_|tbc_|tbd_)\w+)'", obj["sql"])
    meta = {"columns": stub_columns.get(obj["name"], []),
            "bases": [r for r in dict.fromkeys(refs) if r in known_relations and r != obj["name"]]}
    if obj["name"] in VIEW_PURPOSES:
        meta["purpose"] = VIEW_PURPOSES[obj["name"]]
    view_meta[obj["name"]] = meta

counts = {k: sum(item["kind"] == k for item in objects)
          for k in ("table", "view", "trigger", "procedure", "function")}
payload = {
    "database": "db_test",
    "backup": "BD24",
    "catalog_values": catalog_values,
    "mysql_version": "8.0.45",
    "source": "Practica04/backups/BD24.sql",
    "source_date": datetime.fromtimestamp(SRC.stat().st_mtime).astimezone().date().isoformat(),
    "source_modified": local_stamp(datetime.fromtimestamp(SRC.stat().st_mtime).astimezone()),
    "extraction_scope": "CREATE TABLE (incluye índices, claves y CHECK declarados en tabla), CREATE/ALTER TABLE y CREATE INDEX si existen, además de VIEW/TRIGGER/PROCEDURE/FUNCTION. INSERT INTO se descarta durante extracción de esquema.",
    "counts": counts,
    "view_meta": view_meta,
    "objects": objects,
}
(OUT / "estructura.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(counts, ensure_ascii=False))
