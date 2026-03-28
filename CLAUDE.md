# CLAUDE.md — Macuin Autopartes Project Context

Archivo de contexto para sesiones de Claude Code. Cubre arquitectura, decisiones técnicas,
convenciones de código y problemas resueltos para retomar trabajo sin exploración desde cero.

---

## Descripción del Proyecto

Sistema de e-commerce de autopartes con tres servicios web y una base de datos PostgreSQL,
todos orquestados con Docker Compose. El proyecto es un trabajo académico (parcial 3).

- **FastAPI** (`autopartes-api`) — único punto de acceso a la base de datos; toda la lógica de negocio
- **Flask** (`autopartes-flask`) — **"Macuin Admin"** — dashboard interno para staff/admin; delega todo a la API
- **Laravel** (`autopartes-laravel`) — **"Macuin Autopartes"** — portal de clientes externo; delega todo a la API
- **PostgreSQL 16** — base de datos compartida, solo accesible desde la API

**Regla de arquitectura clave:** Flask y Laravel NUNCA tocan la BD directamente. Toda operación
pasa por llamadas HTTP a la API FastAPI.

---

## Puertos

| Servicio    | Puerto local | Notas                              |
|-------------|-------------|-------------------------------------|
| FastAPI     | 8000        | Swagger en `http://localhost:8000/docs` |
| Flask admin | 5000        | Solo personal interno (staff/admin) |
| Laravel     | 8080        | Portal público de clientes          |
| PostgreSQL  | 5432        | `admin` / `admin123` / db: `autopartes` |

---

## Stack por Servicio

### FastAPI (`autopartes-api/`)

| Librería            | Versión  | Uso                                      |
|---------------------|----------|------------------------------------------|
| fastapi             | 0.115.0  | Framework web                            |
| uvicorn[standard]   | 0.30.0   | Servidor ASGI                            |
| sqlalchemy          | 2.0.36   | ORM                                      |
| psycopg2-binary     | 2.9.10   | Driver PostgreSQL                        |
| alembic             | 1.13.3   | Migraciones de BD                        |
| python-jose[cryptography] | 3.3.0 | JWT (HS256)                           |
| passlib[bcrypt]     | 1.7.4    | Hashing de contraseñas                   |
| **bcrypt**          | **3.2.2**| **Pinado — ver sección de bugs resueltos** |
| pydantic-settings   | 2.5.0    | Config desde variables de entorno        |
| reportlab           | 4.2.5    | Generación de PDF                        |
| openpyxl            | 3.1.5    | Generación de Excel (.xlsx)              |
| python-docx         | 1.1.2    | Generación de Word (.docx)               |

### Flask (`autopartes-flask/`)

| Librería  | Versión | Uso                        |
|-----------|---------|----------------------------|
| flask     | 3.0.3   | Framework web              |
| requests  | 2.32.3  | Llamadas HTTP a la API     |

### Laravel (`autopartes-laravel/`)

- Laravel 11, PHP 8.3 (Apache)
- Bootstrap 5.3 para UI
- El proyecto Laravel se genera con `composer create-project` durante el `docker build` (multi-stage)
- No hay `vendor/` ni `node_modules/` en el repositorio

---

## Estructura de Carpetas

