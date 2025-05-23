/**
 * Script principal para el dashboard
 * Inicializa todos los componentes y gráficos
 */

// Ejecutar cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar gráficos
    inicializarGraficoFuentes();
    inicializarGraficoSeccionales();
    inicializarGraficoNecropsias();
    inicializarGraficoDelitos();
    
    // Configurar botón de exportación
    configurarBotonesExportacion();
    
    // Evitar envío de formularios al presionar Enter
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            return false;
        });
    });
    
    console.log('Dashboard inicializado correctamente');
});

/**
 * Configura los botones de exportación en el dashboard
 */
function configurarBotonesExportacion() {
    // Botón principal de exportación del dashboard
    const btnExportarDashboard = document.getElementById('btnExportarDashboard');
    if (btnExportarDashboard) {
        btnExportarDashboard.addEventListener('click', function() {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            
            // Crear un objeto Blob con los datos
            const datos = {
                total_spoa: dashboardData.totalSpoa,
                total_personas: dashboardData.totalPersonas,
                distribucion_fuentes: dashboardData.fuentesLabels.map((label, index) => ({
                    fuente: label,
                    cantidad: dashboardData.fuentesData[index]
                })),
                distribucion_seccionales: dashboardData.seccionalesData,
                total_delitos: {
                    desaparicion_forzada: dashboardData.totalDesaparicion,
                    homicidio: dashboardData.totalHomicidio,
                    secuestro: dashboardData.totalSecuestro,
                    reclutamiento: dashboardData.totalReclutamiento,
                    rud: dashboardData.totalRUD
                }
            };
            
            const blob = new Blob([JSON.stringify(datos, null, 2)], { type: 'application/json' });
            
            // Crear un enlace de descarga
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `dashboard-data-${timestamp}.json`;
            
            // Agregar al documento, hacer clic y eliminar
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        });
    }

    // Configuración del evento para exportar tabla de fuentes
    document.addEventListener('click', function(e) {
        if (e.target && e.target.id === 'btnExportarFuente') {
            const fuente = document.getElementById('fuenteSeleccionada').textContent;
            exportTableToCSV('tablaRegistrosFuente', `registros_${fuente.replace(/\s+/g, '_').toLowerCase()}_${new Date().toISOString().slice(0,10)}.csv`);
        }
        
        if (e.target && e.target.id === 'btnExportarSeccional') {
            const seccional = document.getElementById('seccionalSeleccionada').textContent;
            exportTableToCSV('tablaRegistrosSeccional', `registros_${seccional.replace(/\s+/g, '_').toLowerCase()}_${new Date().toISOString().slice(0,10)}.csv`);
        }
        
        if (e.target && e.target.id === 'btnExportarNecropsia') {
            const necropsia = document.getElementById('necropsiaSeleccionada').textContent;
            exportTableToCSV('tablaRegistrosNecropsia', `registros_${necropsia.replace(/\s+/g, '_').toLowerCase()}_${new Date().toISOString().slice(0,10)}.csv`);
        }
    });
}

/**
 * Gestiona la actualización de los datos en tiempo real (simulado)
 * En una aplicación real, esto se conectaría a un WebSocket o haría polling al servidor
 */
function configurarActualizacionDatos() {
    // Configurar intervalo para actualizar datos cada cierto tiempo (ej: cada 5 minutos)
    // Esta función simularía una actualización en tiempo real de los datos
    setInterval(function() {
        // Verificar si hay actualizaciones disponibles
        fetch('/dashboard/api/check-updates/')
            .then(response => response.json())
            .then(data => {
                if (data.hasUpdates) {
                    console.log('Hay actualizaciones disponibles');
                    // Aquí se actualizarían los datos
                    actualizarDatosDashboard();
                }
            })
            .catch(error => {
                console.error('Error verificando actualizaciones:', error);
            });
    }, 300000); // 5 minutos
}

/**
 * Actualiza los datos del dashboard (simulación)
 */
function actualizarDatosDashboard() {
    // En una aplicación real, esta función obtendría los datos actualizados
    // y refrescaría los gráficos y tablas
    
    fetch('/dashboard/api/dashboard-data/')
        .then(response => response.json())
        .then(data => {
            // Actualizar datos globales
            dashboardData = data;
            
            // Actualizar gráficos
            actualizarGraficoFuentes();
            actualizarGraficoSeccionales();
            actualizarGraficoNecropsias();
            actualizarGraficoDelitos();
            
            // Mostrar notificación de actualización
            mostrarNotificacion('Dashboard actualizado correctamente', 'success');
        })
        .catch(error => {
            console.error('Error actualizando datos:', error);
            mostrarNotificacion('Error al actualizar los datos', 'error');
        });
}

/**
 * Muestra una notificación temporal
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo de notificación (success, error, warning, info)
 */
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear elemento de notificación
    const notificacion = document.createElement('div');
    notificacion.className = `alert alert-${tipo} alert-dismissible fade show notification-toast`;
    notificacion.role = 'alert';
    notificacion.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
    `;
    
    // Agregar al cuerpo del documento
    document.body.appendChild(notificacion);
    
    // Posicionar en la esquina superior derecha
    notificacion.style.position = 'fixed';
    notificacion.style.top = '20px';
    notificacion.style.right = '20px';
    notificacion.style.zIndex = '9999';
    notificacion.style.minWidth = '300px';
    
    // Eliminar después de 5 segundos
    setTimeout(() => {
        notificacion.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notificacion);
        }, 150);
    }, 5000);
}