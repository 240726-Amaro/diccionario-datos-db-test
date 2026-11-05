# Diccionario de datos — BD19

**Motor objetivo:** MySQL 8.0.45. Estructura y totales de registros obtenidos del respaldo BD19.sql (fecha del archivo: 2026-11-04 18:11:43 -06:00). Conteo de registros realizado el: 2026-11-04 18:44:17 -06:00. Los totales corresponden al respaldo, no a la instancia en vivo.
**Alcance:** 25 tablas seleccionadas por prioridad de población; se incluyen todas las vistas y triggers del respaldo BD19. La asociación con cada tabla se indica cuando existe.


## Leyenda de la notación

- `=` significa “se compone de”; `+` significa “y”; `[a | b]` significa “uno de”; `{x}` significa repetición; `(x)` significa opcional; `*texto*` es comentario o dominio.
- `@columna` marca una PK; `#columna` marca una FK. En PK compuestas todas las columnas de la clave se enumeran en la notación y el campo Llave muestra la composición completa.
- Las expresiones atómicas se escriben como `columna = {tipo}` y pueden incluir dominio o fórmula entre `*...*`.

## Criterios de clasificación

- Valor: las llaves y referencias escalares son monovalor; los atributos que se repiten por concepto se identifican con su tabla de relación o componentes. Texto que agrupa datos se marca como compuesto en texto libre.
- Origen: almacenado si se persiste; derivado si es GENERATED, con expresión SQL. Importes persistidos calculables se identifican como almacenados derivables, sin inventar fórmula no declarada.
- Obligatoriedad: NOT NULL es obligatorio, NULL es opcional. Se indica si AUTO_INCREMENT/DEFAULT lo asigna el sistema o si el origen se infiere.
- Llave: PK, PK compuesta (miembros completos), FK (destino), UK o No. Naturaleza: ENUM de estados procesales es ordinal; demás ENUM son nominales; numéricos discretos/continuos y fechas temporales.
- Dominio: tipo, longitud/precisión, valores ENUM y CHECK del DDL; si el SQL no define un rango/formato, se indica el tipo y que no hay una restricción adicional declarada.

## Índice