```
newmcuin/
├── docker-compose.yml              ← Orquestación principal (4 servicios)
│
├── autopartes-api/                 ← FastAPI — núcleo del sistema
│   ├── Dockerfile
│   ├── entrypoint.sh               ← Corre `alembic upgrade head` y luego uvicorn
│   ├── requirements.txt
│   ├── .env / .env.example
│   ├── alembic/
│   │   └── versions/
│   │       ├── 0001_initial_schema.py        ← Schema inicial completo
│   │       ├── 0002_...                      ← (versiones intermedias)
│   │       ├── 0004_add_delivered_status.py  ← ALTER TYPE orderstatus ADD VALUE 'delivered'
│   │       └── 0005_add_image_url_to_parts.py ← ADD COLUMN image_url VARCHAR(500)
│   └── app/
│       ├── main.py                 ← Inicialización FastAPI, CORS, routers, handlers
│       ├── core/
│       │   ├── config.py           ← Settings con pydantic-settings (lee .env)
│       │   ├── security.py         ← hash_password, verify_password, JWT create/decode
│       │   ├── dependencies.py     ← get_db, get_current_user, require_staff, require_admin
│       │   └── exceptions.py       ← Handlers para ValueError y PermissionError
│       ├── db/
│       │   └── session.py          ← SQLAlchemy engine + SessionLocal
│       ├── models/                 ← ORM models (SQLAlchemy declarative)
│       │   ├── base.py             ← Base + TimestampMixin (created_at, updated_at)
│       │   ├── user.py             ← User, UserRole enum
│       │   ├── part.py             ← Part
│       │   ├── order.py            ← Order, OrderItem, OrderStatus enum
│       │   └── inventory_log.py    ← InventoryLog, StatusHistory, InventoryAction enum
│       ├── schemas/                ← Pydantic schemas (request/response)
│       │   ├── auth.py
│       │   ├── user.py
│       │   ├── part.py
│       │   ├── order.py
│       │   ├── inventory_log.py
│       │   └── report.py
│       ├── routers/                ← Endpoints FastAPI (un archivo por recurso)
│       │   ├── auth.py             ← POST /auth/login, GET /auth/me
│       │   ├── users.py            ← CRUD usuarios (admin), POST /users/register (público)
│       │   ├── parts.py            ← CRUD partes + PATCH stock + POST /{id}/image
│       │   ├── orders.py           ← CRUD órdenes + cancel + status + PDF
│       │   ├── inventory.py        ← GET /inventory/logs
│       │   └── reports.py          ← 4 reportes × múltiples formatos
│       ├── services/               ← Lógica de negocio
│       │   ├── auth_service.py
│       │   ├── order_service.py
│       │   ├── part_service.py
│       │   ├── user_service.py
│       │   ├── inventory_service.py
│       │   └── report_service.py   ← Genera PDF/xlsx/docx con ReportLab/openpyxl/python-docx
│       └── repositories/           ← Capa de acceso a datos
│           ├── base.py
│           ├── user_repo.py
│           ├── part_repo.py
│           ├── order_repo.py
│           └── inventory_repo.py
│
├── autopartes-flask/               ← Flask — dashboard interno
│   ├── Dockerfile
│   ├── app.py                      ← TODO el código Flask (rutas + lógica + helper api())
│   └── requirements.txt
│
└── autopartes-laravel/             ← Laravel — portal de clientes
    ├── Dockerfile                  ← Multi-stage: builder (Composer) + runtime (PHP/Apache)
    ├── entrypoint.sh               ← Genera .env de Laravel desde env vars, limpia caché
    ├── bootstrap/app.php
    ├── routes/web.php
    ├── app/Http/
    │   ├── Controllers/
    │   │   ├── AuthController.php
    │   │   ├── PartsController.php
    │   │   └── OrdersController.php
    │   └── Middleware/
    │       └── CheckApiAuth.php    ← Middleware que verifica token en sesión
    └── resources/views/            ← Blade templates con Bootstrap 5.3
        ├── layouts/app.blade.php
        ├── auth/{login,register}.blade.php
        ├── parts/{index,show}.blade.php
        └── orders/{index,create,show}.blade.php
```

---

## Endpoints de la API

Todos bajo prefijo `/api/v1`. Swagger disponible en `http://localhost:8000/docs`.

### Auth
| Método | Ruta            | Auth | Descripción                    |
|--------|-----------------|------|--------------------------------|
| POST   | /auth/login     | No   | Login; devuelve JWT bearer     |
| GET    | /auth/me        | Sí   | Info del usuario autenticado   |

### Users
| Método | Ruta                          | Rol requerido | Descripción                              |
|--------|-------------------------------|---------------|------------------------------------------|
| POST   | /users/register               | Público       | Registro de cliente (role=customer)      |
| GET    | /users/                       | admin         | Listar usuarios (filtros: role, active)  |
| POST   | /users/                       | admin         | Crear usuario interno (staff/admin)      |
| GET    | /users/{id}                   | admin         | Detalle de usuario                       |
| PUT    | /users/{id}                   | admin         | Actualizar usuario                       |
| PATCH  | /users/{id}/toggle-active     | admin         | Activar/desactivar usuario               |

### Parts
| Método | Ruta                     | Rol requerido | Descripción                        |
|--------|--------------------------|---------------|------------------------------------|
| POST   | /parts/                  | staff/admin   | Crear pieza                        |
| GET    | /parts/                  | Cualquier JWT | Listar piezas activas (filtros)    |
| GET    | /parts/{id}              | Cualquier JWT | Detalle de pieza                   |
| PUT    | /parts/{id}              | staff/admin   | Actualizar pieza                   |
| PATCH  | /parts/{id}/stock        | staff/admin   | Ajustar stock manualmente con log  |
| DELETE | /parts/{id}              | staff/admin   | Soft delete (is_active=False)      |

### Orders
| Método | Ruta                      | Rol requerido            | Descripción                                  |
|--------|---------------------------|--------------------------|----------------------------------------------|
| POST   | /orders/                  | Cualquier JWT            | Crear orden (transacción atómica)            |
| GET    | /orders/                  | Cualquier JWT            | Listar (customer=propias, staff=todas)       |
| GET    | /orders/{id}              | Cualquier JWT            | Detalle (customer solo las suyas)            |
| PATCH  | /orders/{id}/cancel       | Cualquier JWT            | Cancelar (no si ya está shipped)             |
| PATCH  | /orders/{id}/status       | staff/admin              | Cambiar estado (processing/shipped/etc)      |
| GET    | /orders/{id}/pdf          | Cualquier JWT            | Descargar recibo PDF                         |

