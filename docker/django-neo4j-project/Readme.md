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
│   │   │ 
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

## Gestión de Datos y Análisis de Redes

Este proyecto incluye scripts para cargar datos desde archivos CSV, crear redes de análisis usando NetworkX y almacenar/gestionar estas redes en Neo4j.

### Carga de Datos

Los datos de SPOA y personas pueden cargarse desde archivos CSV a la base de datos Django utilizando el siguiente comando:

```bash
# Cargar todos los datos
python manage.py cargar_datos

# Cargar solo datos de consolidado SPOA
python manage.py cargar_datos --consolidado

# Cargar solo datos de personas
python manage.py cargar_datos --personas
```

Los archivos CSV deben estar ubicados en la carpeta `dashboard/data/` con los siguientes nombres:
- `consolidado_delitos_2025-04-09.csv`
- `personas_delitos_2025-04-09.csv`

Para preparar la estructura de carpetas necesaria, ejecute:

```bash
python manage.py preparar_carpetas
```

### Creación de Redes en Neo4j

El proyecto incluye funcionalidades para crear una red no dirigida a partir de los datos del SPOA, donde los nodos son los NUNC y las personas, y los enlaces representan las relaciones entre ellos con atributos de calidad de vínculo.

#### Comando básico:

```bash
python manage.py crear_red_neo4j
```

#### Opciones disponibles:

```bash
# Usar un archivo CSV específico
python manage.py crear_red_neo4j --archivo="path/to/consolidado_delitos_2025-04-09.csv"

# No calcular métricas de centralidad (más rápido para redes grandes)
python manage.py crear_red_neo4j --sin-metricas

# Ajustar el tamaño del chunk para procesar el CSV
python manage.py crear_red_neo4j --chunksize=100000

# Ajustar el tamaño del lote para operaciones en Neo4j
python manage.py crear_red_neo4j --batch-size=1000

# Solo crear la red en memoria (no guardarla en Neo4j)
python manage.py crear_red_neo4j --solo-red

# Solo guardar una red previamente creada en Neo4j
python manage.py crear_red_neo4j --solo-guardar
```

#### Ejemplos de uso:

```bash
# Proceso completo con archivo CSV y tamaños de lote optimizados
python manage.py crear_red_neo4j --archivo="data/consolidado_delitos_2025-04-09.csv" --chunksize=100000 --batch-size=1000

# Para archivos muy grandes, proceso en dos etapas:
# 1. Primero crear solo la red (no la guarda en Neo4j)
python manage.py crear_red_neo4j --archivo="data/consolidado_delitos_2025-04-09.csv" --solo-red --chunksize=100000
# 2. Luego guardar la red en Neo4j 
python manage.py crear_red_neo4j --solo-guardar --batch-size=1000

# Para redes de tamaño moderado con todas las métricas
python manage.py crear_red_neo4j --chunksize=50000 --batch-size=5000
```

### Limpieza de Neo4j

Para eliminar todos los nodos y relaciones de la base de datos Neo4j:

```bash
python manage.py limpiar_neo4j
```

Este comando elimina progresivamente relaciones y nodos en pequeños lotes para evitar problemas de memoria.

También está disponible un script independiente para casos donde se necesite una limpieza de muy bajo uso de memoria:

```bash
# Ejecutar con tamaño de lote por defecto (100)
python clean_neo4j.py

# Especificar un tamaño de lote más pequeño
python clean_neo4j.py 50
```

### Consideraciones de Rendimiento

- Para archivos grandes (más de 1 millón de registros), aumente el `chunksize` para la lectura de CSV y reduzca el `batch-size` para operaciones en Neo4j.
- Si encuentra errores de memoria en Neo4j, ajuste la configuración en `neo4j.conf`:
  ```
  dbms.memory.transaction.total.max=4g
  ```
- El procesamiento en etapas (usando `--solo-red` seguido de `--solo-guardar`) permite manejar redes extremadamente grandes.
- Para visualizaciones y consultas rápidas, acceda a Neo4j Browser en http://localhost:7474/browser/

Si se quiere eliminar desde el navegador se debe ejecutar el comando: "MATCH (n) DETACH DELETE n"

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

# Estructura JavaScript del Dashboard

Este documento detalla la estructura de archivos JavaScript utilizados en el dashboard del proyecto.

## Estructura de Carpetas

