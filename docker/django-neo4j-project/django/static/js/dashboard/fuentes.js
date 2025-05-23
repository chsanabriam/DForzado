/**
 * Gráficos y funcionalidad para la sección de Distribución por Fuente
 */

let chartFuenteDonut; // Variable global para el gráfico

/**
 * Inicializa la visualización de distribución por fuente
 */
function inicializarGraficoFuentes() {
    const fuentesLabels = dashboardData.fuentesLabels;
    const fuentesData = dashboardData.fuentesData;
    const coloresFuentes = generarColores(fuentesLabels.length);
    
    // Gráfico de distribución por fuente (Donut)
    const ctxFuenteDonut = document.getElementById('graficaFuenteDonut').getContext('2d');
    chartFuenteDonut = new Chart(ctxFuenteDonut, {
        type: 'doughnut',
        data: {
            labels: fuentesLabels,
            datasets: [{
                data: fuentesData,
                backgroundColor: coloresFuentes,
                borderWidth: 1,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${formatNumber(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    // Evento click en gráfico de fuentes
    ctxFuenteDonut.canvas.addEventListener('click', function(event) {
        const activePoints = chartFuenteDonut.getElementsAtEventForMode(
            event, 'nearest', { intersect: true }, true
        );
        
        if (activePoints.length > 0) {
            const clickedIndex = activePoints[0].index;
            const fuenteSeleccionada = fuentesLabels[clickedIndex];
            
            // Actualizar UI para mostrar fuente seleccionada
            document.getElementById('fuenteSeleccionada').textContent = fuenteSeleccionada;
            document.getElementById('mensajeFuente').style.display = 'none';
            document.getElementById('tablaFuente').style.display = 'block';
            
            // Cargar datos de la fuente seleccionada
            cargarDatosFuente(fuenteSeleccionada, 1);
        }
    });
}

/**
 * Carga datos filtrados por fuente
 * @param {string} fuente - Fuente seleccionada
 * @param {number} pagina - Número de página
 */
function cargarDatosFuente(fuente, pagina) {
    // Simulación de carga (en producción esto sería un AJAX call)
    const tbody = document.getElementById('tablaRegistrosFuente').querySelector('tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div> Cargando...</td></tr>';
    
    // En un caso real, harías una petición AJAX:
    fetch(`/dashboard/api/registros-por-fuente/?fuente=${encodeURIComponent(fuente)}&pagina=${pagina}`)
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
                    <td>${registro.fecha_hechos || '-'}</td>
                    <td>${registro.nombre_completo || '-'}</td>
                    <td>${registro.delito || '-'}</td>
                    <td>${registro.unidad || '-'}</td>
                `;
                tr.style.cursor = 'pointer';
                tr.onclick = function() {
                    mostrarDetallesRegistro(registro.nunc);
                };
                tbody.appendChild(tr);
            });
            
            // Actualizar paginación
            actualizarPaginacion('paginacionFuente', data.total_paginas, pagina, function(p) {
                cargarDatosFuente(fuente, p);
            });
        })
        .catch(error => {
            console.error('Error cargando datos:', error);
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error al cargar datos</td></tr>';
        });
}