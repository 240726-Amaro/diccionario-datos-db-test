# Prompts utilizados

Registro para incluir en el PDF de entrega.

## Actualización de diccionario y diagrama con el respaldo BD16

> Autorizo que uses el respaldo Practica03/backups/BD16.sql como fuente de verdad para actualizar los entregables, ya que no hay conexión a la instancia MySQL.
>
> 1. Lee BD16.sql y extrae de los CREATE TABLE, ALTER TABLE y CREATE INDEX: tablas, columnas, tipos, nulabilidad, defaults, PK, llaves únicas, índices, FK (con ON DELETE / ON UPDATE) y CHECK. Extrae también procedimientos, funciones, vistas y triggers.
> 2. Calcula el total de registros de cada tabla contando las filas de sus sentencias INSERT en el dump (cuenta las filas reales, no las sentencias). Si una tabla no tiene INSERT, escribe 0.
> 3. Compara con el diccionario actual (basado en BD15) y muéstrame la lista de diferencias: tablas nuevas/eliminadas, columnas agregadas/eliminadas/modificadas, FK e índices cambiados.
> 4. Después de mostrarme la lista, actualiza el diccionario y el diagrama de Archify como te indiqué antes. Cambia todas las referencias a BD15 por BD16.
> 5. En el diccionario agrega esta nota: "Estructura y totales de registros obtenidos del respaldo BD16.sql (fecha del archivo: <fecha de modificación del archivo>)". Indícame que los totales corresponden al respaldo y no a la instancia en vivo.
> 6. No ejecutes nada contra ninguna base de datos. No hagas commit ni push sin mostrarme el resumen.


## Actualización del diccionario con BD17 (solo diccionario)

> Mi base de datos MySQL se llama ahora BD17. Respecto a la versión anterior, solo se ejecutó el script generacion_masiva_usuarios.sql, que insertó usuarios en tb_users y tb_people, y creó tablas, funciones y procedimientos nuevos. Necesito que actualices SOLO el diccionario de datos. No modifiques el diagrama relacional de Archify.
>
> FUENTE DE DATOS
> - No hay conexión a la instancia MySQL. Usa como fuente el respaldo BD17.sql del proyecto (si no existe, búscalo en Practica03/backups/ y dime cuál usaste).
> - Obtén la estructura de los CREATE TABLE, ALTER TABLE, CREATE INDEX, CREATE PROCEDURE, CREATE FUNCTION y CREATE TRIGGER del dump.
> - Calcula el total de registros de cada tabla contando las filas reales de sus INSERT (cuenta filas, no sentencias; ten en cuenta los INSERT con múltiples VALUES). Si el dump no trae datos de alguna tabla, escribe "No verificable en el respaldo" en lugar de poner 0.
> - Si hay un archivo con los conteos reales que yo te pase (resultado de SELECT COUNT(*)), úsalo con prioridad sobre el conteo del dump.
>
> PASO 1. Lista de diferencias (muéstramela antes de editar)
> Compara BD17.sql contra el diccionario actual y dime tablas nuevas, eliminadas o renombradas; columnas agregadas, eliminadas o modificadas (tipo, longitud, nulabilidad, default); FK, índices o restricciones cambiados; rutinas, vistas y triggers nuevos o modificados; y tablas cuyo total cambió con valor anterior y nuevo.
>
> PASO 2. Actualizar el diccionario: cambia las referencias de versión por BD17, actualiza conteos y fecha, aclara que son del respaldo, documenta los catálogos tbc_gen_country_profile, tbc_gen_given_names y tbc_gen_family_names con los campos completos exigidos, documenta sp_gen_validate_params, sp_gen_insert_user_person, sp_generate_users y las funciones fn_gen_*, sin quitar contenido válido.
>
> PASO 3. Revisa e informa si las diferencias requieren actualizar el diagrama, pero no lo edites ni exportes.
>
> PASO 4. Verifica el sitio de GitHub Pages y enlaces, registra este prompt y no hagas commit ni push sin mostrar el resumen.
>
> REGLAS: No ejecutes nada contra una base de datos ni modifiques datos, estructura o privilegios. Si una diferencia no permite saber la fuente correcta, pregunta antes de suponer. Al final resume diferencias, tablas agregadas, totales con fecha/fuente y si el diagrama requiere cambios.


## Actualización del diccionario y diagrama con BD23 (db_test)

> Actualiza el diccionario de datos y el diagrama relacional con mi respaldo más reciente de db_test (BD23.sql). Usa la skill de Archify para el diagrama.
>
> Cambios a reflejar: (1) se eliminan tbc_gen_country_profile, tbc_gen_family_names y tbc_gen_given_names con sus vistas, triggers, funciones fn_gen_* y procedimientos sp_gen_* / sp_generate_users dependientes (quedan 26 tablas); (2) tb_orders.cart_ID INT UNSIGNED NOT NULL UNIQUE, FK → tb_carts.ID (1:1 carrito-orden); (3) tb_buyer_orders.order_ID INT UNSIGNED NOT NULL, FK → tb_orders.ID, UNIQUE (order_ID, seller_ID) (1:N orden-subórdenes); (4) tb_carts: uk_cart_user pasa a índice idx_cart_user; (5) tb_shipments: shipment_status agrega 'Failed attempt' y 'At pickup point', nueva columna notes VARCHAR(500) NULL; (6) nuevo procedimiento sp_pay_order(p_order_id, p_user_payment_method_id, p_payment_method_name, p_installments); (7) nuevos registros en tbc_payment_methods_types y tbc_payment_methods. Revisa también el .sql por si hay algo más.
>
> Sitio: el título siempre es "DB Test"; el panel izquierdo muestra la lista de TODAS las tablas como enlaces a su sección, agrupadas por prefijo (tb_, tbc_, tbd_), con la búsqueda funcionando sobre esa lista. Mantén los criterios de cada columna: descripción detallada, mono/multivalor, derivado/almacenado, obligatorio/opcional, llave primaria, naturaleza cualitativa/cuantitativa, notación formal y dominio.
