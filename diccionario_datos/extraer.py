"""Extrae definiciones DDL de BD23.sql (respaldo de db_test); los bloques INSERT se descartan."""
import json
import pathlib
import re
from datetime import datetime

def local_stamp(value):
    offset = value.strftime("%z")
    return f"{value:%Y-%m-%d %H:%M:%S} {offset[:3]}:{offset[3:]}"

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "Practica04" / "backups" / "BD23.sql"
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
final_views = re.findall(r"/\*!50001\s+VIEW\s+`([^`]+)`\s+AS\s+(.*?)\*/;", source_text, re.I | re.S)
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

counts = {k: sum(item["kind"] == k for item in objects)
          for k in ("table", "view", "trigger", "procedure", "function")}
payload = {
    "database": "db_test",
    "backup": "BD23",
    "catalog_values": catalog_values,
    "mysql_version": "8.0.45",
    "source": "Practica04/backups/BD23.sql",
    "source_date": datetime.fromtimestamp(SRC.stat().st_mtime).astimezone().date().isoformat(),
    "source_modified": local_stamp(datetime.fromtimestamp(SRC.stat().st_mtime).astimezone()),
    "extraction_scope": "CREATE TABLE (incluye índices, claves y CHECK declarados en tabla), CREATE/ALTER TABLE y CREATE INDEX si existen, además de VIEW/TRIGGER/PROCEDURE/FUNCTION. INSERT INTO se descarta durante extracción de esquema.",
    "counts": counts,
    "objects": objects,
}
(OUT / "estructura.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(counts, ensure_ascii=False))
