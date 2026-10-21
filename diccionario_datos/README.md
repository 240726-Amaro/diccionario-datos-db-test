# Diccionario de datos de db_test

Se generaron `diccionario_datos.md`, `diccionario_datos.xlsx`, `diagrama_er.mmd` y `schema.dbml`. `estructura.json` contiene exclusivamente definiciones CREATE y metadatos derivados de columnas, restricciones y triggers; no contiene INSERT.

## Regeneración

Desde la raíz del repositorio, con Python 3:

```powershell
python diccionario_datos\extraer.py
python diccionario_datos\generar.py
python diccionario_datos\generar_modelos.py
python diccionario_datos\validar.py
python diccionario_datos\generar_sitio.py
npm --prefix diccionario_datos install
python diccionario_datos\validar_sitio.py
```

El XLSX incluye autofiltros, encabezado congelado y ajuste de texto. `Resumen estadístico` consolida las clasificaciones por naturaleza, obligatoriedad, origen y llaves. `validar.py` revisa secciones por tabla, descripciones y el total de filas de clasificación en Markdown y XLSX. La generación no requiere librerías Python externas; la validación del sitio necesita Node.js y las dependencias Mermaid y DBML fijadas en `package.json`.
