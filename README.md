# Software Médico - MediSoft

Un sistema integral de gestión médica construido con Django (backend), React (frontend), base de datos PostgreSQL y contenedorizado con Docker para una fácil implementación.

## 🌟 Características

- **Gestión de Pacientes**: Registrar y administrar la información de los pacientes
- **Gestión de Doctores**: Mantener perfiles de doctores y especializaciones
- **Programación de Citas**: Programar y rastrear las citas de los pacientes
- **Historias Médicas**: Almacenar y acceder a las historias médicas de los pacientes
- **Control de Acceso basado en Roles (RBAC)**: Sistema de permisos para diferentes roles de usuario

## 🎯 Sistema RBAC (Role-Based Access Control)

El sistema implementa un control de acceso granular por roles:

| Rol | Permisos Principales |
|-----|---------------------|
| **DOCTOR** | Ver/Editar sus pacientes, firmar historias médicas |
| **NURSE** | Ver pacientes asignados, tomar signos vitales |
| **SECRETARY** | Ver/Crear pacientes, programar citas |
| **RECEPTIONIST** | Acceso básico, ver demo de RBAC |
| **ADMINISTRATOR** | Acceso completo al sistema |

### Acceder a la Demo de RBAC
Después de iniciar sesión, navega a `/rbac-demo` para ver todos los controles de permisos en acción. Esta página muestra:
- Verificación de permisos en tiempo real
- Botones que aparecen/ocultan según tus permisos
- Mensajes de error cuando faltan privilegios

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11, Django 3.2, Django REST Framework
- **Frontend**: React 18, Material UI, Vite
- **Base de Datos**: PostgreSQL 15
- **Contenedorización**: Docker, Docker Compose
- **Proxy Inverso**: Nginx (para producción)

## 📚 Documentación Adicional

### READMEFIXES.md - Guía de Fixes y Soluciones

**Importante para desarrollo futuro**: Este archivo contiene el registro detallado de todos los errores encontrados y soluciones implementadas durante el desarrollo. Incluye:

- Problemas técnicos encontrados (como errores de login, CORS, autenticación)
- Causas raíz y cómo se diagnosticaron
- Soluciones paso a paso implementadas
- Comandos útiles para depuración

**Antes de hacer cambios o troubleshooting**, revisa `READMEFIXES.md` para entender qué soluciones ya fueron intentadas y evitar reinventar soluciones.

## 📋 Requisitos Previos

- Docker y Docker Compose instalados (recomendado)
- Node.js 18+ (para desarrollo local sin Docker)
- Python 3.11+ (para desarrollo local sin Docker)

## 🚀 Inicio Rápido con Docker

### Paso 1: Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus valores si es necesario
```

### Paso 2: Construir e iniciar los contenedores
```bash
docker-compose up --build -d
```

### Paso 3: Acceder a la aplicación

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interfaz de usuario React |
| **Backend API** | http://localhost:8000/api/ | Endpoints REST |
| **Django Admin** | http://localhost:8000/admin/ | Panel de administración |
| **RBAC Demo** | http://localhost:3000/rbac-demo | Demostración de permisos |

### Paso 4: Crear usuario administrador
```bash
docker-compose exec backend python manage.py createsuperuser
```

## 🧑‍💻 Desarrollo Local (sin Docker)

### Configuración del Backend

1. Crear y activar el entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o
   .\venv\Scripts\activate  # Windows
   ```

2. Instalar dependencias:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Ejecutar migraciones:
   ```bash
   python manage.py migrate
   ```

4. Crear superusuario (opcional):
   ```bash
   python manage.py createsuperuser
   ```

5. Iniciar servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

### Configuración del Frontend

1. Navegar al directorio frontend e instalar dependencias:
   ```bash
   cd frontend
   npm install
   ```

2. Crear archivo `.env.local` con:
   ```
   VITE_API_URL=http://localhost:8000/api
   ```

3. Iniciar servidor de desarrollo:
   ```bash
   npm run dev
   ```

El frontend se ejecutará en http://localhost:5173 y hará proxy de las peticiones API al backend Django.

## 📂 Estructura del Directorio

```
medisoft/
├── backend/              # Aplicación Django backend
│   ├── api/             # App médica (pacientes, doctores, citas)
│   ├── rbac/            # Sistema de control de acceso por roles
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # Aplicación React frontend
│   ├── src/
│   │   ├── components/  # Componentes reutilizables
│   │   ├── pages/       # Páginas de la aplicación
│   │   ├── lib/rbac/    # Utilidades RBAC (can, canWithState)
│   │   ├── utils/       # Funciones auxiliares
│   │   └── App.jsx      # Componente principal
│   ├── nginx.conf       # Configuración Nginx para producción
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml   # Definición de servicios Docker
├── nginx.conf           # Proxy inverso para producción
├── .env.example         # Template de variables de entorno
└── README.md           # Este archivo
```

## 🔌 Endpoints de la API

### Autenticación
- `POST /api/token/` - Obtener token JWT
- `GET /api/user/` - Información del usuario actual

