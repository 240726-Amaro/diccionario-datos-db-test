from html.parser import HTMLParser
from pathlib import Path
import json
import re
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SOURCE = ROOT / "diccionario_datos" / "estructura.json"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src"):
            value = attrs.get(key, "")
            if value and not value.startswith(("https://", "http://", "#", "mailto:")):
                self.targets.append(value.split("#", 1)[0])


data = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
expected = {"tables": 29, "views": 25, "triggers": 75, "procedures": 8, "functions": 15}
objects = data.get("objects", [])
actual = {
    "tables": sum(o.get("kind") == "table" for o in objects),
    "views": sum(o.get("kind") == "view" for o in objects),
    "triggers": sum(o.get("kind") == "trigger" for o in objects),
    "procedures": sum(o.get("kind") == "procedure" for o in objects),
    "functions": sum(o.get("kind") == "function" for o in objects),
}
assert actual == expected, (actual, expected)

required = [
    DOCS / "index.html",
    DOCS / ".nojekyll",
    DOCS / "assets" / "site.css",
    DOCS / "assets" / "site.js",
    DOCS / "descargas" / "diccionario_datos.xlsx",
    DOCS / "descargas" / "diccionario_datos.md",
    DOCS / "descargas" / "schema.dbml",
    DOCS / "descargas" / "prompts_utilizados.md",
    DOCS / "diagrama" / "db-test-archify.html",
]
assert all(path.is_file() for path in required), [str(p) for p in required if not p.is_file()]

with ZipFile(DOCS / "descargas" / "diccionario_datos.xlsx") as book:
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    workbook = ET.fromstring(book.read("xl/workbook.xml"))
    sheet_names = [s.attrib["name"] for s in workbook.findall("m:sheets/m:sheet", ns)]
    assert "Volumen_datos" in sheet_names and "Historial_cambios" in sheet_names and "Convenciones" in sheet_names, sheet_names
    worksheet_checks = []
    for index in range(1, len(sheet_names) + 1):
        root = ET.fromstring(book.read(f"xl/worksheets/sheet{index}.xml"))
        worksheet_checks.append(root.find("m:autoFilter", ns) is not None and root.find("m:sheetViews/m:sheetView/m:pane", ns) is not None)
    assert all(worksheet_checks), "Falta autofiltro o encabezado congelado en alguna hoja"

html = (DOCS / "index.html").read_text(encoding="utf-8")
parser = Links()
parser.feed(html)
broken = []
for value in parser.targets:
    if value.startswith("/"):
        broken.append(f"absolute:{value}")
    elif not (DOCS / value).exists():
        broken.append(f"missing:{value}")
assert not broken, broken
volume_total = f"{sum(v for v in data.get('row_counts', {}).values() if isinstance(v,int)):,}"
for marker in ('id="volumen"', 'Volumen de datos', volume_total, 'Historial de cambios', 'Procedimientos'):
    assert marker in html or marker in (DOCS / "descargas" / "diccionario_datos.md").read_text(encoding="utf-8"), marker

patterns = {"@" + "utxicotepec": 0, "@" + "example.": 0, "$" + "2": 0}
for path in DOCS.rglob("*"):
    if not path.is_file():
        continue
    if path.suffix.lower() == ".xlsx":
        try:
            with ZipFile(path) as archive:
                contents = [archive.read(name).decode("utf-8", errors="ignore")
                            for name in archive.namelist() if name.endswith(".xml")]
        except BadZipFile:
            contents = []
    else:
        contents = [path.read_bytes().decode("utf-8", errors="ignore")]
    for content in contents:
        for pattern in patterns:
            patterns[pattern] += content.count(pattern)
assert not any(patterns.values()), patterns

print(f"Conteos: {actual}")
print(f"Archivos requeridos: {len(required)}/{len(required)}")
print(f"Rutas locales válidas: {len(parser.targets)}; rutas absolutas o faltantes: 0")
print("Patrones sensibles: " + ", ".join(f"{key}={value}" for key,value in patterns.items()))