### Inventory
| Método | Ruta              | Rol requerido | Descripción                            |
|--------|-------------------|---------------|----------------------------------------|
| GET    | /inventory/logs   | staff/admin   | Bitácora de movimientos de inventario  |

### Reports
| Método | Ruta                       | Rol requerido | Formato   |
|--------|----------------------------|---------------|-----------|
| GET    | /reports/summary           | staff/admin   | JSON      |
| GET    | /reports/summary/pdf       | staff/admin   | PDF       |
| GET    | /reports/summary/xlsx      | staff/admin   | Excel     |
| GET    | /reports/summary/docx      | staff/admin   | Word      |
| GET    | /reports/orders            | staff/admin   | JSON      |
| GET    | /reports/orders/pdf        | staff/admin   | PDF       |
| GET    | /reports/clients           | staff/admin   | JSON      |
| GET    | /reports/clients/pdf       | staff/admin   | PDF       |
| GET    | /reports/inventory         | staff/admin   | JSON      |
| GET    | /reports/inventory/pdf     | staff/admin   | PDF       |

---

## Modelos de Base de Datos

### ENUMs PostgreSQL (todos en minúsculas)
```sql
userrole:       customer, staff, admin
orderstatus:    received, processing, shipped, cancelled
inventoryaction: restock, adjustment, sale, return
```

### Tablas
```
users           id(UUID PK), email(UNIQUE), hashed_password, full_name, role, is_active, timestamps
parts           id(UUID PK), sku(UNIQUE), name, description, brand, category, price(10,2), stock_quantity, is_active, timestamps
orders          id(UUID PK), user_id(FK→users), status, total_amount(12,2), cancelled_at, timestamps
order_items     id(UUID PK), order_id(FK→orders), part_id(FK→parts), quantity, unit_price(10,2), subtotal(12,2)
inventory_logs  id(UUID PK), part_id(FK→parts), user_id(FK→users), action_type, qty_before, qty_after, delta, reason, timestamps
status_history  id(UUID PK), order_id(FK→orders), changed_by(FK→users), old_status, new_status, notes, changed_at(tz)
```

---

## Convenciones de Código

### FastAPI
- **Estructura en capas:** `router → service → repository` (no hay queries SQL directas en los routers,
  salvo `orders.py` que por simplicidad tiene la lógica transaccional embebida)
- **Dependencias de autenticación:** siempre via `Depends(get_current_user)`, `Depends(require_staff)`,
  `Depends(require_admin)` — nunca verificación manual de roles
- **Commits atómicos en operaciones críticas:** create_order y cancel_order hacen UN solo `db.commit()`
  al final; todas las mutaciones previas son sin commit
- **Errores con HTTPException:** siempre con `detail=` en español
- **Soft delete en Parts:** nunca se borra físicamente; se pone `is_active=False`
- **TimestampMixin:** todos los modelos heredan `created_at` / `updated_at` desde `base.py`
- **UUIDs como PK:** `Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)`
- **ENUMs con `values_callable`:** obligatorio para que SQLAlchemy use el `.value` (minúsculas)
  en lugar del `.name` (MAYÚSCULAS) al escribir en PostgreSQL

### Flask
- Todo el código está en un único archivo `app.py`
- Helper `api(method, path, **kwargs)` centraliza todas las llamadas a la API FastAPI,
  inyectando automáticamente el JWT de la sesión
- Decorator `@login_required` en todas las rutas protegidas
- Al login, verifica `role != "customer"` y rechaza si es cliente

### Laravel
- Controladores delgados: toda la lógica es llamar a la API con `Http::withToken(session('token'))`
- Middleware `CheckApiAuth` redirige a login si no hay token en sesión
- Blade templates usan Bootstrap 5.3
- Variables de entorno de Laravel se generan en `entrypoint.sh` desde las env vars de Docker

---

## Decisiones Técnicas Importantes

### 1. bcrypt pinado a 3.2.2
`passlib==1.7.4` es **incompatible con bcrypt>=4.0**. bcrypt 4.x cambió su API interna y lanza
`ValueError("password cannot be longer than 72 bytes")` incluso para contraseñas cortas. FastAPI
atrapa los `ValueError` y los devuelve como error 422. La solución es `bcrypt==3.2.2` en
`requirements.txt`. **No actualizar bcrypt sin actualizar también passlib.**