### Pacientes
- `GET /api/patients/` - Listar todos los pacientes
- `POST /api/patients/` - Crear un nuevo paciente
- `GET /api/patients/:id/` - Obtener detalles de un paciente
- `PUT /api/patients/:id/` - Actualizar paciente

### Doctores
- `GET /api/doctors/` - Listar todos los doctores
- `POST /api/doctors/` - Crear un nuevo doctor

### Citas
- `GET /api/appointments/` - Listar todas las citas
- `POST /api/appointments/` - Programar una nueva cita
- `PUT /api/appointments/:id/status/` - Actualizar estado de cita

### Historias Médicas
- `GET /api/medical-records/` - Listar historias médicas
- `POST /api/medical-records/` - Crear historia médica
- `GET /api/medical-records/patient/:id/` - Historia de un paciente

## ⚙️ Variables de Entorno

El archivo `.env` debe contener las siguientes variables:

```
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-change-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=medical_software
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db  # or localhost for local development
DB_PORT=5432

# Frontend (set automatically by Docker)
VITE_API_URL=http://backend:8000/api
```

## 🐳 Comandos Útiles de Docker

```bash
# Construir e iniciar todos los servicios
docker-compose up --build -d

# Ver logs en tiempo real
docker-compose logs -f

# Ejecutar comandos dentro de un contenedor
docker-compose exec backend python manage.py shell
docker-compose exec frontend npm run build

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (¡cuidado! elimina la base de datos)
docker-compose down -v

# Reiniciar solo el backend
docker-compose restart backend

# Ver estado de los contenedores
docker-compose ps
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Docker Testing
```bash
# Construir todos los servicios
docker-compose build

# Iniciar y verificar salud de contenedores
docker-compose up -d
sleep 10  # Esperar a que la DB esté lista
curl http://localhost:8000/api/  # Verificar backend
curl http://localhost:3000  # Verificar frontend
```

## 🔍 Quality Assurance

### Linting Python
```bash
ruff check backend
```

### Linting JavaScript
```bash
cd frontend
npm run lint
```

### Type Checking (si se usa TypeScript)
```bash
cd frontend
npm run typecheck
```

## 📊 Base de Datos y Migraciones

```bash
# Aplicar migraciones pendientes
docker-compose exec backend python manage.py migrate

# Crear una nueva migración
docker-compose exec backend python manage.py makemigrations

# Cargar datos de prueba
docker-compose exec backend python manage.py loaddata demo_data.json

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser
```

## 🔐 Autenticación y Autorización

### Token Authentication (Django REST Framework)

Los endpoints protegidos requieren el header:
```
Authorization: Token <your-token>
```

### RBAC Permissions

El sistema verifica permisos en tres niveles:

1. **Route-level**: Control de acceso al menú de navegación
2. **Component-level**: Mostrar/ocultar botones según permisos
3. **Data-level**: Validar acceso a recursos específicos

Ejemplo de uso:
```javascript
import { can, canWithState, getButtonGuard } from './lib/rbac/can';

// Verificar permiso simple
if (can(user, 'edit', 'patients')) {
  // Mostrar botón de editar
}

// Verificar con estado del recurso
const result = canWithState(user, 'sign', 'clinical_records');
if (!result.allowed) return <Tooltip title={result.reason}>{/* ... */}</Tooltip>;

// Botón con guard completo
const guard = getButtonGuard(user, 'create', 'patients');
return guard.visible ? <Button disabled={guard.disabled} /> : null;
```

## 🌐 Nginx Configuration (Producción)

El archivo `nginx.conf` configura:
- Proxy inverso al frontend y backend
- Gzip compression para mejor rendimiento
- Cache headers para archivos estáticos
- Manejo de CORS
- Páginas de error personalizadas

Para usar en producción, copia el archivo a tu servidor Nginx y ajusta los `server_name` y puertos según necesites.

## 📦 Producción Build

```bash
# Construir frontend
cd frontend
npm run build

# Iniciar con Docker Compose (producción)
docker-compose -f docker-compose.yml up -d --build
```

## 🛠️ Troubleshooting

### Puerto en uso
```bash
# Cambiar puertos en docker-compose.yml o detener servicios que usan esos puertos
lsof -i :3000  # Ver qué está usando el puerto 3000
```

### Error de conexión a base de datos
```bash
# Verificar que la DB esté healthy
docker-compose ps db

# Revisar logs
docker-compose logs db
```

### CORS errors
```bash
# Verificar DJANGO_ALLOWED_HOSTS en .env
# Asegurar que incluya localhost, 127.0.0.1 y tu dominio
```

### Contenedor no inicia
```bash
# Revisar logs del contenedor específico
docker-compose logs frontend

# Reiniciar contenedor
docker-compose restart frontend
```

## 🤝 Contributing

1. Fork el repositorio
2. Crea una rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Haz tus cambios y commit (`git commit -m 'Add some feature'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

MIT License

---

**Nota**: Este es un sistema de demostración para fines educativos y no cumple con requisitos de cumplimiento HIPAA. No debe usarse para almacenar datos médicos reales en producción.
