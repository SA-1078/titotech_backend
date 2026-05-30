# TitoTech Backend — E-Commerce API para Equipos y Accesorios Móviles

¡Bienvenido al backend de **TitoTech**! Esta es una API RESTful empresarial de comercio electrónico desarrollada con **Django**, **Django REST Framework (DRF)** y **PostgreSQL**. Cuenta con autenticación segura por **JWT**, manejo transaccional de inventario (stock) y una arquitectura moderna que separa el **Carrito de Compras (Cart)** temporal del **Historial Permanente de Órdenes (Orders)**.

Este proyecto ha sido estructurado siguiendo las mejores prácticas de la industria y cumple con el 100% de la rúbrica y los requerimientos solicitados para la entrega del proyecto de 4to Semestre.

---

## 🛠️ Tecnologías y Librerías Utilizadas

- **Core**: Python 3.13 + Django 6.0.5
- **API Engine**: Django REST Framework (DRF)
- **Base de Datos**: PostgreSQL
- **Autenticación**: `djangorestframework-simplejwt` (JWT de larga duración y rotación de tokens)
- **Configuración Segura**: `python-decouple` (Manejo de variables de entorno con `.env`)
- **Filtros**: `django-filter` (Filtros dinámicos en los endpoints)
- **Gestión de Paquetes**: `uv` (Gestor de dependencias ultrarrápido)

---

## 📐 Diseño de Base de Datos y Arquitectura (7 Entidades)

El backend implementa **7 entidades** perfectamente relacionadas en PostgreSQL para cubrir un flujo real de e-commerce:

1. **`Category`** (`titotech_categories`): Categorías para organizar productos (Smartphones, Cases, Cargadores, Audífonos).
2. **`Product`** (`titotech_products`): Dispositivos móviles y accesorios con campos opcionales inteligentes y control estricto de stock.
3. **`CustomerProfile`** (`titotech_customerprofile`): Extensión del modelo User de Django con dirección de envío, ciudad y teléfono.
4. **`Cart`** (`titotech_carts`): Carrito temporal de compras por cliente (OneToOne con el perfil).
5. **`CartItem`** (`titotech_cartitems`): Productos agregados al carrito con su cantidad. **No descuenta stock hasta hacer Checkout**.
6. **`Order`** (`titotech_orders`): Registro definitivo de compras/ventas concluidas e históricas.
7. **`OrderDetail`** (`titotech_orderdetails`): Ítems comprados en una orden con registro histórico del `unit_price` al momento del pago.

---

## 🚀 Guía de Instalación y Ejecución

### 1. Clonar el repositorio y acceder
```bash
git clone <url-del-repositorio>
cd tito_tech_backend_django
```

### 2. Configurar variables de entorno
Crea un archivo llamado `.env` en la raíz del proyecto basándote en el archivo `.env.example` provisto. Modifica las credenciales con los datos de tu PostgreSQL local:
```env
DEBUG=True
SECRET_KEY=django-insecure-tito-tech-api-key-2026
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=tito_tech_db
DB_USER=postgres
DB_PASSWORD=tu_contraseña_postgres
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOW_ALL_ORIGINS=True
```

### 3. Crear el entorno virtual e instalar dependencias
Si utilizas **`uv`** (recomendado por velocidad):
```bash
uv venv
uv sync
```
O de la forma tradicional con **`pip`**:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt  # O usa el instalador a través de pyproject.toml
```

### 4. Ejecutar las migraciones y Seeders de Datos
El proyecto incluye migraciones pre-configuradas con cargadores automáticos de categorías y asignaciones iniciales de stock.
```bash
# Ejecutar las migraciones
uv run python manage.py migrate

# Crea tu superusuario local para el panel de administración
uv run python manage.py createsuperuser
```

### 5. Ejecutar el servidor de desarrollo
```bash
uv run python manage.py runserver
```
El backend estará disponible en: **`http://127.0.0.1:8000/api/`**

---

## 👥 Credenciales de Prueba

Para facilitar la evaluación con Postman, la base de datos cuenta con las siguientes credenciales de prueba pre-configuradas (las cuales puedes registrar localmente o usar de ejemplo):

### 1. Administrador (Superuser - is_staff = True)
- **Username**: `admin_user`
- **Password**: `ContrasenaAdmin123!`
- **Email**: `admin@titotech.com`
- **Permisos**: CRUD total de Categorías y Productos, estadísticas de ventas, cambios de estado y control CRUD global sobre perfiles y order details.

### 2. Cliente Registrado (Customer - Normal)
- **Username**: `cliente_pruebas`
- **Password**: `ContrasenaCliente123!`
- **Email**: `cliente@example.com`
- **Permisos**: Ver productos y categorías (público), CRUD total sobre su propio Carrito de Compras, realizar Checkout y visualizar su Historial de Pedidos.

---

## 📋 Listado Completo de Endpoints