### 2. `values_callable` en todos los Enum de SQLAlchemy
SQLAlchemy `Enum(PythonEnum)` usa por defecto el atributo `.name` del enum (ej: `"CUSTOMER"`),
pero los ENUMs en PostgreSQL fueron creados con valores en minúsculas (`"customer"`). Sin
`values_callable=lambda obj: [e.value for e in obj]`, cada INSERT/UPDATE lanza:
```
sqlalchemy.exc.DataError: invalid input value for enum userrole: "CUSTOMER"
```
Afecta a: `user.py` (userrole), `order.py` (orderstatus), `inventory_log.py` (inventoryaction).
También requiere `name="userrole"` y `create_type=False` para no intentar recrear el tipo.

### 3. Migraciones idempotentes con bloques DO $$
PostgreSQL no soporta `CREATE TYPE IF NOT EXISTS`. La migración usa bloques PL/pgSQL:
```sql
DO $$ BEGIN
    CREATE TYPE userrole AS ENUM ('customer', 'staff', 'admin');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
```
Esto permite que `alembic upgrade head` se ejecute múltiples veces sin error (el entrypoint
lo hace en cada arranque del contenedor).

### 4. Laravel generado en build time (multi-stage Dockerfile)
`composer create-project laravel/laravel` corre durante `docker build`, no en el repo.
El stage `builder` genera el proyecto base y luego copia encima los archivos del repo
(`routes/`, `app/`, `resources/views/`, `bootstrap/app.php`). Por eso no hay `vendor/`
en el directorio `autopartes-laravel/`.

### 5. JWT almacenado en sesión de servidor (Flask y Laravel)
Ningún frontend expone el JWT al navegador directamente. Flask lo guarda en la sesión de Flask
(cookie firmada server-side). Laravel lo guarda en `session('token')`. Los controladores lo
inyectan en cada llamada a la API.

### 6. Transacción atómica en creación de órdenes
El flujo de `POST /orders` tiene 3 fases explícitas antes del commit:
1. Validar que todas las piezas existen y tienen stock suficiente
2. Crear el registro `Order` con sus `OrderItem`
3. Decrementar stock y crear `InventoryLog` (tipo SALE) por cada ítem

Un único `db.commit()` al final garantiza consistencia. Si algo falla en la fase 1,
no se muta nada. Cancelación sigue el mismo patrón (revierte stock + crea logs RETURN).

---

## Flujo de Creación del Primer Admin

No hay seed de datos. Para crear el primer usuario admin:

```bash
# 1. Registrar via endpoint público (crea con role=customer)
Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/v1/users/register \
  -ContentType 'application/json' \
  -Body '{"email":"admin@autopartes.com","password":"admin123","full_name":"Admin"}'

# 2. Promover a admin via psql
docker exec -it <db_container> psql -U admin -d autopartes \
  -c "UPDATE users SET role='admin' WHERE email='admin@autopartes.com';"
```

---

## Comandos Útiles

```bash
# Levantar todo
docker compose up --build

# Ver logs de la API
docker compose logs -f api

# Acceder a PostgreSQL
docker exec -it newmcuin-db-1 psql -U admin -d autopartes

# Reconstruir solo un servicio
docker compose up --build api

# Parar y limpiar volúmenes (BORRA la BD)
docker compose down -v
```

---

## Variables de Entorno (docker-compose.yml)

| Variable                     | Servicio | Valor                                    |
|------------------------------|----------|------------------------------------------|
| DATABASE_URL                 | api      | postgresql://admin:admin123@db:5432/autopartes |
| SECRET_KEY                   | api      | super-secret-key-for-jwt-2024            |
| ALGORITHM                    | api      | HS256                                    |
| ACCESS_TOKEN_EXPIRE_MINUTES  | api      | 60                                       |
| API_URL                      | flask    | http://api:8000/api/v1                   |
| SECRET_KEY                   | flask    | flask-secret-key-2024                    |
| API_URL                      | laravel  | http://api:8000/api/v1                   |
| APP_KEY                      | laravel  | base64:kJ5dNvTt... (hardcodeado)         |

---

## Estado del Proyecto (a 2026-03-27)

Proyecto **funcionalmente completo** según el rubric del tercer parcial (100 pts):
- 2 frontends (Flask interno + Laravel cliente) ✓
- Toda lógica en FastAPI ✓
- API estructurada por routers ✓
- Modelos SQLAlchemy ✓
- BD solo accesible via API ✓
- Docker para todos los componentes ✓
- Endpoint de registro de usuarios ✓
- Endpoint de órdenes (1 a N productos) ✓
- Endpoint de historial de órdenes ✓
- CRUD interno de usuarios ✓
- CRUD de piezas ✓
- 4+ tipos de reportes ✓
- Reportes en PDF, xlsx, docx ✓