- [Tablas](#tablas)
- [Vistas](#vistas)
- [Triggers](#triggers)
- [Procedimientos](#procedimientos)
- [Funciones](#funciones)
- [Volumen de datos](#volumen-de-datos)
- [Catálogo de dominios](#catálogo-de-dominios)
- [Convenciones](#convenciones-de-nombres)
- [Observaciones de calidad](#observaciones-de-calidad-del-diseño)
- [Historial de cambios](#historial-de-cambios)
- [Pendientes por confirmar](#pendientes-por-confirmar)

## Tablas

### `tb_logs`

- **Total de registros:** 65632. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** auditoría (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Registra operaciones de auditoría emitidas por triggers, con tabla, evento, usuario de base de datos y descripción del cambio.
  - Pertenece al módulo de auditoría (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: ninguna FK declarada. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: sin FK salientes con acciones. Columnas generadas: ninguna.
  - Triggers asociados: ninguno; esta tabla recibe registros generados por triggers de otras tablas.

**Notación formal:** `tb_logs = @ID + table_name + operation + db_user + description + operation_date + operation_status`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `table_name` | `varchar(100)` | 100 | NO | Sin default | — | — | Identifica el nombre de la tabla cuya operación se registra; lo asignan los triggers de auditoría. |
| 3 | `operation` | `enum('Create','Read','Update','Delete')` | 'Create','Read','Update','Delete' | NO | Sin default | — | — | Clasifica la operación registrada; el dominio ENUM limita el valor a Create, Read, Update o Delete. Los triggers asignan Create, Update o Delete según el evento. |
| 4 | `db_user` | `varchar(80)` | 80 | NO | Sin default | — | — | Guarda la identidad de base de datos devuelta por USER() al generar el registro de auditoría. |
| 5 | `description` | `text` | — | NO | Sin default | — | — | Contiene el mensaje de auditoría con atributos relevantes del registro afectado; los triggers lo construyen con CONCAT y valores NEW u OLD. |
| 6 | `operation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 7 | `operation_status` | `bit(1)` | 1 | Sí | b'1' | — | — | Marca el resultado/estado de la entrada de auditoría; el SQL permite los valores de bit(1) y declara DEFAULT b'1'. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`

**Relaciones**

- Sin FK salientes.

**Triggers asociados:** Ninguno.

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `table_name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | table_name = {carácter} | table_name ∈ cadena(≤100); tipo varchar(100) | Identifica el nombre de la tabla cuya operación se registra; lo asignan los triggers de auditoría. |
| `operation` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | operation = [ Create \| Read \| Update \| Delete ] | operation ∈ {Create, Read, Update, Delete}; tipo enum('Create','Read','Update','Delete') | Clasifica la operación registrada; el dominio ENUM limita el valor a Create, Read, Update o Delete. Los triggers asignan Create, Update o Delete según el evento. |
| `db_user` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | db_user = {carácter} | db_user ∈ cadena(≤80); tipo varchar(80) | Guarda la identidad de base de datos devuelta por USER() al generar el registro de auditoría. |
| `description` | Monovalor (contiene datos compuestos en texto libre) | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | description = {carácter} | description ∈ texto (text); formato no restringido por CHECK | Contiene el mensaje de auditoría con atributos relevantes del registro afectado; los triggers lo construyen con CONCAT y valores NEW u OLD. |
| `operation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | operation_date = {fecha/hora} | operation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `operation_status` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | operation_status = {0 \| 1} | operation_status ∈ {0,1}; bit(1) | Marca el resultado/estado de la entrada de auditoría; el SQL permite los valores de bit(1) y declara DEFAULT b'1'. |

### `tb_people`

- **Total de registros:** 10225. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** usuarios y perfiles personales (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Almacena datos personales de contacto e identificación asociados a una cuenta de usuario.
  - Pertenece al módulo de usuarios y perfiles personales (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `user_ID` → tb_users.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: CHECK ((`gender_ID` in (1,2,3))); sin UNIQUE. Acciones ON DELETE/UPDATE: fk_people_user: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_people_after_insert`, `trg_tb_people_after_update`, `trg_tb_people_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_people = @person_ID + #user_ID + courtesy_title_ID + given_names + family_names + birth_date + gender_ID + country_code + phone + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `person_ID` | `bigint unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `user_ID` | `int` | — | NO | Sin default | — | FK → tb_users.ID | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `courtesy_title_ID` | `char(10)` | 10 | Sí | NULL | — | — | Guarda el código de tratamiento honorífico asociado a la persona; el DDL no declara catálogo ni FK. (inferido). |
| 4 | `given_names` | `varchar(150)` | 150 | NO | Sin default | — | — | Guarda los nombres propios de la persona para identificarla en registros de entrega o cuenta. (inferido). |
| 5 | `family_names` | `varchar(150)` | 150 | NO | Sin default | — | — | Guarda los apellidos de la persona para completar su nombre de identificación. (inferido). |
| 6 | `birth_date` | `date` | — | Sí | NULL | — | — | Registra la fecha de nacimiento de la persona. (inferido). |
| 7 | `gender_ID` | `tinyint unsigned` | — | Sí | NULL | — | — | Guarda un código de género; el DDL no declara catálogo ni FK para interpretarlo. (inferido). |
| 8 | `country_code` | `char(2)` | 2 | Sí | NULL | — | — | Guarda el código de país asociado a la persona; el DDL no declara catálogo ni FK. (inferido). |
| 9 | `phone` | `varchar(25)` | 25 | Sí | NULL | — | — | Guarda el teléfono de contacto de la persona. (inferido). |
| 10 | `last_update` | `datetime` | — | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`person_ID\`)`
- `KEY \`fk_people_user\` (\`user_ID\`)`
- `CONSTRAINT \`fk_people_user\` FOREIGN KEY (\`user_ID\`) REFERENCES \`tb_users\` (\`ID\`)`
- `CONSTRAINT \`chk_gender_values\` CHECK ((\`gender_ID\` in (1,2,3)))`

**Relaciones**

- `user_ID` → `tb_users.ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tb_people_after_insert`, `trg_tb_people_after_update`, `trg_tb_people_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `person_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | person_ID = {dígito} | person_ID ∈ ℤ⁺; tipo bigint unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `user_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID | Cualitativa nominal | user_ID = {dígito} | user_ID ∈ {tb_users.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `courtesy_title_ID` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | courtesy_title_ID = {dígito} | courtesy_title_ID ∈ cadena(≤10); tipo char(10) | Guarda el código de tratamiento honorífico asociado a la persona; el DDL no declara catálogo ni FK. (inferido). |
| `given_names` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | given_names = {carácter} | given_names ∈ cadena(≤150); tipo varchar(150) | Guarda los nombres propios de la persona para identificarla en registros de entrega o cuenta. (inferido). |
| `family_names` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | family_names = {carácter} | family_names ∈ cadena(≤150); tipo varchar(150) | Guarda los apellidos de la persona para completar su nombre de identificación. (inferido). |
| `birth_date` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | birth_date = {fecha/hora} | birth_date ∈ DATE; default NULL | Registra la fecha de nacimiento de la persona. (inferido). |
| `gender_ID` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | gender_ID = {dígito} | gender_ID ∈ ℤ⁺ ∪ {0}; tipo tinyint unsigned; CHECK ((`gender_ID` in (1,2,3))) | Guarda un código de género; el DDL no declara catálogo ni FK para interpretarlo. (inferido). |
| `country_code` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | country_code = {carácter} | country_code ∈ cadena(≤2); tipo char(2) | Guarda el código de país asociado a la persona; el DDL no declara catálogo ni FK. (inferido). |
| `phone` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | phone = {carácter} | phone ∈ cadena(≤25); tipo varchar(25) | Guarda el teléfono de contacto de la persona. (inferido). |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tb_products`

- **Total de registros:** 15007. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** productos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Mantiene el catálogo de productos con SKU, descripción, precio vigente, existencias y estado de publicación.
  - Pertenece al módulo de productos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: ninguna FK declarada. Relaciones entrantes: tbd_products_categories.`product_ID`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `SKU` (`SKU`). Acciones ON DELETE/UPDATE: sin FK salientes con acciones. Columnas generadas: ninguna.
  - Triggers asociados: `trg_products_after_insert`, `trg_products_after_update`, `trg_products_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_products = @ID + SKU + name + description + current_price + current_stock + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `SKU` | `varchar(50)` | 50 | NO | Sin default | — | UK | Guarda el código SKU que distingue el producto en el catálogo; se captura al dar de alta o importar el producto (inferido). Es obligatorio y único para localizar y controlar ese producto. |
| 3 | `name` | `varchar(250)` | 250 | NO | Sin default | — | — | Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido). |
| 4 | `description` | `text` | — | Sí | Sin default | — | — | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| 5 | `current_price` | `decimal(10,2)` | 10,2 | NO | '0.00' | — | — | Guarda el precio vigente del producto y se usa para calcular el importe de venta (inferido). Es obligatorio; si no se informa al insertar, comienza en 0.00 y luego se actualiza con el precio autorizado (inferido). |
| 6 | `current_stock` | `int unsigned` | — | NO | '0' | — | — | Guarda las unidades disponibles del producto y sirve para consultar y actualizar inventario (inferido). Es obligatorio; el sistema inicializa el valor en cero y el proceso de venta o reposición lo modifica (inferido). |
| 7 | `status` | `tinyint` | — | Sí | '1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT '1'. |
| 8 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 9 | `last_update` | `datetime` | — | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`SKU\` (\`SKU\`)`

**Relaciones**

- Sin FK salientes.
- Referenciada por `tbd_products_categories` mediante `product_ID`.

**Triggers asociados:** `trg_products_after_insert`, `trg_products_after_update`, `trg_products_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `SKU` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | SKU = {carácter} | SKU ∈ cadena(≤50); tipo varchar(50) | Guarda el código SKU que distingue el producto en el catálogo; se captura al dar de alta o importar el producto (inferido). Es obligatorio y único para localizar y controlar ese producto. |
| `name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | name = {carácter} | name ∈ cadena(≤250); tipo varchar(250) | Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido). |
| `description` | Monovalor | Almacenado | Opcional (NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | description = {carácter} | description ∈ texto (text); formato no restringido por CHECK | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| `current_price` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0.00') | No | Cuantitativa continua | current_price = {número real} | current_price ∈ ℝ, precisión 10,2; decimal(10,2); sin rango adicional salvo CHECK explícito | Guarda el precio vigente del producto y se usa para calcular el importe de venta (inferido). Es obligatorio; si no se informa al insertar, comienza en 0.00 y luego se actualiza con el precio autorizado (inferido). |
| `current_stock` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0') | No | Cuantitativa discreta | current_stock = {entero} | current_stock ∈ ℤ⁺ ∪ {0}; tipo int unsigned | Guarda las unidades disponibles del producto y sirve para consultar y actualizar inventario (inferido). Es obligatorio; el sistema inicializa el valor en cero y el proceso de venta o reposición lo modifica (inferido). |
| `status` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT '1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ ℤ; tipo tinyint | Indica el estado lógico del registro (inferido); usa DEFAULT '1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tb_users`

- **Total de registros:** 10227. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** usuarios (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa cuentas de acceso con correo, alias, hash de contraseña, fechas de actividad y estado.
  - Pertenece al módulo de usuarios (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: ninguna FK declarada. Relaciones entrantes: tb_people.`user_ID`; tb_buyer_orders.`seller_ID`; tb_carts.`user_ID`; tb_order_cancellations.`user_ID`; tb_orders.`user_id`; tb_returns.`user_ID`; tb_user_addresses.`user_ID`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `email` (`email`); UNIQUE UNIQUE KEY `nickname` (`nickname`). Acciones ON DELETE/UPDATE: sin FK salientes con acciones. Columnas generadas: ninguna.
  - Triggers asociados: `trg_users_after_insert`, `trg_users_after_update`, `trg_users_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_users = @ID + email + nickname + password + creation_date + last_login + status`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `email` | `varchar(80)` | 80 | NO | Sin default | — | UK | Guarda el correo de contacto o acceso asociado a la cuenta (inferido); el SQL fija su longitud y cualquier restricción UNIQUE detectada. |
| 3 | `nickname` | `varchar(100)` | 100 | NO | Sin default | — | UK | Guarda el alias visible del usuario para identificar su perfil en la aplicación (inferido). |
| 4 | `password` | `varchar(255)` | 255 | NO | Sin default | — | — | Almacena el hash de la contraseña de la cuenta para verificarla durante la autenticación; el algoritmo de hash no está declarado en el esquema (inferido). |
| 5 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 6 | `last_login` | `datetime` | — | Sí | NULL | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |
| 7 | `status` | `bit(1)` | 1 | Sí | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`email\` (\`email\`)`
- `UNIQUE KEY \`nickname\` (\`nickname\`)`

**Relaciones**

- Sin FK salientes.
- Referenciada por `tb_people` mediante `user_ID`.
- Referenciada por `tb_buyer_orders` mediante `seller_ID`.
- Referenciada por `tb_carts` mediante `user_ID`.
- Referenciada por `tb_order_cancellations` mediante `user_ID`.
- Referenciada por `tb_orders` mediante `user_id`.
- Referenciada por `tb_returns` mediante `user_ID`.
- Referenciada por `tb_user_addresses` mediante `user_ID`.

**Triggers asociados:** `trg_users_after_insert`, `trg_users_after_update`, `trg_users_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `email` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | email = usuario + "@" + dominio | email ∈ cadena(≤80); tipo varchar(80) | Guarda el correo de contacto o acceso asociado a la cuenta (inferido); el SQL fija su longitud y cualquier restricción UNIQUE detectada. |
| `nickname` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | nickname = {carácter} | nickname ∈ cadena(≤100); tipo varchar(100) | Guarda el alias visible del usuario para identificar su perfil en la aplicación (inferido). |
| `password` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | password = {carácter} | password ∈ cadena(≤255); tipo varchar(255) | Almacena el hash de la contraseña de la cuenta para verificarla durante la autenticación; el algoritmo de hash no está declarado en el esquema (inferido). |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_login` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_login = {fecha/hora} | last_login ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |
| `status` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |

### `tbc_categories`

- **Total de registros:** 160. 
- **Prefijo/tipo:** catálogo (tbc_). **Módulo:** productos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Define categorías de productos y la relación jerárquica opcional entre categorías.
  - Pertenece al módulo de productos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `sup_id_category` → tbc_categories.`ID`. Relaciones entrantes: tbc_categories.`sup_id_category`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `name` (`name`). Acciones ON DELETE/UPDATE: fk_superior_category: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbc_categories_after_insert`, `trg_tbc_categories_after_update`, `trg_tbc_categories_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbc_categories = @ID + name + description + #sup_id_category + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `name` | `varchar(120)` | 120 | NO | Sin default | — | UK | Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido). |
| 3 | `description` | `text` | — | Sí | Sin default | — | — | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| 4 | `sup_id_category` | `int unsigned` | — | Sí | NULL | — | FK → tbc_categories.ID | Identifica o enlaza el registro con `tbc_categories.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 5 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 6 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 7 | `last_update` | `datetime` | — | Sí | NULL | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`name\` (\`name\`)`
- `KEY \`fk_superior_category\` (\`sup_id_category\`)`
- `CONSTRAINT \`fk_superior_category\` FOREIGN KEY (\`sup_id_category\`) REFERENCES \`tbc_categories\` (\`ID\`)`

**Relaciones**

- `sup_id_category` → `tbc_categories.ID`; sin acción referencial explícita
- Referenciada por `tbc_categories` mediante `sup_id_category`.

**Triggers asociados:** `trg_tbc_categories_after_insert`, `trg_tbc_categories_after_update`, `trg_tbc_categories_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | name = {carácter} | name ∈ cadena(≤120); tipo varchar(120) | Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido). |
| `description` | Monovalor | Almacenado | Opcional (NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | description = {carácter} | description ∈ texto (text); formato no restringido por CHECK | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| `sup_id_category` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | FK → tbc_categories.ID | Cualitativa nominal | sup_id_category = {entero} | sup_id_category ∈ {tbc_categories.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbc_categories.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tbc_gen_country_profile`

- **Total de registros:** 12. 
- **Prefijo/tipo:** catálogo (tbc_). **Módulo:** direcciones (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Catálogo de apoyo para la generación masiva de usuarios; define el país y los parámetros locales usados para construir teléfono y título de cortesía.
  - Pertenece al módulo de direcciones (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: ninguna FK declarada. Relaciones entrantes: tbc_gen_family_names.`country_code`; tbc_gen_given_names.`country_code`.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: sin FK salientes con acciones. Columnas generadas: ninguna.
  - Triggers asociados: ninguno.

**Notación formal:** `tbc_gen_country_profile = @country_code + country_name + phone_prefix + phone_digits + title_male + title_female + status`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `country_code` | `char(2)` | 2 | NO | Sin default | — | PK | Código ISO de dos caracteres que identifica el país usado como clave del perfil de generación; permite relacionar los catálogos auxiliares con sus parámetros locales. |
| 2 | `country_name` | `varchar(60)` | 60 | NO | Sin default | — | — | Nombre legible del país asociado al código country_code. |
| 3 | `phone_prefix` | `varchar(6)` | 6 | NO | Sin default | — | — | Prefijo telefónico internacional que se antepone a los dígitos locales al generar teléfonos. |
| 4 | `phone_digits` | `tinyint` | — | NO | Sin default | — | — | Cantidad de dígitos locales que deben generarse para completar el teléfono del país. |
| 5 | `title_male` | `varchar(10)` | 10 | NO | Sin default | — | — | Título de cortesía que se asigna a personas del género masculino en el contexto del país. |
| 6 | `title_female` | `varchar(10)` | 10 | NO | Sin default | — | — | Título de cortesía que se asigna a personas del género femenino en el contexto del país. |
| 7 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`country_code\`)`

**Relaciones**

- Sin FK salientes.
- Referenciada por `tbc_gen_family_names` mediante `country_code`.
- Referenciada por `tbc_gen_given_names` mediante `country_code`.

**Triggers asociados:** Ninguno.

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `country_code` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK | Cualitativa nominal | country_code = {carácter} | country_code ∈ cadena(≤2); tipo char(2) | Código ISO de dos caracteres que identifica el país usado como clave del perfil de generación; permite relacionar los catálogos auxiliares con sus parámetros locales. |
| `country_name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | country_name = {carácter} | country_name ∈ cadena(≤60); tipo varchar(60) | Nombre legible del país asociado al código country_code. |
| `phone_prefix` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | phone_prefix = {carácter} | phone_prefix ∈ cadena(≤6); tipo varchar(6) | Prefijo telefónico internacional que se antepone a los dígitos locales al generar teléfonos. |
| `phone_digits` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | phone_digits = {entero} | phone_digits ∈ ℤ; tipo tinyint | Cantidad de dígitos locales que deben generarse para completar el teléfono del país. |
| `title_male` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | title_male = {carácter} | title_male ∈ cadena(≤10); tipo varchar(10) | Título de cortesía que se asigna a personas del género masculino en el contexto del país. |
| `title_female` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | title_female = {carácter} | title_female ∈ cadena(≤10); tipo varchar(10) | Título de cortesía que se asigna a personas del género femenino en el contexto del país. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |

### `tbc_gen_family_names`

- **Total de registros:** 225. 
- **Prefijo/tipo:** catálogo (tbc_). **Módulo:** direcciones (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Catálogo de apoyo para la generación masiva de usuarios; almacena apellidos por país y mantiene FK al perfil del país.
  - Pertenece al módulo de direcciones (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `country_code` → tbc_gen_country_profile.`country_code`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `uk_gen_family` (`country_code`,`name`). Acciones ON DELETE/UPDATE: fk_gen_family_country: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: ninguno.

**Notación formal:** `tbc_gen_family_names = @ID + #country_code + name`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `country_code` | `char(2)` | 2 | NO | Sin default | — | FK → tbc_gen_country_profile.country_code; UK | Identifica o enlaza el registro con `tbc_gen_country_profile.country_code`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `name` | `varchar(60)` | 60 | NO | Sin default | — | UK | Apellido disponible para selección aleatoria durante la generación masiva de usuarios. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`uk_gen_family\` (\`country_code\`,\`name\`)`
- `CONSTRAINT \`fk_gen_family_country\` FOREIGN KEY (\`country_code\`) REFERENCES \`tbc_gen_country_profile\` (\`country_code\`)`

**Relaciones**

- `country_code` → `tbc_gen_country_profile.country_code`; sin acción referencial explícita

**Triggers asociados:** Ninguno.

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `country_code` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tbc_gen_country_profile.country_code; UK | Cualitativa nominal | country_code = {carácter} | country_code ∈ {tbc_gen_country_profile.country_code}; ON DELETE sin acción | Identifica o enlaza el registro con `tbc_gen_country_profile.country_code`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | name = {carácter} | name ∈ cadena(≤60); tipo varchar(60) | Apellido disponible para selección aleatoria durante la generación masiva de usuarios. |

### `tbc_gen_given_names`

- **Total de registros:** 344. 
- **Prefijo/tipo:** catálogo (tbc_). **Módulo:** direcciones (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Catálogo de apoyo para la generación masiva de usuarios; almacena nombres por país y género, con FK al perfil del país y CHECK de género.
  - Pertenece al módulo de direcciones (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `country_code` → tbc_gen_country_profile.`country_code`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: CHECK ((`gender_ID` in (1,2))); UNIQUE UNIQUE KEY `uk_gen_given` (`country_code`,`gender_ID`,`name`). Acciones ON DELETE/UPDATE: fk_gen_given_country: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: ninguno.

**Notación formal:** `tbc_gen_given_names = @ID + #country_code + gender_ID + name`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `country_code` | `char(2)` | 2 | NO | Sin default | — | FK → tbc_gen_country_profile.country_code; UK | Identifica o enlaza el registro con `tbc_gen_country_profile.country_code`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `gender_ID` | `tinyint unsigned` | — | NO | Sin default | — | UK | Identificador del género al que se asocia el nombre; CHECK restringe el valor a 1 o 2. |
| 4 | `name` | `varchar(60)` | 60 | NO | Sin default | — | UK | Nombre de pila disponible para selección por país y género durante la generación masiva de usuarios. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`uk_gen_given\` (\`country_code\`,\`gender_ID\`,\`name\`)`
- `CONSTRAINT \`fk_gen_given_country\` FOREIGN KEY (\`country_code\`) REFERENCES \`tbc_gen_country_profile\` (\`country_code\`)`
- `CONSTRAINT \`chk_gen_given_gender\` CHECK ((\`gender_ID\` in (1,2)))`

**Relaciones**

- `country_code` → `tbc_gen_country_profile.country_code`; sin acción referencial explícita

**Triggers asociados:** Ninguno.

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `country_code` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tbc_gen_country_profile.country_code; UK | Cualitativa nominal | country_code = {carácter} | country_code ∈ {tbc_gen_country_profile.country_code}; ON DELETE sin acción | Identifica o enlaza el registro con `tbc_gen_country_profile.country_code`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `gender_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | gender_ID = {dígito} | gender_ID ∈ ℤ⁺ ∪ {0}; tipo tinyint unsigned; CHECK ((`gender_ID` in (1,2))) | Identificador del género al que se asocia el nombre; CHECK restringe el valor a 1 o 2. |
| `name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | name = {carácter} | name ∈ cadena(≤60); tipo varchar(60) | Nombre de pila disponible para selección por país y género durante la generación masiva de usuarios. |

### `tbc_payment_methods`

- **Total de registros:** 1. 
- **Prefijo/tipo:** catálogo (tbc_). **Módulo:** pagos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Lista los métodos de pago disponibles para registrar pagos.
  - Pertenece al módulo de pagos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: ninguna FK declarada. Relaciones entrantes: tb_payments.`payment_method_id`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `name` (`name`). Acciones ON DELETE/UPDATE: sin FK salientes con acciones. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbc_payment_methods_after_insert`, `trg_tbc_payment_methods_after_update`, `trg_tbc_payment_methods_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbc_payment_methods = @ID + name + description + status + creation_date`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `name` | `varchar(100)` | 100 | NO | Sin default | — | UK | Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido). |
| 3 | `description` | `text` | — | Sí | Sin default | — | — | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| 4 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 5 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`name\` (\`name\`)`

**Relaciones**

- Sin FK salientes.
- Referenciada por `tb_payments` mediante `payment_method_id`.

**Triggers asociados:** `trg_tbc_payment_methods_after_insert`, `trg_tbc_payment_methods_after_update`, `trg_tbc_payment_methods_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | name = {carácter} | name ∈ cadena(≤100); tipo varchar(100) | Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido). |
| `description` | Monovalor | Almacenado | Opcional (NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | description = {carácter} | description ∈ texto (text); formato no restringido por CHECK | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tbc_payment_methods_types`

- **Total de registros:** 1. 
- **Prefijo/tipo:** catálogo (tbc_). **Módulo:** pagos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Define tipos codificados que clasifican métodos de pago de usuarios.
  - Pertenece al módulo de pagos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: ninguna FK declarada. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `code_UNIQUE` (`code`). Acciones ON DELETE/UPDATE: sin FK salientes con acciones. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbc_payment_methods_types_after_insert`, `trg_tbc_payment_methods_types_after_update`, `trg_tbc_payment_methods_types_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbc_payment_methods_types = @ID + code + description + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `code` | `varchar(30)` | 30 | NO | Sin default | — | UK | Guarda el código estable que identifica cada tipo de método de pago en el catálogo (inferido). Es obligatorio, único y se asigna al configurar el catálogo para que otras filas puedan distinguir el tipo. |
| 3 | `description` | `text` | — | NO | Sin default | — | — | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| 4 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 5 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 6 | `last_update` | `datetime` | — | Sí | NULL | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`code_UNIQUE\` (\`code\`)`

**Relaciones**

- Sin FK salientes.

**Triggers asociados:** `trg_tbc_payment_methods_types_after_insert`, `trg_tbc_payment_methods_types_after_update`, `trg_tbc_payment_methods_types_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `code` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | code = {carácter} | code ∈ cadena(≤30); tipo varchar(30) | Guarda el código estable que identifica cada tipo de método de pago en el catálogo (inferido). Es obligatorio, único y se asigna al configurar el catálogo para que otras filas puedan distinguir el tipo. |
| `description` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | description = {carácter} | description ∈ texto (text); formato no restringido por CHECK | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tbd_products_categories`

- **Total de registros:** 5000. 
- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** productos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Asocia productos con categorías para permitir su clasificación en el catálogo.
  - Pertenece al módulo de productos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `product_ID` → tb_products.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_product: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbd_products_categories_after_insert`, `trg_tbd_products_categories_after_update`, `trg_tbd_products_categories_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_products_categories = @category_ID + @#product_ID + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `category_ID` | `int unsigned` | — | NO | Sin default | — | PK compuesta (category_ID, product_ID) | Guarda el identificador lógico de categoría asociado al producto o relación; esta columna no declara FK en el DDL. |
| 2 | `product_ID` | `int unsigned` | — | NO | Sin default | — | PK compuesta (category_ID, product_ID); FK → tb_products.ID | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 4 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 5 | `last_update` | `datetime` | — | NO | Sin default | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se captura al guardar. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`category_ID\`,\`product_ID\`)`
- `KEY \`fk_product\` (\`product_ID\`)`
- `CONSTRAINT \`fk_product\` FOREIGN KEY (\`product_ID\`) REFERENCES \`tb_products\` (\`ID\`)`

**Relaciones**

- `product_ID` → `tb_products.ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tbd_products_categories_after_insert`, `trg_tbd_products_categories_after_update`, `trg_tbd_products_categories_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `category_ID` | Multivalor resuelto mediante tabla tbd_products_categories | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (category_ID, product_ID) | Cualitativa nominal | category_ID = {dígito} | category_ID ∈ ℤ⁺ ∪ {0}; tipo int unsigned | Guarda el identificador lógico de categoría asociado al producto o relación; esta columna no declara FK en el DDL. |
| `product_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (category_ID, product_ID); FK → tb_products.ID | Cualitativa nominal | product_ID = {dígito} | product_ID ∈ {tb_products.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default sin default | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se captura al guardar. |

### `tb_buyer_orders`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** órdenes (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Conserva las órdenes del flujo de compra asociadas al vendedor, sus importes y su etapa de cumplimiento; el DDL no contiene una columna de comprador.
  - Pertenece al módulo de órdenes (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `seller_ID` → tb_users.`ID`. Relaciones entrantes: tb_order_cancellations.`buyer_order_ID`; tb_returns.`buyer_order_ID`; tb_shipments.`buyer_order_ID`; tbd_order_items.`buyer_order_ID`.
  - Reglas SQL: CHECK ((`shipping_cost` >= 0)); CHECK ((`subtotal` >= 0)); sin UNIQUE. Acciones ON DELETE/UPDATE: fk_seller_orders_seller: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_buyer_orders_after_insert`, `trg_tb_buyer_orders_after_update`, `trg_tb_buyer_orders_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_buyer_orders = @ID + #seller_ID + subtotal + shipping_cost + fulfillment_status + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `seller_ID` | `int` | — | NO | Sin default | — | FK → tb_users.ID | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `subtotal` | `decimal(12,2)` | 12,2 | NO | '0.00' | — | — | Guarda o calcula el importe de esta línea de orden; si es GENERATED, su fórmula es la declarada en la expresión SQL. |
| 4 | `shipping_cost` | `decimal(12,2)` | 12,2 | NO | '0.00' | — | — | Guarda el costo de envío de la orden; se sujeta al CHECK de no negatividad declarado en el DDL. |
| 5 | `fulfillment_status` | `enum('Pending','Accepted','Preparing','Sent','Delivered','Canceled','Returned')` | 'Pending','Accepted','Preparing','Sent','Delivered','Canceled','Returned' | NO | 'Pending' | — | — | Representa la etapa del cumplimiento de la orden dentro del conjunto ENUM ordenado del flujo. |
| 6 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 7 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 8 | `last_update` | `datetime` | — | Sí | NULL | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_seller_orders_seller\` (\`seller_ID\`)`
- `CONSTRAINT \`fk_seller_orders_seller\` FOREIGN KEY (\`seller_ID\`) REFERENCES \`tb_users\` (\`ID\`)`
- `CONSTRAINT \`chk_seller_orders_shipping\` CHECK ((\`shipping_cost\` >= 0))`
- `CONSTRAINT \`chk_seller_orders_subtotal\` CHECK ((\`subtotal\` >= 0))`

**Relaciones**

- `seller_ID` → `tb_users.ID`; sin acción referencial explícita
- Referenciada por `tb_order_cancellations` mediante `buyer_order_ID`.
- Referenciada por `tb_returns` mediante `buyer_order_ID`.
- Referenciada por `tb_shipments` mediante `buyer_order_ID`.
- Referenciada por `tbd_order_items` mediante `buyer_order_ID`.

**Triggers asociados:** `trg_tb_buyer_orders_after_insert`, `trg_tb_buyer_orders_after_update`, `trg_tb_buyer_orders_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `seller_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID | Cualitativa nominal | seller_ID = {dígito} | seller_ID ∈ {tb_users.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `subtotal` | Monovalor | Almacenado (derivable de la suma de tbd_order_items.subtotal; fórmula no declarada, inferido) | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0.00') | No | Cuantitativa continua | subtotal = {número real} | subtotal ∈ ℝ, precisión 12,2; decimal(12,2); sin rango adicional salvo CHECK explícito; CHECK ((`subtotal` >= 0)) | Guarda o calcula el importe de esta línea de orden; si es GENERATED, su fórmula es la declarada en la expresión SQL. |
| `shipping_cost` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0.00') | No | Cuantitativa continua | shipping_cost = {número real} | shipping_cost ∈ ℝ, precisión 12,2; decimal(12,2); sin rango adicional salvo CHECK explícito; CHECK ((`shipping_cost` >= 0)) | Guarda el costo de envío de la orden; se sujeta al CHECK de no negatividad declarado en el DDL. |
| `fulfillment_status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Pending') | No | Cualitativa ordinal | fulfillment_status = [ Pending \| Accepted \| Preparing \| Sent \| Delivered \| Canceled \| Returned ] | fulfillment_status ∈ {Pending, Accepted, Preparing, Sent, Delivered, Canceled, Returned}; tipo enum('Pending','Accepted','Preparing','Sent','Delivered','Canceled','Returned') | Representa la etapa del cumplimiento de la orden dentro del conjunto ENUM ordenado del flujo. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tb_carts`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** carritos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa el carrito activo o histórico de un usuario para agrupar artículos antes de convertirlos en orden.
  - Pertenece al módulo de carritos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `user_ID` → tb_users.`ID`. Relaciones entrantes: tbd_carts_items.`cart_ID`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `uk_cart_user` (`user_ID`). Acciones ON DELETE/UPDATE: fk_carts_user: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_carts_after_insert`, `trg_tb_carts_after_update`, `trg_tb_carts_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_carts = @ID + #user_ID + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `user_ID` | `int` | — | NO | Sin default | — | FK → tb_users.ID; UK | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `status` | `bit(1)` | 1 | Sí | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 4 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 5 | `last_update` | `datetime` | — | Sí | NULL | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`uk_cart_user\` (\`user_ID\`)`
- `CONSTRAINT \`fk_carts_user\` FOREIGN KEY (\`user_ID\`) REFERENCES \`tb_users\` (\`ID\`)`

**Relaciones**

- `user_ID` → `tb_users.ID`; sin acción referencial explícita
- Referenciada por `tbd_carts_items` mediante `cart_ID`.

**Triggers asociados:** `trg_tb_carts_after_insert`, `trg_tb_carts_after_update`, `trg_tb_carts_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `user_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID; UK | Cualitativa nominal | user_ID = {dígito} | user_ID ∈ {tb_users.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `status` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tb_order_cancellations`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** envíos, devoluciones y cancelaciones (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Registra solicitudes para cancelar órdenes de comprador, con usuario solicitante, motivo y estado del trámite.
  - Pertenece al módulo de envíos, devoluciones y cancelaciones (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `buyer_order_ID` → tb_buyer_orders.`ID`; `user_ID` → tb_users.`ID`. Relaciones entrantes: tb_refunds.`cancellation_ID`; tbd_cancellation_items.`cancellation_ID`.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_cancellations_buyer_order: sin acción referencial explícita; fk_cancellations_user: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_order_cancellations_after_insert`, `trg_tb_order_cancellations_after_update`, `trg_tb_order_cancellations_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_order_cancellations = @ID + #buyer_order_ID + #user_ID + reason + cancellation_status + request_date + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `buyer_order_ID` | `int unsigned` | — | NO | Sin default | — | FK → tb_buyer_orders.ID | Identifica o enlaza el registro con `tb_buyer_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `user_ID` | `int` | — | NO | Sin default | — | FK → tb_users.ID | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `reason` | `varchar(500)` | 500 | NO | Sin default | — | — | Explica el motivo indicado para cancelar la orden. (inferido). |
| 5 | `cancellation_status` | `enum('Requested','Approved','Rejected','Completed')` | 'Requested','Approved','Rejected','Completed' | NO | 'Requested' | — | — | Registra la etapa de la cancelación dentro del ENUM del flujo. (inferido). |
| 6 | `request_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Marca cuándo se presentó la solicitud de cancelación. (inferido). |
| 7 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 8 | `last_update` | `datetime` | — | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_cancellations_buyer_order\` (\`buyer_order_ID\`)`
- `KEY \`fk_cancellations_user\` (\`user_ID\`)`
- `CONSTRAINT \`fk_cancellations_buyer_order\` FOREIGN KEY (\`buyer_order_ID\`) REFERENCES \`tb_buyer_orders\` (\`ID\`)`
- `CONSTRAINT \`fk_cancellations_user\` FOREIGN KEY (\`user_ID\`) REFERENCES \`tb_users\` (\`ID\`)`

**Relaciones**

- `buyer_order_ID` → `tb_buyer_orders.ID`; sin acción referencial explícita
- `user_ID` → `tb_users.ID`; sin acción referencial explícita
- Referenciada por `tb_refunds` mediante `cancellation_ID`.
- Referenciada por `tbd_cancellation_items` mediante `cancellation_ID`.

**Triggers asociados:** `trg_tb_order_cancellations_after_insert`, `trg_tb_order_cancellations_after_update`, `trg_tb_order_cancellations_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `buyer_order_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_buyer_orders.ID | Cualitativa nominal | buyer_order_ID = {dígito} | buyer_order_ID ∈ {tb_buyer_orders.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_buyer_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `user_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID | Cualitativa nominal | user_ID = {dígito} | user_ID ∈ {tb_users.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `reason` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | reason = {carácter} | reason ∈ cadena(≤500); tipo varchar(500) | Explica el motivo indicado para cancelar la orden. (inferido). |
| `cancellation_status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Requested') | No | Cualitativa ordinal | cancellation_status = [ Requested \| Approved \| Rejected \| Completed ] | cancellation_status ∈ {Requested, Approved, Rejected, Completed}; tipo enum('Requested','Approved','Rejected','Completed') | Registra la etapa de la cancelación dentro del ENUM del flujo. (inferido). |
| `request_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | request_date = {fecha/hora} | request_date ∈ DATETIME; default CURRENT_TIMESTAMP | Marca cuándo se presentó la solicitud de cancelación. (inferido). |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tb_orders`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** órdenes (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa órdenes del modelo principal vinculadas a una cuenta, con importe, estado y dirección de envío en texto.
  - Pertenece al módulo de órdenes (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `user_id` → tb_users.`ID`. Relaciones entrantes: tb_payments.`order_id`.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_orders_user: ON DELETE CASCADE. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_orders_after_insert`, `trg_tb_orders_after_update`, `trg_tb_orders_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_orders = @ID + #user_id + total_amount + status + shipping_address + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `user_id` | `int` | — | NO | Sin default | — | FK → tb_users.ID | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `total_amount` | `decimal(10,2)` | 10,2 | NO | '0.00' | — | — | Guarda el importe total de la orden; puede derivarse de sus líneas de detalle, pero el DDL no declara una fórmula de actualización (inferido). |
| 4 | `status` | `enum('Pending','Processing','Shipped','Delivered','Cancelled')` | 'Pending','Processing','Shipped','Delivered','Cancelled' | NO | 'Pending' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT 'Pending'. |
| 5 | `shipping_address` | `text` | — | Sí | Sin default | — | — | Conserva la dirección de envío en texto libre; el formato interno no está normalizado por el DDL (inferido). |
| 6 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 7 | `last_update` | `datetime` | — | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_orders_user\` (\`user_id\`)`
- `CONSTRAINT \`fk_orders_user\` FOREIGN KEY (\`user_id\`) REFERENCES \`tb_users\` (\`ID\`) ON DELETE CASCADE`

**Relaciones**

- `user_id` → `tb_users.ID`; ON DELETE CASCADE
- Referenciada por `tb_payments` mediante `order_id`.

**Triggers asociados:** `trg_tb_orders_after_insert`, `trg_tb_orders_after_update`, `trg_tb_orders_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `user_id` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID | Cualitativa nominal | user_id = {dígito} | user_id ∈ {tb_users.ID}; ON DELETE cascade | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `total_amount` | Monovalor | Almacenado (derivable de la suma de tbd_order_details.subtotal; fórmula no declarada, inferido) | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0.00') | No | Cuantitativa continua | total_amount = {número real} | total_amount ∈ ℝ, precisión 10,2; decimal(10,2); sin rango adicional salvo CHECK explícito | Guarda el importe total de la orden; puede derivarse de sus líneas de detalle, pero el DDL no declara una fórmula de actualización (inferido). |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Pending') | No | Cualitativa ordinal | status = [ Pending \| Processing \| Shipped \| Delivered \| Cancelled ] | status ∈ {Pending, Processing, Shipped, Delivered, Cancelled}; tipo enum('Pending','Processing','Shipped','Delivered','Cancelled') | Indica el estado lógico del registro (inferido); usa DEFAULT 'Pending'. |
| `shipping_address` | Monovalor (contiene datos compuestos en texto libre) | Almacenado | Opcional (NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | shipping_address = {carácter} | shipping_address ∈ texto (text); formato no restringido por CHECK | Conserva la dirección de envío en texto libre; el formato interno no está normalizado por el DDL (inferido). |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tb_payment_transaction`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** pagos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Conserva los movimientos enviados o recibidos por la pasarela de pago, su importe, resultado y referencia externa.
  - Pertenece al módulo de pagos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `payment_ID` → tb_payments.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_payment_transaction_payment: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_payment_transaction_after_insert`, `trg_tb_payment_transaction_after_update`, `trg_tb_payment_transaction_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_payment_transaction = @ID + #payment_ID + transaction_type + amount + transaction_status + gateway_reference + response_message + transaction_date + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `payment_ID` | `int unsigned` | — | NO | Sin default | — | FK → tb_payments.ID | Identifica o enlaza el registro con `tb_payments.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `transaction_type` | `enum('Charge','Refund','Void')` | 'Charge','Refund','Void' | NO | 'Charge' | — | — | Distingue el tipo de movimiento financiero descrito por el ENUM (por ejemplo, cargo o reembolso). (inferido). |
| 4 | `amount` | `decimal(10,2)` | 10,2 | NO | Sin default | — | — | Registra el importe asociado a este movimiento del pago; la moneda no está declarada (inferido). (inferido). |
| 5 | `transaction_status` | `enum('Pending','Completed','Failed')` | 'Pending','Completed','Failed' | NO | 'Pending' | — | — | Registra el resultado o etapa del movimiento financiero. (inferido). |
| 6 | `gateway_reference` | `varchar(150)` | 150 | Sí | NULL | — | — | Conserva la referencia asignada por la pasarela para consultar o conciliar el movimiento. (inferido). |
| 7 | `response_message` | `varchar(500)` | 500 | Sí | NULL | — | — | Conserva el mensaje devuelto por la pasarela para explicar el resultado de la operación. (inferido). |
| 8 | `transaction_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra cuándo ocurrió el movimiento en la pasarela. (inferido). |
| 9 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 10 | `last_update` | `datetime` | — | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_payment_transaction_payment\` (\`payment_ID\`)`
- `CONSTRAINT \`fk_payment_transaction_payment\` FOREIGN KEY (\`payment_ID\`) REFERENCES \`tb_payments\` (\`ID\`)`

**Relaciones**

- `payment_ID` → `tb_payments.ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tb_payment_transaction_after_insert`, `trg_tb_payment_transaction_after_update`, `trg_tb_payment_transaction_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `payment_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_payments.ID | Cualitativa nominal | payment_ID = {dígito} | payment_ID ∈ {tb_payments.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_payments.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `transaction_type` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Charge') | No | Cualitativa nominal | transaction_type = [ Charge \| Refund \| Void ] | transaction_type ∈ {Charge, Refund, Void}; tipo enum('Charge','Refund','Void') | Distingue el tipo de movimiento financiero descrito por el ENUM (por ejemplo, cargo o reembolso). (inferido). |
| `amount` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa continua | amount = {número real} | amount ∈ ℝ, precisión 10,2; decimal(10,2); sin rango adicional salvo CHECK explícito | Registra el importe asociado a este movimiento del pago; la moneda no está declarada (inferido). (inferido). |
| `transaction_status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Pending') | No | Cualitativa ordinal | transaction_status = [ Pending \| Completed \| Failed ] | transaction_status ∈ {Pending, Completed, Failed}; tipo enum('Pending','Completed','Failed') | Registra el resultado o etapa del movimiento financiero. (inferido). |
| `gateway_reference` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | gateway_reference = {carácter} | gateway_reference ∈ cadena(≤150); tipo varchar(150) | Conserva la referencia asignada por la pasarela para consultar o conciliar el movimiento. (inferido). |
| `response_message` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | response_message = {carácter} | response_message ∈ cadena(≤500); tipo varchar(500) | Conserva el mensaje devuelto por la pasarela para explicar el resultado de la operación. (inferido). |
| `transaction_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | transaction_date = {fecha/hora} | transaction_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra cuándo ocurrió el movimiento en la pasarela. (inferido). |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tb_payments`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** pagos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Registra los pagos asociados a órdenes del modelo principal y al método de pago utilizado.
  - Pertenece al módulo de pagos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `payment_method_id` → tbc_payment_methods.`ID`; `order_id` → tb_orders.`ID`; `user_payment_method_ID` → tbd_user_payment_methods.`ID`. Relaciones entrantes: tb_payment_transaction.`payment_ID`; tb_refunds.`payment_ID`.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_payments_method: sin acción referencial explícita; fk_payments_order: ON DELETE CASCADE; fk_payments_user_method: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_payments_after_insert`, `trg_tb_payments_after_update`, `trg_tb_payments_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_payments = @ID + #order_id + #payment_method_id + #user_payment_method_ID + amount + payment_status + transaction_reference + payment_date`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `order_id` | `int unsigned` | — | NO | Sin default | — | FK → tb_orders.ID | Identifica o enlaza el registro con `tb_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `payment_method_id` | `int unsigned` | — | NO | Sin default | — | FK → tbc_payment_methods.ID | Identifica o enlaza el registro con `tbc_payment_methods.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `user_payment_method_ID` | `bigint unsigned` | — | Sí | NULL | — | FK → tbd_user_payment_methods.ID | Identifica o enlaza el registro con `tbd_user_payment_methods.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 5 | `amount` | `decimal(10,2)` | 10,2 | NO | Sin default | — | — | Guarda el importe asociado al pago; su precisión procede del tipo decimal y la moneda no está especificada (inferido). |
| 6 | `payment_status` | `enum('Pending','Completed','Failed','Refunded')` | 'Pending','Completed','Failed','Refunded' | NO | 'Pending' | — | — | Representa la etapa del pago dentro del conjunto ENUM declarado. |
| 7 | `transaction_reference` | `varchar(150)` | 150 | Sí | NULL | — | — | Guarda la referencia externa de la transacción para localizar el pago en el procesador o institución financiera (inferido). Es opcional y puede quedar NULL cuando el proveedor todavía no devuelve una referencia o el medio de pago no la proporciona (inferido). |
| 8 | `payment_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra la fecha y hora en que se registra el pago; si no se proporciona, el sistema asigna CURRENT_TIMESTAMP. El valor obligatorio permite ordenar y conciliar los pagos. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_payments_order\` (\`order_id\`)`
- `KEY \`fk_payments_method\` (\`payment_method_id\`)`
- `KEY \`fk_payments_user_method\` (\`user_payment_method_ID\`)`
- `CONSTRAINT \`fk_payments_method\` FOREIGN KEY (\`payment_method_id\`) REFERENCES \`tbc_payment_methods\` (\`ID\`)`
- `CONSTRAINT \`fk_payments_order\` FOREIGN KEY (\`order_id\`) REFERENCES \`tb_orders\` (\`ID\`) ON DELETE CASCADE`
- `CONSTRAINT \`fk_payments_user_method\` FOREIGN KEY (\`user_payment_method_ID\`) REFERENCES \`tbd_user_payment_methods\` (\`ID\`)`

**Relaciones**

- `payment_method_id` → `tbc_payment_methods.ID`; sin acción referencial explícita
- `order_id` → `tb_orders.ID`; ON DELETE CASCADE
- `user_payment_method_ID` → `tbd_user_payment_methods.ID`; sin acción referencial explícita
- Referenciada por `tb_payment_transaction` mediante `payment_ID`.
- Referenciada por `tb_refunds` mediante `payment_ID`.

**Triggers asociados:** `trg_tb_payments_after_insert`, `trg_tb_payments_after_update`, `trg_tb_payments_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `order_id` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_orders.ID | Cualitativa nominal | order_id = {dígito} | order_id ∈ {tb_orders.ID}; ON DELETE cascade | Identifica o enlaza el registro con `tb_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `payment_method_id` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tbc_payment_methods.ID | Cualitativa nominal | payment_method_id = {dígito} | payment_method_id ∈ {tbc_payment_methods.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbc_payment_methods.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `user_payment_method_ID` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | FK → tbd_user_payment_methods.ID | Cualitativa nominal | user_payment_method_ID = {dígito} | user_payment_method_ID ∈ {tbd_user_payment_methods.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbd_user_payment_methods.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `amount` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa continua | amount = {número real} | amount ∈ ℝ, precisión 10,2; decimal(10,2); sin rango adicional salvo CHECK explícito | Guarda el importe asociado al pago; su precisión procede del tipo decimal y la moneda no está especificada (inferido). |
| `payment_status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Pending') | No | Cualitativa ordinal | payment_status = [ Pending \| Completed \| Failed \| Refunded ] | payment_status ∈ {Pending, Completed, Failed, Refunded}; tipo enum('Pending','Completed','Failed','Refunded') | Representa la etapa del pago dentro del conjunto ENUM declarado. |
| `transaction_reference` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | transaction_reference = {carácter alfanumérico} | transaction_reference ∈ cadena(≤150); tipo varchar(150) | Guarda la referencia externa de la transacción para localizar el pago en el procesador o institución financiera (inferido). Es opcional y puede quedar NULL cuando el proveedor todavía no devuelve una referencia o el medio de pago no la proporciona (inferido). |
| `payment_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | payment_date = {fecha/hora} | payment_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra la fecha y hora en que se registra el pago; si no se proporciona, el sistema asigna CURRENT_TIMESTAMP. El valor obligatorio permite ordenar y conciliar los pagos. |

### `tb_refunds`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** envíos, devoluciones y cancelaciones (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Registra importes devueltos y su vínculo opcional con una devolución o una cancelación.
  - Pertenece al módulo de envíos, devoluciones y cancelaciones (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `cancellation_ID` → tb_order_cancellations.`ID`; `payment_ID` → tb_payments.`ID`; `return_ID` → tb_returns.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_refunds_cancellation: sin acción referencial explícita; fk_refunds_payment: sin acción referencial explícita; fk_refunds_return: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_refunds_after_insert`, `trg_tb_refunds_after_update`, `trg_tb_refunds_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_refunds = @ID + #payment_ID + #return_ID + #cancellation_ID + amount + refund_status + reason + refund_date + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `payment_ID` | `int unsigned` | — | NO | Sin default | — | FK → tb_payments.ID | Identifica o enlaza el registro con `tb_payments.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `return_ID` | `int unsigned` | — | Sí | NULL | — | FK → tb_returns.ID | Identifica o enlaza el registro con `tb_returns.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `cancellation_ID` | `int unsigned` | — | Sí | NULL | — | FK → tb_order_cancellations.ID | Identifica o enlaza el registro con `tb_order_cancellations.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 5 | `amount` | `decimal(10,2)` | 10,2 | NO | Sin default | — | — | Registra el importe que se devuelve al cliente; la moneda no está declarada (inferido). (inferido). |
| 6 | `refund_status` | `enum('Pending','Processed','Rejected')` | 'Pending','Processed','Rejected' | NO | 'Pending' | — | — | Registra la etapa del reembolso dentro del ENUM del flujo. (inferido). |
| 7 | `reason` | `varchar(500)` | 500 | Sí | NULL | — | — | Describe el motivo del reembolso. (inferido). |
| 8 | `refund_date` | `datetime` | — | Sí | NULL | — | — | Registra cuándo se procesó o registró el reembolso. (inferido). |
| 9 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 10 | `last_update` | `datetime` | — | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_refunds_payment\` (\`payment_ID\`)`
- `KEY \`fk_refunds_return\` (\`return_ID\`)`
- `KEY \`fk_refunds_cancellation\` (\`cancellation_ID\`)`
- `CONSTRAINT \`fk_refunds_cancellation\` FOREIGN KEY (\`cancellation_ID\`) REFERENCES \`tb_order_cancellations\` (\`ID\`)`
- `CONSTRAINT \`fk_refunds_payment\` FOREIGN KEY (\`payment_ID\`) REFERENCES \`tb_payments\` (\`ID\`)`
- `CONSTRAINT \`fk_refunds_return\` FOREIGN KEY (\`return_ID\`) REFERENCES \`tb_returns\` (\`ID\`)`

**Relaciones**

- `cancellation_ID` → `tb_order_cancellations.ID`; sin acción referencial explícita
- `payment_ID` → `tb_payments.ID`; sin acción referencial explícita
- `return_ID` → `tb_returns.ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tb_refunds_after_insert`, `trg_tb_refunds_after_update`, `trg_tb_refunds_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `payment_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_payments.ID | Cualitativa nominal | payment_ID = {dígito} | payment_ID ∈ {tb_payments.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_payments.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `return_ID` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | FK → tb_returns.ID | Cualitativa nominal | return_ID = {dígito} | return_ID ∈ {tb_returns.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_returns.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `cancellation_ID` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | FK → tb_order_cancellations.ID | Cualitativa nominal | cancellation_ID = {dígito} | cancellation_ID ∈ {tb_order_cancellations.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_order_cancellations.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `amount` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa continua | amount = {número real} | amount ∈ ℝ, precisión 10,2; decimal(10,2); sin rango adicional salvo CHECK explícito | Registra el importe que se devuelve al cliente; la moneda no está declarada (inferido). (inferido). |
| `refund_status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Pending') | No | Cualitativa ordinal | refund_status = [ Pending \| Processed \| Rejected ] | refund_status ∈ {Pending, Processed, Rejected}; tipo enum('Pending','Processed','Rejected') | Registra la etapa del reembolso dentro del ENUM del flujo. (inferido). |
| `reason` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | reason = {carácter} | reason ∈ cadena(≤500); tipo varchar(500) | Describe el motivo del reembolso. (inferido). |
| `refund_date` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | refund_date = {fecha/hora} | refund_date ∈ DATETIME; default NULL | Registra cuándo se procesó o registró el reembolso. (inferido). |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tb_returns`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** envíos, devoluciones y cancelaciones (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa solicitudes de devolución asociadas a una orden de comprador y su estado de atención.
  - Pertenece al módulo de envíos, devoluciones y cancelaciones (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `buyer_order_ID` → tb_buyer_orders.`ID`; `user_ID` → tb_users.`ID`. Relaciones entrantes: tb_refunds.`return_ID`.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_returns_buyer_order: sin acción referencial explícita; fk_returns_user: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_returns_after_insert`, `trg_tb_returns_after_update`, `trg_tb_returns_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_returns = @ID + #buyer_order_ID + #user_ID + reason + return_status + request_date + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `buyer_order_ID` | `int unsigned` | — | NO | Sin default | — | FK → tb_buyer_orders.ID | Identifica o enlaza el registro con `tb_buyer_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `user_ID` | `int` | — | NO | Sin default | — | FK → tb_users.ID | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `reason` | `varchar(500)` | 500 | NO | Sin default | — | — | Describe el motivo indicado para devolver artículos. (inferido). |
| 5 | `return_status` | `enum('Requested','Approved','Rejected','Received','Refunded')` | 'Requested','Approved','Rejected','Received','Refunded' | NO | 'Requested' | — | — | Registra la etapa de la devolución dentro del ENUM del flujo. (inferido). |
| 6 | `request_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra cuándo se solicitó la devolución. (inferido). |
| 7 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 8 | `last_update` | `datetime` | — | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_returns_buyer_order\` (\`buyer_order_ID\`)`
- `KEY \`fk_returns_user\` (\`user_ID\`)`
- `CONSTRAINT \`fk_returns_buyer_order\` FOREIGN KEY (\`buyer_order_ID\`) REFERENCES \`tb_buyer_orders\` (\`ID\`)`
- `CONSTRAINT \`fk_returns_user\` FOREIGN KEY (\`user_ID\`) REFERENCES \`tb_users\` (\`ID\`)`

**Relaciones**

- `buyer_order_ID` → `tb_buyer_orders.ID`; sin acción referencial explícita
- `user_ID` → `tb_users.ID`; sin acción referencial explícita
- Referenciada por `tb_refunds` mediante `return_ID`.

**Triggers asociados:** `trg_tb_returns_after_insert`, `trg_tb_returns_after_update`, `trg_tb_returns_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `buyer_order_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_buyer_orders.ID | Cualitativa nominal | buyer_order_ID = {dígito} | buyer_order_ID ∈ {tb_buyer_orders.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_buyer_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `user_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID | Cualitativa nominal | user_ID = {dígito} | user_ID ∈ {tb_users.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `reason` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | reason = {carácter} | reason ∈ cadena(≤500); tipo varchar(500) | Describe el motivo indicado para devolver artículos. (inferido). |
| `return_status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Requested') | No | Cualitativa ordinal | return_status = [ Requested \| Approved \| Rejected \| Received \| Refunded ] | return_status ∈ {Requested, Approved, Rejected, Received, Refunded}; tipo enum('Requested','Approved','Rejected','Received','Refunded') | Registra la etapa de la devolución dentro del ENUM del flujo. (inferido). |
| `request_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | request_date = {fecha/hora} | request_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra cuándo se solicitó la devolución. (inferido). |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tb_shipments`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** envíos, devoluciones y cancelaciones (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Registra el envío de una orden, la dirección de destino, la transportista, el rastreo y las fechas logísticas.
  - Pertenece al módulo de envíos, devoluciones y cancelaciones (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `address_ID` → tb_user_addresses.`ID`; `buyer_order_ID` → tb_buyer_orders.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_shipments_address: sin acción referencial explícita; fk_shipments_buyer_order: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_shipments_after_insert`, `trg_tb_shipments_after_update`, `trg_tb_shipments_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_shipments = @ID + #buyer_order_ID + #address_ID + carrier + tracking_number + shipment_status + shipped_date + estimated_delivery_date + delivered_date + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `buyer_order_ID` | `int unsigned` | — | NO | Sin default | — | FK → tb_buyer_orders.ID | Identifica o enlaza el registro con `tb_buyer_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `address_ID` | `bigint unsigned` | — | NO | Sin default | — | FK → tb_user_addresses.ID | Identifica o enlaza el registro con `tb_user_addresses.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `carrier` | `varchar(100)` | 100 | Sí | NULL | — | — | Guarda el nombre de la empresa transportista encargada del envío. (inferido). |
| 5 | `tracking_number` | `varchar(100)` | 100 | Sí | NULL | — | — | Conserva el código que permite consultar el recorrido del paquete con la transportista. (inferido). |
| 6 | `shipment_status` | `enum('Preparing','Shipped','In transit','Delivered','Returned')` | 'Preparing','Shipped','In transit','Delivered','Returned' | NO | 'Preparing' | — | — | Registra la etapa logística del envío dentro del ENUM declarado. (inferido). |
| 7 | `shipped_date` | `datetime` | — | Sí | NULL | — | — | Registra cuándo la transportista recibió o despachó el paquete. (inferido). |
| 8 | `estimated_delivery_date` | `datetime` | — | Sí | NULL | — | — | Registra la fecha estimada de entrega comunicada para el envío. (inferido). |
| 9 | `delivered_date` | `datetime` | — | Sí | NULL | — | — | Registra cuándo se marcó el paquete como entregado. (inferido). |
| 10 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 11 | `last_update` | `datetime` | — | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_shipments_buyer_order\` (\`buyer_order_ID\`)`
- `KEY \`fk_shipments_address\` (\`address_ID\`)`
- `CONSTRAINT \`fk_shipments_address\` FOREIGN KEY (\`address_ID\`) REFERENCES \`tb_user_addresses\` (\`ID\`)`
- `CONSTRAINT \`fk_shipments_buyer_order\` FOREIGN KEY (\`buyer_order_ID\`) REFERENCES \`tb_buyer_orders\` (\`ID\`)`

**Relaciones**

- `address_ID` → `tb_user_addresses.ID`; sin acción referencial explícita
- `buyer_order_ID` → `tb_buyer_orders.ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tb_shipments_after_insert`, `trg_tb_shipments_after_update`, `trg_tb_shipments_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `buyer_order_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_buyer_orders.ID | Cualitativa nominal | buyer_order_ID = {dígito} | buyer_order_ID ∈ {tb_buyer_orders.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_buyer_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `address_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_user_addresses.ID | Cualitativa nominal | address_ID = {dígito} | address_ID ∈ {tb_user_addresses.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_user_addresses.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `carrier` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | carrier = {carácter} | carrier ∈ cadena(≤100); tipo varchar(100) | Guarda el nombre de la empresa transportista encargada del envío. (inferido). |
| `tracking_number` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | tracking_number = {carácter} | tracking_number ∈ cadena(≤100); tipo varchar(100) | Conserva el código que permite consultar el recorrido del paquete con la transportista. (inferido). |
| `shipment_status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Preparing') | No | Cualitativa ordinal | shipment_status = [ Preparing \| Shipped \| In transit \| Delivered \| Returned ] | shipment_status ∈ {Preparing, Shipped, In transit, Delivered, Returned}; tipo enum('Preparing','Shipped','In transit','Delivered','Returned') | Registra la etapa logística del envío dentro del ENUM declarado. (inferido). |
| `shipped_date` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | shipped_date = {fecha/hora} | shipped_date ∈ DATETIME; default NULL | Registra cuándo la transportista recibió o despachó el paquete. (inferido). |
| `estimated_delivery_date` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | estimated_delivery_date = {fecha/hora} | estimated_delivery_date ∈ DATETIME; default NULL | Registra la fecha estimada de entrega comunicada para el envío. (inferido). |
| `delivered_date` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | delivered_date = {fecha/hora} | delivered_date ∈ DATETIME; default NULL | Registra cuándo se marcó el paquete como entregado. (inferido). |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tb_user_addresses`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** principal (tb_). **Módulo:** usuarios (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Conserva direcciones de entrega de usuarios, sus datos de contacto, coordenadas e instrucciones.
  - Pertenece al módulo de usuarios (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `user_ID` → tb_users.`ID`. Relaciones entrantes: tb_shipments.`address_ID`; tbd_address_components.`address_ID`.
  - Reglas SQL: CHECK ((((`latitude` is null) and (`longitude` is null)) or ((`latitude` is not null) and (`longitude` is not null)))); CHECK ((`latitude` between -(90) and 90)); CHECK ((`longitude` between -(180) and 180)); sin UNIQUE. Acciones ON DELETE/UPDATE: fk_addresses_users: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_user_addresses_after_insert`, `trg_tb_user_addresses_after_update`, `trg_tb_user_addresses_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_user_addresses = @ID + #user_ID + address_label + recipient_name + recipient_phone + delivery_instructions + latitude + longitude + is_default + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `bigint unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `user_ID` | `int` | — | NO | Sin default | — | FK → tb_users.ID | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `address_label` | `varchar(100)` | 100 | NO | Sin default | — | — | Guarda la etiqueta que permite al usuario distinguir esta dirección, por ejemplo casa o trabajo (inferido). Es obligatoria y la aporta el usuario al registrar la dirección. |
| 4 | `recipient_name` | `varchar(150)` | 150 | Sí | NULL | — | — | Guarda el nombre de quien recibirá el envío (inferido). Es opcional y se captura cuando el destinatario difiere del titular o se necesita identificarlo para la entrega (inferido). |
| 5 | `recipient_phone` | `varchar(25)` | 25 | Sí | NULL | — | — | Guarda un teléfono de contacto para coordinar la entrega (inferido). Es opcional y se captura cuando hace falta contactar al destinatario (inferido). |
| 6 | `delivery_instructions` | `varchar(500)` | 500 | Sí | NULL | — | — | Guarda indicaciones para localizar el domicilio o completar la entrega (inferido). Es opcional porque la dirección puede registrarse sin instrucciones adicionales; el usuario las aporta cuando son necesarias (inferido). |
| 7 | `latitude` | `decimal(10,7)` | 10,7 | Sí | NULL | — | — | Guarda la latitud geográfica; CHECK limita el valor al intervalo de −90 a 90 y chk_coordinates exige pareja con longitude. |
| 8 | `longitude` | `decimal(10,7)` | 10,7 | Sí | NULL | — | — | Guarda la longitud geográfica; CHECK limita el valor al intervalo de −180 a 180 y chk_coordinates exige pareja con latitude. |
| 9 | `is_default` | `tinyint(1)` | 1 | NO | '0' | — | — | Indica si el método de pago se marca como preferido para el usuario, según el nombre de la columna (inferido). |
| 10 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 11 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 12 | `last_update` | `datetime` | — | Sí | NULL | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`idx_user_addresses\` (\`user_ID\`)`
- `CONSTRAINT \`fk_addresses_users\` FOREIGN KEY (\`user_ID\`) REFERENCES \`tb_users\` (\`ID\`)`
- `CONSTRAINT \`chk_coordinates\` CHECK ((((\`latitude\` is null) and (\`longitude\` is null)) or ((\`latitude\` is not null) and (\`longitude\` is not null))))`
- `CONSTRAINT \`chk_latitude\` CHECK ((\`latitude\` between -(90) and 90))`
- `CONSTRAINT \`chk_longitude\` CHECK ((\`longitude\` between -(180) and 180))`

**Relaciones**

- `user_ID` → `tb_users.ID`; sin acción referencial explícita
- Referenciada por `tb_shipments` mediante `address_ID`.
- Referenciada por `tbd_address_components` mediante `address_ID`.

**Triggers asociados:** `trg_tb_user_addresses_after_insert`, `trg_tb_user_addresses_after_update`, `trg_tb_user_addresses_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo bigint unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `user_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID | Cualitativa nominal | user_ID = {dígito} | user_ID ∈ {tb_users.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `address_label` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | address_label = {carácter} | address_label ∈ cadena(≤100); tipo varchar(100) | Guarda la etiqueta que permite al usuario distinguir esta dirección, por ejemplo casa o trabajo (inferido). Es obligatoria y la aporta el usuario al registrar la dirección. |
| `recipient_name` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | recipient_name = {carácter} | recipient_name ∈ cadena(≤150); tipo varchar(150) | Guarda el nombre de quien recibirá el envío (inferido). Es opcional y se captura cuando el destinatario difiere del titular o se necesita identificarlo para la entrega (inferido). |
| `recipient_phone` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | recipient_phone = {carácter} | recipient_phone ∈ cadena(≤25); tipo varchar(25) | Guarda un teléfono de contacto para coordinar la entrega (inferido). Es opcional y se captura cuando hace falta contactar al destinatario (inferido). |
| `delivery_instructions` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | delivery_instructions = {carácter} | delivery_instructions ∈ cadena(≤500); tipo varchar(500) | Guarda indicaciones para localizar el domicilio o completar la entrega (inferido). Es opcional porque la dirección puede registrarse sin instrucciones adicionales; el usuario las aporta cuando son necesarias (inferido). |
| `latitude` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa continua | coordenadas = latitude + longitude | latitude ∈ ℝ, precisión 10,7; decimal(10,7); sin rango adicional salvo CHECK explícito; CHECK ((((`latitude` is null) and (`longitude` is null)) or ((`latitude` is not null) and (`longitude` is not null)))) y ((`latitude` between -(90) and 90)) | Guarda la latitud geográfica; CHECK limita el valor al intervalo de −90 a 90 y chk_coordinates exige pareja con longitude. |
| `longitude` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa continua | coordenadas = latitude + longitude | longitude ∈ ℝ, precisión 10,7; decimal(10,7); sin rango adicional salvo CHECK explícito; CHECK ((((`latitude` is null) and (`longitude` is null)) or ((`latitude` is not null) and (`longitude` is not null)))) y ((`longitude` between -(180) and 180)) | Guarda la longitud geográfica; CHECK limita el valor al intervalo de −180 a 180 y chk_coordinates exige pareja con latitude. |
| `is_default` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0') | No | Cualitativa nominal | is_default = {entero} | is_default ∈ ℤ; tipo tinyint(1) | Indica si el método de pago se marca como preferido para el usuario, según el nombre de la columna (inferido). |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tbd_address_components`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** direcciones (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Desglosa una dirección en componentes tipados y permite una relación jerárquica entre componentes.
  - Pertenece al módulo de direcciones (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `address_ID` → tb_user_addresses.`ID`; `address_ID`, `address_sup_ID` → tbd_address_components.`address_ID`, `ID`. Relaciones entrantes: tbd_address_components.`address_ID`, `address_sup_ID`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `uk_address_component` (`address_ID`,`ID`). Acciones ON DELETE/UPDATE: fk_component_address: ON DELETE RESTRICT; fk_component_parent: ON DELETE RESTRICT. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbd_address_components_after_insert`, `trg_tbd_address_components_after_update`, `trg_tbd_address_components_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_address_components = @ID + #address_ID + value + component_type + status + #address_sup_ID + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `bigint unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK; UK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `address_ID` | `bigint unsigned` | — | NO | Sin default | — | FK → tbd_address_components.address_ID; UK | Identifica o enlaza el registro con `tbd_address_components.address_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `value` | `varchar(255)` | 255 | NO | Sin default | — | — | Guarda el contenido de un componente individual de la dirección, como una calle o localidad (inferido). Es obligatorio y se captura al desglosar la dirección para poder consultar cada componente junto con su tipo. |
| 4 | `component_type` | `varchar(50)` | 50 | NO | Sin default | — | — | Indica qué clase de dato contiene `value`, por ejemplo calle, ciudad o código postal (inferido). Es obligatorio y se captura al estructurar la dirección para interpretar cada componente. |
| 5 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 6 | `address_sup_ID` | `bigint unsigned` | — | Sí | NULL | — | FK → tbd_address_components.ID | Identifica o enlaza el registro con `tbd_address_components.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 7 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 8 | `last_update` | `datetime` | — | Sí | NULL | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`uk_address_component\` (\`address_ID\`,\`ID\`)`
- `KEY \`idx_address_parent\` (\`address_ID\`,\`address_sup_ID\`)`
- `CONSTRAINT \`fk_component_address\` FOREIGN KEY (\`address_ID\`) REFERENCES \`tb_user_addresses\` (\`ID\`) ON DELETE RESTRICT`
- `CONSTRAINT \`fk_component_parent\` FOREIGN KEY (\`address_ID\`, \`address_sup_ID\`) REFERENCES \`tbd_address_components\` (\`address_ID\`, \`ID\`) ON DELETE RESTRICT`

**Relaciones**

- `address_ID` → `tb_user_addresses.ID`; ON DELETE RESTRICT
- `address_ID, address_sup_ID` → `tbd_address_components.address_ID, ID`; ON DELETE RESTRICT
- Referenciada por `tbd_address_components` mediante `address_ID, address_sup_ID`.

**Triggers asociados:** `trg_tbd_address_components_after_insert`, `trg_tbd_address_components_after_update`, `trg_tbd_address_components_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK; UK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo bigint unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `address_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tbd_address_components.address_ID; UK | Cualitativa nominal | address_ID = {dígito} | address_ID ∈ {tb_user_addresses.ID}; ON DELETE restrict; address_ID ∈ {tbd_address_components.address_ID}; ON DELETE restrict | Identifica o enlaza el registro con `tbd_address_components.address_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `value` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | value = {carácter} | value ∈ cadena(≤255); tipo varchar(255) | Guarda el contenido de un componente individual de la dirección, como una calle o localidad (inferido). Es obligatorio y se captura al desglosar la dirección para poder consultar cada componente junto con su tipo. |
| `component_type` | Multivalor resuelto mediante tabla tbd_address_components | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | component_type = {carácter} | component_type ∈ cadena(≤50); tipo varchar(50) | Indica qué clase de dato contiene `value`, por ejemplo calle, ciudad o código postal (inferido). Es obligatorio y se captura al estructurar la dirección para interpretar cada componente. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `address_sup_ID` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | FK → tbd_address_components.ID | Cualitativa nominal | address_sup_ID = {dígito} | address_sup_ID ∈ {tbd_address_components.ID}; ON DELETE restrict | Identifica o enlaza el registro con `tbd_address_components.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tbd_cancellation_items`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** envíos, devoluciones y cancelaciones (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Detalla qué líneas y cantidades de una orden se incluyen en una solicitud de cancelación.
  - Pertenece al módulo de envíos, devoluciones y cancelaciones (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `cancellation_ID` → tb_order_cancellations.`ID`; `order_item_ID` → tbd_order_items.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_cancellation_items_cancellation: sin acción referencial explícita; fk_cancellation_items_order_item: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbd_cancellation_items_after_insert`, `trg_tbd_cancellation_items_after_update`, `trg_tbd_cancellation_items_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_cancellation_items = @#cancellation_ID + @#order_item_ID + quantity + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `cancellation_ID` | `int unsigned` | — | NO | Sin default | — | PK compuesta (cancellation_ID, order_item_ID); FK → tb_order_cancellations.ID | Identifica o enlaza el registro con `tb_order_cancellations.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 2 | `order_item_ID` | `int unsigned` | — | NO | Sin default | — | PK compuesta (cancellation_ID, order_item_ID); FK → tbd_order_items.ID | Identifica o enlaza el registro con `tbd_order_items.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `quantity` | `int unsigned` | — | NO | '1' | — | — | Registra cuántas unidades de la línea original se pretende cancelar; el DDL no exige quantity > 0. (inferido). |
| 4 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 5 | `last_update` | `datetime` | — | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`cancellation_ID\`,\`order_item_ID\`)`
- `KEY \`fk_cancellation_items_order_item\` (\`order_item_ID\`)`
- `CONSTRAINT \`fk_cancellation_items_cancellation\` FOREIGN KEY (\`cancellation_ID\`) REFERENCES \`tb_order_cancellations\` (\`ID\`)`
- `CONSTRAINT \`fk_cancellation_items_order_item\` FOREIGN KEY (\`order_item_ID\`) REFERENCES \`tbd_order_items\` (\`ID\`)`

**Relaciones**

- `cancellation_ID` → `tb_order_cancellations.ID`; sin acción referencial explícita
- `order_item_ID` → `tbd_order_items.ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tbd_cancellation_items_after_insert`, `trg_tbd_cancellation_items_after_update`, `trg_tbd_cancellation_items_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `cancellation_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (cancellation_ID, order_item_ID); FK → tb_order_cancellations.ID | Cualitativa nominal | cancellation_ID = {dígito} | cancellation_ID ∈ {tb_order_cancellations.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_order_cancellations.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `order_item_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (cancellation_ID, order_item_ID); FK → tbd_order_items.ID | Cualitativa nominal | order_item_ID = {dígito} | order_item_ID ∈ {tbd_order_items.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbd_order_items.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `quantity` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '1') | No | Cuantitativa discreta | quantity = {entero} | quantity ∈ ℤ⁺ ∪ {0}; tipo int unsigned | Registra cuántas unidades de la línea original se pretende cancelar; el DDL no exige quantity > 0. (inferido). |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tbd_carts_items`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** carritos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Relaciona carritos con productos y proveedores, indicando la cantidad solicitada.
  - Pertenece al módulo de carritos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `cart_ID` → tb_carts.`ID`; `provider_ID`, `product_ID` → tbd_products_users_providers.`user_ID`, `product_ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: CHECK ((`quantity` > 0)); sin UNIQUE. Acciones ON DELETE/UPDATE: fk_cart_items_cart: sin acción referencial explícita; fk_cart_items_provider_product: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbd_carts_items_after_insert`, `trg_tbd_carts_items_after_update`, `trg_tbd_carts_items_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_carts_items = @#cart_ID + @#provider_ID + @#product_ID + quantity + creation_date`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `cart_ID` | `int unsigned` | — | NO | Sin default | — | PK compuesta (cart_ID, provider_ID, product_ID); FK → tb_carts.ID | Identifica o enlaza el registro con `tb_carts.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 2 | `provider_ID` | `int` | — | NO | Sin default | — | PK compuesta (cart_ID, provider_ID, product_ID); FK → tbd_products_users_providers.user_ID | Identifica o enlaza el registro con `tbd_products_users_providers.user_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `product_ID` | `int unsigned` | — | NO | Sin default | — | PK compuesta (cart_ID, provider_ID, product_ID); FK → tbd_products_users_providers.product_ID | Identifica o enlaza el registro con `tbd_products_users_providers.product_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `quantity` | `int unsigned` | — | NO | '1' | — | — | Indica cuántas unidades del producto contiene esta línea; los CHECK aplicables definen el mínimo permitido. |
| 5 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`cart_ID\`,\`provider_ID\`,\`product_ID\`)`
- `KEY \`idx_cart_provider_product\` (\`provider_ID\`,\`product_ID\`)`
- `CONSTRAINT \`fk_cart_items_cart\` FOREIGN KEY (\`cart_ID\`) REFERENCES \`tb_carts\` (\`ID\`)`
- `CONSTRAINT \`fk_cart_items_provider_product\` FOREIGN KEY (\`provider_ID\`, \`product_ID\`) REFERENCES \`tbd_products_users_providers\` (\`user_ID\`, \`product_ID\`)`
- `CONSTRAINT \`chk_cart_quantity\` CHECK ((\`quantity\` > 0))`

**Relaciones**

- `cart_ID` → `tb_carts.ID`; sin acción referencial explícita
- `provider_ID, product_ID` → `tbd_products_users_providers.user_ID, product_ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tbd_carts_items_after_insert`, `trg_tbd_carts_items_after_update`, `trg_tbd_carts_items_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `cart_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (cart_ID, provider_ID, product_ID); FK → tb_carts.ID | Cualitativa nominal | cart_ID = {dígito} | cart_ID ∈ {tb_carts.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_carts.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `provider_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (cart_ID, provider_ID, product_ID); FK → tbd_products_users_providers.user_ID | Cualitativa nominal | provider_ID = {dígito} | provider_ID ∈ {tbd_products_users_providers.user_ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbd_products_users_providers.user_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `product_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (cart_ID, provider_ID, product_ID); FK → tbd_products_users_providers.product_ID | Cualitativa nominal | product_ID = {dígito} | product_ID ∈ {tbd_products_users_providers.product_ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbd_products_users_providers.product_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `quantity` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '1') | No | Cuantitativa discreta | quantity = {entero} | quantity ∈ ℤ⁺; tipo int unsigned; CHECK ((`quantity` > 0)) | Indica cuántas unidades del producto contiene esta línea; los CHECK aplicables definen el mínimo permitido. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tbd_order_items`

- **Total de registros:** No verificable en el respaldo. 
- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** órdenes (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Conserva las líneas de las órdenes de comprador con nombre histórico, cantidad, precio unitario e importe.
  - Pertenece al módulo de órdenes (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `buyer_order_ID` → tb_buyer_orders.`ID`; `provider_ID`, `product_ID` → tbd_products_users_providers.`user_ID`, `product_ID`. Relaciones entrantes: tbd_cancellation_items.`order_item_ID`.
  - Reglas SQL: CHECK ((`quantity` > 0)); CHECK ((`unit_price` >= 0)); sin UNIQUE. Acciones ON DELETE/UPDATE: fk_order_items_buyer_order: sin acción referencial explícita; fk_order_items_provider_product: sin acción referencial explícita. Columnas generadas: subtotal decimal(12,2).
  - Triggers asociados: `trg_tbd_order_items_after_insert`, `trg_tbd_order_items_after_update`, `trg_tbd_order_items_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_order_items = @ID + #buyer_order_ID + #product_ID + #provider_ID + product_name + quantity + unit_price + subtotal + creation_date`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int unsigned` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `buyer_order_ID` | `int unsigned` | — | NO | Sin default | — | FK → tb_buyer_orders.ID | Identifica o enlaza el registro con `tb_buyer_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `product_ID` | `int unsigned` | — | NO | Sin default | — | FK → tbd_products_users_providers.product_ID | Identifica o enlaza el registro con `tbd_products_users_providers.product_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `provider_ID` | `int` | — | NO | Sin default | — | FK → tbd_products_users_providers.user_ID | Identifica o enlaza el registro con `tbd_products_users_providers.user_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 5 | `product_name` | `varchar(255)` | 255 | NO | Sin default | — | — | Guarda el nombre del producto mostrado en esta línea de la orden; probablemente se copia del catálogo al crearla para conservar el detalle histórico (inferido). Es obligatorio y permite identificar el artículo en el comprobante aunque cambie su nombre en el catálogo. |
| 6 | `quantity` | `int unsigned` | — | NO | Sin default | — | — | Indica cuántas unidades del producto contiene esta línea; los CHECK aplicables definen el mínimo permitido. |
| 7 | `unit_price` | `decimal(12,2)` | 12,2 | NO | Sin default | — | — | Guarda el precio unitario aplicado a la línea; el SQL determina su precisión y puede imponer un límite mediante CHECK. |
| 8 | `subtotal` | `decimal(12,2)` | 12,2 | Sí | Sin default | GENERATED STORED | — | Almacena un valor calculado por la base de datos; fórmula `((`quantity` * `unit_price`))` y columna generada según DDL. |
| 9 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_order_items_buyer_order\` (\`buyer_order_ID\`)`
- `KEY \`idx_order_items_provider_product\` (\`provider_ID\`,\`product_ID\`)`
- `CONSTRAINT \`fk_order_items_buyer_order\` FOREIGN KEY (\`buyer_order_ID\`) REFERENCES \`tb_buyer_orders\` (\`ID\`)`
- `CONSTRAINT \`fk_order_items_provider_product\` FOREIGN KEY (\`provider_ID\`, \`product_ID\`) REFERENCES \`tbd_products_users_providers\` (\`user_ID\`, \`product_ID\`)`
- `CONSTRAINT \`chk_order_items_quantity\` CHECK ((\`quantity\` > 0))`
- `CONSTRAINT \`chk_order_items_unit_price\` CHECK ((\`unit_price\` >= 0))`

**Relaciones**

- `buyer_order_ID` → `tb_buyer_orders.ID`; sin acción referencial explícita
- `provider_ID, product_ID` → `tbd_products_users_providers.user_ID, product_ID`; sin acción referencial explícita
- Referenciada por `tbd_cancellation_items` mediante `order_item_ID`.

**Triggers asociados:** `trg_tbd_order_items_after_insert`, `trg_tbd_order_items_after_update`, `trg_tbd_order_items_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int unsigned; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `buyer_order_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_buyer_orders.ID | Cualitativa nominal | buyer_order_ID = {dígito} | buyer_order_ID ∈ {tb_buyer_orders.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_buyer_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `product_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tbd_products_users_providers.product_ID | Cualitativa nominal | product_ID = {dígito} | product_ID ∈ {tbd_products_users_providers.product_ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbd_products_users_providers.product_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `provider_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tbd_products_users_providers.user_ID | Cualitativa nominal | provider_ID = {dígito} | provider_ID ∈ {tbd_products_users_providers.user_ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbd_products_users_providers.user_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `product_name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | product_name = {carácter} | product_name ∈ cadena(≤255); tipo varchar(255) | Guarda el nombre del producto mostrado en esta línea de la orden; probablemente se copia del catálogo al crearla para conservar el detalle histórico (inferido). Es obligatorio y permite identificar el artículo en el comprobante aunque cambie su nombre en el catálogo. |
| `quantity` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa discreta | quantity = {entero} | quantity ∈ ℤ⁺; tipo int unsigned; CHECK ((`quantity` > 0)) | Indica cuántas unidades del producto contiene esta línea; los CHECK aplicables definen el mínimo permitido. |
| `unit_price` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa continua | unit_price = {número real} | unit_price ∈ ℝ, precisión 12,2; decimal(12,2); sin rango adicional salvo CHECK explícito; CHECK ((`unit_price` >= 0)) | Guarda el precio unitario aplicado a la línea; el SQL determina su precisión y puede imponer un límite mediante CHECK. |
| `subtotal` | Monovalor | Derivado: ((`quantity` * `unit_price`)) | Opcional (NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa continua | subtotal = quantity × unit_price | subtotal ∈ ℝ, precisión 12,2; decimal(12,2); sin rango adicional salvo CHECK explícito | Almacena un valor calculado por la base de datos; fórmula `((`quantity` * `unit_price`))` y columna generada según DDL. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

## Vistas

### `vw_trazabilidad_cancelaciones_ordenes`

- **Propósito:** presenta trazabilidad de cancelaciones ordenes mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tb_order_cancellations`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_carritos`

- **Propósito:** presenta trazabilidad de carritos mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tb_carts`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_categorias`

- **Propósito:** presenta trazabilidad de categorias mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tbc_categories`, `tbd_products_categories`.
- **Columnas expuestas:** `categoria_id` (tipo derivado de expresión; origen en SELECT), `categoria_nombre` (tipo derivado de expresión; origen en SELECT), `categoria_descripcion` (tipo derivado de expresión; origen en SELECT), `categoria_padre` (tipo derivado de expresión; origen en SELECT), `estado` (tipo derivado de expresión; origen en SELECT), `total_productos_asociados` (tipo derivado de expresión; origen en SELECT), `fecha_creacion` (tipo derivado de expresión; origen en SELECT), `ultima_actualizacion` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_componentes_direccion`

- **Propósito:** presenta trazabilidad de componentes direccion mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tbd_address_components`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_detalle_cancelaciones`

- **Propósito:** presenta trazabilidad de detalle cancelaciones mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tbd_cancellation_items`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_detalle_devoluciones`

- **Propósito:** presenta trazabilidad de detalle devoluciones mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tbd_return_items`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_devoluciones`

- **Propósito:** presenta trazabilidad de devoluciones mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tb_returns`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_direcciones_usuario`

- **Propósito:** presenta trazabilidad de direcciones usuario mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tb_user_addresses`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_envios`

- **Propósito:** presenta trazabilidad de envios mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tb_shipments`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_items_carrito`

- **Propósito:** presenta trazabilidad de items carrito mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tbd_carts_items`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_items_orden_comprador`

- **Propósito:** presenta trazabilidad de items orden comprador mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tbd_order_items`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_metodos_pago`

- **Propósito:** presenta trazabilidad de metodos pago mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tbc_payment_methods`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_ordenes`

- **Propósito:** presenta trazabilidad de ordenes mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tb_orders`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_ordenes_comprador`

- **Propósito:** presenta trazabilidad de ordenes comprador mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tb_buyer_orders`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_pagos`

- **Propósito:** presenta trazabilidad de pagos mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tb_payments`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_personas`

- **Propósito:** presenta trazabilidad de personas mediante la consulta definida en SQL (inferido).
- **Tablas base:** `mysql`, `tb_people`, `tb_users`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `person_ID` (tipo derivado de expresión; origen en SELECT), `user_ID` (tipo derivado de expresión; origen en SELECT), `user_nickname` (tipo derivado de expresión; origen en SELECT), `user_email` (tipo derivado de expresión; origen en SELECT), `full_name` (tipo derivado de expresión; origen en SELECT), `phone` (tipo derivado de expresión; origen en SELECT), `country_code` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `roles` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_productos`

- **Propósito:** presenta trazabilidad de productos mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tb_products`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_productos_categorias`

- **Propósito:** presenta trazabilidad de productos categorias mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tbd_products_categories`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_proveedores_productos`

- **Propósito:** presenta trazabilidad de proveedores productos mediante la consulta definida en SQL (inferido).
- **Tablas base:** `mysql`, `tbd_products_users_providers`, `tb_users`, `tb_products`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `user_ID` (tipo derivado de expresión; origen en SELECT), `provider_nickname` (tipo derivado de expresión; origen en SELECT), `provider_email` (tipo derivado de expresión; origen en SELECT), `product_ID` (tipo derivado de expresión; origen en SELECT), `product_name` (tipo derivado de expresión; origen en SELECT), `type_ownership` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `roles` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_reembolsos`

- **Propósito:** presenta trazabilidad de reembolsos mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tb_refunds`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_tipos_metodos_pago`

- **Propósito:** presenta trazabilidad de tipos metodos pago mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tbc_payment_methods_types`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_transacciones_pago`

- **Propósito:** presenta trazabilidad de transacciones pago mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tb_payment_transaction`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_usuario_metodos_pago`

- **Propósito:** presenta trazabilidad de usuario metodos pago mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tbd_user_payment_methods`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_usuarios_creados`

- **Propósito:** presenta trazabilidad de usuarios creados mediante la consulta definida en SQL (inferido).
- **Tablas base:** `mysql`, `tb_users`.
- **Columnas expuestas:** `nickname` (tipo derivado de expresión; origen en SELECT), `email` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `roles` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_usuarios_wishlist_productos`

- **Propósito:** presenta trazabilidad de usuarios wishlist productos mediante la consulta definida en SQL (inferido).
- **Tablas base:** `tb_logs`, `tbd_users_wishlist_products`.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

## Triggers

| Nombre | Tabla | Evento | Momento | Registro en tb_logs |
|---|---|---|---|---|
| `trg_tb_buyer_orders_after_insert` | `tb_buyer_orders` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Orden de comprador creado.  ID= , seller_ID= NULL , subtotal= NULL , shipping_cost= NULL , fulfillment_status= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_buyer_orders_after_update` | `tb_buyer_orders` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Orden de comprador actualizado.  ID= . Cambios:  ,  seller_ID: [ NULL ] -> [ NULL ] subtotal: [ NULL ] -> [ NULL ] shipping_cost: [ NULL ] -> [ NULL ] fulfillment_status: [ NULL ] -> [ NULL ] status: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_buyer_orders_after_delete` | `tb_buyer_orders` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Orden de comprador eliminado.  ID= , seller_ID= NULL , subtotal= NULL , shipping_cost= NULL , fulfillment_status= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_carts_after_insert` | `tb_carts` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Carrito creado.  ID= , user_ID= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_carts_after_update` | `tb_carts` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Carrito actualizado.  ID= . Cambios:  ,  user_ID: [ NULL ] -> [ NULL ] status: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_carts_after_delete` | `tb_carts` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Carrito eliminado.  ID= , user_ID= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_order_cancellations_after_insert` | `tb_order_cancellations` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_order_cancellations_after_update` | `tb_order_cancellations` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Cancelación de orden actualizada.  ID= . Cambios:  ,  buyer_order_ID: [ NULL ] -> [ NULL ] user_ID: [ NULL ] -> [ NULL ] cancellation_status: [ NULL ] -> [ NULL ] reason modificado` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_order_cancellations_after_delete` | `tb_order_cancellations` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_orders_after_insert` | `tb_orders` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Orden creado.  ID= , user_id= NULL , total_amount= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_orders_after_update` | `tb_orders` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Orden actualizado.  ID= . Cambios:  ,  user_id: [ NULL ] -> [ NULL ] total_amount: [ NULL ] -> [ NULL ] status: [ NULL ] -> [ NULL ] shipping_address modificado` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_orders_after_delete` | `tb_orders` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Orden eliminado.  ID= , user_id= NULL , total_amount= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_payment_transaction_after_insert` | `tb_payment_transaction` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_payment_transaction_after_update` | `tb_payment_transaction` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Transacción de pago actualizada.  ID= . Cambios:  ,  payment_ID: [ NULL ] -> [ NULL ] transaction_type: [ NULL ] -> [ NULL ] amount: [ NULL ] -> [ NULL ] transaction_status: [ NULL ] -> [ NULL ] gateway_reference: [ NULL ] -> [ NULL ] response_message modificado` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_payment_transaction_after_delete` | `tb_payment_transaction` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_payments_after_insert` | `tb_payments` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Pago creado.  ID= , order_id= NULL , payment_method_id= NULL , amount= NULL , payment_status= NULL , transaction_reference= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_payments_after_update` | `tb_payments` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Pago actualizado.  ID= . Cambios:  ,  order_id: [ NULL ] -> [ NULL ] payment_method_id: [ NULL ] -> [ NULL ] amount: [ NULL ] -> [ NULL ] payment_status: [ NULL ] -> [ NULL ] transaction_reference: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_payments_after_delete` | `tb_payments` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Pago eliminado.  ID= , order_id= NULL , payment_method_id= NULL , amount= NULL , payment_status= NULL , transaction_reference= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_people_after_insert` | `tb_people` | INSERT | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `Persona creada. person_ID= , user_ID= , nombres= , apellidos= , teléfono= Sin registro` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_people_after_update` | `tb_people` | UPDATE | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `Persona actualizada. person_ID= . Cambios:  ,  nombres: [ ] -> [ ] apellidos: [ ] -> [ ] teléfono: [ NULL ] -> [ NULL ] país: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_people_after_delete` | `tb_people` | DELETE | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_products_after_insert` | `tb_products` | INSERT | AFTER | 
        table_name,
        operation,
        db_user,
        description,
        operation_date,
        operation_status
    ; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_products_after_update` | `tb_products` | UPDATE | AFTER | 
        table_name,
        operation,
        db_user,
        description,
        operation_date,
        operation_status
    ; description: `Producto actualizado. ID= . Cambios:  ,  SKU: [ NULL ] -> [ NULL ] name: [ NULL ] -> [ NULL ] description: [ NULL ] -> [ NULL ] price: [ 0 ] -> [ 0 ] stock: [ 0 ] -> [ 0 ] status: [ 0 ] -> [ 0 ]` (valores dinámicos NEW/OLD según operación). |
| `trg_products_after_delete` | `tb_products` | DELETE | AFTER | 
        table_name,
        operation,
        db_user,
        description,
        operation_date,
        operation_status
    ; description: `Producto eliminado. ID= , SKU= NULL , Nombre= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_refunds_after_insert` | `tb_refunds` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_refunds_after_update` | `tb_refunds` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Reembolso actualizado.  ID= . Cambios:  ,  payment_ID: [ NULL ] -> [ NULL ] return_ID: [ NULL ] -> [ NULL ] cancellation_ID: [ NULL ] -> [ NULL ] amount: [ NULL ] -> [ NULL ] refund_status: [ NULL ] -> [ NULL ] reason modificado refund_date: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_refunds_after_delete` | `tb_refunds` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_returns_after_insert` | `tb_returns` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_returns_after_update` | `tb_returns` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Devolución actualizada.  ID= . Cambios:  ,  buyer_order_ID: [ NULL ] -> [ NULL ] user_ID: [ NULL ] -> [ NULL ] return_status: [ NULL ] -> [ NULL ] reason modificado` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_returns_after_delete` | `tb_returns` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_shipments_after_insert` | `tb_shipments` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_shipments_after_update` | `tb_shipments` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Envío actualizado.  ID= . Cambios:  ,  buyer_order_ID: [ NULL ] -> [ NULL ] address_ID: [ NULL ] -> [ NULL ] carrier: [ NULL ] -> [ NULL ] tracking_number: [ NULL ] -> [ NULL ] shipment_status: [ NULL ] -> [ NULL ] shipped_date: [ NULL ] -> [ NULL ] estimated_delivery_date: [ NULL ] -> [ NULL ] delivered_date: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_shipments_after_delete` | `tb_shipments` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_user_addresses_after_insert` | `tb_user_addresses` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Dirección de usuario creada. ID= , user_ID= , etiqueta= , is_default= , status=` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_user_addresses_after_update` | `tb_user_addresses` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Dirección de usuario actualizada. ID= . Cambios:  ,  user_ID: [ ] -> [ ] etiqueta: [ ] -> [ ] recipient_name modificado recipient_phone modificado delivery_instructions modificado coordenadas modificadas is_default: [ ] -> [ ] status: [ ] -> [ ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_user_addresses_after_delete` | `tb_user_addresses` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Dirección de usuario eliminada. ID= , user_ID= , etiqueta= , status=` (valores dinámicos NEW/OLD según operación). |
| `trg_users_after_insert` | `tb_users` | INSERT | AFTER | 
        table_name,
        operation,
        db_user,
        description,
        operation_date,
        operation_status
    ; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_users_after_update` | `tb_users` | UPDATE | AFTER | 
        table_name,
        operation,
        db_user,
        description,
        operation_date,
        operation_status
    ; description: `Usuario actualizado. ID= . Cambios:  ,  email: [ NULL ] -> [ NULL ] nickname: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_users_after_delete` | `tb_users` | DELETE | AFTER | 
        table_name,
        operation,
        db_user,
        description,
        operation_date,
        operation_status
    ; description: `Usuario eliminado. ID= , email= NULL , nickname= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbc_categories_after_insert` | `tbc_categories` | INSERT | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbc_categories_after_update` | `tbc_categories` | UPDATE | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbc_categories_after_delete` | `tbc_categories` | DELETE | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbc_payment_methods_after_insert` | `tbc_payment_methods` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Método de pago creado.  ID= , name= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbc_payment_methods_after_update` | `tbc_payment_methods` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Método de pago actualizado.  ID= . Cambios:  ,  name: [ NULL ] -> [ NULL ] description modificado status: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbc_payment_methods_after_delete` | `tbc_payment_methods` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Método de pago eliminado.  ID= , name= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbc_payment_methods_types_after_insert` | `tbc_payment_methods_types` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Tipo de método de pago creado.  ID= , code= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbc_payment_methods_types_after_update` | `tbc_payment_methods_types` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Tipo de método de pago actualizado.  ID= . Cambios:  ,  code: [ NULL ] -> [ NULL ] description modificado status: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbc_payment_methods_types_after_delete` | `tbc_payment_methods_types` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Tipo de método de pago eliminado.  ID= , code= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_address_components_after_insert` | `tbd_address_components` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Componente de dirección creado. ID= , address_ID= , tipo= , address_sup_ID= NULL , status=` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_address_components_after_update` | `tbd_address_components` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Componente de dirección actualizado. ID= , address_ID= . Cambios:  ,  address_ID: [ ] -> [ ] value modificado tipo: [ ] -> [ ] address_sup_ID: [ NULL ] -> [ NULL ] status: [ ] -> [ ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_address_components_after_delete` | `tbd_address_components` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Componente de dirección eliminado. ID= , address_ID= , tipo= , address_sup_ID= NULL , status=` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_cancellation_items_after_insert` | `tbd_cancellation_items` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_cancellation_items_after_update` | `tbd_cancellation_items` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Producto de cancelación actualizado.  cancellation_ID= , order_item_ID= . Cambios:  ,  cancellation_ID: [ NULL ] -> [ NULL ] order_item_ID: [ NULL ] -> [ NULL ] quantity: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_cancellation_items_after_delete` | `tbd_cancellation_items` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_carts_items_after_insert` | `tbd_carts_items` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Ítem de carrito creado.  cart_ID= , provider_ID= , product_ID= , quantity= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_carts_items_after_update` | `tbd_carts_items` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Ítem de carrito actualizado.  cart_ID= , provider_ID= , product_ID= . Cambios:  ,  quantity: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_carts_items_after_delete` | `tbd_carts_items` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Ítem de carrito eliminado.  cart_ID= , provider_ID= , product_ID= , quantity= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_order_items_after_insert` | `tbd_order_items` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Ítem de orden de comprador creado.  ID= , buyer_order_ID= NULL , product_ID= NULL , provider_ID= NULL , product_name= NULL , quantity= NULL , unit_price= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_order_items_after_update` | `tbd_order_items` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Ítem de orden de comprador actualizado.  ID= . Cambios:  ,  buyer_order_ID: [ NULL ] -> [ NULL ] product_ID: [ NULL ] -> [ NULL ] provider_ID: [ NULL ] -> [ NULL ] product_name: [ NULL ] -> [ NULL ] quantity: [ NULL ] -> [ NULL ] unit_price: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_order_items_after_delete` | `tbd_order_items` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Ítem de orden de comprador eliminado.  ID= , buyer_order_ID= NULL , product_ID= NULL , provider_ID= NULL , product_name= NULL , quantity= NULL , unit_price= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_products_categories_after_insert` | `tbd_products_categories` | INSERT | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_products_categories_after_update` | `tbd_products_categories` | UPDATE | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_products_categories_after_delete` | `tbd_products_categories` | DELETE | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_products_users_providers_after_insert` | `tbd_products_users_providers` | INSERT | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_products_users_providers_after_update` | `tbd_products_users_providers` | UPDATE | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `Asociación proveedor-producto actualizada. user_ID= , product_ID= . Cambios:  ,  tipo: [ NULL ] -> [ NULL ] status: [ ] -> [ ] fecha: [ ] -> [ ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_products_users_providers_after_delete` | `tbd_products_users_providers` | DELETE | AFTER | 
        table_name,
        operation,
        db_user,
        operation_date,
        description,
        operation_status
    ; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_return_items_after_insert` | `tbd_return_items` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_return_items_after_update` | `tbd_return_items` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Producto de devolución actualizado.  return_ID= , order_item_ID= . Cambios:  ,  return_ID: [ NULL ] -> [ NULL ] order_item_ID: [ NULL ] -> [ NULL ] quantity: [ NULL ] -> [ NULL ] condition_notes modificado` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_return_items_after_delete` | `tbd_return_items` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `description sin plantilla CONCAT identificable` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_user_payment_methods_after_insert` | `tbd_user_payment_methods` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Método de pago de usuario creado.  ID= , user_ID= NULL , payment_method_type_ID= NULL , provider= NULL , label= NULL , last_four= NULL , is_default= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_user_payment_methods_after_update` | `tbd_user_payment_methods` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Método de pago de usuario actualizado.  ID= . Cambios:  ,  user_ID: [ NULL ] -> [ NULL ] payment_method_type_ID: [ NULL ] -> [ NULL ] provider: [ NULL ] -> [ NULL ] label: [ NULL ] -> [ NULL ] last_four: [ NULL ] -> [ NULL ] is_default: [ NULL ] -> [ NULL ] status: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_user_payment_methods_after_delete` | `tbd_user_payment_methods` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Método de pago de usuario eliminado.  ID= , user_ID= NULL , payment_method_type_ID= NULL , provider= NULL , label= NULL , last_four= NULL , is_default= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_users_wishlist_products_after_insert` | `tbd_users_wishlist_products` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Producto en lista de deseos creado.  user_ID= , product_ID= , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_users_wishlist_products_after_update` | `tbd_users_wishlist_products` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Producto en lista de deseos actualizado.  user_ID= , product_ID= . Cambios:  ,  status: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_users_wishlist_products_after_delete` | `tbd_users_wishlist_products` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Producto en lista de deseos eliminado.  user_ID= , product_ID= , status= NULL` (valores dinámicos NEW/OLD según operación). |

## Procedimientos

### `sp_generate_users`

- **Parámetros:** IN p_total INT; IN p_country CHAR(2); IN p_min_age INT; IN p_max_age INT; IN p_active_pct DECIMAL(5,2).
- **Pasos:** Valida parámetros y genera en lote cuentas y personas usando los catálogos y funciones fn_gen_*; controla la operación con transacción.
- **Tablas afectadas:** `tb_users`, `tb_people`, `tbc_gen_*`; `tb_logs` mediante triggers.
- **Ejemplo:** `CALL sp_generate_users(@p_total, @p_country, @p_min_age, @p_max_age, @p_active_pct);`

### `sp_gen_insert_user_person`

- **Parámetros:** IN p_email VARCHAR(80); IN p_nickname VARCHAR(100); IN p_password_hash VARCHAR(255); IN p_creation_date DATETIME; IN p_last_login DATETIME; IN p_status TINYINT; IN p_courtesy_title CHAR(10); IN p_given_names VARCHAR(150); IN p_family_names VARCHAR(150); IN p_birth_date DATE; IN p_gender_ID TINYINT UNSIGNED; IN p_country_code CHAR(2); IN p_phone VARCHAR(25); OUT p_user_id INT.
- **Pasos:** Inserta la cuenta en tb_users y su perfil en tb_people; devuelve el identificador mediante parámetro OUT.
- **Tablas afectadas:** `tb_users`, `tb_people`.
- **Ejemplo:** `CALL sp_gen_insert_user_person(@p_email, @p_nickname, @p_password_hash, @p_creation_date, @p_last_login, @p_status, @p_courtesy_title, @p_given_names, @p_family_names, @p_birth_date, @p_gender_ID, @p_country_code, @p_phone, @p_user_id);`

### `sp_gen_validate_params`

- **Parámetros:** IN p_total INT; IN p_country CHAR(2); IN p_min_age INT; IN p_max_age INT; IN p_active_pct DECIMAL(5,2).
- **Pasos:** Valida total, rango de edades, porcentaje activo y país; genera error SQL si algún parámetro no cumple sus límites.
- **Tablas afectadas:** `tbc_gen_country_profile`.
- **Ejemplo:** `CALL sp_gen_validate_params(@p_total, @p_country, @p_min_age, @p_max_age, @p_active_pct);`

### `sp_process_payment`

- **Parámetros:** IN p_order_id INT UNSIGNED; IN p_user_payment_method_id BIGINT UNSIGNED; IN p_payment_method_id INT UNSIGNED.
- **Pasos:** Realiza las validaciones y operaciones indicadas por su cuerpo SQL. (inferido)
- **Tablas afectadas:** Sin tablas modificadas detectables..
- **Ejemplo:** `CALL sp_process_payment(@p_order_id, @p_user_payment_method_id, @p_payment_method_id);`

### `sp_register_user_person`

- **Parámetros:** IN p_nickname VARCHAR(100); IN p_password VARCHAR(255); IN p_given_names VARCHAR(150); IN p_family_names VARCHAR(150); IN p_birth_date DATE; IN p_gender_ID TINYINT UNSIGNED; IN p_country_code CHAR(2); IN p_phone VARCHAR(25).
- **Pasos:** Valida los datos de una cuenta y registra el usuario junto con su perfil de persona como una operación coordinada; el propósito se infiere del nombre del procedimiento.
- **Tablas afectadas:** `tb_users`, `tb_people` (inferido).
- **Ejemplo:** `CALL sp_register_user_person(@p_nickname, @p_password, @p_given_names, @p_family_names, @p_birth_date, @p_gender_ID, @p_country_code, @p_phone);`

### `sp_soft_delete`

- **Parámetros:** IN p_table_name VARCHAR(64); IN p_record_id BIGINT UNSIGNED.
- **Pasos:** Valida el nombre de tabla y el identificador recibidos, y aplica el borrado lógico al registro indicado si la tabla está permitida.
- **Tablas afectadas:** Tabla indicada por p_table_name (dinámico).
- **Ejemplo:** `CALL sp_soft_delete(@p_table_name, @p_record_id);`

### `sp_soft_delete_product`

- **Parámetros:** IN p_product_id INT UNSIGNED.
- **Pasos:** Comprueba el producto solicitado y cambia su status a inactivo para conservar el registro y su historial.
- **Tablas afectadas:** `tb_products`.
- **Ejemplo:** `CALL sp_soft_delete_product(@p_product_id);`

### `sp_soft_delete_user`

- **Parámetros:** IN p_user_id INT UNSIGNED.
- **Pasos:** Comprueba la cuenta solicitada y cambia su status a inactivo para impedir su uso sin borrar su historial.
- **Tablas afectadas:** `tb_users`.
- **Ejemplo:** `CALL sp_soft_delete_user(@p_user_id);`

## Funciones

### `fn_gen_birth_date`
- **Parámetros:** `p_min_age INT, p_max_age INT`.
- **Retorno:** `date`.
- **Características:** NO SQL.
- **Qué hace:** Genera fecha de nacimiento aleatoria dentro del rango de edades indicado. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_birth_date(...);`

### `fn_gen_courtesy_title`
- **Parámetros:** `p_country CHAR(2), p_gender TINYINT UNSIGNED`.
- **Retorno:** `char(10)`.
- **Características:** READS SQL DATA.
- **Qué hace:** Devuelve el título de cortesía según país y género. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_courtesy_title(...);`

### `fn_gen_datetime_between`
- **Parámetros:** `p_from DATETIME, p_to DATETIME`.
- **Retorno:** `datetime`.
- **Características:** NO SQL.
- **Qué hace:** Genera DATETIME aleatorio entre dos límites. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_datetime_between(...);`

### `fn_gen_email`
- **Parámetros:** `p_given VARCHAR(60), p_family VARCHAR(60), p_seq BIGINT`.
- **Retorno:** `varchar(80)`.
- **Características:** NO SQL.
- **Qué hace:** Construye correo con nombre, apellido, secuencia y dominio de prueba. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_email(...);`

### `fn_gen_email_domain`
- **Parámetros:** ``.
- **Retorno:** `varchar(20)`.
- **Características:** NO SQL.
- **Qué hace:** Elige example.com, example.org o example.net. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_email_domain(...);`

### `fn_gen_family_name`
- **Parámetros:** `p_country CHAR(2)`.
- **Retorno:** `varchar(60)`.
- **Características:** READS SQL DATA.
- **Qué hace:** Selecciona apellido al azar del catálogo del país. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_family_name(...);`

### `fn_gen_gender_id`
- **Parámetros:** ``.
- **Retorno:** `tinyint`.
- **Características:** NO SQL.
- **Qué hace:** Devuelve aleatoriamente 1 o 2. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_gender_id(...);`

### `fn_gen_given_name`
- **Parámetros:** `p_country CHAR(2), p_gender TINYINT UNSIGNED`.
- **Retorno:** `varchar(60)`.
- **Características:** READS SQL DATA.
- **Qué hace:** Selecciona nombre al azar por país y género. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_given_name(...);`

### `fn_gen_is_active`
- **Parámetros:** `p_index INT, p_total INT, p_active_pct DECIMAL(5,2)`.
- **Retorno:** `tinyint`.
- **Características:** DETERMINISTIC, NO SQL.
- **Qué hace:** Distribuye el estado activo conforme al porcentaje solicitado. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_is_active(...);`

### `fn_gen_nickname`
- **Parámetros:** `p_given VARCHAR(60), p_family VARCHAR(60), p_seq BIGINT`.
- **Retorno:** `varchar(100)`.
- **Características:** DETERMINISTIC, NO SQL.
- **Qué hace:** Construye alias con inicial, apellido normalizado y secuencia. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_nickname(...);`

### `fn_gen_password_hash`
- **Parámetros:** ``.
- **Retorno:** `varchar(255)`.
- **Características:** NO SQL.
- **Qué hace:** Genera hash SHA-256 sobre texto aleatorio con UUID y RAND(). (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_password_hash(...);`

### `fn_gen_phone`
- **Parámetros:** `p_country CHAR(2)`.
- **Retorno:** `varchar(25)`.
- **Características:** READS SQL DATA.
- **Qué hace:** Construye teléfono con prefijo y longitud del perfil del país. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_phone(...);`

### `fn_gen_random_country`
- **Parámetros:** ``.
- **Retorno:** `char(2)`.
- **Características:** READS SQL DATA.
- **Qué hace:** Selecciona un país cuyo perfil esté activo. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_random_country(...);`

### `fn_gen_random_int`
- **Parámetros:** `p_min INT, p_max INT`.
- **Retorno:** `int`.
- **Características:** NO SQL.
- **Qué hace:** Devuelve entero aleatorio en el intervalo inclusivo indicado. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_random_int(...);`

### `fn_gen_slug`
- **Parámetros:** `p_text VARCHAR(150)`.
- **Retorno:** `varchar(150)`.
- **Características:** DETERMINISTIC, NO SQL.
- **Qué hace:** Normaliza a minúsculas y elimina espacios, apóstrofos, guiones y puntos. (descripción derivada del SQL).
- **Ejemplo:** `SELECT fn_gen_slug(...);`

## Catálogo de dominios

### ENUM

- `enum('Create','Read','Update','Delete')` — `tb_logs.operation`
- `enum('Pending','Accepted','Preparing','Sent','Delivered','Canceled','Returned')` — `tb_buyer_orders.fulfillment_status`
- `enum('Requested','Approved','Rejected','Completed')` — `tb_order_cancellations.cancellation_status`
- `enum('Pending','Processing','Shipped','Delivered','Cancelled')` — `tb_orders.status`
- `enum('Charge','Refund','Void')` — `tb_payment_transaction.transaction_type`
- `enum('Pending','Completed','Failed')` — `tb_payment_transaction.transaction_status`
- `enum('Pending','Completed','Failed','Refunded')` — `tb_payments.payment_status`
- `enum('Pending','Processed','Rejected')` — `tb_refunds.refund_status`
- `enum('Requested','Approved','Rejected','Received','Refunded')` — `tb_returns.return_status`
- `enum('Preparing','Shipped','In transit','Delivered','Returned')` — `tb_shipments.shipment_status`

### status

- `bit`: `tb_users.status (bit(1))`, `tbc_categories.status (bit(1))`, `tbc_gen_country_profile.status (bit(1))`, `tbc_payment_methods.status (bit(1))`, `tbc_payment_methods_types.status (bit(1))`, `tbd_products_categories.status (bit(1))`, `tb_buyer_orders.status (bit(1))`, `tb_carts.status (bit(1))`, `tb_user_addresses.status (bit(1))`, `tbd_address_components.status (bit(1))`.
- `tinyint`: `tb_products.status (tinyint)`.

## Convenciones de nombres

- `tb_`: tabla principal; `tbc_`: catálogo; `tbd_`: detalle/relación; `vw_`: vista; `trg_`: trigger; `sp_`: procedimiento; `fk_`: restricción FK; `uk_`: restricción UNIQUE; `chk_`: CHECK.
- `creation_date`, `last_update` y `status` son columnas de auditoría/estado cuando aparecen; el SQL define defaults y comportamiento concretos en cada tabla. `status` no se asume equivalente entre tipos.

## Observaciones de calidad del diseño

- **Alta —** `tbd_products_categories.category_ID` carece de FK a `tbc_categories`. Recomendación: declarar FK y decidir acciones referenciales.
- **Alta —** coexisten `tb_orders`/`tbd_order_details` y `tb_buyer_orders`/`tbd_order_items`; `tb_payments` referencia `tb_orders`, mientras envíos, devoluciones y cancelaciones referencian `tb_buyer_orders`. Recomendación: confirmar si son flujos distintos y definir un modelo canónico de pagos/órdenes.
- **Alta —** `tb_buyer_orders` solo guarda `seller_ID`; no identifica comprador. Recomendación: agregar vínculo al comprador si el proceso lo requiere.
- **Alta —** `tb_refunds.return_ID` y `cancellation_ID` son opcionales y no hay CHECK que exija exactamente uno. Recomendación: agregar CHECK/XOR o separar los tipos de origen.
- **Alta —** `tbd_return_items.quantity` y `tbd_cancellation_items.quantity` no tienen CHECK `quantity > 0`. Recomendación: agregar restricción positiva.
- **Media —** `tb_payments.transaction_reference` y `tb_payment_transaction.gateway_reference` pueden representar la misma referencia de pasarela. Recomendación: definir qué identificador es canónico y evitar duplicar valores divergentes.
- **Media —** tablas sin columna genérica `status`: `tb_order_cancellations`, `tb_payment_transaction`, `tb_people`, `tb_refunds`, `tb_returns`, `tb_shipments`, `tbd_cancellation_items`, `tbd_return_items`; varias tienen estados de proceso específicos. Recomendación: documentar si esos estados sustituyen deliberadamente a `status` y mantener transiciones válidas.
- **Media —** las llaves relacionadas usan tipos INT, INT UNSIGNED y BIGINT; `status` combina bit(1) y tinyint. Recomendación: normalizar tipos/signo y dominios documentando una migración compatible.
- **Media —** `tbd_carts_items` y `tbd_order_items` separan referencias a usuario y producto hacia `tbd_products_users_providers` en vez de declarar una FK compuesta. Recomendación: añadir integridad compuesta o validación equivalente.
- **Baja —** courtesy_title_ID y country_code sin catálogo ni FK: en `tb_people` son `char(10)` y `char(2)` respectivamente; tampoco existe `fk_people_courtesy_title` ni `fk_people_country`. Recomendación: incorporar catálogos y restricciones si esos códigos deben validarse.

**Referencias huérfanas:** las definiciones de BD19 no contienen referencias a `tbd_order_details`, `tbd_wishlist`, `tbd_shopping_cart` ni `tb_users_offer_products`; esas tablas no aparecen en esta versión. La ausencia de referencias se verifica en DDL, no en valores de filas.

## Pendientes por confirmar

- Confirmar con negocio si órdenes, pagos, devoluciones y envíos comparten una entidad canónica o pertenecen a flujos separados.
- Confirmar el catálogo y semántica de `tb_people.gender_ID`, `courtesy_title_ID` y `country_code`.
- Confirmar si `tb_people` tiene vínculo obligatorio 1:1 con `tb_users` y el uso de los perfiles.
- Confirmar qué pasarelas crean `gateway_reference` y `transaction_reference` y cómo se concilian.
- Confirmar cardinalidades no garantizadas por FK/UNIQUE y las inferencias de negocio señaladas en las fichas.
- En vistas, algunos tipos dependen de expresiones SQL; deben confirmarse con DESCRIBE en una instancia.
- Los mensajes de `description` de triggers incluyen valores NEW/OLD; su formato exacto depende del evento.


## Resumen estadístico

- Columnas clasificadas: 184.
- llave:FK: 32.
- llave:PK: 29.
- llave:UK: 14.
- naturaleza:Cualitativa nominal: 115.
- naturaleza:Cualitativa ordinal: 8.
- naturaleza:Cuantitativa (temporal): 46.
- naturaleza:Cuantitativa continua: 11.
- naturaleza:Cuantitativa discreta: 4.
- obligatoriedad:Obligatorio: 143.
- obligatoriedad:Opcional: 41.
- origen:Almacenado: 183.
- origen:Derivado: 1.

## Volumen de datos

Estructura y totales de registros obtenidos del respaldo BD19.sql (fecha del archivo: 2026-11-04 18:11:43 -06:00). Conteo de registros realizado el: 2026-11-04 18:44:17 -06:00. Los totales corresponden al respaldo, no a la instancia en vivo.
- Conteo de registros realizado el: 2026-11-04 18:44:17 -06:00. Los valores son conteos de filas INSERT del respaldo BD19.sql, no de la instancia en vivo.
- Total verificable: 106,834 registros en 11 tablas; 14 tablas sin INSERT no son verificables en el respaldo.

| Tabla | Registros | Porcentaje del total verificable |
|---|---:|---:|
| `tb_logs` | 65632 | 61.43% |
| `tb_products` | 15007 | 14.05% |
| `tb_users` | 10227 | 9.57% |
| `tb_people` | 10225 | 9.57% |
| `tbd_products_categories` | 5000 | 4.68% |
| `tbc_gen_given_names` | 344 | 0.32% |
| `tbc_gen_family_names` | 225 | 0.21% |
| `tbc_categories` | 160 | 0.15% |
| `tbc_gen_country_profile` | 12 | 0.01% |
| `tbc_payment_methods` | 1 | 0.00% |
| `tbc_payment_methods_types` | 1 | 0.00% |
| `tb_buyer_orders` | No verificable en el respaldo | — |
| `tb_carts` | No verificable en el respaldo | — |
| `tb_order_cancellations` | No verificable en el respaldo | — |
| `tb_orders` | No verificable en el respaldo | — |
| `tb_payment_transaction` | No verificable en el respaldo | — |
| `tb_payments` | No verificable en el respaldo | — |
| `tb_refunds` | No verificable en el respaldo | — |
| `tb_returns` | No verificable en el respaldo | — |
| `tb_shipments` | No verificable en el respaldo | — |
| `tb_user_addresses` | No verificable en el respaldo | — |
| `tbd_address_components` | No verificable en el respaldo | — |
| `tbd_cancellation_items` | No verificable en el respaldo | — |
| `tbd_carts_items` | No verificable en el respaldo | — |
| `tbd_order_items` | No verificable en el respaldo | — |
| **Total verificable** | **106834** | **100.00%** |

## Historial de cambios

- Fuente actualizada a BD19 (`Practica03/backups/BD19.sql`), versión MySQL 8.0.45.
- Esquema completo BD19: 29 tablas, 25 vistas, 75 triggers, 8 procedimientos, 15 funciones, 213 columnas y 38 FK.
- Este diccionario documenta 25 tablas, 25 vistas y 75 triggers. Selección: todas las tablas con filas verificables primero (11), luego tablas sin filas verificables hasta completar 25.

## Descripciones marcadas (inferido)

- Tabla `tb_logs`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_logs.table_name`: interpretación funcional o aporte inferido.
- Columna `tb_logs.operation`: interpretación funcional o aporte inferido.
- Columna `tb_logs.db_user`: interpretación funcional o aporte inferido.
- Columna `tb_logs.description`: interpretación funcional o aporte inferido.
- Columna `tb_logs.operation_date`: interpretación funcional o aporte inferido.
- Tabla `tb_people`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_people.user_ID`: interpretación funcional o aporte inferido.
- Columna `tb_people.courtesy_title_ID`: interpretación funcional o aporte inferido.
- Columna `tb_people.given_names`: interpretación funcional o aporte inferido.
- Columna `tb_people.family_names`: interpretación funcional o aporte inferido.
- Columna `tb_people.birth_date`: interpretación funcional o aporte inferido.
- Columna `tb_people.gender_ID`: interpretación funcional o aporte inferido.
- Columna `tb_people.country_code`: interpretación funcional o aporte inferido.
- Columna `tb_people.phone`: interpretación funcional o aporte inferido.
- Columna `tb_people.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_products`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_products.SKU`: interpretación funcional o aporte inferido.
- Columna `tb_products.name`: interpretación funcional o aporte inferido.
- Columna `tb_products.description`: interpretación funcional o aporte inferido.
- Columna `tb_products.current_price`: interpretación funcional o aporte inferido.
- Columna `tb_products.current_stock`: interpretación funcional o aporte inferido.
- Columna `tb_products.status`: interpretación funcional o aporte inferido.
- Columna `tb_products.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_products.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_users`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_users.email`: interpretación funcional o aporte inferido.
- Columna `tb_users.nickname`: interpretación funcional o aporte inferido.
- Columna `tb_users.password`: interpretación funcional o aporte inferido.
- Columna `tb_users.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_users.last_login`: interpretación funcional o aporte inferido.
- Columna `tb_users.status`: interpretación funcional o aporte inferido.
- Tabla `tbc_categories`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbc_categories.name`: interpretación funcional o aporte inferido.
- Columna `tbc_categories.description`: interpretación funcional o aporte inferido.
- Columna `tbc_categories.status`: interpretación funcional o aporte inferido.
- Columna `tbc_categories.creation_date`: interpretación funcional o aporte inferido.
- Columna `tbc_categories.last_update`: interpretación funcional o aporte inferido.
- Tabla `tbc_gen_country_profile`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbc_gen_country_profile.country_code`: interpretación funcional o aporte inferido.
- Columna `tbc_gen_country_profile.country_name`: interpretación funcional o aporte inferido.
- Columna `tbc_gen_country_profile.phone_prefix`: interpretación funcional o aporte inferido.
- Columna `tbc_gen_country_profile.phone_digits`: interpretación funcional o aporte inferido.
- Columna `tbc_gen_country_profile.title_male`: interpretación funcional o aporte inferido.
- Columna `tbc_gen_country_profile.title_female`: interpretación funcional o aporte inferido.
- Columna `tbc_gen_country_profile.status`: interpretación funcional o aporte inferido.
- Tabla `tbc_gen_family_names`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbc_gen_family_names.country_code`: interpretación funcional o aporte inferido.
- Columna `tbc_gen_family_names.name`: interpretación funcional o aporte inferido.
- Tabla `tbc_gen_given_names`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbc_gen_given_names.country_code`: interpretación funcional o aporte inferido.
- Columna `tbc_gen_given_names.gender_ID`: interpretación funcional o aporte inferido.
- Columna `tbc_gen_given_names.name`: interpretación funcional o aporte inferido.
- Tabla `tbc_payment_methods`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbc_payment_methods.name`: interpretación funcional o aporte inferido.
- Columna `tbc_payment_methods.description`: interpretación funcional o aporte inferido.
- Columna `tbc_payment_methods.status`: interpretación funcional o aporte inferido.
- Columna `tbc_payment_methods.creation_date`: interpretación funcional o aporte inferido.
- Tabla `tbc_payment_methods_types`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbc_payment_methods_types.code`: interpretación funcional o aporte inferido.
- Columna `tbc_payment_methods_types.description`: interpretación funcional o aporte inferido.
- Columna `tbc_payment_methods_types.status`: interpretación funcional o aporte inferido.
- Columna `tbc_payment_methods_types.creation_date`: interpretación funcional o aporte inferido.
- Columna `tbc_payment_methods_types.last_update`: interpretación funcional o aporte inferido.
- Tabla `tbd_products_categories`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_products_categories.category_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_products_categories.product_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_products_categories.status`: interpretación funcional o aporte inferido.
- Columna `tbd_products_categories.creation_date`: interpretación funcional o aporte inferido.
- Columna `tbd_products_categories.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_buyer_orders`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_buyer_orders.seller_ID`: interpretación funcional o aporte inferido.
- Columna `tb_buyer_orders.status`: interpretación funcional o aporte inferido.
- Columna `tb_buyer_orders.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_buyer_orders.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_carts`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_carts.user_ID`: interpretación funcional o aporte inferido.
- Columna `tb_carts.status`: interpretación funcional o aporte inferido.
- Columna `tb_carts.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_carts.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_order_cancellations`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_order_cancellations.buyer_order_ID`: interpretación funcional o aporte inferido.
- Columna `tb_order_cancellations.user_ID`: interpretación funcional o aporte inferido.
- Columna `tb_order_cancellations.reason`: interpretación funcional o aporte inferido.
- Columna `tb_order_cancellations.cancellation_status`: interpretación funcional o aporte inferido.
- Columna `tb_order_cancellations.request_date`: interpretación funcional o aporte inferido.
- Columna `tb_order_cancellations.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_order_cancellations.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_orders`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_orders.user_id`: interpretación funcional o aporte inferido.
- Columna `tb_orders.total_amount`: interpretación funcional o aporte inferido.
- Columna `tb_orders.status`: interpretación funcional o aporte inferido.
- Columna `tb_orders.shipping_address`: interpretación funcional o aporte inferido.
- Columna `tb_orders.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_orders.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_payment_transaction`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_payment_transaction.payment_ID`: interpretación funcional o aporte inferido.
- Columna `tb_payment_transaction.transaction_type`: interpretación funcional o aporte inferido.
- Columna `tb_payment_transaction.amount`: interpretación funcional o aporte inferido.
- Columna `tb_payment_transaction.transaction_status`: interpretación funcional o aporte inferido.
- Columna `tb_payment_transaction.gateway_reference`: interpretación funcional o aporte inferido.
- Columna `tb_payment_transaction.response_message`: interpretación funcional o aporte inferido.
- Columna `tb_payment_transaction.transaction_date`: interpretación funcional o aporte inferido.
- Columna `tb_payment_transaction.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_payment_transaction.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_payments`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_payments.order_id`: interpretación funcional o aporte inferido.
- Columna `tb_payments.payment_method_id`: interpretación funcional o aporte inferido.
- Columna `tb_payments.amount`: interpretación funcional o aporte inferido.
- Columna `tb_payments.transaction_reference`: interpretación funcional o aporte inferido.
- Tabla `tb_refunds`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_refunds.payment_ID`: interpretación funcional o aporte inferido.
- Columna `tb_refunds.amount`: interpretación funcional o aporte inferido.
- Columna `tb_refunds.refund_status`: interpretación funcional o aporte inferido.
- Columna `tb_refunds.reason`: interpretación funcional o aporte inferido.
- Columna `tb_refunds.refund_date`: interpretación funcional o aporte inferido.
- Columna `tb_refunds.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_refunds.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_returns`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_returns.buyer_order_ID`: interpretación funcional o aporte inferido.
- Columna `tb_returns.user_ID`: interpretación funcional o aporte inferido.
- Columna `tb_returns.reason`: interpretación funcional o aporte inferido.
- Columna `tb_returns.return_status`: interpretación funcional o aporte inferido.
- Columna `tb_returns.request_date`: interpretación funcional o aporte inferido.
- Columna `tb_returns.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_returns.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_shipments`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_shipments.buyer_order_ID`: interpretación funcional o aporte inferido.
- Columna `tb_shipments.address_ID`: interpretación funcional o aporte inferido.
- Columna `tb_shipments.carrier`: interpretación funcional o aporte inferido.
- Columna `tb_shipments.tracking_number`: interpretación funcional o aporte inferido.
- Columna `tb_shipments.shipment_status`: interpretación funcional o aporte inferido.
- Columna `tb_shipments.shipped_date`: interpretación funcional o aporte inferido.
- Columna `tb_shipments.estimated_delivery_date`: interpretación funcional o aporte inferido.
- Columna `tb_shipments.delivered_date`: interpretación funcional o aporte inferido.
- Columna `tb_shipments.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_shipments.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_user_addresses`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_user_addresses.user_ID`: interpretación funcional o aporte inferido.
- Columna `tb_user_addresses.address_label`: interpretación funcional o aporte inferido.
- Columna `tb_user_addresses.recipient_name`: interpretación funcional o aporte inferido.
- Columna `tb_user_addresses.recipient_phone`: interpretación funcional o aporte inferido.
- Columna `tb_user_addresses.delivery_instructions`: interpretación funcional o aporte inferido.
- Columna `tb_user_addresses.is_default`: interpretación funcional o aporte inferido.
- Columna `tb_user_addresses.status`: interpretación funcional o aporte inferido.
- Columna `tb_user_addresses.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_user_addresses.last_update`: interpretación funcional o aporte inferido.
- Tabla `tbd_address_components`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_address_components.address_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_address_components.value`: interpretación funcional o aporte inferido.
- Columna `tbd_address_components.component_type`: interpretación funcional o aporte inferido.
- Columna `tbd_address_components.status`: interpretación funcional o aporte inferido.
- Columna `tbd_address_components.creation_date`: interpretación funcional o aporte inferido.
- Columna `tbd_address_components.last_update`: interpretación funcional o aporte inferido.
- Tabla `tbd_cancellation_items`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_cancellation_items.cancellation_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_cancellation_items.order_item_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_cancellation_items.quantity`: interpretación funcional o aporte inferido.
- Columna `tbd_cancellation_items.creation_date`: interpretación funcional o aporte inferido.
- Columna `tbd_cancellation_items.last_update`: interpretación funcional o aporte inferido.
- Tabla `tbd_carts_items`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_carts_items.cart_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_carts_items.provider_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_carts_items.product_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_carts_items.creation_date`: interpretación funcional o aporte inferido.
- Tabla `tbd_order_items`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_order_items.buyer_order_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.product_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.provider_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.product_name`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.quantity`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.unit_price`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.subtotal`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.creation_date`: interpretación funcional o aporte inferido.

## Pendientes por confirmar — inferencias

- Confirmar con responsables de negocio las descripciones y módulos marcados (inferido).
- Confirmar el origen de captura de los campos no identificados como AUTO_INCREMENT o DEFAULT; el SQL no identifica la interfaz de captura.
- Confirmar fórmulas de importes almacenados derivables; solo se declaran como derivadas las expresiones GENERATED del DDL.

## Descripciones genéricas detectadas y reescritas

- `tb_payments.transaction_reference`
- `tb_payments.payment_date`
- `tb_products.SKU`
- `tb_products.current_price`
- `tb_products.current_stock`
- `tb_user_addresses.address_label`
- `tb_user_addresses.recipient_name`
- `tb_user_addresses.recipient_phone`
- `tb_user_addresses.delivery_instructions`
- `tbc_payment_methods_types.code`
- `tbd_address_components.value`
- `tbd_address_components.component_type`
- `tbd_order_items.product_name`
- `tbd_products_users_providers.type_ownership`
- `tbd_products_users_providers.avalaible_date`
- `tbd_user_payment_methods.provider`
- `tbd_user_payment_methods.provider_method_ref`

## Pendientes por confirmar — significado de columnas

- tb_payments.transaction_reference: confirmar qué pasarelas o medios pueden dejar la referencia NULL y el momento en que se recibe.
- tb_products.SKU: confirmar el estándar del código y si se captura manualmente o se importa desde otro sistema.
- tb_products.current_price: confirmar qué proceso o rol autoriza y actualiza el precio vigente.
- tb_products.current_stock: confirmar si el inventario se actualiza automáticamente con ventas y reposiciones.
- tb_user_addresses.address_label: confirmar las etiquetas de dirección permitidas y su captura en la aplicación.
- tb_user_addresses.recipient_name, recipient_phone y delivery_instructions: confirmar en qué operaciones de entrega son necesarios.
- tbc_payment_methods_types.code: confirmar el sistema que asigna los códigos del catálogo.
- tbd_address_components.value y component_type: confirmar los tipos de componente y las reglas para dividir/validar direcciones.
- tbd_order_items.product_name: confirmar si se guarda como copia histórica del nombre al crear la orden.
- tbd_products_users_providers.type_ownership y avalaible_date: confirmar cuándo se asigna el rol y qué evento define la fecha de disponibilidad.
- tbd_user_payment_methods.provider y provider_method_ref: confirmar el formato y el origen exacto de la referencia externa; no se infiere que contenga datos completos de tarjeta.
