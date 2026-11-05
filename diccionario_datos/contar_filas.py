"""Cuenta tuplas de INSERT en streaming; solo persiste totales por tabla."""
import json
import pathlib
import re
from datetime import datetime

def local_stamp(value):
    offset = value.strftime("%z")
    return f"{value:%Y-%m-%d %H:%M:%S} {offset[:3]}:{offset[3:]}"

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Practica03" / "backups" / "BD19.sql"
OUT = ROOT / "Practica03" / "diccionario_datos" / "estructura.json"
counts = {}
table = None
in_insert = False
values_started = False
quote = None
escaped = False
depth = 0
DELIMITER = re.compile(r"""['"`();\\]""")

def take_header(line):
    match = re.match(r"\s*INSERT\s+INTO\s+`([\w$]+)`", line, re.I)
    return match.group(1) if match else None

with SOURCE.open("r", encoding="utf-8", errors="replace") as source:
    for line in source:
        prefix = line.lstrip()[:500]
        if not in_insert and prefix.startswith(("CREATE", "/*!")) and re.search(r"\bVIEW\b", prefix, re.I):
            # In mysqldump, view/trigger/routine DDL follows the table data section.
            break
        if not in_insert:
            if not line.lstrip().upper().startswith("INSERT INTO `"):
                continue
            table = take_header(line)
            if table is None:
                continue
            counts.setdefault(table, 0)
            in_insert = True
            values_started = False
            quote = None
            escaped = False
            depth = 0
        start = 0
        if not values_started:
            marker = re.search(r"\bVALUES\b", line, re.I)
            if not marker: continue
            values_started = True
            start = marker.end()
        # The regex engine locates only SQL delimiters; data text stays opaque.
        escaped_at = None
        skip_quote = False
        for token_match in DELIMITER.finditer(line, start):
            pos = token_match.start(); token = token_match.group(0)
            if escaped_at is not None:
                if pos == escaped_at+1: escaped_at = None; continue
                escaped_at = None
            if quote:
                if token == "\\": escaped_at = pos
                elif token == quote:
                    if skip_quote: skip_quote = False
                    elif pos+1 < len(line) and line[pos+1] == quote: skip_quote = True
                    else: quote = None
                continue
            if token in ("'", '"', '`'):
                quote = token; continue
            if token == "(":
                if depth == 0: counts[table] += 1
                depth += 1
            elif token == ")" and depth: depth -= 1
            elif token == ";" and depth == 0:
                in_insert = False; table = None; values_started = False; break

data = json.loads(OUT.read_text(encoding="utf-8"))
for obj in data.get("objects", []):
    if obj.get("kind") == "table": counts.setdefault(obj["name"], "No verificable en el respaldo")
data["row_counts"] = counts
table_order = [obj["name"] for obj in data.get("objects", []) if obj.get("kind") == "table"]
trigger_targets = {
    match.group(1)
    for obj in data.get("objects", []) if obj.get("kind") == "trigger"
    for match in [re.search(r"\bON\s+`([^`]+)`", obj.get("sql", ""), re.I)]
    if match
}
audited = [name for name in table_order if name in trigger_targets]
populated_audited = [name for name in audited if isinstance(counts.get(name), int) and counts[name] > 0]
empty_audited = [name for name in audited if name not in populated_audited]
logs = [name for name in table_order if name == "tb_logs"]
selected = set(populated_audited + empty_audited[:max(0, 24-len(populated_audited))] + logs)
data["dictionary_tables"] = [
    name for name in table_order if name in selected and isinstance(counts.get(name), int) and counts[name] > 0
] + [name for name in table_order if name in selected and not (isinstance(counts.get(name), int) and counts[name] > 0)]
counted_at = local_stamp(datetime.now().astimezone())
data["row_counted_at"] = counted_at
data["row_count_source"] = f"Conteo streaming de filas reales en sentencias INSERT de BD19.sql; {counted_at}; corresponde al respaldo, no a la instancia en vivo."
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
verified = [value for value in counts.values() if isinstance(value, int)]
print(json.dumps({"tablas_con_insert": len(verified), "total_filas_verificables": sum(verified),
                  "tablas_sin_insert": sum(value == "No verificable en el respaldo" for value in counts.values())}, ensure_ascii=False))