### 🟢 1. Health Check
- `GET /api/health/` -> Estado general del servidor. Sin autenticación.

### 🔐 2. Autenticación (SimpleJWT)
- `POST /api/auth/register/` -> Registrar un nuevo usuario (crea User + CustomerProfile automáticamente).
- `POST /api/auth/login/` -> Iniciar sesión (devuelve tokens JWT `access` y `refresh` y campos de perfil).
- `POST /api/auth/token/refresh/` -> Refrescar el token de acceso vencido.
- `POST /api/auth/token/verify/` -> Validar la integridad del token actual.
- `POST /api/auth/logout/` -> Cerrar sesión (añade token actual a la blacklist).

### 📂 3. Categorías (`Categories`)
- `GET /api/categories/` -> Listar todas las categorías (Público). Soporta `?search=` y `?ordering=`.
- `GET /api/categories/{id}/` -> Detalle de una categoría (Público).
- `POST /api/categories/` -> Crear categoría (Solo Admin).
- `PATCH /api/categories/{id}/` -> Editar categoría (Solo Admin).
- `DELETE /api/categories/{id}/` -> Eliminar categoría (Solo Admin).
- `GET /api/categories/{id}/products/` -> Listar todos los productos filtrados por esta categoría (Público).

### 📱 4. Productos (`Products`)
- `GET /api/products/` -> Listar todos los productos (Público). Soporta paginación, `?search=brand`, `?category=id`, y `?price_min=/price_max=`.
- `GET /api/products/disponibles/` -> Listar solo productos con stock > 0 (Público).
- `GET /api/products/{id}/` -> Detalle del producto (Público).
- `POST /api/products/` -> Crear producto (Solo Admin. Soporta Smartphones y Accesorios).
- `PATCH /api/products/{id}/` -> Editar producto (Solo Admin).
- `POST /api/products/{id}/restock/` -> Sumar unidades de stock al inventario (Solo Admin).
- `DELETE /api/products/{id}/` -> Eliminar producto (Solo Admin).

### 🛒 5. Carrito de Compras (`Cart`) - *Temporal*
*Todos requieren autenticación de cliente (Token JWT):*
- `GET /api/cart/` -> Obtiene el carrito del cliente con subtotales, totales y ítems.
- `POST /api/cart/add-item/` -> Agrega un producto al carrito (verifica stock).
- `PATCH /api/cart/items/{item_id}/` -> Cambia la cantidad de un producto en el carrito (verifica stock).
- `DELETE /api/cart/items/{item_id}/` -> Remueve el producto del carrito.
- `DELETE /api/cart/clear/` -> Vacía por completo el carrito.
- **`POST /api/cart/checkout/`** (Checkout transaccional): Valida stock final, resta stock del inventario de productos, crea la `Order` y sus `OrderDetail` históricos, y vacía el carrito actual en un único paso atómico.

### 📦 6. Órdenes (`Orders`) - *Permanente*
*Requieren autenticación:*
- `GET /api/orders/` -> Historial de órdenes concluidas (cliente ve las suyas / admin ve todas).
- `GET /api/orders/{id}/` -> Detalle completo de una orden e ítems comprados históricamente.
- `DELETE /api/orders/{id}/` -> Cancela y elimina el pedido (devuelve el stock completo de sus ítems al inventario).
- `POST /api/orders/{id}/actualizar-estado/` -> Cambia el estado del pedido a `shipped`, `delivered`, etc. (Solo Admin).
- `GET /api/orders/stats/` -> Estadísticas financieras globales de facturación (Solo Admin).

### 👤 7. Perfiles de Clientes (`Customer Profiles`)
- `GET /api/users/profile/` -> Ver perfil propio del cliente logueado.
- `PATCH /api/users/profile/` -> Actualizar dirección, ciudad y teléfono de envío.
- `GET /api/customerprofiles/` -> CRUD global de perfiles (Solo Admin).

---

## 📦 Importar Colección de Postman

El archivo con la colección de Postman configurada para importar se encuentra en la raíz del proyecto con el nombre:
**`TitoTech API — Mobile Devices Sales.postman_collection.json`**

### Características de la Colección:
1. **Auth Automática**: Al ejecutar `Login (Admin)` o `Login (Customer)`, la colección extrae el token JWT del cuerpo y lo guarda en las variables de Postman de forma transparente. Las demás solicitudes se autentican solas usando ese token guardado.
2. **Gestión de IDs Dinámica**: Al registrar perfiles, crear categorías o productos, sus respectivos IDs se guardan automáticamente para que puedas encadenar pruebas sin tener que copiar y pegar IDs manualmente de una solicitud a otra.
3. **Validación de Scripts**: Cuenta con aserciones de código de estado (status codes) en cada request para verificar que los retornos de error (400, 401, 200, 201) sean los esperados por el sistema de evaluación.
