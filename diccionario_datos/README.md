# Diccionario de datos de BD19

Entregables generados desde el DDL extraído de `Practica03/backups/BD19.sql`: `diccionario_datos.md`, `diccionario_datos.xlsx`, `estructura.json`, `diagrama_er.mmd`, `schema.dbml` y el sitio estático `Practica03/docs`. El diccionario contiene `tb_logs` y 24 tablas auditadas, con prioridad para las pobladas entre las auditadas; incluye sus 24 vistas y 72 triggers. Los tres catálogos poblados `tbc_gen_*` se omiten porque BD19 no les declara vistas ni triggers. `estructura.json` conserva el esquema completo de 29 tablas. No se guardan valores de filas del volcado.

## Regeneración segura

Desde la raíz del repositorio, con Python 3:

```powershell
python Practica03\diccionario_datos\extraer.py
python Practica03\diccionario_datos\contar_filas.py
python Practica03\diccionario_datos\generar.py
python Practica03\diccionario_datos\generar_modelos.py
python Practica03\diccionario_datos\generar_sitio.py
```

`extraer.py` conserva exclusivamente DDL. `contar_filas.py` procesa las tuplas INSERT en streaming y persiste solo conteos agregados. Los conteos pertenecen al respaldo BD19, no a una instancia en vivo.