```
django-neo4j-project/
└── django/
    └── static/
        ├── css/
        │   └── style.css            # Estilos globales
        ├── js/
        │   ├── dashboard/           # Scripts específicos del dashboard
        │   │   ├── utils.js         # Funciones de utilidad comunes
        │   │   ├── fuentes.js       # Funcionalidad para sección de fuentes
        │   │   ├── seccionales.js   # Funcionalidad para sección de seccionales
        │   │   ├── necropsias.js    # Funcionalidad para sección de necropsias
        │   │   ├── delitos.js       # Funcionalidad para sección de delitos
        │   │   └── main.js          # Script principal que inicializa todo
        │   └── otra_app/            # Scripts para otras apps (si es necesario)
        └── vendors/                 # Librerías de terceros
            ├── chart.js/            # Para gráficos
            ├── highcharts/          # Para treemap
            └── bootstrap/           # Framework CSS
```

## Descripción de los Archivos JavaScript

### 1. `utils.js`

Contiene funciones de utilidad generales usadas en todo el dashboard:

- Configuración global para Chart.js
- Generación de colores aleatorios para gráficos
- Formateo de números
- Gestión de paginación
- Visualización de detalles de registros
- Exportación de tablas a CSV

### 2. `fuentes.js`

Maneja la visualización de la distribución por fuente:

- Gráfico de tipo donut para mostrar la distribución
- Interactividad al hacer clic en las secciones del gráfico
- Carga de datos filtrados por fuente seleccionada
- Visualización de tabla paginada con los registros

### 3. `seccionales.js`

Gestiona la visualización de la distribución por seccional:

- Creación del treemap para visualizar seccionales
- Gráficos de barras horizontales para unidades y despachos
- Carga de datos anidados (unidades y despachos por seccional)
- Visualización de tabla paginada con los registros

### 4. `necropsias.js`

Maneja la visualización de la distribución por necropsia:

- Gráfico de tipo donut para mostrar la distribución
- Interactividad al hacer clic en las secciones del gráfico
- Carga de datos filtrados por necropsia seleccionada
- Visualización de tabla paginada con los registros

### 5. `delitos.js`

Gestiona el análisis de personas por delitos:

- Interactividad en las tarjetas de delitos
- Visualización de intersecciones entre delitos
- Actualización dinámica del gráfico según el delito seleccionado

### 6. `main.js`

Script principal que inicializa todos los componentes:

- Inicialización de todos los gráficos cuando el DOM está cargado
- Configuración de botones de exportación
- Manejo de actualizaciones de datos en tiempo real (simulado)
- Sistema de notificaciones

## Uso en la Aplicación

Los scripts se incluyen en `dashboard.html` de la siguiente manera:

```html
{% block js %}
<!-- Librerías de terceros -->
<script src="{% static 'vendors/chart.js/chart.min.js' %}"></script>
<script src="{% static 'vendors/highcharts/highcharts.js' %}"></script>
<script src="{% static 'vendors/highcharts/modules/treemap.js' %}"></script>
<script src="{% static 'vendors/highcharts/modules/exporting.js' %}"></script>

<!-- Datos del backend para usar en JavaScript -->
<script>
    // Datos que vienen del backend
    const dashboardData = {
        totalSpoa: {{ total_spoa }},
        totalPersonas: {{ total_personas }},
        // Otros datos...
    };
</script>

<!-- Scripts del dashboard -->
<script src="{% static 'js/dashboard/utils.js' %}"></script>
<script src="{% static 'js/dashboard/fuentes.js' %}"></script>
<script src="{% static 'js/dashboard/seccionales.js' %}"></script>
<script src="{% static 'js/dashboard/necropsias.js' %}"></script>
<script src="{% static 'js/dashboard/delitos.js' %}"></script>
<script src="{% static 'js/dashboard/main.js' %}"></script>
{% endblock %}
```

## Consideraciones para la implementación

1. **Requisitos para instalar las dependencias**:
   - Chart.js (v3.x)
   - Highcharts (para el treemap)
   - Bootstrap 5.x para los estilos

2. **Backend**: 
   - Las rutas de API mencionadas en los archivos JS deben implementarse en las vistas de Django.
   - Los datos deben seguir el formato esperado por los scripts.

3. **Orden de carga**:
   - Los scripts deben cargarse en el orden especificado para garantizar que las dependencias se resuelvan correctamente.