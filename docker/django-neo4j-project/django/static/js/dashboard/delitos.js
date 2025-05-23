/**
 * Gráficos y funcionalidad para la sección de Análisis de Personas por Delitos
 */

let chartIntersecciones; // Variable global para el gráfico
let delitoCategoriaActiva = null; // Delito actualmente seleccionado

/**
 * Inicializa la visualización de análisis de personas por delitos
 */
function inicializarGraficoDelitos() {
    // Configurar los eventos de click para las tarjetas de delitos
    document.getElementById('cardDesaparicion').addEventListener('click', function() {
        mostrarInterseccionesDelito('desaparcion_forzada', 'Desaparición Forzada');
    });
    
    document.getElementById('cardHomicidio').addEventListener('click', function() {
        mostrarInterseccionesDelito('homicidio', 'Homicidio');
    });
    
    document.getElementById('cardSecuestro').addEventListener('click', function() {
        mostrarInterseccionesDelito('secuestro', 'Secuestro');
    });
    
    document.getElementById('cardReclutamiento').addEventListener('click', function() {
        mostrarInterseccionesDelito('reclutamiento_ilicito', 'Reclutamiento');
    });
    
    document.getElementById('cardRUD').addEventListener('click', function() {
        mostrarInterseccionesDelito('rud', 'RUD');
    });
    
    // Inicializar el canvas para el gráfico de intersecciones
    const ctxIntersecciones = document.getElementById('graficaIntersecciones').getContext('2d');
    
    // Crear un gráfico vacío inicialmente
    chartIntersecciones = new Chart(ctxIntersecciones, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Personas',
                data: [],
                backgroundColor: generarColores(5),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${formatNumber(context.raw)}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Muestra las intersecciones de un delito específico con otros delitos
 * @param {string} categoriaDelito - Categoría interna del delito (campo en BD)
 * @param {string} nombreDelito - Nombre mostrado del delito
 */
function mostrarInterseccionesDelito(categoriaDelito, nombreDelito) {
    // Desactivar tarjeta anterior si existe
    if (delitoCategoriaActiva) {
        document.getElementById(`card${campoAClase(delitoCategoriaActiva)}`).classList.remove('bg-primary', 'text-white');
    }
    
    // Activar la nueva tarjeta
    document.getElementById(`card${campoAClase(categoriaDelito)}`).classList.add('bg-primary', 'text-white');
    delitoCategoriaActiva = categoriaDelito;
    
    // Actualizar título
    document.getElementById('tituloIntersecciones').textContent = `Personas relacionadas con ${nombreDelito} por otros delitos`;
    
    // En un caso real, harías una petición AJAX:
    fetch(`/dashboard/api/intersecciones-delito/?delito=${encodeURIComponent(categoriaDelito)}`)
        .then(response => response.json())
        .then(data => {
            // Actualizar gráfico con los datos de intersección
            actualizarGraficoIntersecciones(data, nombreDelito);
        })
        .catch(error => {
            console.error('Error cargando intersecciones:', error);
        });
}

/**
 * Actualiza el gráfico de intersecciones con nuevos datos
 * @param {Object} data - Datos de intersecciones
 * @param {string} nombreDelito - Nombre del delito principal
 */
function actualizarGraficoIntersecciones(data, nombreDelito) {
    // Preparar los datos para el gráfico
    const labels = data.intersecciones.map(i => i.delito);
    const valores = data.intersecciones.map(i => i.cantidad);
    const colores = generarColores(labels.length);
    
    // Actualizar el gráfico
    chartIntersecciones.data.labels = labels;
    chartIntersecciones.data.datasets[0].data = valores;
    chartIntersecciones.data.datasets[0].backgroundColor = colores;
    chartIntersecciones.data.datasets[0].label = `Intersección con ${nombreDelito}`;
    chartIntersecciones.update();
}

/**
 * Convierte un nombre de campo de la base de datos a una clase CSS
 * @param {string} campo - Nombre del campo
 * @returns {string} - Nombre de clase CSS
 */
function campoAClase(campo) {
    if (campo === 'desaparcion_forzada') return 'Desaparicion';
    if (campo === 'homicidio') return 'Homicidio';
    if (campo === 'secuestro') return 'Secuestro';
    if (campo === 'reclutamiento_ilicito') return 'Reclutamiento';
    if (campo === 'rud') return 'RUD';
    return campo.charAt(0).toUpperCase() + campo.slice(1);
}