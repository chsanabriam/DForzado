/**
 * Gráficos y funcionalidad para la sección de Distribución por Seccional
 */

let chartUnidades;     // Variable global para el gráfico de unidades
let chartDespachos;    // Variable global para el gráfico de despachos
let treemapSeccional;  // Variable global para el treemap

/**
 * Inicializa la visualización de distribución por seccional
 */
function inicializarGraficoSeccionales() {
    const seccionalesData = dashboardData.seccionalesData;
    
    // Crear TreeMap de seccionales
    treemapSeccional = Highcharts.chart('treemapSeccional', {
        series: [{
            type: 'treemap',
            layoutAlgorithm: 'squarified',
            data: seccionalesData.map((item, index) => ({
                name: item.seccional,
                value: item.cantidad,
                colorValue: index,
                id: item.seccional
            })),
            dataLabels: {
                enabled: true,
                format: '{point.name}<br>{point.value}'
            },
            events: {
                click: function(event) {
                    const seccional = event.point.name;
                    seleccionarSeccional(seccional);
                }
            }
        }],
        title: {
            text: null
        },
        colorAxis: {
            minColor: '#FAFAFA',
            maxColor: '#4285F4'
        },
        tooltip: {
            formatter: function() {
                return `<b>${this.point.name}</b><br>
                        Registros: ${formatNumber(this.point.value)}<br>
                        Porcentaje: ${((this.point.value / dashboardData.totalSpoa) * 100).toFixed(2)}%`;
            }
        }
    });
}

/**
 * Gestiona la selección de una seccional
 * @param {string} seccional - Seccional seleccionada
 */
function seleccionarSeccional(seccional) {
    document.getElementById('seccionalSeleccionada').textContent = seccional;
    document.getElementById('mensajeSeccional').style.display = 'none';
    document.getElementById('contenidoSeccional').style.display = 'block';
    
    // Cargar los datos para esta seccional (unidades y despachos)
    cargarDatosSeccional(seccional);
}

/**
 * Carga datos de una seccional (unidades, despachos y registros)
 * @param {string} seccional - Seccional seleccionada
 */
function cargarDatosSeccional(seccional) {
    // En un caso real, harías peticiones AJAX:
    Promise.all([
        fetch(`/dashboard/api/unidades-por-seccional/?seccional=${encodeURIComponent(seccional)}`).then(r => r.json()),
        fetch(`/dashboard/api/despachos-por-seccional/?seccional=${encodeURIComponent(seccional)}`).then(r => r.json())
    ])
    .then(([datosUnidades, datosDespachos]) => {
        // Actualizar gráfico de unidades
        crearGraficoUnidadesPorSeccional(datosUnidades);
        
        // Actualizar gráfico de despachos
        crearGraficoDespachosPorSeccional(datosDespachos);
        
        // Cargar registros para la primera página
        cargarRegistrosSeccional(seccional, 1);
    })
    .catch(error => {
        console.error('Error cargando datos de seccional:', error);
    });
}

/**
 * Crea o actualiza el gráfico de unidades por seccional
 * @param {Array} datos - Datos de unidades
 */
function crearGraficoUnidadesPorSeccional(datos) {
    const ctx = document.getElementById('graficaUnidadesPorSeccional').getContext('2d');
    
    // Destruir gráfico existente si lo hay
    if (window.chartUnidades) {
        window.chartUnidades.destroy();
    }
    
    // Crear nuevo gráfico horizontal bar
    window.chartUnidades = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: datos.map(d => d.unidad),
            datasets: [{
                label: 'Registros',
                data: datos.map(d => d.cantidad),
                backgroundColor: generarColores(datos.length),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Registros: ${formatNumber(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Crea o actualiza el gráfico de despachos por seccional
 * @param {Array} datos - Datos de despachos
 */
function crearGraficoDespachosPorSeccional(datos) {
    const ctx = document.getElementById('graficaDespachosPorSeccional').getContext('2d');
    
    // Destruir gráfico existente si lo hay
    if (window.chartDespachos) {
        window.chartDespachos.destroy();
    }
    
    // Limitar a los 15 despachos principales si hay muchos
    let datosLimitados = datos;
    if (datos.length > 15) {
        // Ordenar por cantidad descendente
        datosLimitados = [...datos].sort((a, b) => b.cantidad - a.cantidad).slice(0, 15);
    }
    
    // Crear nuevo gráfico horizontal bar
    window.chartDespachos = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: datosLimitados.map(d => d.despacho),
            datasets: [{
                label: 'Registros',
                data: datosLimitados.map(d => d.cantidad),
                backgroundColor: generarColores(datosLimitados.length),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Carga registros de una seccional paginados
 * @param {string} seccional - Seccional seleccionada
 * @param {number} pagina - Número de página
 */
function cargarRegistrosSeccional(seccional, pagina) {
    const tbody = document.getElementById('tablaRegistrosSeccional').querySelector('tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div> Cargando...</td></tr>';
    
    // En un caso real, harías una petición AJAX:
    fetch(`/dashboard/api/registros-por-seccional/?seccional=${encodeURIComponent(seccional)}&pagina=${pagina}`)
        .then(response => response.json())
        .then(data => {
            // Llenar la tabla con los datos
            tbody.innerHTML = '';
            
            if (data.registros.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No hay registros disponibles</td></tr>';
                return;
            }
            
            data.registros.forEach(registro => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${registro.nunc}</td>
                    <td>${registro.unidad || '-'}</td>
                    <td>${registro.despacho || '-'}</td>
                    <td>${registro.delito || '-'}</td>
                    <td>${registro.fecha_hechos || '-'}</td>
                `;
                tr.style.cursor = 'pointer';
                tr.onclick = function() {
                    mostrarDetallesRegistro(registro.nunc);
                };
                tbody.appendChild(tr);
            });
            
            // Actualizar paginación
            actualizarPaginacion('paginacionSeccional', data.total_paginas, pagina, function(p) {
                cargarRegistrosSeccional(seccional, p);
            });
        })
        .catch(error => {
            console.error('Error cargando registros:', error);
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error al cargar datos</td></tr>';
        });
}