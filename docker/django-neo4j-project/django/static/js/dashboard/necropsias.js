/**
 * Gráficos y funcionalidad para la sección de Distribución por Necropsia
 */

let chartNecropsia; // Variable global para el gráfico

/**
 * Inicializa la visualización de distribución por necropsia
 */
function inicializarGraficoNecropsias() {
    const necropsiasLabels = dashboardData.necropsiasLabels;
    const necropsiasData = dashboardData.necropsiasData;
    const coloresNecropsias = generarColores(necropsiasLabels.length);
    
    // Gráfico de distribución por necropsia (Donut)
    const ctxNecropsia = document.getElementById('graficaNecropsia').getContext('2d');
    chartNecropsia = new Chart(ctxNecropsia, {
        type: 'doughnut',
        data: {
            labels: necropsiasLabels,
            datasets: [{
                data: necropsiasData,
                backgroundColor: coloresNecropsias,
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
    
    // Evento click en gráfico de necropsias
    ctxNecropsia.canvas.addEventListener('click', function(event) {
        const activePoints = chartNecropsia.getElementsAtEventForMode(
            event, 'nearest', { intersect: true }, true
        );
        
        if (activePoints.length > 0) {
            const clickedIndex = activePoints[0].index;
            const necropsiaSeleccionada = necropsiasLabels[clickedIndex];
            
            // Actualizar UI para mostrar necropsia seleccionada
            document.getElementById('necropsiaSeleccionada').textContent = necropsiaSeleccionada;
            document.getElementById('mensajeNecropsia').style.display = 'none';
            document.getElementById('tablaNecropsia').style.display = 'block';
            
            // Cargar datos de la necropsia seleccionada
            cargarDatosNecropsia(necropsiaSeleccionada, 1);
        }
    });
}

/**
 * Carga datos filtrados por necropsia
 * @param {string} necropsia - Necropsia seleccionada
 * @param {number} pagina - Número de página
 */
function cargarDatosNecropsia(necropsia, pagina) {
    // Simulación de carga (en producción esto sería un AJAX call)
    const tbody = document.getElementById('tablaRegistrosNecropsia').querySelector('tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div> Cargando...</td></tr>';
    
    // En un caso real, harías una petición AJAX:
    fetch(`/dashboard/api/registros-por-necropsia/?necropsia=${encodeURIComponent(necropsia)}&pagina=${pagina}`)
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
                    <td>${registro.fuente || '-'}</td>
                `;
                tr.style.cursor = 'pointer';
                tr.onclick = function() {
                    mostrarDetallesRegistro(registro.nunc);
                };
                tbody.appendChild(tr);
            });
            
            // Actualizar paginación
            actualizarPaginacion('paginacionNecropsia', data.total_paginas, pagina, function(p) {
                cargarDatosNecropsia(necropsia, p);
            });
        })
        .catch(error => {
            console.error('Error cargando datos:', error);
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error al cargar datos</td></tr>';
        });
}