# Django + Neo4j + Nginx Project

Este proyecto integra Django, Neo4j y Nginx utilizando Docker para crear una aplicación web con una base de datos de grafos. Incluye un panel de control (dashboard) para visualizar y administrar los datos de Neo4j.

## Estructura del Proyecto

```
django-neo4j-project/
├── .env                     # Variables de entorno
├── docker-compose.yml       # Configuración de Docker Compose
├── nginx/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── conf.d/
│   │   └── default.conf
├── django/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── entrypoint.sh
│   ├── manage.py
│   ├── static/              # Archivos estáticos globales
│   │   ├── css/             # CSS global
│   │   ├── js/              # JS global
│   │   ├── img/             # Imágenes globales
│   │   ├── vendors/         # Librerías de terceros
│   │   ├── dashboard/       # Estáticos específicos del dashboard
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── img/
│   │   └── otra_app/        # Estáticos para otras apps
│   ├── templates/           # Templates globales
│   │   ├── base.html        # Template base
│   │   ├── dashboard/       # Templates del dashboard
│   │   │   ├── index.html
│   │   │   ├── components/
│   │   │   │   ├── navbar.html
│   │   │   │   ├── sidebar.html
│   │   │   │   └── footer.html
│   │   │   └── pages/
│   │   │       ├── home.html
│   │   │       ├── analytics.html
│   │   │       └── settings.html
│   │   └── otra_app/        # Templates para otras apps
│   ├── myproject/           # Proyecto principal de Django
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── neo4j_driver.py
│   ├── dashboard/           # App de dashboard
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── utils.py
│   │   ├── services.py      # Servicios para interactuar con Neo4j
│   │   └── tests/
│   └── otra_app/            # Otras apps
├── neo4j/
│   ├── data/                # Datos de Neo4j
│   ├── logs/                # Logs de Neo4j
│   └── conf/                # Configuración de Neo4j
│       └── neo4j.conf
└── README.md
```

## Requisitos Previos

- Docker
- Docker Compose

## Configuración

1. Clona este repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd django-neo4j-project
   ```

2. Copia el archivo `.env.example` a `.env` y modifica las variables según tus necesidades:
   ```bash
   cp .env.example .env
   ```

3. Crea las carpetas necesarias para Neo4j y para los archivos estáticos/templates:
   ```bash
   # Para Neo4j
   mkdir -p neo4j/data neo4j/logs neo4j/conf
   chmod -R 777 neo4j/data neo4j/logs neo4j/conf
   
   # Para Django
   mkdir -p django/templates
   mkdir -p django/templates/dashboard/components
   mkdir -p django/templates/dashboard/pages
   mkdir -p django/static/css django/static/js django/static/img django/static/vendors
   mkdir -p django/static/dashboard/css django/static/dashboard/js django/static/dashboard/img
   ```

## Inicio del Proyecto

1. Construye e inicia los contenedores:
   ```bash
   docker-compose up -d
   ```

2. Verifica que todos los servicios estén funcionando:
   ```bash
   docker-compose ps
   ```

3. Para ver los logs de un servicio específico:
   ```bash
   docker-compose logs django
   docker-compose logs neo4j
   docker-compose logs nginx
   ```

## Acceso a los Servicios

- **Aplicación Django**: http://localhost
- **Panel de Control**: http://localhost/dashboard/
- **Neo4j Browser**: http://localhost:7474 (usuario: neo4j, contraseña: definida en `.env`)

## Desarrollo

### Trabajando con Django

El código de Django se monta como un volumen en el contenedor, por lo que puedes editar los archivos localmente y los cambios se reflejarán en tiempo real.

Para ejecutar comandos de Django:

```bash
docker-compose exec django python manage.py <comando>
```

Ejemplos:
```bash
docker-compose exec django python manage.py makemigrations
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
```

### Configuración de Templates y Archivos Estáticos

El proyecto está configurado para buscar templates y archivos estáticos en las siguientes ubicaciones:

- **Templates**: `django/templates/` (fuera de las apps)
- **Archivos estáticos**: `django/static/` (fuera de las apps)

Esto permite organizar los templates y archivos estáticos por app sin necesidad de incluirlos dentro de las carpetas de cada app.

### Creando una nueva App

Para crear una nueva app en el proyecto:

```bash
docker-compose exec django python manage.py startapp nueva_app
```

Después de crear la app:

1. Añádela a `INSTALLED_APPS` en `settings.py`
2. Crea las carpetas para templates y estáticos:
   ```bash
   mkdir -p django/templates/nueva_app
   mkdir -p django/static/nueva_app/css django/static/nueva_app/js django/static/nueva_app/img
   ```

### Trabajando con Neo4j

Para acceder a la consola de Neo4j Cypher:

```bash
docker-compose exec neo4j cypher-shell -u neo4j -p <tu-contraseña>
```

### Conexión de Django a Neo4j

El proyecto incluye una configuración básica para conectar Django a Neo4j utilizando el driver oficial de Neo4j para Python.

Ejemplo de uso en Django:

```python
from myproject.neo4j_driver import execute_query

# Consulta a Neo4j
results = execute_query("MATCH (n) RETURN n LIMIT 10")
```

## Solución de Problemas

### Permisos de Neo4j

Si tienes problemas con los permisos de Neo4j:

```bash
sudo chown -R 7474:7474 neo4j/data
sudo chown -R 7474:7474 neo4j/logs
```

### Script de Entrypoint no ejecutable

Si el script entrypoint.sh no tiene permisos de ejecución:

```bash
chmod +x django/entrypoint.sh
```

### Error SSL con Neo4j

Si Neo4j muestra errores relacionados con SSL, asegúrate de tener las configuraciones correctas:

- En `neo4j.conf`:
  ```
  dbms.connector.bolt.tls_level=DISABLED
  ```

- O en `docker-compose.yml`:
  ```yaml
  environment:
    - NEO4J_dbms_connector_bolt_tls__level=DISABLED
  ```

## Dashboard

El panel de control (dashboard) proporciona una interfaz para visualizar y administrar los datos en Neo4j. Incluye:

- Página principal con resumen de estadísticas
- Página de análisis con visualización de relaciones
- Página de configuración

Para acceder al dashboard, navega a http://localhost/dashboard/ después de iniciar el proyecto.

## Parada del Proyecto

Para detener los contenedores:

```bash
docker-compose down
```

Para detener y eliminar los volúmenes (¡perderás los datos!):

```bash
docker-compose down -v
```

## Producción

Este proyecto está configurado principalmente para desarrollo. Para un entorno de producción, considera:

1. Configurar HTTPS con certificados reales
2. Mejorar la seguridad de Neo4j con SSL/TLS adecuado
3. Ajustar la configuración de memoria para los servicios
4. Implementar un sistema de respaldo para Neo4j
5. Configurar monitorización y logging

## Tecnologías

- **Django**: Framework web de Python
- **Neo4j**: Base de datos de grafos
- **Nginx**: Servidor web y proxy inverso
- **Docker**: Plataforma de contenedores
- **Docker Compose**: Herramienta para definir y ejecutar aplicaciones Docker multi-contenedor
- **Bootstrap**: Framework CSS para la interfaz de usuario
- **Chart.js**: Biblioteca JavaScript para visualización de datos
