from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess
import html as html_lib
from zipfile import BadZipFile, ZipFile


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
expected = {"tables": 20, "views": 18, "triggers": 57, "procedures": 3}
objects = data.get("objects", [])
actual = {
    "tables": sum(o.get("kind") == "table" for o in objects),
    "views": sum(o.get("kind") == "view" for o in objects),
    "triggers": sum(o.get("kind") == "trigger" for o in objects),
    "procedures": sum(o.get("kind") == "procedure" for o in objects),
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
]
assert all(path.is_file() for path in required), [str(p) for p in required if not p.is_file()]

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

# Parse diagrams with Mermaid's own parser so the validation follows the same
# grammar as the generated ER diagrams. Install the pinned parsers with
# `npm --prefix diccionario_datos install` before running this validator.
mermaid_modules = [html_lib.unescape(x) for x in re.findall(
    r'<pre\s+class="mermaid">([\s\S]*?)</pre>', html
)]
full_mmd = (ROOT / "diccionario_datos" / "diagrama_er.mmd").read_text(encoding="utf-8")
node_validation = r'''(async () => {
  const fs = require('node:fs');
  const { createRequire } = require('node:module');
  const { pathToFileURL } = require('node:url');
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  const localRequire = createRequire(input.packagePath);
  const mermaid = await import(pathToFileURL(localRequire.resolve('mermaid')));
  const parseMermaid = mermaid.default.parse;
  const errors = [];
  for (let i = 0; i < input.modules.length; i++) {
    try { await parseMermaid(input.modules[i]); console.log(`Mermaid módulo ${i + 1}: OK`); }
  catch (e) { errors.push(`Módulo ${i + 1}: ${e.message || e}`); console.log(`Mermaid módulo ${i + 1}: ERROR`); }
  }
  try { await parseMermaid(input.full); console.log('Mermaid archivo completo: OK'); }
  catch (e) { errors.push(`Archivo completo: ${e.message || e}`); console.log('Mermaid archivo completo: ERROR'); }
  const dbml = await import(pathToFileURL(localRequire.resolve('@dbml/core')));
  const parser = dbml.Parser || dbml.default?.Parser;
  try { parser.parse(input.dbml, 'dbml'); console.log('DBML schema.dbml: OK'); }
  catch (e) { errors.push(`schema.dbml: ${e.message || e.diags?.map(d => d.message).join('; ') || e}`); console.log('DBML schema.dbml: ERROR'); }
  if (errors.length) { console.error(errors.join('\n')); process.exitCode = 1; }
})().catch(e => { console.error(`No se pudo cargar Mermaid/@dbml/core: ${e.message}`); process.exit(2); });'''
dbml_text = (ROOT / "diccionario_datos" / "schema.dbml").read_text(encoding="utf-8")
validation = subprocess.run(
    ["node", "-e", node_validation],
    input=json.dumps({"modules": mermaid_modules, "full": full_mmd, "dbml": dbml_text,
                      "packagePath": str(SOURCE.parent / "package.json")}),
    text=True, capture_output=True,
)
print(validation.stdout, end="")
if validation.returncode:
    raise AssertionError(validation.stderr or "La validación de parsers falló")

patterns = {"@utxicotepec": 0, "$2": 0}
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
print(f"Patrones sensibles: @utxicotepec={patterns['@utxicotepec']}, $2={patterns['$2']}")
