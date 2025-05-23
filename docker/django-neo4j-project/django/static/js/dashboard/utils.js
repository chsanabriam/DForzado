/**
 * Funciones de utilidad para el dashboard
 */

// Configuración global para Chart.js
Chart.defaults.font.family = 'system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif';
Chart.defaults.font.size = 12;
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 4;

/**
 * Genera un array de colores aleatorios
 * @param {number} cantidad - Cantidad de colores a generar
 * @returns {Array} - Array de colores en formato HSL
 */
function generarColores(cantidad) {
    const colores = [];
    for (let i = 0; i < cantidad; i++) {
        colores.push(`hsl(${Math.floor(Math.random() * 360)}, 70%, 50%)`);
    }
    return colores;
}

/**
 * Formatea un número con separador de miles
 * @param {number} num - Número a formatear
 * @returns {string} - Número formateado
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

/**
 * Actualiza los elementos de paginación
 * @param {string} elementId - ID del elemento de paginación
 * @param {number} totalPaginas - Total de páginas
 * @param {number} paginaActual - Página actual
 * @param {Function} callback - Función a ejecutar al cambiar de página
 */
function actualizarPaginacion(elementId, totalPaginas, paginaActual, callback) {
    const paginacion = document.getElementById(elementId);
    paginacion.innerHTML = '';
    
    // Calcular rango de páginas a mostrar
    let inicio = Math.max(1, paginaActual - 2);
    let fin = Math.min(totalPaginas, inicio + 4);
    
    if (fin - inicio < 4 && totalPaginas > 4) {
        inicio = Math.max(1, fin - 4);
    }
    
    // Botón Anterior
    const liAnterior = document.createElement('li');
    liAnterior.className = `page-item ${paginaActual === 1 ? 'disabled' : ''}`;
    const aAnterior = document.createElement('a');
    aAnterior.className = 'page-link';
    aAnterior.href = '#';
    aAnterior.textContent = 'Anterior';
    if (paginaActual > 1) {
        aAnterior.onclick = (e) => {
            e.preventDefault();
            callback(paginaActual - 1);
        };
    }
    liAnterior.appendChild(aAnterior);
    paginacion.appendChild(liAnterior);
    
    // Primera página si estamos lejos
    if (inicio > 1) {
        const li = document.createElement('li');
        li.className = 'page-item';
        const a = document.createElement('a');
        a.className = 'page-link';
        a.href = '#';
        a.textContent = '1';
        a.onclick = (e) => {
            e.preventDefault();
            callback(1);
        };
        li.appendChild(a);
        paginacion.appendChild(li);
        
        if (inicio > 2) {
            const liElipsis = document.createElement('li');
            liElipsis.className = 'page-item disabled';
            const aElipsis = document.createElement('a');
            aElipsis.className = 'page-link';
            aElipsis.href = '#';
            aElipsis.textContent = '...';
            liElipsis.appendChild(aElipsis);
            paginacion.appendChild(liElipsis);
        }
    }
    
    // Páginas
    for (let i = inicio; i <= fin; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === paginaActual ? 'active' : ''}`;
        const a = document.createElement('a');
        a.className = 'page-link';
        a.href = '#';
        a.textContent = i;
        if (i !== paginaActual) {
            a.onclick = (e) => {
                e.preventDefault();
                callback(i);
            };
        }
        li.appendChild(a);
        paginacion.appendChild(li);
    }
    
    // Última página si estamos lejos
    if (fin < totalPaginas) {
        if (fin < totalPaginas - 1) {
            const liElipsis = document.createElement('li');
            liElipsis.className = 'page-item disabled';
            const aElipsis = document.createElement('a');
            aElipsis.className = 'page-link';
            aElipsis.href = '#';
            aElipsis.textContent = '...';
            liElipsis.appendChild(aElipsis);
            paginacion.appendChild(liElipsis);
        }
        
        const li = document.createElement('li');
        li.className = 'page-item';
        const a = document.createElement('a');
        a.className = 'page-link';
        a.href = '#';
        a.textContent = totalPaginas;
        a.onclick = (e) => {
            e.preventDefault();
            callback(totalPaginas);
        };
        li.appendChild(a);
        paginacion.appendChild(li);
    }
    
    // Botón Siguiente
    const liSiguiente = document.createElement('li');
    liSiguiente.className = `page-item ${paginaActual === totalPaginas ? 'disabled' : ''}`;
    const aSiguiente = document.createElement('a');
    aSiguiente.className = 'page-link';
    aSiguiente.href = '#';
    aSiguiente.textContent = 'Siguiente';
    if (paginaActual < totalPaginas) {
        aSiguiente.onclick = (e) => {
            e.preventDefault();
            callback(paginaActual + 1);
        };
    }
    liSiguiente.appendChild(aSiguiente);
    paginacion.appendChild(liSiguiente);
}

/**
 * Muestra los detalles de un registro específico en un modal
 * @param {string} nunc - Identificador NUNC del registro
 */
function mostrarDetallesRegistro(nunc) {
    const modalContenido = document.getElementById('modalDetallesContenido');
    modalContenido.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p>Cargando detalles...</p></div>';
    
    // Mostrar el modal
    const modal = new bootstrap.Modal(document.getElementById('modalDetalles'));
    modal.show();
    
    // En un caso real, harías una petición AJAX para obtener los detalles del registro
    fetch(`/dashboard/api/detalle-registro/?nunc=${encodeURIComponent(nunc)}`)
        .then(response => response.json())
        .then(data => {
            // Crear el contenido del modal con los detalles del registro
            let contenido = '<div class="container-fluid">';
            contenido += '<div class="row">';
            
            // Columna izquierda
            contenido += '<div class="col-md-6">';
            contenido += `<h5>Información General</h5>`;
            contenido += `<p><strong>NUNC:</strong> ${data.nunc}</p>`;
            contenido += `<p><strong>Fecha Hechos:</strong> ${data.fecha_hechos || 'No especificada'}</p>`;
            contenido += `<p><strong>Fecha Denuncia:</strong> ${data.fecha_denuncia || 'No especificada'}</p>`;
            contenido += `<p><strong>Seccional:</strong> ${data.seccional || 'No especificada'}</p>`;
            contenido += `<p><strong>Unidad:</strong> ${data.unidad || 'No especificada'}</p>`;
            contenido += `<p><strong>Despacho:</strong> ${data.despacho || 'No especificado'}</p>`;
            contenido += '</div>';
            
            // Columna derecha
            contenido += '<div class="col-md-6">';
            contenido += `<h5>Detalles</h5>`;
            contenido += `<p><strong>Nombre:</strong> ${data.nombre_completo || 'No especificado'}</p>`;
            contenido += `<p><strong>Documento:</strong> ${data.numero_documento || 'No especificado'}</p>`;
            contenido += `<p><strong>Delito:</strong> ${data.delito || 'No especificado'}</p>`;
            contenido += `<p><strong>Grupo Delito:</strong> ${data.grupo_delito || 'No especificado'}</p>`;
            contenido += `<p><strong>Necropsia:</strong> ${data.necropsia || 'No especificada'}</p>`;
            contenido += `<p><strong>Fuente:</strong> ${data.fuente || 'No especificada'}</p>`;
            contenido += '</div>';
            
            contenido += '</div>';
            
            // Relato
            if (data.relato) {
                contenido += '<div class="row mt-3">';
                contenido += '<div class="col-12">';
                contenido += '<h5>Relato</h5>';
                contenido += `<div class="p-3 bg-light rounded">${data.relato}</div>`;
                contenido += '</div>';
                contenido += '</div>';
            }
            
            contenido += '</div>';
            modalContenido.innerHTML = contenido;
        })
        .catch(error => {
            console.error('Error obteniendo detalles:', error);
            modalContenido.innerHTML = '<div class="alert alert-danger">Error al cargar los detalles del registro</div>';
        });
}

/**
 * Exporta los datos de una tabla a CSV
 * @param {string} tableId - ID de la tabla
 * @param {string} filename - Nombre del archivo
 */
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    let csv = [];
    
    for (let i = 0; i < rows.length; i++) {
        const row = [], cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
            // Escapar comillas y comas
            let data = cols[j].innerText;
            data = data.replace(/"/g, '""');
            row.push('"' + data + '"');
        }
        
        csv.push(row.join(','));
    }
    
    // Descargar CSV
    const csvString = csv.join('\n');
    const link = document.createElement('a');
    link.style.display = 'none';
    link.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvString));
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}