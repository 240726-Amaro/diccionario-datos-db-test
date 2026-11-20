# Diccionario de datos — DB Test (BD24)

Entregables generados desde el DDL extraído de `Practica04/backups/BD24.sql` (base `db_test`): `diccionario_datos.md`, `diccionario_datos.xlsx`, `estructura.json`, `diagrama_er.mmd`, `schema.dbml`, el diagrama Archify `Practica04/diagrama/db-test-archify.html` y el sitio estático `Practica04/docs`. El diccionario documenta las 26 tablas (`tb_logs` y 25 tablas auditadas), sus 31 vistas (25 por tabla, `vw_trazabilidad_compras` y 5 vistas por caso de prueba), 75 triggers, 6 procedimientos y 10 funciones. Única excepción a “no guardar valores de filas”: se transcriben ID, código/nombre y descripción de los catálogos `tbc_payment_methods_types` y `tbc_payment_methods`.

El diagrama Archify se genera aparte (sigue reflejando BD23; BD24 no cambia tablas ni relaciones): `python Practica04\diccionario_datos\generar_archify.py` escribe el candidato y luego se ejecuta `archify finalize erd`.

## Regeneración segura

Desde la raíz del repositorio, con Python 3:

```powershell
python Practica04\diccionario_datos\extraer.py
python Practica04\diccionario_datos\contar_filas.py
python Practica04\diccionario_datos\generar.py
python Practica04\diccionario_datos\generar_modelos.py
python Practica04\diccionario_datos\generar_sitio.py
```

`extraer.py` conserva exclusivamente DDL. `contar_filas.py` procesa las tuplas INSERT en streaming y persiste solo conteos agregados. Los conteos pertenecen al respaldo BD24, no a una instancia en vivo.
