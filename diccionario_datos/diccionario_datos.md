# Diccionario de datos — db_test

**Motor objetivo:** MySQL 8.0.36. Fuente de esquema: `BD13.sql`; las sentencias INSERT no se procesan.

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
- [Catálogo de dominios](#catálogo-de-dominios)
- [Convenciones](#convenciones-de-nombres)
- [Observaciones de calidad](#observaciones-de-calidad-del-diseño)
- [Pendientes por confirmar](#pendientes-por-confirmar)

## Tablas

### `tb_buyer_orders`

- **Prefijo/tipo:** principal (tb_). **Módulo:** órdenes (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tb_buyer_orders` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de órdenes (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `seller_ID` → tb_users.`ID`. Relaciones entrantes: tbd_order_items.`buyer_order_ID`.
  - Reglas SQL: CHECK ((`shipping_cost` >= 0)); CHECK ((`subtotal` >= 0)); sin UNIQUE. Acciones ON DELETE/UPDATE: fk_seller_orders_seller: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_buyer_orders_after_insert`, `trg_tb_buyer_orders_after_update`, `trg_tb_buyer_orders_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_buyer_orders = @ID + #seller_ID + subtotal + shipping_cost + fulfillment_status + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
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
- Referenciada por `tbd_order_items` mediante `buyer_order_ID`.

**Triggers asociados:** `trg_tb_buyer_orders_after_insert`, `trg_tb_buyer_orders_after_update`, `trg_tb_buyer_orders_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `seller_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID | Cualitativa nominal | seller_ID = {dígito} | seller_ID ∈ {tb_users.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `subtotal` | Monovalor | Almacenado (derivable de la suma de tbd_order_items.subtotal; fórmula no declarada, inferido) | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0.00') | No | Cuantitativa continua | subtotal = {número real} | subtotal ∈ ℝ, precisión 12,2; decimal(12,2); sin rango adicional salvo CHECK explícito; CHECK ((`subtotal` >= 0)) | Guarda o calcula el importe de esta línea de orden; si es GENERATED, su fórmula es la declarada en la expresión SQL. |
| `shipping_cost` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0.00') | No | Cuantitativa continua | shipping_cost = {número real} | shipping_cost ∈ ℝ, precisión 12,2; decimal(12,2); sin rango adicional salvo CHECK explícito; CHECK ((`shipping_cost` >= 0)) | Guarda el costo de envío de la orden; se sujeta al CHECK de no negatividad declarado en el DDL. |
| `fulfillment_status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Pending') | No | Cualitativa ordinal | fulfillment_status = [ Pending \| Accepted \| Preparing \| Sent \| Delivered \| Canceled \| Returned ] | fulfillment_status ∈ {Pending, Accepted, Preparing, Sent, Delivered, Canceled, Returned}; tipo enum('Pending','Accepted','Preparing','Sent','Delivered','Canceled','Returned') | Representa la etapa del cumplimiento de la orden dentro del conjunto ENUM ordenado del flujo. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tb_carts`

- **Prefijo/tipo:** principal (tb_). **Módulo:** carritos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tb_carts` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de carritos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `user_ID` → tb_users.`ID`. Relaciones entrantes: tbd_carts_items.`cart_ID`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `uk_cart_user` (`user_ID`). Acciones ON DELETE/UPDATE: fk_carts_user: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_carts_after_insert`, `trg_tb_carts_after_update`, `trg_tb_carts_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_carts = @ID + #user_ID + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
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
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `user_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID; UK | Cualitativa nominal | user_ID = {dígito} | user_ID ∈ {tb_users.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `status` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tb_logs`

- **Prefijo/tipo:** principal (tb_). **Módulo:** auditoría (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tb_logs` a partir de los nombres y tipos de sus atributos (inferido).
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

### `tb_orders`

- **Prefijo/tipo:** principal (tb_). **Módulo:** órdenes (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tb_orders` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de órdenes (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `user_id` → tb_users.`ID`. Relaciones entrantes: tb_payments.`order_id`; tbd_order_details.`order_id`.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_orders_user: ON DELETE CASCADE. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_orders_after_insert`, `trg_tb_orders_after_update`, `trg_tb_orders_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_orders = @ID + #user_id + total_amount + status + shipping_address + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
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
- Referenciada por `tbd_order_details` mediante `order_id`.

**Triggers asociados:** `trg_tb_orders_after_insert`, `trg_tb_orders_after_update`, `trg_tb_orders_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `user_id` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID | Cualitativa nominal | user_id = {dígito} | user_id ∈ {tb_users.ID}; ON DELETE cascade | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `total_amount` | Monovalor | Almacenado (derivable de la suma de tbd_order_details.subtotal; fórmula no declarada, inferido) | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0.00') | No | Cuantitativa continua | total_amount = {número real} | total_amount ∈ ℝ, precisión 10,2; decimal(10,2); sin rango adicional salvo CHECK explícito | Guarda el importe total de la orden; puede derivarse de sus líneas de detalle, pero el DDL no declara una fórmula de actualización (inferido). |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Pending') | No | Cualitativa ordinal | status = [ Pending \| Processing \| Shipped \| Delivered \| Cancelled ] | status ∈ {Pending, Processing, Shipped, Delivered, Cancelled}; tipo enum('Pending','Processing','Shipped','Delivered','Cancelled') | Indica el estado lógico del registro (inferido); usa DEFAULT 'Pending'. |
| `shipping_address` | Monovalor (contiene datos compuestos en texto libre) | Almacenado | Opcional (NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | shipping_address = {carácter} | shipping_address ∈ texto (text); formato no restringido por CHECK | Conserva la dirección de envío en texto libre; el formato interno no está normalizado por el DDL (inferido). |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tb_payments`

- **Prefijo/tipo:** principal (tb_). **Módulo:** pagos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tb_payments` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de pagos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `payment_method_id` → tbc_payment_methods.`ID`; `order_id` → tb_orders.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_payments_method: sin acción referencial explícita; fk_payments_order: ON DELETE CASCADE. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_payments_after_insert`, `trg_tb_payments_after_update`, `trg_tb_payments_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_payments = @ID + #order_id + #payment_method_id + amount + payment_status + transaction_reference + payment_date`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `order_id` | `int` | — | NO | Sin default | — | FK → tb_orders.ID | Identifica o enlaza el registro con `tb_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `payment_method_id` | `int` | — | NO | Sin default | — | FK → tbc_payment_methods.ID | Identifica o enlaza el registro con `tbc_payment_methods.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `amount` | `decimal(10,2)` | 10,2 | NO | Sin default | — | — | Guarda el importe asociado al pago; su precisión procede del tipo decimal y la moneda no está especificada (inferido). |
| 5 | `payment_status` | `enum('Pending','Completed','Failed','Refunded')` | 'Pending','Completed','Failed','Refunded' | NO | 'Pending' | — | — | Representa la etapa del pago dentro del conjunto ENUM declarado. |
| 6 | `transaction_reference` | `varchar(150)` | 150 | Sí | NULL | — | — | Guarda la referencia externa de la transacción para localizar el pago en el procesador o institución financiera (inferido). Es opcional y puede quedar NULL cuando el proveedor todavía no devuelve una referencia o el medio de pago no la proporciona (inferido). |
| 7 | `payment_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra la fecha y hora en que se registra el pago; si no se proporciona, el sistema asigna CURRENT_TIMESTAMP. El valor obligatorio permite ordenar y conciliar los pagos. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_payments_order\` (\`order_id\`)`
- `KEY \`fk_payments_method\` (\`payment_method_id\`)`
- `CONSTRAINT \`fk_payments_method\` FOREIGN KEY (\`payment_method_id\`) REFERENCES \`tbc_payment_methods\` (\`ID\`)`
- `CONSTRAINT \`fk_payments_order\` FOREIGN KEY (\`order_id\`) REFERENCES \`tb_orders\` (\`ID\`) ON DELETE CASCADE`

**Relaciones**

- `payment_method_id` → `tbc_payment_methods.ID`; sin acción referencial explícita
- `order_id` → `tb_orders.ID`; ON DELETE CASCADE

**Triggers asociados:** `trg_tb_payments_after_insert`, `trg_tb_payments_after_update`, `trg_tb_payments_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `order_id` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_orders.ID | Cualitativa nominal | order_id = {dígito} | order_id ∈ {tb_orders.ID}; ON DELETE cascade | Identifica o enlaza el registro con `tb_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `payment_method_id` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tbc_payment_methods.ID | Cualitativa nominal | payment_method_id = {dígito} | payment_method_id ∈ {tbc_payment_methods.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbc_payment_methods.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `amount` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa continua | amount = {número real} | amount ∈ ℝ, precisión 10,2; decimal(10,2); sin rango adicional salvo CHECK explícito | Guarda el importe asociado al pago; su precisión procede del tipo decimal y la moneda no está especificada (inferido). |
| `payment_status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT 'Pending') | No | Cualitativa ordinal | payment_status = [ Pending \| Completed \| Failed \| Refunded ] | payment_status ∈ {Pending, Completed, Failed, Refunded}; tipo enum('Pending','Completed','Failed','Refunded') | Representa la etapa del pago dentro del conjunto ENUM declarado. |
| `transaction_reference` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | transaction_reference = {carácter alfanumérico} | transaction_reference ∈ cadena(≤150); tipo varchar(150) | Guarda la referencia externa de la transacción para localizar el pago en el procesador o institución financiera (inferido). Es opcional y puede quedar NULL cuando el proveedor todavía no devuelve una referencia o el medio de pago no la proporciona (inferido). |
| `payment_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | payment_date = {fecha/hora} | payment_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra la fecha y hora en que se registra el pago; si no se proporciona, el sistema asigna CURRENT_TIMESTAMP. El valor obligatorio permite ordenar y conciliar los pagos. |

### `tb_products`

- **Prefijo/tipo:** principal (tb_). **Módulo:** productos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tb_products` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de productos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: ninguna FK declarada. Relaciones entrantes: tbd_order_details.`product_id`; tbd_products_categories.`product_ID`; tbd_products_users_providers.`product_ID`; tbd_users_wishlist_products.`product_ID`; tbd_wishlist.`product_id`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `SKU` (`SKU`). Acciones ON DELETE/UPDATE: sin FK salientes con acciones. Columnas generadas: ninguna.
  - Triggers asociados: `trg_products_after_insert`, `trg_products_after_update`, `trg_products_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_products = @ID + SKU + name + description + current_price + current_stock + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `SKU` | `varchar(50)` | 50 | NO | Sin default | — | UK | Guarda el código SKU que distingue el producto en el catálogo; se captura al dar de alta o importar el producto (inferido). Es obligatorio y único para localizar y controlar ese producto. |
| 3 | `name` | `varchar(250)` | 250 | NO | Sin default | — | — | Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido). |
| 4 | `description` | `text` | — | Sí | Sin default | — | — | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| 5 | `current_price` | `decimal(10,2)` | 10,2 | NO | '0.00' | — | — | Guarda el precio vigente del producto y se usa para calcular el importe de venta (inferido). Es obligatorio; si no se informa al insertar, comienza en 0.00 y luego se actualiza con el precio autorizado (inferido). |
| 6 | `current_stock` | `int` | — | NO | '0' | — | — | Guarda las unidades disponibles del producto y sirve para consultar y actualizar inventario (inferido). Es obligatorio; el sistema inicializa el valor en cero y el proceso de venta o reposición lo modifica (inferido). |
| 7 | `status` | `tinyint` | — | Sí | '1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT '1'. |
| 8 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 9 | `last_update` | `datetime` | — | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`SKU\` (\`SKU\`)`

**Relaciones**

- Sin FK salientes.
- Referenciada por `tbd_order_details` mediante `product_id`.
- Referenciada por `tbd_products_categories` mediante `product_ID`.
- Referenciada por `tbd_products_users_providers` mediante `product_ID`.
- Referenciada por `tbd_users_wishlist_products` mediante `product_ID`.
- Referenciada por `tbd_wishlist` mediante `product_id`.

**Triggers asociados:** `trg_products_after_insert`, `trg_products_after_update`, `trg_products_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `SKU` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | SKU = {carácter} | SKU ∈ cadena(≤50); tipo varchar(50) | Guarda el código SKU que distingue el producto en el catálogo; se captura al dar de alta o importar el producto (inferido). Es obligatorio y único para localizar y controlar ese producto. |
| `name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | name = {carácter} | name ∈ cadena(≤250); tipo varchar(250) | Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido). |
| `description` | Monovalor | Almacenado | Opcional (NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | description = {carácter} | description ∈ texto (text); formato no restringido por CHECK | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| `current_price` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0.00') | No | Cuantitativa continua | current_price = {número real} | current_price ∈ ℝ, precisión 10,2; decimal(10,2); sin rango adicional salvo CHECK explícito | Guarda el precio vigente del producto y se usa para calcular el importe de venta (inferido). Es obligatorio; si no se informa al insertar, comienza en 0.00 y luego se actualiza con el precio autorizado (inferido). |
| `current_stock` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0') | No | Cuantitativa discreta | current_stock = {entero} | current_stock ∈ ℤ⁺ ∪ {0}; tipo int | Guarda las unidades disponibles del producto y sirve para consultar y actualizar inventario (inferido). Es obligatorio; el sistema inicializa el valor en cero y el proceso de venta o reposición lo modifica (inferido). |
| `status` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT '1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ ℤ; tipo tinyint | Indica el estado lógico del registro (inferido); usa DEFAULT '1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tb_user_addresses`

- **Prefijo/tipo:** principal (tb_). **Módulo:** usuarios (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tb_user_addresses` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de usuarios (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `user_ID` → tb_users.`ID`. Relaciones entrantes: tbd_address_components.`address_ID`.
  - Reglas SQL: CHECK ((((`latitude` is null) and (`longitude` is null)) or ((`latitude` is not null) and (`longitude` is not null)))); CHECK ((`latitude` between -(90) and 90)); CHECK ((`longitude` between -(180) and 180)); sin UNIQUE. Acciones ON DELETE/UPDATE: fk_addresses_users: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tb_user_addresses_after_insert`, `trg_tb_user_addresses_after_update`, `trg_tb_user_addresses_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tb_user_addresses = @ID + #user_ID + address_label + recipient_name + recipient_phone + delivery_instructions + latitude + longitude + is_default + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `bigint` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
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
- Referenciada por `tbd_address_components` mediante `address_ID`.

**Triggers asociados:** `trg_tb_user_addresses_after_insert`, `trg_tb_user_addresses_after_update`, `trg_tb_user_addresses_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo bigint; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
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

### `tb_users`

- **Prefijo/tipo:** principal (tb_). **Módulo:** usuarios (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tb_users` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de usuarios (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: ninguna FK declarada. Relaciones entrantes: tb_buyer_orders.`seller_ID`; tb_carts.`user_ID`; tb_orders.`user_id`; tb_user_addresses.`user_ID`; tbd_products_users_providers.`user_ID`; tbd_user_payment_methods.`user_ID`; tbd_users_wishlist_products.`user_ID`; tbd_wishlist.`user_id`.
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
- Referenciada por `tb_buyer_orders` mediante `seller_ID`.
- Referenciada por `tb_carts` mediante `user_ID`.
- Referenciada por `tb_orders` mediante `user_id`.
- Referenciada por `tb_user_addresses` mediante `user_ID`.
- Referenciada por `tbd_products_users_providers` mediante `user_ID`.
- Referenciada por `tbd_user_payment_methods` mediante `user_ID`.
- Referenciada por `tbd_users_wishlist_products` mediante `user_ID`.
- Referenciada por `tbd_wishlist` mediante `user_id`.

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

- **Prefijo/tipo:** catálogo (tbc_). **Módulo:** productos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbc_categories` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de productos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `sup_id_category` → tbc_categories.`ID`. Relaciones entrantes: tbc_categories.`sup_id_category`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `name` (`name`). Acciones ON DELETE/UPDATE: fk_superior_category: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbc_categories_after_insert`, `trg_tbc_categories_after_update`, `trg_tbc_categories_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbc_categories = @ID + name + description + #sup_id_category + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `name` | `varchar(120)` | 120 | NO | Sin default | — | UK | Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido). |
| 3 | `description` | `text` | — | Sí | Sin default | — | — | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| 4 | `sup_id_category` | `int` | — | Sí | NULL | — | FK → tbc_categories.ID | Identifica o enlaza el registro con `tbc_categories.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
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
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | name = {carácter} | name ∈ cadena(≤120); tipo varchar(120) | Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido). |
| `description` | Monovalor | Almacenado | Opcional (NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | description = {carácter} | description ∈ texto (text); formato no restringido por CHECK | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| `sup_id_category` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | FK → tbc_categories.ID | Cualitativa nominal | sup_id_category = {entero} | sup_id_category ∈ {tbc_categories.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbc_categories.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tbc_payment_methods`

- **Prefijo/tipo:** catálogo (tbc_). **Módulo:** pagos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbc_payment_methods` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de pagos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: ninguna FK declarada. Relaciones entrantes: tb_payments.`payment_method_id`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `name` (`name`). Acciones ON DELETE/UPDATE: sin FK salientes con acciones. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbc_payment_methods_after_insert`, `trg_tbc_payment_methods_after_update`, `trg_tbc_payment_methods_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbc_payment_methods = @ID + name + description + status + creation_date`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
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
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | name = {carácter} | name ∈ cadena(≤100); tipo varchar(100) | Guarda el nombre legible de la entidad o elemento del catálogo identificado por la fila (inferido). |
| `description` | Monovalor | Almacenado | Opcional (NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | description = {carácter} | description ∈ texto (text); formato no restringido por CHECK | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tbc_payment_methods_types`

- **Prefijo/tipo:** catálogo (tbc_). **Módulo:** pagos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbc_payment_methods_types` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de pagos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: ninguna FK declarada. Relaciones entrantes: tbd_user_payment_methods.`payment_method_type_ID`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `code_UNIQUE` (`code`). Acciones ON DELETE/UPDATE: sin FK salientes con acciones. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbc_payment_methods_types_after_insert`, `trg_tbc_payment_methods_types_after_update`, `trg_tbc_payment_methods_types_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbc_payment_methods_types = @ID + code + description + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
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
- Referenciada por `tbd_user_payment_methods` mediante `payment_method_type_ID`.

**Triggers asociados:** `trg_tbc_payment_methods_types_after_insert`, `trg_tbc_payment_methods_types_after_update`, `trg_tbc_payment_methods_types_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `code` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | code = {carácter} | code ∈ cadena(≤30); tipo varchar(30) | Guarda el código estable que identifica cada tipo de método de pago en el catálogo (inferido). Es obligatorio, único y se asigna al configurar el catálogo para que otras filas puedan distinguir el tipo. |
| `description` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | description = {carácter} | description ∈ texto (text); formato no restringido por CHECK | Guarda texto descriptivo del registro; en `tb_logs` contiene además el mensaje compuesto por los triggers. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tbd_address_components`

- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** direcciones (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbd_address_components` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de direcciones (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `address_ID` → tb_user_addresses.`ID`; `address_ID`, `address_sup_ID` → tbd_address_components.`address_ID`, `ID`. Relaciones entrantes: tbd_address_components.`address_ID`, `address_sup_ID`.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `uk_address_component` (`address_ID`,`ID`). Acciones ON DELETE/UPDATE: fk_component_address: ON DELETE RESTRICT; fk_component_parent: ON DELETE RESTRICT. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbd_address_components_after_insert`, `trg_tbd_address_components_after_update`, `trg_tbd_address_components_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_address_components = @ID + #address_ID + value + component_type + status + #address_sup_ID + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `bigint` | — | NO | Sin default | AUTO_INCREMENT | PK; UK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `address_ID` | `bigint` | — | NO | Sin default | — | FK → tbd_address_components.address_ID; UK | Identifica o enlaza el registro con `tbd_address_components.address_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `value` | `varchar(255)` | 255 | NO | Sin default | — | — | Guarda el contenido de un componente individual de la dirección, como una calle o localidad (inferido). Es obligatorio y se captura al desglosar la dirección para poder consultar cada componente junto con su tipo. |
| 4 | `component_type` | `varchar(50)` | 50 | NO | Sin default | — | — | Indica qué clase de dato contiene `value`, por ejemplo calle, ciudad o código postal (inferido). Es obligatorio y se captura al estructurar la dirección para interpretar cada componente. |
| 5 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 6 | `address_sup_ID` | `bigint` | — | Sí | NULL | — | FK → tbd_address_components.ID | Identifica o enlaza el registro con `tbd_address_components.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
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
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK; UK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo bigint; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `address_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tbd_address_components.address_ID; UK | Cualitativa nominal | address_ID = {dígito} | address_ID ∈ {tb_user_addresses.ID}; ON DELETE restrict; address_ID ∈ {tbd_address_components.address_ID}; ON DELETE restrict | Identifica o enlaza el registro con `tbd_address_components.address_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `value` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | value = {carácter} | value ∈ cadena(≤255); tipo varchar(255) | Guarda el contenido de un componente individual de la dirección, como una calle o localidad (inferido). Es obligatorio y se captura al desglosar la dirección para poder consultar cada componente junto con su tipo. |
| `component_type` | Multivalor resuelto mediante tabla tbd_address_components | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | component_type = {carácter} | component_type ∈ cadena(≤50); tipo varchar(50) | Indica qué clase de dato contiene `value`, por ejemplo calle, ciudad o código postal (inferido). Es obligatorio y se captura al estructurar la dirección para interpretar cada componente. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `address_sup_ID` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | FK → tbd_address_components.ID | Cualitativa nominal | address_sup_ID = {dígito} | address_sup_ID ∈ {tbd_address_components.ID}; ON DELETE restrict | Identifica o enlaza el registro con `tbd_address_components.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tbd_carts_items`

- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** carritos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbd_carts_items` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de carritos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `cart_ID` → tb_carts.`ID`; `product_ID` → tbd_products_users_providers.`product_ID`; `provider_ID` → tbd_products_users_providers.`user_ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: CHECK ((`quantity` > 0)); sin UNIQUE. Acciones ON DELETE/UPDATE: fk_cart_items_cart: sin acción referencial explícita; fk_cart_items_product: sin acción referencial explícita; fk_cart_items_provider: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbd_carts_items_after_insert`, `trg_tbd_carts_items_after_update`, `trg_tbd_carts_items_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_carts_items = @#cart_ID + @#provider_ID + @#product_ID + quantity + creation_date`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `cart_ID` | `int` | — | NO | Sin default | — | PK compuesta (cart_ID, provider_ID, product_ID); FK → tb_carts.ID | Identifica o enlaza el registro con `tb_carts.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 2 | `provider_ID` | `int` | — | NO | Sin default | — | PK compuesta (cart_ID, provider_ID, product_ID); FK → tbd_products_users_providers.user_ID | Identifica o enlaza el registro con `tbd_products_users_providers.user_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `product_ID` | `int` | — | NO | Sin default | — | PK compuesta (cart_ID, provider_ID, product_ID); FK → tbd_products_users_providers.product_ID | Identifica o enlaza el registro con `tbd_products_users_providers.product_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `quantity` | `int` | — | NO | '1' | — | — | Indica cuántas unidades del producto contiene esta línea; los CHECK aplicables definen el mínimo permitido. |
| 5 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`cart_ID\`,\`provider_ID\`,\`product_ID\`)`
- `KEY \`fk_cart_items_provider\` (\`provider_ID\`)`
- `KEY \`fk_cart_items_product\` (\`product_ID\`)`
- `CONSTRAINT \`fk_cart_items_cart\` FOREIGN KEY (\`cart_ID\`) REFERENCES \`tb_carts\` (\`ID\`)`
- `CONSTRAINT \`fk_cart_items_product\` FOREIGN KEY (\`product_ID\`) REFERENCES \`tbd_products_users_providers\` (\`product_ID\`)`
- `CONSTRAINT \`fk_cart_items_provider\` FOREIGN KEY (\`provider_ID\`) REFERENCES \`tbd_products_users_providers\` (\`user_ID\`)`
- `CONSTRAINT \`chk_cart_quantity\` CHECK ((\`quantity\` > 0))`

**Relaciones**

- `cart_ID` → `tb_carts.ID`; sin acción referencial explícita
- `product_ID` → `tbd_products_users_providers.product_ID`; sin acción referencial explícita
- `provider_ID` → `tbd_products_users_providers.user_ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tbd_carts_items_after_insert`, `trg_tbd_carts_items_after_update`, `trg_tbd_carts_items_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `cart_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (cart_ID, provider_ID, product_ID); FK → tb_carts.ID | Cualitativa nominal | cart_ID = {dígito} | cart_ID ∈ {tb_carts.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_carts.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `provider_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (cart_ID, provider_ID, product_ID); FK → tbd_products_users_providers.user_ID | Cualitativa nominal | provider_ID = {dígito} | provider_ID ∈ {tbd_products_users_providers.user_ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbd_products_users_providers.user_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `product_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (cart_ID, provider_ID, product_ID); FK → tbd_products_users_providers.product_ID | Cualitativa nominal | product_ID = {dígito} | product_ID ∈ {tbd_products_users_providers.product_ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbd_products_users_providers.product_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `quantity` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '1') | No | Cuantitativa discreta | quantity = {entero} | quantity ∈ ℤ⁺; tipo int; CHECK ((`quantity` > 0)) | Indica cuántas unidades del producto contiene esta línea; los CHECK aplicables definen el mínimo permitido. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tbd_order_details`

- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** órdenes (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbd_order_details` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de órdenes (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `order_id` → tb_orders.`ID`; `product_id` → tb_products.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_order_details_order: ON DELETE CASCADE; fk_order_details_product: sin acción referencial explícita. Columnas generadas: subtotal decimal(10,2).
  - Triggers asociados: `trg_tbd_order_details_after_insert`, `trg_tbd_order_details_after_update`, `trg_tbd_order_details_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_order_details = @ID + #order_id + #product_id + quantity + unit_price + subtotal + creation_date`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `order_id` | `int` | — | NO | Sin default | — | FK → tb_orders.ID | Identifica o enlaza el registro con `tb_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `product_id` | `int` | — | NO | Sin default | — | FK → tb_products.ID | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `quantity` | `int` | — | NO | '1' | — | — | Indica cuántas unidades del producto contiene esta línea; los CHECK aplicables definen el mínimo permitido. |
| 5 | `unit_price` | `decimal(10,2)` | 10,2 | NO | Sin default | — | — | Guarda el precio unitario aplicado a la línea; el SQL determina su precisión y puede imponer un límite mediante CHECK. |
| 6 | `subtotal` | `decimal(10,2)` | 10,2 | Sí | Sin default | GENERATED STORED | — | Almacena un valor calculado por la base de datos; fórmula `((`quantity` * `unit_price`))` y columna generada según DDL. |
| 7 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_order_details_order\` (\`order_id\`)`
- `KEY \`fk_order_details_product\` (\`product_id\`)`
- `CONSTRAINT \`fk_order_details_order\` FOREIGN KEY (\`order_id\`) REFERENCES \`tb_orders\` (\`ID\`) ON DELETE CASCADE`
- `CONSTRAINT \`fk_order_details_product\` FOREIGN KEY (\`product_id\`) REFERENCES \`tb_products\` (\`ID\`)`

**Relaciones**

- `order_id` → `tb_orders.ID`; ON DELETE CASCADE
- `product_id` → `tb_products.ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tbd_order_details_after_insert`, `trg_tbd_order_details_after_update`, `trg_tbd_order_details_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `order_id` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_orders.ID | Cualitativa nominal | order_id = {dígito} | order_id ∈ {tb_orders.ID}; ON DELETE cascade | Identifica o enlaza el registro con `tb_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `product_id` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_products.ID | Cualitativa nominal | product_id = {dígito} | product_id ∈ {tb_products.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `quantity` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '1') | No | Cuantitativa discreta | quantity = {entero} | quantity ∈ ℤ⁺ ∪ {0}; tipo int | Indica cuántas unidades del producto contiene esta línea; los CHECK aplicables definen el mínimo permitido. |
| `unit_price` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa continua | unit_price = {número real} | unit_price ∈ ℝ, precisión 10,2; decimal(10,2); sin rango adicional salvo CHECK explícito | Guarda el precio unitario aplicado a la línea; el SQL determina su precisión y puede imponer un límite mediante CHECK. |
| `subtotal` | Monovalor | Derivado: ((`quantity` * `unit_price`)) | Opcional (NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa continua | subtotal = quantity × unit_price | subtotal ∈ ℝ, precisión 10,2; decimal(10,2); sin rango adicional salvo CHECK explícito | Almacena un valor calculado por la base de datos; fórmula `((`quantity` * `unit_price`))` y columna generada según DDL. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tbd_order_items`

- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** órdenes (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbd_order_items` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de órdenes (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `buyer_order_ID` → tb_buyer_orders.`ID`; `product_ID` → tbd_products_users_providers.`product_ID`; `provider_ID` → tbd_products_users_providers.`user_ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: CHECK ((`quantity` > 0)); CHECK ((`unit_price` >= 0)); sin UNIQUE. Acciones ON DELETE/UPDATE: fk_order_items_buyer_order: sin acción referencial explícita; fk_order_items_product: sin acción referencial explícita; fk_order_items_provider: sin acción referencial explícita. Columnas generadas: subtotal decimal(12,2).
  - Triggers asociados: `trg_tbd_order_items_after_insert`, `trg_tbd_order_items_after_update`, `trg_tbd_order_items_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_order_items = @ID + #buyer_order_ID + #product_ID + #provider_ID + product_name + quantity + unit_price + subtotal + creation_date`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `buyer_order_ID` | `int` | — | NO | Sin default | — | FK → tb_buyer_orders.ID | Identifica o enlaza el registro con `tb_buyer_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `product_ID` | `int` | — | NO | Sin default | — | FK → tbd_products_users_providers.product_ID | Identifica o enlaza el registro con `tbd_products_users_providers.product_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `provider_ID` | `int` | — | NO | Sin default | — | FK → tbd_products_users_providers.user_ID | Identifica o enlaza el registro con `tbd_products_users_providers.user_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 5 | `product_name` | `varchar(255)` | 255 | NO | Sin default | — | — | Guarda el nombre del producto mostrado en esta línea de la orden; probablemente se copia del catálogo al crearla para conservar el detalle histórico (inferido). Es obligatorio y permite identificar el artículo en el comprobante aunque cambie su nombre en el catálogo. |
| 6 | `quantity` | `int` | — | NO | Sin default | — | — | Indica cuántas unidades del producto contiene esta línea; los CHECK aplicables definen el mínimo permitido. |
| 7 | `unit_price` | `decimal(12,2)` | 12,2 | NO | Sin default | — | — | Guarda el precio unitario aplicado a la línea; el SQL determina su precisión y puede imponer un límite mediante CHECK. |
| 8 | `subtotal` | `decimal(12,2)` | 12,2 | Sí | Sin default | GENERATED STORED | — | Almacena un valor calculado por la base de datos; fórmula `((`quantity` * `unit_price`))` y columna generada según DDL. |
| 9 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `KEY \`fk_order_items_buyer_order\` (\`buyer_order_ID\`)`
- `KEY \`fk_order_items_product\` (\`product_ID\`)`
- `KEY \`fk_order_items_provider\` (\`provider_ID\`)`
- `CONSTRAINT \`fk_order_items_buyer_order\` FOREIGN KEY (\`buyer_order_ID\`) REFERENCES \`tb_buyer_orders\` (\`ID\`)`
- `CONSTRAINT \`fk_order_items_product\` FOREIGN KEY (\`product_ID\`) REFERENCES \`tbd_products_users_providers\` (\`product_ID\`)`
- `CONSTRAINT \`fk_order_items_provider\` FOREIGN KEY (\`provider_ID\`) REFERENCES \`tbd_products_users_providers\` (\`user_ID\`)`
- `CONSTRAINT \`chk_order_items_quantity\` CHECK ((\`quantity\` > 0))`
- `CONSTRAINT \`chk_order_items_unit_price\` CHECK ((\`unit_price\` >= 0))`

**Relaciones**

- `buyer_order_ID` → `tb_buyer_orders.ID`; sin acción referencial explícita
- `product_ID` → `tbd_products_users_providers.product_ID`; sin acción referencial explícita
- `provider_ID` → `tbd_products_users_providers.user_ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tbd_order_items_after_insert`, `trg_tbd_order_items_after_update`, `trg_tbd_order_items_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `buyer_order_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_buyer_orders.ID | Cualitativa nominal | buyer_order_ID = {dígito} | buyer_order_ID ∈ {tb_buyer_orders.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_buyer_orders.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `product_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tbd_products_users_providers.product_ID | Cualitativa nominal | product_ID = {dígito} | product_ID ∈ {tbd_products_users_providers.product_ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbd_products_users_providers.product_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `provider_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tbd_products_users_providers.user_ID | Cualitativa nominal | provider_ID = {dígito} | provider_ID ∈ {tbd_products_users_providers.user_ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbd_products_users_providers.user_ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `product_name` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cualitativa nominal | product_name = {carácter} | product_name ∈ cadena(≤255); tipo varchar(255) | Guarda el nombre del producto mostrado en esta línea de la orden; probablemente se copia del catálogo al crearla para conservar el detalle histórico (inferido). Es obligatorio y permite identificar el artículo en el comprobante aunque cambie su nombre en el catálogo. |
| `quantity` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa discreta | quantity = {entero} | quantity ∈ ℤ⁺; tipo int; CHECK ((`quantity` > 0)) | Indica cuántas unidades del producto contiene esta línea; los CHECK aplicables definen el mínimo permitido. |
| `unit_price` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa continua | unit_price = {número real} | unit_price ∈ ℝ, precisión 12,2; decimal(12,2); sin rango adicional salvo CHECK explícito; CHECK ((`unit_price` >= 0)) | Guarda el precio unitario aplicado a la línea; el SQL determina su precisión y puede imponer un límite mediante CHECK. |
| `subtotal` | Monovalor | Derivado: ((`quantity` * `unit_price`)) | Opcional (NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa continua | subtotal = quantity × unit_price | subtotal ∈ ℝ, precisión 12,2; decimal(12,2); sin rango adicional salvo CHECK explícito | Almacena un valor calculado por la base de datos; fórmula `((`quantity` * `unit_price`))` y columna generada según DDL. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tbd_products_categories`

- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** productos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbd_products_categories` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de productos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `product_ID` → tb_products.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_product: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbd_products_categories_after_insert`, `trg_tbd_products_categories_after_update`, `trg_tbd_products_categories_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_products_categories = @category_ID + @#product_ID + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `category_ID` | `int` | — | NO | Sin default | — | PK compuesta (category_ID, product_ID) | Guarda el identificador lógico de categoría asociado al producto o relación; esta columna no declara FK en el DDL. |
| 2 | `product_ID` | `int` | — | NO | Sin default | — | PK compuesta (category_ID, product_ID); FK → tb_products.ID | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
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
| `category_ID` | Multivalor resuelto mediante tabla tbd_products_categories | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (category_ID, product_ID) | Cualitativa nominal | category_ID = {dígito} | category_ID ∈ ℤ⁺ ∪ {0}; tipo int | Guarda el identificador lógico de categoría asociado al producto o relación; esta columna no declara FK en el DDL. |
| `product_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (category_ID, product_ID); FK → tb_products.ID | Cualitativa nominal | product_ID = {dígito} | product_ID ∈ {tb_products.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default sin default | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se captura al guardar. |

### `tbd_products_users_providers`

- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** usuarios (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbd_products_users_providers` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de usuarios (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `product_ID` → tb_products.`ID`; `user_ID` → tb_users.`ID`. Relaciones entrantes: tbd_carts_items.`product_ID`; tbd_carts_items.`provider_ID`; tbd_order_items.`product_ID`; tbd_order_items.`provider_ID`.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_products2: sin acción referencial explícita; fk_user1: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbd_products_users_providers_after_insert`, `trg_tbd_products_users_providers_after_update`, `trg_tbd_products_users_providers_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_products_users_providers = @#user_ID + @#product_ID + type_ownership + status + avalaible_date + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `user_ID` | `int` | — | NO | Sin default | — | PK compuesta (user_ID, product_ID); FK → tb_users.ID | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 2 | `product_ID` | `int` | — | NO | Sin default | — | PK compuesta (user_ID, product_ID); FK → tb_products.ID | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `type_ownership` | `enum('Owner','Reseller','Distributor')` | 'Owner','Reseller','Distributor' | Sí | NULL | — | — | Clasifica la relación del usuario con el producto mediante Owner, Reseller o Distributor. Es opcional porque DEFAULT NULL permite registrar la relación sin asignar todavía un tipo; se usa para distinguir la función del proveedor (inferido). |
| 4 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 5 | `avalaible_date` | `datetime` | — | NO | Sin default | — | — | Registra desde cuándo está disponible el producto del proveedor (inferido); el valor se captura al registrar su disponibilidad. Es obligatorio y permite determinar desde qué fecha ofrecerlo. |
| 6 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 7 | `last_update` | `datetime` | — | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`user_ID\`,\`product_ID\`)`
- `KEY \`fk_products2\` (\`product_ID\`)`
- `CONSTRAINT \`fk_products2\` FOREIGN KEY (\`product_ID\`) REFERENCES \`tb_products\` (\`ID\`)`
- `CONSTRAINT \`fk_user1\` FOREIGN KEY (\`user_ID\`) REFERENCES \`tb_users\` (\`ID\`)`

**Relaciones**

- `product_ID` → `tb_products.ID`; sin acción referencial explícita
- `user_ID` → `tb_users.ID`; sin acción referencial explícita
- Referenciada por `tbd_carts_items` mediante `product_ID`.
- Referenciada por `tbd_carts_items` mediante `provider_ID`.
- Referenciada por `tbd_order_items` mediante `product_ID`.
- Referenciada por `tbd_order_items` mediante `provider_ID`.

**Triggers asociados:** `trg_tbd_products_users_providers_after_insert`, `trg_tbd_products_users_providers_after_update`, `trg_tbd_products_users_providers_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `user_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (user_ID, product_ID); FK → tb_users.ID | Cualitativa nominal | user_ID = {dígito} | user_ID ∈ {tb_users.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `product_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (user_ID, product_ID); FK → tb_products.ID | Cualitativa nominal | product_ID = {dígito} | product_ID ∈ {tb_products.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `type_ownership` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | type_ownership = [ Owner \| Reseller \| Distributor ] | type_ownership ∈ {Owner, Reseller, Distributor}; tipo enum('Owner','Reseller','Distributor') | Clasifica la relación del usuario con el producto mediante Owner, Reseller o Distributor. Es opcional porque DEFAULT NULL permite registrar la relación sin asignar todavía un tipo; se usa para distinguir la función del proveedor (inferido). |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `avalaible_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa (temporal) | avalaible_date = {fecha/hora} | avalaible_date ∈ DATETIME; default sin default | Registra desde cuándo está disponible el producto del proveedor (inferido); el valor se captura al registrar su disponibilidad. Es obligatorio y permite determinar desde qué fecha ofrecerlo. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

### `tbd_user_payment_methods`

- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** usuarios (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbd_user_payment_methods` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de usuarios (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `user_ID` → tb_users.`ID`; `payment_method_type_ID` → tbc_payment_methods_types.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `uk_provider_method` (`provider`,`provider_method_ref`). Acciones ON DELETE/UPDATE: tbd_user_payment_methods_ibfk_1: sin acción referencial explícita; tbd_user_payment_methods_ibfk_2: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbd_user_payment_methods_after_insert`, `trg_tbd_user_payment_methods_after_update`, `trg_tbd_user_payment_methods_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_user_payment_methods = @ID + #user_ID + #payment_method_type_ID + provider + provider_method_ref + label + last_four + is_default + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `bigint` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `user_ID` | `int` | — | NO | Sin default | — | FK → tb_users.ID | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `payment_method_type_ID` | `int` | — | NO | Sin default | — | FK → tbc_payment_methods_types.ID | Identifica o enlaza el registro con `tbc_payment_methods_types.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `provider` | `varchar(60)` | 60 | NO | Sin default | — | UK | Guarda el nombre del proveedor o servicio que administra el método de pago (inferido). Es obligatorio y se aporta al vincular el método para identificar qué sistema debe procesar o consultar la referencia externa. |
| 5 | `provider_method_ref` | `varchar(255)` | 255 | NO | Sin default | — | UK | Guarda el identificador que el proveedor asigna al método de pago del usuario (inferido), sin implicar que sea el número completo de tarjeta. Es obligatorio y se usa junto con `provider` para localizar ese método; ambos campos tienen unicidad conjunta. |
| 6 | `label` | `varchar(100)` | 100 | Sí | NULL | — | — | Guarda una etiqueta legible para distinguir este método de pago del usuario (inferido). |
| 7 | `last_four` | `char(4)` | 4 | Sí | NULL | — | — | Conserva los últimos cuatro caracteres de una referencia de pago para mostrarla parcialmente (inferido). |
| 8 | `is_default` | `tinyint(1)` | 1 | NO | '0' | — | — | Indica si el método de pago se marca como preferido para el usuario, según el nombre de la columna (inferido). |
| 9 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 10 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 11 | `last_update` | `datetime` | — | Sí | NULL | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`uk_provider_method\` (\`provider\`,\`provider_method_ref\`)`
- `KEY \`user_ID\` (\`user_ID\`)`
- `KEY \`payment_method_type_ID\` (\`payment_method_type_ID\`)`
- `CONSTRAINT \`tbd_user_payment_methods_ibfk_1\` FOREIGN KEY (\`user_ID\`) REFERENCES \`tb_users\` (\`ID\`)`
- `CONSTRAINT \`tbd_user_payment_methods_ibfk_2\` FOREIGN KEY (\`payment_method_type_ID\`) REFERENCES \`tbc_payment_methods_types\` (\`ID\`)`

**Relaciones**

- `user_ID` → `tb_users.ID`; sin acción referencial explícita
- `payment_method_type_ID` → `tbc_payment_methods_types.ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tbd_user_payment_methods_after_insert`, `trg_tbd_user_payment_methods_after_update`, `trg_tbd_user_payment_methods_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo bigint; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `user_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID | Cualitativa nominal | user_ID = {dígito} | user_ID ∈ {tb_users.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `payment_method_type_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tbc_payment_methods_types.ID | Cualitativa nominal | payment_method_type_ID = {dígito} | payment_method_type_ID ∈ {tbc_payment_methods_types.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tbc_payment_methods_types.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `provider` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | provider = {carácter} | provider ∈ cadena(≤60); tipo varchar(60) | Guarda el nombre del proveedor o servicio que administra el método de pago (inferido). Es obligatorio y se aporta al vincular el método para identificar qué sistema debe procesar o consultar la referencia externa. |
| `provider_method_ref` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | UK | Cualitativa nominal | provider_method_ref = {carácter} | provider_method_ref ∈ cadena(≤255); tipo varchar(255) | Guarda el identificador que el proveedor asigna al método de pago del usuario (inferido), sin implicar que sea el número completo de tarjeta. Es obligatorio y se usa junto con `provider` para localizar ese método; ambos campos tienen unicidad conjunta. |
| `label` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | label = {carácter} | label ∈ cadena(≤100); tipo varchar(100) | Guarda una etiqueta legible para distinguir este método de pago del usuario (inferido). |
| `last_four` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cualitativa nominal | last_four = {carácter alfanumérico} | last_four ∈ cadena(≤4); tipo char(4) | Conserva los últimos cuatro caracteres de una referencia de pago para mostrarla parcialmente (inferido). |
| `is_default` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT '0') | No | Cualitativa nominal | is_default = {entero} | is_default ∈ ℤ; tipo tinyint(1) | Indica si el método de pago se marca como preferido para el usuario, según el nombre de la columna (inferido). |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Opcional (NULL); valor por sistema (DEFAULT NULL) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default NULL | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto NULL. |

### `tbd_users_wishlist_products`

- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** usuarios (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbd_users_wishlist_products` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de usuarios (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `product_ID` → tb_products.`ID`; `user_ID` → tb_users.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; sin UNIQUE. Acciones ON DELETE/UPDATE: fk_products3: sin acción referencial explícita; fk_user2: sin acción referencial explícita. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbd_users_wishlist_products_after_insert`, `trg_tbd_users_wishlist_products_after_update`, `trg_tbd_users_wishlist_products_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_users_wishlist_products = @#user_ID + @#product_ID + status + creation_date + last_update`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `user_ID` | `int` | — | NO | Sin default | — | PK compuesta (user_ID, product_ID); FK → tb_users.ID | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 2 | `product_ID` | `int` | — | NO | Sin default | — | PK compuesta (user_ID, product_ID); FK → tb_products.ID | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `status` | `bit(1)` | 1 | NO | b'1' | — | — | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| 4 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| 5 | `last_update` | `datetime` | — | NO | Sin default | ON UPDATE CURRENT_TIMESTAMP | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se captura al guardar. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`user_ID\`,\`product_ID\`)`
- `KEY \`fk_products3\` (\`product_ID\`)`
- `CONSTRAINT \`fk_products3\` FOREIGN KEY (\`product_ID\`) REFERENCES \`tb_products\` (\`ID\`)`
- `CONSTRAINT \`fk_user2\` FOREIGN KEY (\`user_ID\`) REFERENCES \`tb_users\` (\`ID\`)`

**Relaciones**

- `product_ID` → `tb_products.ID`; sin acción referencial explícita
- `user_ID` → `tb_users.ID`; sin acción referencial explícita

**Triggers asociados:** `trg_tbd_users_wishlist_products_after_insert`, `trg_tbd_users_wishlist_products_after_update`, `trg_tbd_users_wishlist_products_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `user_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (user_ID, product_ID); FK → tb_users.ID | Cualitativa nominal | user_ID = {dígito} | user_ID ∈ {tb_users.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `product_ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | PK compuesta (user_ID, product_ID); FK → tb_products.ID | Cualitativa nominal | product_ID = {dígito} | product_ID ∈ {tb_products.ID}; ON DELETE sin acción | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `status` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT b'1') | No | Cualitativa nominal | status = {0 \| 1} | status ∈ {0,1}; 1 activo, 0 inactivo (borrado lógico); bit(1) | Indica el estado lógico del registro (inferido); usa DEFAULT b'1'. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |
| `last_update` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | No | Cuantitativa (temporal) | last_update = {fecha/hora} | last_update ∈ DATETIME; default sin default | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se captura al guardar. |

### `tbd_wishlist`

- **Prefijo/tipo:** detalle/relación (tbd_). **Módulo:** carritos (inferido).
- **Motor/charset/collation:** InnoDB / utf8mb4 / utf8mb4_0900_ai_ci, según opciones del DDL.
- **Descripción general detallada:**
  - Representa la entidad o asociación `tbd_wishlist` a partir de los nombres y tipos de sus atributos (inferido).
  - Pertenece al módulo de carritos (inferido por el prefijo y el nombre del objeto).
  - Relaciones salientes: `product_id` → tb_products.`ID`; `user_id` → tb_users.`ID`. Relaciones entrantes: ninguna FK entrante.
  - Reglas SQL: sin CHECK; UNIQUE UNIQUE KEY `uk_user_product_wishlist` (`user_id`,`product_id`). Acciones ON DELETE/UPDATE: fk_wishlist_product: ON DELETE CASCADE; fk_wishlist_user: ON DELETE CASCADE. Columnas generadas: ninguna.
  - Triggers asociados: `trg_tbd_wishlist_after_insert`, `trg_tbd_wishlist_after_update`, `trg_tbd_wishlist_after_delete`; sus acciones de auditoría registran operación y valores NEW/OLD.

**Notación formal:** `tbd_wishlist = @ID + #user_id + #product_id + creation_date`

**Tabla técnica de columnas**

| # | Nombre | Tipo | Longitud/precisión | NULL | Default | Extras | Llave | Descripción |
|---:|---|---|---|:---:|---|---|---|---|
| 1 | `ID` | `int` | — | NO | Sin default | AUTO_INCREMENT | PK | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| 2 | `user_id` | `int` | — | NO | Sin default | — | FK → tb_users.ID; UK | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 3 | `product_id` | `int` | — | NO | Sin default | — | FK → tb_products.ID; UK | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| 4 | `creation_date` | `datetime` | — | NO | CURRENT_TIMESTAMP | — | — | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

**Restricciones e índices del DDL**

- `PRIMARY KEY (\`ID\`)`
- `UNIQUE KEY \`uk_user_product_wishlist\` (\`user_id\`,\`product_id\`)`
- `KEY \`fk_wishlist_product\` (\`product_id\`)`
- `CONSTRAINT \`fk_wishlist_product\` FOREIGN KEY (\`product_id\`) REFERENCES \`tb_products\` (\`ID\`) ON DELETE CASCADE`
- `CONSTRAINT \`fk_wishlist_user\` FOREIGN KEY (\`user_id\`) REFERENCES \`tb_users\` (\`ID\`) ON DELETE CASCADE`

**Relaciones**

- `product_id` → `tb_products.ID`; ON DELETE CASCADE
- `user_id` → `tb_users.ID`; ON DELETE CASCADE

**Triggers asociados:** `trg_tbd_wishlist_after_insert`, `trg_tbd_wishlist_after_update`, `trg_tbd_wishlist_after_delete`

**Tabla de clasificación de columnas**

| Nombre | Valor | Origen | Obligatoriedad | Llave | Naturaleza | Composición formal | Dominio | Descripción detallada |
|---|---|---|---|---|---|---|---|---|
| `ID` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor aportado por sistema (AUTO_INCREMENT) | PK | Cualitativa nominal | ID = {dígito} | ID ∈ ℤ⁺; tipo int; AUTO_INCREMENT | Identificador numérico generado automáticamente para distinguir registros; es llave primaria y se incrementa al insertar. |
| `user_id` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_users.ID; UK | Cualitativa nominal | user_id = {dígito} | user_id ∈ {tb_users.ID}; ON DELETE cascade | Identifica o enlaza el registro con `tb_users.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `product_id` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor capturado por usuario/proceso (inferido) | FK → tb_products.ID; UK | Cualitativa nominal | product_id = {dígito} | product_id ∈ {tb_products.ID}; ON DELETE cascade | Identifica o enlaza el registro con `tb_products.ID`; su valor se almacena al crear la relación y debe corresponder a la fila referenciada. |
| `creation_date` | Monovalor | Almacenado | Obligatorio (NOT NULL); valor por sistema (DEFAULT CURRENT_TIMESTAMP) | No | Cuantitativa (temporal) | creation_date = {fecha/hora} | creation_date ∈ DATETIME; default CURRENT_TIMESTAMP | Registra una fecha u hora del ciclo de vida/auditoría (inferido); se asigna por defecto CURRENT_TIMESTAMP. |

## Vistas

### `vw_trazabilidad_carritos`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_categorias`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `categoria_id` (tipo derivado de expresión; origen en SELECT), `categoria_nombre` (tipo derivado de expresión; origen en SELECT), `categoria_descripcion` (tipo derivado de expresión; origen en SELECT), `categoria_padre` (tipo derivado de expresión; origen en SELECT), `estado` (tipo derivado de expresión; origen en SELECT), `total_productos_asociados` (tipo derivado de expresión; origen en SELECT), `fecha_creacion` (tipo derivado de expresión; origen en SELECT), `ultima_actualizacion` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_componentes_direccion`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_detalle_ordenes`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_direcciones_usuario`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_items_carrito`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_items_orden_comprador`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_metodos_pago`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_ordenes`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_ordenes_comprador`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_pagos`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_productos`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_proveedores_productos`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `user_ID` (tipo derivado de expresión; origen en SELECT), `provider_nickname` (tipo derivado de expresión; origen en SELECT), `provider_email` (tipo derivado de expresión; origen en SELECT), `product_ID` (tipo derivado de expresión; origen en SELECT), `product_name` (tipo derivado de expresión; origen en SELECT), `type_ownership` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `roles` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_tipos_metodos_pago`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_usuario_metodos_pago`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_usuarios_creados`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `nickname` (tipo derivado de expresión; origen en SELECT), `email` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `roles` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_usuarios_wishlist_productos`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
- **Columnas expuestas:** `log_id` (tipo derivado de expresión; origen en SELECT), `operation` (tipo derivado de expresión; origen en SELECT), `inserted_by` (tipo derivado de expresión; origen en SELECT), `operation_description` (tipo derivado de expresión; origen en SELECT), `operation_date` (tipo derivado de expresión; origen en SELECT).

### `vw_trazabilidad_wishlist`

- **Propósito:** trazabilidad/consulta derivada según su SELECT.
- **Tablas base:** No especificado.
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
| `trg_tb_orders_after_insert` | `tb_orders` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Orden creado.  ID= , user_id= NULL , total_amount= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_orders_after_update` | `tb_orders` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Orden actualizado.  ID= . Cambios:  ,  user_id: [ NULL ] -> [ NULL ] total_amount: [ NULL ] -> [ NULL ] status: [ NULL ] -> [ NULL ] shipping_address modificado` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_orders_after_delete` | `tb_orders` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Orden eliminado.  ID= , user_id= NULL , total_amount= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_payments_after_insert` | `tb_payments` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Pago creado.  ID= , order_id= NULL , payment_method_id= NULL , amount= NULL , payment_status= NULL , transaction_reference= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_payments_after_update` | `tb_payments` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Pago actualizado.  ID= . Cambios:  ,  order_id: [ NULL ] -> [ NULL ] payment_method_id: [ NULL ] -> [ NULL ] amount: [ NULL ] -> [ NULL ] payment_status: [ NULL ] -> [ NULL ] transaction_reference: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tb_payments_after_delete` | `tb_payments` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Pago eliminado.  ID= , order_id= NULL , payment_method_id= NULL , amount= NULL , payment_status= NULL , transaction_reference= NULL` (valores dinámicos NEW/OLD según operación). |
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
| `trg_tbd_carts_items_after_insert` | `tbd_carts_items` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Ítem de carrito creado.  cart_ID= , provider_ID= , product_ID= , quantity= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_carts_items_after_update` | `tbd_carts_items` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Ítem de carrito actualizado.  cart_ID= , provider_ID= , product_ID= . Cambios:  ,  quantity: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_carts_items_after_delete` | `tbd_carts_items` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Ítem de carrito eliminado.  cart_ID= , provider_ID= , product_ID= , quantity= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_order_details_after_insert` | `tbd_order_details` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Detalle de orden creado.  ID= , order_id= NULL , product_id= NULL , quantity= NULL , unit_price= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_order_details_after_update` | `tbd_order_details` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Detalle de orden actualizado.  ID= . Cambios:  ,  order_id: [ NULL ] -> [ NULL ] product_id: [ NULL ] -> [ NULL ] quantity: [ NULL ] -> [ NULL ] unit_price: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_order_details_after_delete` | `tbd_order_details` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Detalle de orden eliminado.  ID= , order_id= NULL , product_id= NULL , quantity= NULL , unit_price= NULL` (valores dinámicos NEW/OLD según operación). |
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
| `trg_tbd_user_payment_methods_after_insert` | `tbd_user_payment_methods` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Método de pago de usuario creado.  ID= , user_ID= NULL , payment_method_type_ID= NULL , provider= NULL , label= NULL , last_four= NULL , is_default= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_user_payment_methods_after_update` | `tbd_user_payment_methods` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Método de pago de usuario actualizado.  ID= . Cambios:  ,  user_ID: [ NULL ] -> [ NULL ] payment_method_type_ID: [ NULL ] -> [ NULL ] provider: [ NULL ] -> [ NULL ] label: [ NULL ] -> [ NULL ] last_four: [ NULL ] -> [ NULL ] is_default: [ NULL ] -> [ NULL ] status: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_user_payment_methods_after_delete` | `tbd_user_payment_methods` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Método de pago de usuario eliminado.  ID= , user_ID= NULL , payment_method_type_ID= NULL , provider= NULL , label= NULL , last_four= NULL , is_default= NULL , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_users_wishlist_products_after_insert` | `tbd_users_wishlist_products` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Producto en lista de deseos creado.  user_ID= , product_ID= , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_users_wishlist_products_after_update` | `tbd_users_wishlist_products` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Producto en lista de deseos actualizado.  user_ID= , product_ID= . Cambios:  ,  status: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_users_wishlist_products_after_delete` | `tbd_users_wishlist_products` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Producto en lista de deseos eliminado.  user_ID= , product_ID= , status= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_wishlist_after_insert` | `tbd_wishlist` | INSERT | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Lista de deseos creado.  ID= , user_id= NULL , product_id= NULL` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_wishlist_after_update` | `tbd_wishlist` | UPDATE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Lista de deseos actualizado.  ID= . Cambios:  ,  user_id: [ NULL ] -> [ NULL ] product_id: [ NULL ] -> [ NULL ]` (valores dinámicos NEW/OLD según operación). |
| `trg_tbd_wishlist_after_delete` | `tbd_wishlist` | DELETE | AFTER | table_name, operation, db_user, operation_date, description, operation_status; description: `Lista de deseos eliminado.  ID= , user_id= NULL , product_id= NULL` (valores dinámicos NEW/OLD según operación). |

## Procedimientos

### `sp_soft_delete`

- **Parámetros:** `IN p_table_name VARCHAR(64), IN p_record_id BIGINT UNSIGNED` (dirección/tipo conforme a la firma; si no tiene modo explícito, MySQL lo considera IN).
- **Pasos:** valida parámetros/estado y actualiza el status para borrado lógico, según cuerpo; pasos específicos no inferibles de la firma.
- **Tablas afectadas:** No especificado.
- **Ejemplo:** `CALL sp_soft_delete(/* p_table_name */, /* p_record_id */);`

### `sp_soft_delete_product`

- **Parámetros:** `IN p_product_id INT UNSIGNED` (dirección/tipo conforme a la firma; si no tiene modo explícito, MySQL lo considera IN).
- **Pasos:** valida parámetros/estado y actualiza el status para borrado lógico, según cuerpo; pasos específicos no inferibles de la firma.
- **Tablas afectadas:** `tb_products`.
- **Ejemplo:** `CALL sp_soft_delete_product(/* p_product_id */);`

### `sp_soft_delete_user`

- **Parámetros:** `No especificado` (dirección/tipo conforme a la firma; si no tiene modo explícito, MySQL lo considera IN).
- **Pasos:** valida parámetros/estado y actualiza el status para borrado lógico, según cuerpo; pasos específicos no inferibles de la firma.
- **Tablas afectadas:** `tb_users`.
- **Ejemplo:** `CALL sp_soft_delete_user();`

## Catálogo de dominios

### ENUM

- `enum('Pending','Accepted','Preparing','Sent','Delivered','Canceled','Returned')` — `tb_buyer_orders.fulfillment_status`
- `enum('Create','Read','Update','Delete')` — `tb_logs.operation`
- `enum('Pending','Processing','Shipped','Delivered','Cancelled')` — `tb_orders.status`
- `enum('Pending','Completed','Failed','Refunded')` — `tb_payments.payment_status`
- `enum('Owner','Reseller','Distributor')` — `tbd_products_users_providers.type_ownership`

### status

- `bit`: `tb_buyer_orders.status (bit(1))`, `tb_carts.status (bit(1))`, `tb_user_addresses.status (bit(1))`, `tb_users.status (bit(1))`, `tbc_categories.status (bit(1))`, `tbc_payment_methods.status (bit(1))`, `tbc_payment_methods_types.status (bit(1))`, `tbd_address_components.status (bit(1))`, `tbd_products_categories.status (bit(1))`, `tbd_products_users_providers.status (bit(1))`, `tbd_user_payment_methods.status (bit(1))`, `tbd_users_wishlist_products.status (bit(1))`.
- `tinyint`: `tb_products.status (tinyint)`.

## Convenciones de nombres

- `tb_`: tabla principal; `tbc_`: catálogo; `tbd_`: detalle/relación; `vw_`: vista; `trg_`: trigger; `sp_`: procedimiento; `fk_`: restricción FK; `uk_`: restricción UNIQUE; `chk_`: CHECK.
- `creation_date`, `last_update` y `status` son columnas de auditoría/estado cuando aparecen; el SQL define defaults y comportamiento concretos en cada tabla. `status` no se asume equivalente entre tipos.

## Observaciones de calidad del diseño

- **Alta —** `tbd_products_categories.category_ID` carece de FK a `tbc_categories`. Recomendación: declarar FK y decidir acciones referenciales.
- **Alta —** existen dos posibles modelos paralelos de órdenes: `tb_orders`/`tbd_order_details` y `tb_buyer_orders`/`tbd_order_items`. Recomendación: confirmar si cubren flujos distintos y documentar el límite funcional.
- **Alta —** `tb_buyer_orders` solo guarda `seller_ID`; no identifica comprador. Recomendación: agregar vínculo al comprador si el proceso lo requiere.
- **Media —** `tbd_carts_items` y `tbd_order_items` separan referencias `user_ID` y `product_ID` hacia `tbd_products_users_providers` en vez de una FK compuesta. Recomendación: usar FK compuesta o validar consistencia en otro mecanismo.
- **Media —** las llaves relacionadas usan tipos INT, INT UNSIGNED y BIGINT; `status` combina bit(1) y tinyint. Recomendación: normalizar tipos/signo y dominio documentando migración.
- **Baja —** se detectaron variaciones en nombres de triggers (por ejemplo, prefijos omitidos). Recomendación: adoptar convención uniforme.

**Verificación de nombres obsoletos:** Verificado: sin referencias huérfanas

## Pendientes por confirmar

- Propósito de negocio de tablas/vistas que no esté expresado en nombres o relaciones SQL.
- Semántica de cardinalidad 1:1/N:M cuando no existe restricción única/FK que la garantice.
- En vistas, algunos tipos de columnas dependen de expresiones SQL y no están declarados explícitamente; deben confirmarse mediante DESCRIBE en una instancia.
- Valores exactos de `description` se deben interpretar junto con el SQL de cada trigger; no representan necesariamente formatos uniformes.


## Resumen estadístico

- Columnas clasificadas: 141.
- llave:FK: 26.
- llave:PK: 25.
- llave:UK: 13.
- naturaleza:Cualitativa nominal: 89.
- naturaleza:Cualitativa ordinal: 3.
- naturaleza:Cuantitativa (temporal): 34.
- naturaleza:Cuantitativa continua: 11.
- naturaleza:Cuantitativa discreta: 4.
- obligatoriedad:Obligatorio: 112.
- obligatoriedad:Opcional: 29.
- origen:Almacenado: 139.
- origen:Derivado: 2.

## Descripciones marcadas (inferido)

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
- Tabla `tb_logs`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_logs.table_name`: interpretación funcional o aporte inferido.
- Columna `tb_logs.operation`: interpretación funcional o aporte inferido.
- Columna `tb_logs.db_user`: interpretación funcional o aporte inferido.
- Columna `tb_logs.description`: interpretación funcional o aporte inferido.
- Columna `tb_logs.operation_date`: interpretación funcional o aporte inferido.
- Tabla `tb_orders`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_orders.user_id`: interpretación funcional o aporte inferido.
- Columna `tb_orders.total_amount`: interpretación funcional o aporte inferido.
- Columna `tb_orders.status`: interpretación funcional o aporte inferido.
- Columna `tb_orders.shipping_address`: interpretación funcional o aporte inferido.
- Columna `tb_orders.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_orders.last_update`: interpretación funcional o aporte inferido.
- Tabla `tb_payments`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_payments.order_id`: interpretación funcional o aporte inferido.
- Columna `tb_payments.payment_method_id`: interpretación funcional o aporte inferido.
- Columna `tb_payments.amount`: interpretación funcional o aporte inferido.
- Columna `tb_payments.transaction_reference`: interpretación funcional o aporte inferido.
- Tabla `tb_products`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tb_products.SKU`: interpretación funcional o aporte inferido.
- Columna `tb_products.name`: interpretación funcional o aporte inferido.
- Columna `tb_products.description`: interpretación funcional o aporte inferido.
- Columna `tb_products.current_price`: interpretación funcional o aporte inferido.
- Columna `tb_products.current_stock`: interpretación funcional o aporte inferido.
- Columna `tb_products.status`: interpretación funcional o aporte inferido.
- Columna `tb_products.creation_date`: interpretación funcional o aporte inferido.
- Columna `tb_products.last_update`: interpretación funcional o aporte inferido.
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
- Tabla `tbd_address_components`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_address_components.address_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_address_components.value`: interpretación funcional o aporte inferido.
- Columna `tbd_address_components.component_type`: interpretación funcional o aporte inferido.
- Columna `tbd_address_components.status`: interpretación funcional o aporte inferido.
- Columna `tbd_address_components.creation_date`: interpretación funcional o aporte inferido.
- Columna `tbd_address_components.last_update`: interpretación funcional o aporte inferido.
- Tabla `tbd_carts_items`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_carts_items.cart_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_carts_items.provider_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_carts_items.product_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_carts_items.creation_date`: interpretación funcional o aporte inferido.
- Tabla `tbd_order_details`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_order_details.order_id`: interpretación funcional o aporte inferido.
- Columna `tbd_order_details.product_id`: interpretación funcional o aporte inferido.
- Columna `tbd_order_details.unit_price`: interpretación funcional o aporte inferido.
- Columna `tbd_order_details.subtotal`: interpretación funcional o aporte inferido.
- Columna `tbd_order_details.creation_date`: interpretación funcional o aporte inferido.
- Tabla `tbd_order_items`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_order_items.buyer_order_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.product_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.provider_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.product_name`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.quantity`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.unit_price`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.subtotal`: interpretación funcional o aporte inferido.
- Columna `tbd_order_items.creation_date`: interpretación funcional o aporte inferido.
- Tabla `tbd_products_categories`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_products_categories.category_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_products_categories.product_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_products_categories.status`: interpretación funcional o aporte inferido.
- Columna `tbd_products_categories.creation_date`: interpretación funcional o aporte inferido.
- Columna `tbd_products_categories.last_update`: interpretación funcional o aporte inferido.
- Tabla `tbd_products_users_providers`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_products_users_providers.user_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_products_users_providers.product_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_products_users_providers.type_ownership`: interpretación funcional o aporte inferido.
- Columna `tbd_products_users_providers.status`: interpretación funcional o aporte inferido.
- Columna `tbd_products_users_providers.avalaible_date`: interpretación funcional o aporte inferido.
- Columna `tbd_products_users_providers.creation_date`: interpretación funcional o aporte inferido.
- Columna `tbd_products_users_providers.last_update`: interpretación funcional o aporte inferido.
- Tabla `tbd_user_payment_methods`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_user_payment_methods.user_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_user_payment_methods.payment_method_type_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_user_payment_methods.provider`: interpretación funcional o aporte inferido.
- Columna `tbd_user_payment_methods.provider_method_ref`: interpretación funcional o aporte inferido.
- Columna `tbd_user_payment_methods.label`: interpretación funcional o aporte inferido.
- Columna `tbd_user_payment_methods.last_four`: interpretación funcional o aporte inferido.
- Columna `tbd_user_payment_methods.is_default`: interpretación funcional o aporte inferido.
- Columna `tbd_user_payment_methods.status`: interpretación funcional o aporte inferido.
- Columna `tbd_user_payment_methods.creation_date`: interpretación funcional o aporte inferido.
- Columna `tbd_user_payment_methods.last_update`: interpretación funcional o aporte inferido.
- Tabla `tbd_users_wishlist_products`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_users_wishlist_products.user_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_users_wishlist_products.product_ID`: interpretación funcional o aporte inferido.
- Columna `tbd_users_wishlist_products.status`: interpretación funcional o aporte inferido.
- Columna `tbd_users_wishlist_products.creation_date`: interpretación funcional o aporte inferido.
- Columna `tbd_users_wishlist_products.last_update`: interpretación funcional o aporte inferido.
- Tabla `tbd_wishlist`: descripción de propósito/módulo inferida de nombres y relaciones.
- Columna `tbd_wishlist.user_id`: interpretación funcional o aporte inferido.
- Columna `tbd_wishlist.product_id`: interpretación funcional o aporte inferido.
- Columna `tbd_wishlist.creation_date`: interpretación funcional o aporte inferido.

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
