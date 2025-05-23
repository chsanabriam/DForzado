// // Variables globales
// let paginaActual = 1;
// let registrosPorPagina = 10;
// let totalPaginas = 0;
// let modoBusqueda = 'texto'; // 'texto' o 'delitos'

let paginacionState = {
    paginaActual: 1,
    registrosPorPagina: 10,
    totalPaginas: 0,
    modoBusqueda: 'texto'
};

// Al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Inicialmente mostrar mensaje de instrucción
    if (typeof mostrarEstadoBusqueda === 'function') {
        mostrarEstadoBusqueda('info', 'Ingrese un nombre o documento para buscar personas específicas, o use la pestaña "Búsqueda por Delitos" para encontrar personas por tipos de delito.');
    }
    
    // Evento para buscar por texto
    const btnBuscarTexto = document.getElementById('btnBuscarTexto');
    if (btnBuscarTexto) {
        btnBuscarTexto.addEventListener('click', function() {
            paginacionState.paginaActual = 1;
            paginacionState.modoBusqueda = 'texto';
            buscarPersonas();
        });
    } else {
        console.error("Elemento 'btnBuscarTexto' no encontrado en el DOM");
    }
    
    // Evento para buscar por delitos
    const btnBuscarDelitos = document.getElementById('btnBuscarDelitos');
    if (btnBuscarDelitos) {
        btnBuscarDelitos.addEventListener('click', function() {
            paginacionState.paginaActual = 1;
            paginacionState.modoBusqueda = 'delitos';
            buscarPersonas();
        });
    } else {
        console.error("Elemento 'btnBuscarDelitos' no encontrado en el DOM");
    }
    
    // Tecla Enter en campo de búsqueda
    const inputBusqueda = document.getElementById('inputBusqueda');
    if (inputBusqueda) {
        inputBusqueda.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                paginacionState.paginaActual = 1;
                paginacionState.modoBusqueda = 'texto';
                buscarPersonas();
            }
        });
    } else {
        console.error("Elemento 'inputBusqueda' no encontrado en el DOM");
    }
    
    // Eventos para limpiar búsquedas
    const btnLimpiarBusquedaTexto = document.getElementById('btnLimpiarBusquedaTexto');
    if (btnLimpiarBusquedaTexto) {
        btnLimpiarBusquedaTexto.addEventListener('click', function() {
            if (inputBusqueda) {
                inputBusqueda.value = '';
            }
            if (typeof mostrarEstadoBusqueda === 'function') {
                mostrarEstadoBusqueda('info', 'Ingrese un nombre o documento para buscar personas específicas.');
            }
            const tablaPersonas = document.getElementById('tablaPersonas');
            if (tablaPersonas) {
                tablaPersonas.innerHTML = '';
            }
            const paginacion = document.getElementById('paginacion');
            if (paginacion) {
                paginacion.innerHTML = '';
            }
        });
    } else {
        console.error("Elemento 'btnLimpiarBusquedaTexto' no encontrado en el DOM");
    }
    
    const btnLimpiarBusquedaDelitos = document.getElementById('btnLimpiarBusquedaDelitos');
    if (btnLimpiarBusquedaDelitos) {
        btnLimpiarBusquedaDelitos.addEventListener('click', function() {
            limpiarFiltrosDelitos();
            if (typeof mostrarEstadoBusqueda === 'function') {
                mostrarEstadoBusqueda('info', 'Seleccione al menos un filtro de delito y haga clic en "Buscar por Delitos".');
            }
            const tablaPersonas = document.getElementById('tablaPersonas');
            if (tablaPersonas) {
                tablaPersonas.innerHTML = '';
            }
            const paginacion = document.getElementById('paginacion');
            if (paginacion) {
                paginacion.innerHTML = '';
            }
        });
    } else {
        console.error("Elemento 'btnLimpiarBusquedaDelitos' no encontrado en el DOM");
    }
    
    // Eventos de cambio de tab para actualizar instrucciones
    const busquedaNombreTab = document.getElementById('busqueda-nombre-tab');
    if (busquedaNombreTab) {
        busquedaNombreTab.addEventListener('click', function() {
            if (typeof mostrarEstadoBusqueda === 'function') {
                mostrarEstadoBusqueda('info', 'Ingrese un nombre o documento para buscar personas específicas.');
            }
        });
    } else {
        console.error("Elemento 'busqueda-nombre-tab' no encontrado en el DOM");
    }
    
    const busquedaDelitosTab = document.getElementById('busqueda-delitos-tab');
    if (busquedaDelitosTab) {
        busquedaDelitosTab.addEventListener('click', function() {
            if (typeof mostrarEstadoBusqueda === 'function') {
                mostrarEstadoBusqueda('info', 'Seleccione al menos un filtro de delito y haga clic en "Buscar por Delitos".');
            }
        });
    } else {
        console.error("Elemento 'busqueda-delitos-tab' no encontrado en el DOM");
    }
    
    // Cambio de registros por página
    const registrosPorPaginaElements = document.querySelectorAll('.registros-por-pagina');
    if (registrosPorPaginaElements.length > 0) {
        registrosPorPaginaElements.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                paginacionState.registrosPorPagina = parseInt(this.getAttribute('data-valor'));
                const dropdownResultados = document.getElementById('dropdownResultados');
                if (dropdownResultados) {
                    dropdownResultados.textContent = this.textContent;
                }
                paginacionState.paginaActual = 1;
                if (hayFiltrosActivos()) {
                    buscarPersonas();
                }
            });
        });
    } else {
        console.error("No se encontraron elementos con clase 'registros-por-pagina'");
    }
    
    // Exportar a CSV
    const btnExportarCSV = document.getElementById('btnExportarCSV');
    if (btnExportarCSV) {
        btnExportarCSV.addEventListener('click', exportarCSV);
    } else {
        console.error("Elemento 'btnExportarCSV' no encontrado en el DOM");
    }
    
    // Exportar a PDF
    const btnExportarPDF = document.getElementById('btnExportarPDF');
    if (btnExportarPDF) {
        btnExportarPDF.addEventListener('click', function() {
            alert('Funcionalidad de exportación a PDF en desarrollo');
        });
    } else {
        console.error("Elemento 'btnExportarPDF' no encontrado en el DOM");
    }
});

// Función para mostrar estado de búsqueda
function mostrarEstadoBusqueda(tipo, mensaje) {
    const estadoBusqueda = document.getElementById('estadoBusqueda');
    if (!estadoBusqueda) {
        console.error("Elemento 'estadoBusqueda' no encontrado en el DOM");
        return;
    }
    
    estadoBusqueda.className = `alert alert-${tipo} mb-3`;
    estadoBusqueda.textContent = mensaje;
    estadoBusqueda.classList.remove('d-none');
}

// Función para verificar si hay filtros activos
function hayFiltrosActivos() {
    if (paginacionState.modoBusqueda === 'texto') {
        const inputBusqueda = document.getElementById('inputBusqueda');
        return inputBusqueda && inputBusqueda.value.trim() !== '';
    } else {
        // Verificar si hay algún filtro de delito seleccionado
        const selectDesaparicion = document.getElementById('selectDesaparicion');
        const selectHomicidio = document.getElementById('selectHomicidio');
        const selectSecuestro = document.getElementById('selectSecuestro');
        const selectReclutamiento = document.getElementById('selectReclutamiento');
        const selectRUD = document.getElementById('selectRUD');
        const selectFuncionario = document.getElementById('selectFuncionario');
        
        if (!selectDesaparicion || !selectHomicidio || !selectSecuestro || 
            !selectReclutamiento || !selectRUD || !selectFuncionario) {
            console.error("Uno o más selectores de filtro no encontrados en el DOM");
            return false;
        }
        
        return selectDesaparicion.value !== 'cualquiera' || 
               selectHomicidio.value !== 'cualquiera' || 
               selectSecuestro.value !== 'cualquiera' || 
               selectReclutamiento.value !== 'cualquiera' || 
               selectRUD.value !== 'cualquiera' ||
               selectFuncionario.value !== 'cualquiera';
    }
}

// Función para limpiar filtros de delitos
function limpiarFiltrosDelitos() {
    const selectores = [
        'selectDesaparicion', 
        'selectHomicidio', 
        'selectSecuestro', 
        'selectReclutamiento', 
        'selectRUD',
        'selectFuncionario'
    ];
    
    selectores.forEach(id => {
        const selector = document.getElementById(id);
        if (selector) {
            selector.value = 'cualquiera';
        } else {
            console.error(`Elemento '${id}' no encontrado en el DOM`);
        }
    });
}

// Función principal para buscar personas
function buscarPersonas() {
    if (paginacionState.modoBusqueda === 'texto') {
        const inputBusqueda = document.getElementById('inputBusqueda');
        if (!inputBusqueda) {
            console.error("Elemento 'inputBusqueda' no encontrado en el DOM");
            return;
        }
        
        if (inputBusqueda.value.trim() === '') {
            mostrarEstadoBusqueda('warning', 'Debe ingresar un texto para buscar.');
            return;
        }
    }
    
    if (paginacionState.modoBusqueda === 'delitos' && !hayFiltrosActivos()) {
        mostrarEstadoBusqueda('warning', 'Debe seleccionar al menos un filtro de delito.');
        return;
    }
    
    // Antes de construir la URL, verifica el valor actual
    console.log("Valor de paginacionState.paginaActual al construir URL:", paginacionState.paginaActual);

    // Construir URL base
    let url = `/dashboard/api/personas/?pagina=${paginacionState.paginaActual}&por_pagina=${paginacionState.registrosPorPagina}`;
    console.log("URL base: " + url);
    
    // Agregar parámetros según el modo de búsqueda
    if (paginacionState.modoBusqueda === 'texto') {
        const inputBusqueda = document.getElementById('inputBusqueda');
        if (!inputBusqueda) {
            console.error("Elemento 'inputBusqueda' no encontrado en el DOM");
            return;
        }
        
        const busqueda = inputBusqueda.value.trim();
        url += `&busqueda=${encodeURIComponent(busqueda)}&modo=texto`;
        mostrarEstadoBusqueda('primary', `Buscando: "${busqueda}"`);
    } else {
        // Obtener valores de los selectores de delitos
        const selectores = {
            'desaparicion': document.getElementById('selectDesaparicion'),
            'homicidio': document.getElementById('selectHomicidio'),
            'secuestro': document.getElementById('selectSecuestro'),
            'reclutamiento': document.getElementById('selectReclutamiento'),
            'rud_estado': document.getElementById('selectRUD'),  // Cambiado a rud_estado
            'funcionario': document.getElementById('selectFuncionario')
        };
        
        // Verificar que todos los selectores existan
        for (const [nombre, selector] of Object.entries(selectores)) {
            if (!selector) {
                console.error(`Elemento 'select${nombre.charAt(0).toUpperCase() + nombre.slice(1)}' no encontrado en el DOM`);
                return;
            }
        }
        
        url += '&modo=delitos';
        
        // Construir mensaje de búsqueda
        let mensajeFiltros = [];
        
        // Agregar parámetros para cada filtro de delito
        for (const [param, selector] of Object.entries(selectores)) {
            if (selector.value !== 'cualquiera') {
                // Manejo especial para el selector de RUD
                if (param === 'rud_estado') {
                    url += `&${param}=${selector.value}`;
                    
                    // Obtener el texto visible para mostrar en el mensaje
                    const optionSelected = selector.options[selector.selectedIndex];
                    mensajeFiltros.push(`Estado RUD: ${optionSelected.text}`);
                } else {
                    url += `&${param}=${selector.value === 'si' ? 'true' : 'false'}`;
                    
                    const nombreVisible = param.charAt(0).toUpperCase() + param.slice(1);
                    mensajeFiltros.push(`${nombreVisible}: ${selector.value === 'si' ? 'Sí' : 'No'}`);
                }
            }
        }
        
        mostrarEstadoBusqueda('primary', `Buscando por delitos: ${mensajeFiltros.join(', ')}`);
    }
    
    // Realizar petición
    fetch(url)
        .then(response => response.json())
        .then(data => {
            renderizarTablaPersonas(data.personas);
            renderizarPaginacion(data.pagina_actual, data.total_paginas, data.total_registros);
            paginacionState.totalPaginas = data.total_paginas;
            
            // Actualizar mensaje con resultados
            if (data.total_registros === 0) {
                mostrarEstadoBusqueda('warning', 'No se encontraron resultados para la búsqueda.');
            } else {
                const modo = paginacionState.modoBusqueda === 'texto' ? 'nombre/documento' : 'delitos';
                mostrarEstadoBusqueda('success', `Se encontraron ${data.total_registros} personas para la búsqueda por ${modo}.`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarEstadoBusqueda('danger', 'Error al realizar la búsqueda. Por favor intente nuevamente.');
        });
}

// Función para renderizar la tabla de personas
function renderizarTablaPersonas(personas) {
    const tabla = document.getElementById('tablaPersonas');
    if (!tabla) {
        console.error("Elemento 'tablaPersonas' no encontrado en el DOM");
        return;
    }
    
    tabla.innerHTML = '';
    
    if (personas.length === 0) {
        const fila = document.createElement('tr');
        fila.innerHTML = `<td colspan="8" class="text-center">No se encontraron registros</td>`;
        tabla.appendChild(fila);
        return;
    }
    
    personas.forEach(persona => {
        const fila = document.createElement('tr');
        
        // Crear celdas de información básica
        fila.innerHTML = `
            <td>${persona.id}</td>
            <td>${persona.nombre}</td>
        `;
        
        // Celda para desaparición
        const celdaDesaparicion = document.createElement('td');
        if (persona.desaparicion) {
            celdaDesaparicion.innerHTML = `
                <button class="btn btn-sm btn-danger ver-noticia" data-documento="${persona.id}" data-delito="desaparicion">
                    Ver
                </button>
            `;
        } else {
            celdaDesaparicion.textContent = 'No';
        }
        fila.appendChild(celdaDesaparicion);
        
        // Celda para homicidio
        const celdaHomicidio = document.createElement('td');
        if (persona.homicidio) {
            celdaHomicidio.innerHTML = `
                <button class="btn btn-sm btn-danger ver-noticia" data-documento="${persona.id}" data-delito="homicidio">
                    Ver
                </button>
            `;
        } else {
            celdaHomicidio.textContent = 'No';
        }
        fila.appendChild(celdaHomicidio);
        
        // Celda para secuestro
        const celdaSecuestro = document.createElement('td');
        if (persona.secuestro) {
            celdaSecuestro.innerHTML = `
                <button class="btn btn-sm btn-danger ver-noticia" data-documento="${persona.id}" data-delito="secuestro">
                    Ver
                </button>
            `;
        } else {
            celdaSecuestro.textContent = 'No';
        }
        fila.appendChild(celdaSecuestro);
        
        // Celda para reclutamiento
        const celdaReclutamiento = document.createElement('td');
        if (persona.reclutamiento) {
            celdaReclutamiento.innerHTML = `
                <button class="btn btn-sm btn-danger ver-noticia" data-documento="${persona.id}" data-delito="reclutamiento">
                    Ver
                </button>
            `;
        } else {
            celdaReclutamiento.textContent = 'No';
        }
        fila.appendChild(celdaReclutamiento);
        
        // Celda para RUD
        const celdaRUD = document.createElement('td');
        if (persona.rud) {
            celdaRUD.innerHTML = `
                <button class="btn btn-sm btn-danger ver-noticia" data-documento="${persona.id}" data-delito="rud">
                    Ver
                </button>
            `;
        } else {
            celdaRUD.textContent = 'No';
        }
        fila.appendChild(celdaRUD);
        
        // Celda para Funcionario
        const celdaFuncionario = document.createElement('td');
        if (persona.funcionario) {
            celdaFuncionario.innerHTML = `
                <button class="btn btn-sm btn-danger ver-funcionario" data-documento="${persona.id}" data-delito="funcionario">
                    Ver
                </button>
            `;
        } else {
            celdaFuncionario.textContent = 'No';
        }
        fila.appendChild(celdaFuncionario);

        // Celda para línea de tiempo
        const celdaTimeline = document.createElement('td');
        celdaTimeline.innerHTML = `
            <button class="btn btn-sm btn-info ver-timeline" data-documento="${persona.id}">
                <i class="bi bi-clock-history"></i>
            </button>
        `;
        fila.appendChild(celdaTimeline);

        // Celda para perfil
        const celdaPerfil = document.createElement('td');
        celdaPerfil.innerHTML = `
            <button class="btn btn-sm btn-primary ver-perfil" data-documento="${persona.id}" data-nombre="${persona.nombre}">
                <i class="bi bi-person-badge"></i>
            </button>
        `;
        fila.appendChild(celdaPerfil);

        // Celda para subred
        const celdaSubred = document.createElement('td');
        celdaSubred.innerHTML = `
            <button class="btn btn-sm btn-info ver-red" data-documento="${persona.id}" data-nombre="${persona.nombre}">
                <i class="bi bi-diagram-3"></i>
            </button>
        `;
        fila.appendChild(celdaSubred);
        
        tabla.appendChild(fila);
    });
    
    // Agregar event listeners a los botones
    document.querySelectorAll('.ver-noticia').forEach(boton => {
        boton.addEventListener('click', function() {
            const documento = this.getAttribute('data-documento');
            const delito = this.getAttribute('data-delito');
            abrirModalNoticias(documento, delito);
        });
    });

    // Y luego añadir un event listener específico
    document.querySelectorAll('.ver-funcionario').forEach(boton => {
        boton.addEventListener('click', function() {
            const documento = this.getAttribute('data-documento');
            abrirModalFuncionario(documento);
        });
    });
    
    document.querySelectorAll('.ver-timeline').forEach(boton => {
        boton.addEventListener('click', function() {
            const documento = this.getAttribute('data-documento');
            abrirModalTimeline(documento);
        });
    });

    // event listener para los botones de perfil:
    document.querySelectorAll('.ver-perfil').forEach(boton => {
        boton.addEventListener('click', function() {
            const documento = this.getAttribute('data-documento');
            const nombre = this.getAttribute('data-nombre');
            console.log('Botón de perfil clickeado:', documento, nombre); // Añadir este log
            abrirModalPerfil(documento, nombre);
        });
    });

    // Agregar después de los otros event listeners en la función renderizarTablaPersonas
    document.querySelectorAll('.ver-red').forEach(boton => {
        boton.addEventListener('click', function() {
            const documento = this.getAttribute('data-documento');
            // Abrir en una nueva ventana la visualización de red
            window.open(`/networks/visualization/${documento}/`, '_blank');
        });
    });
}

// Función para renderizar la paginación
function renderizarPaginacion(paginaActual, totalPaginas, totalRegistros) {
    const paginacion = document.getElementById('paginacion');
    if (!paginacion) {
        console.error("Elemento 'paginacion' no encontrado en el DOM");
        return;
    }
    
    paginacion.innerHTML = '';
    
    if (totalPaginas === 0) {
        return;
    }
    
    // Eliminar contador anterior si existe
    const contadorAnterior = paginacion.parentNode.querySelector('.contador-registros');
    if (contadorAnterior) {
        contadorAnterior.remove();
    }
    
    // Contador de registros
    const contadorRegistros = document.createElement('div');
    contadorRegistros.className = 'text-center mb-2 contador-registros';
    contadorRegistros.textContent = `Mostrando ${Math.min(paginacionState.registrosPorPagina, totalRegistros)} de ${totalRegistros} registros`;
    paginacion.parentNode.insertBefore(contadorRegistros, paginacion);
    
    // Botón anterior
    const itemAnterior = document.createElement('li');
    itemAnterior.className = `page-item ${paginacionState.paginaActual === 1 ? 'disabled' : ''}`;
    itemAnterior.innerHTML = `<a class="page-link" href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a>`;
    itemAnterior.addEventListener('click', function(e) {
        e.preventDefault();
        if (paginacionState.paginaActual > 1) {
            console.log("Actual" + paginacionState.paginaActual);
            paginacionState.paginaActual--;
            console.log("Anterior" + paginacionState.paginaActual);
            buscarPersonas();
        }
    });
    paginacion.appendChild(itemAnterior);
    
    // Números de página
    const mostrarPaginas = 5;
    let inicio = Math.max(1, paginacionState.paginaActual - Math.floor(mostrarPaginas / 2));
    let fin = Math.min(paginacionState.totalPaginas, inicio + mostrarPaginas - 1);
    
    if (fin - inicio + 1 < mostrarPaginas) {
        inicio = Math.max(1, fin - mostrarPaginas + 1);
    }
    
    for (let i = inicio; i <= fin; i++) {
        const item = document.createElement('li');
        item.className = `page-item ${i === paginacionState.paginaActual ? 'active' : ''}`;
        item.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        item.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Actual" + paginacionState.paginaActual);
            paginacionState.paginaActual = i;
            console.log("Número de página" + paginacionState.paginaActual);
            buscarPersonas();
        });
        paginacion.appendChild(item);
    }
    
    // Botón siguiente
    const itemSiguiente = document.createElement('li');
    itemSiguiente.className = `page-item ${paginacionState.paginaActual === paginacionState.totalPaginas ? 'disabled' : ''}`;
    itemSiguiente.innerHTML = `<a class="page-link" href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a>`;
    itemSiguiente.addEventListener('click', function(e) {
        e.preventDefault();
        if (paginacionState.paginaActual < paginacionState.totalPaginas) {
            console.log("Actual" + paginacionState.paginaActual);
            paginacionState.paginaActual++;
            console.log("Siguiente" + paginacionState.paginaActual);
            buscarPersonas();
        }
    });
    paginacion.appendChild(itemSiguiente);
}

// Función para abrir modal de noticias criminales
function abrirModalNoticias(documento, delito) {
    // Actualizar título del modal
    const modalNoticiasLabel = document.getElementById('modalNoticiasLabel');
    if (!modalNoticiasLabel) {
        console.error("Elemento 'modalNoticiasLabel' no encontrado en el DOM");
        return;
    }
    
    console.log("Delito: " + delito);
    // Título personalizado para RUD
    if (delito === 'rud') {
        modalNoticiasLabel.textContent = 'Registro Único de Desaparecidos';
    } else {
        modalNoticiasLabel.textContent = `Noticias Criminales - ${delito.charAt(0).toUpperCase() + delito.slice(1)}`;
    }
    
    // Limpiar tabla
    const tablaNoticias = document.getElementById('tablaNoticias');
    const relatoNoticia = document.getElementById('relatoNoticia');
    
    if (!tablaNoticias || !relatoNoticia) {
        console.error("Elementos para noticias no encontrados en el DOM");
        return;
    }
    
    tablaNoticias.innerHTML = '';
    relatoNoticia.textContent = '';

    // Eliminar div de información de aparecidos vivos si existe
    const aparecidosVivosDiv = document.getElementById('infoAparecidosVivos');
    if (aparecidosVivosDiv) {
        aparecidosVivosDiv.remove();
    }
    
    // Mostrar modal
    const modalElement = document.getElementById('modalNoticias');
    if (!modalElement) {
        console.error("Elemento 'modalNoticias' no encontrado en el DOM");
        return;
    }
    
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Cargar datos
    fetch(`/dashboard/api/noticias/?documento=${documento}&delito=${delito}`)
        .then(response => response.json())
        .then(data => {
            console.log("Datos de noticias:", data);
            
            // Pasar los datos adicionales al renderizador
            const extraData = {
                en_aparecidos_vivos: data.en_aparecidos_vivos
            };
            
            renderizarTablaNoticias(data.noticias, extraData);
        })
        .catch(error => {
            console.error('Error:', error);
            if (tablaNoticias) {
                tablaNoticias.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Error al cargar noticias: ${error}</td></tr>`;
            }
        });
}

// Resto de funciones...
// Función para abrir modal de línea de tiempo (versión actualizada)
function abrirModalTimeline(documento) {
    // Actualizar título del modal
    const modalTimelineLabel = document.getElementById('modalTimelineLabel');
    if (!modalTimelineLabel) {
        console.error("Elemento 'modalTimelineLabel' no encontrado en el DOM");
        return;
    }
    
    modalTimelineLabel.textContent = `Línea de Tiempo - Documento: ${documento}`;
    
    // Limpiar contenedor
    const timelineContainer = document.getElementById('timelineContainer');
    if (!timelineContainer) {
        console.error("Elemento 'timelineContainer' no encontrado en el DOM");
        return;
    }
    
    timelineContainer.innerHTML = '<div class="d-flex justify-content-center my-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>';
    
    // Mostrar modal
    const modalElement = document.getElementById('modalTimeline');
    if (!modalElement) {
        console.error("Elemento 'modalTimeline' no encontrado en el DOM");
        return;
    }
    
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Cargar datos
    fetch(`/dashboard/api/timeline/?documento=${documento}`)
        .then(response => response.json())
        .then(data => {
            // Usar la nueva función de línea de tiempo horizontal
            renderizarTimelineHorizontal(data.timeline);
        })
        .catch(error => {
            console.error('Error:', error);
            if (timelineContainer) {
                timelineContainer.innerHTML = `<div class="alert alert-danger">Error al cargar línea de tiempo: ${error}</div>`;
            }
        });
}

// Función para abrir modal de perfil
function abrirModalPerfil(documento, nombre) {
    console.log('Iniciando abrirModalPerfil para:', documento, nombre);
    // Actualizar el modal con la información básica
    const perfilNombre = document.getElementById('perfilNombre');
    const perfilDocumento = document.getElementById('perfilDocumento');
    
    if (perfilNombre && perfilDocumento) {
        perfilNombre.textContent = nombre;
        perfilDocumento.textContent = `Documento: ${documento}`;
    } else {
        console.error('No se encontraron elementos perfilNombre o perfilDocumento');
    }
    
    // Limpiar contenido anterior y mostrar indicador de carga
    const perfilContenido = document.getElementById('perfilContenido');
    if (perfilContenido) {
        perfilContenido.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div><p class="mt-2">Cargando perfil...</p></div>';
    } else {
        console.error('No se encontró el elemento perfilContenido');
    }
    
    // Resetear el estado de los delitos
    resetearEstadoDelitos();
    
    // Mostrar modal
    const modalElement = document.getElementById('modalPerfil');
    if (!modalElement) {
        console.error("Elemento 'modalPerfil' no encontrado en el DOM");
        return;
    }
    
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Obtener datos del perfil desde la API
    fetch(`/dashboard/api/perfil/?documento=${documento}`)
        .then(response => {
            console.log("Respuesta de la API:", response);
            if (!response.ok) {
                throw new Error('Error al obtener el perfil');
            }
            return response.json();
        })
        .then(data => {
            // Actualizar información del perfil
            actualizarDatosPerfil(data);
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarErrorPerfil('No se pudo cargar el perfil. Por favor intente nuevamente.');
        });

    // Agregar esta línea en la función abrirModalPerfil o en el DOMContentLoaded
    document.getElementById('btnExportarPerfil').addEventListener('click', exportarPerfilPDF);
}

/**
 * Abre el modal con la información básica del funcionario
 * @param {string} documento - Documento de identidad del funcionario
 */
function abrirModalFuncionario(documento) {
    // Actualizar título del modal
    const modalFuncionariosLabel = document.getElementById('modalFuncionariosLabel');
    if (!modalFuncionariosLabel) {
        console.error("Elemento 'modalFuncionariosLabel' no encontrado en el DOM");
        return;
    }
    
    modalFuncionariosLabel.textContent = `Información de Funcionario - Documento: ${documento}`;
    
    // Limpiar información previa
    document.getElementById('funcionarioNombre').textContent = 'Cargando...';
    document.getElementById('funcionarioDocumento').textContent = documento;
    document.getElementById('funcionarioCargo').textContent = '-';
    document.getElementById('funcionarioSeccional').textContent = '-';
    document.getElementById('funcionarioDependencia').textContent = '-';
    document.getElementById('funcionarioEstado').textContent = '-';
    document.getElementById('funcionarioEstado').className = 'badge bg-secondary';
    document.getElementById('funcionarioFuente').textContent = '-';
    document.getElementById('funcionarioFechaRegistro').textContent = '-';
    
    // Ocultar mensajes de error
    document.getElementById('funcionarioErrorMsg').classList.add('d-none');
    
    // Mostrar modal
    const modalElement = document.getElementById('modalFuncionarios');
    if (!modalElement) {
        console.error("Elemento 'modalFuncionarios' no encontrado en el DOM");
        return;
    }
    
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Cargar datos del funcionario
    fetch(`/dashboard/api/funcionario/?documento=${documento}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al obtener información del funcionario');
            }
            return response.json();
        })
        .then(data => {
            // Actualizar información básica
            document.getElementById('funcionarioNombre').textContent = data.nombres_apellidos || 'No disponible';
            document.getElementById('funcionarioDocumento').textContent = `Documento: ${data.numero_documento}`;
            document.getElementById('funcionarioCargo').textContent = data.nom_cargo || 'No especificado';
            document.getElementById('funcionarioSeccional').textContent = data.seccional || 'No especificado';
            document.getElementById('funcionarioDependencia').textContent = data.nom_dependencia || 'No especificado';
            
            // Actualizar estado con color adecuado
            const estadoElement = document.getElementById('funcionarioEstado');
            estadoElement.textContent = data.estado || 'No especificado';
            
            // Asignar clase según el estado
            if (data.estado) {
                if (data.estado.toLowerCase() === 'activo') {
                    estadoElement.className = 'badge bg-success';
                } else if (data.estado.toLowerCase() === 'inactivo') {
                    estadoElement.className = 'badge bg-warning text-dark';
                } else if (data.estado.toLowerCase().includes('retir')) {
                    estadoElement.className = 'badge bg-secondary';
                } else {
                    estadoElement.className = 'badge bg-info';
                }
            }
            
            // Actualizar información adicional
            document.getElementById('funcionarioFuente').textContent = data.fuente || 'No especificado';
            
            // Formatear fecha de registro
            if (data.fecha_registro) {
                const fecha = new Date(data.fecha_registro);
                document.getElementById('funcionarioFechaRegistro').textContent = fecha.toLocaleString('es-CO');
            } else {
                document.getElementById('funcionarioFechaRegistro').textContent = 'No disponible';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('funcionarioErrorMsg').textContent = `Error: ${error.message}`;
            document.getElementById('funcionarioErrorMsg').classList.remove('d-none');
        });
}

// Función para actualizar datos del perfil en el modal
function actualizarDatosPerfil(data) {
    // Actualizar total de casos
    const perfilTotalCasos = document.getElementById('perfilTotalCasos');
    if (perfilTotalCasos) {
        perfilTotalCasos.textContent = data.total_casos || 0;
    }
    
    // Actualizar contenido del perfil
    const perfilContenido = document.getElementById('perfilContenido');
    if (perfilContenido) {
        if (data.encontrado_en_json) {
            // Si se encontró en el JSON, mostrar el perfil completo
            // Convertir Markdown a HTML simple
            const htmlPerfil = convertirMarkdownAHTML(data.perfil);
            perfilContenido.innerHTML = htmlPerfil;
        } else {
            // Si no se encontró en el JSON, mostrar mensaje predeterminado
            perfilContenido.innerHTML = '<p class="text-muted">Caracterización de la persona en construcción</p>';
        }
    }
    
    // Actualizar estados de delitos
    if (data.estados_delitos) {
        actualizarEstadoDelitos(data.estados_delitos);
    }
}

// Función para actualizar los badges de estado de delitos
function actualizarEstadoDelitos(estados) {
    // Actualizar cada badge según el estado del delito
    actualizarBadgeDelito('perfilEstadoDesaparicion', estados.desaparicion);
    actualizarBadgeDelito('perfilEstadoHomicidio', estados.homicidio);
    actualizarBadgeDelito('perfilEstadoSecuestro', estados.secuestro);
    actualizarBadgeDelito('perfilEstadoReclutamiento', estados.reclutamiento);
    actualizarBadgeDelito('perfilEstadoRUD', estados.rud);
    actualizarBadgeDelito('perfilEstadoFuncionario', estados.funcionario);
}

// Función para actualizar un badge de delito individual
function actualizarBadgeDelito(elementId, tieneDelito) {
    const badge = document.getElementById(elementId);
    if (!badge) return;
    
    if (tieneDelito) {
        badge.textContent = 'Sí';
        badge.className = 'badge bg-danger';
    } else {
        badge.textContent = 'No';
        badge.className = 'badge bg-secondary';
    }
}

// Función para resetear todos los badges de delitos
function resetearEstadoDelitos() {
    const delitos = [
        'perfilEstadoDesaparicion',
        'perfilEstadoHomicidio',
        'perfilEstadoSecuestro',
        'perfilEstadoReclutamiento',
        'perfilEstadoRUD',
        'perfilEstadoFuncionario'
    ];
    
    delitos.forEach(id => {
        const badge = document.getElementById(id);
        if (badge) {
            badge.textContent = 'No';
            badge.className = 'badge bg-secondary';
        }
    });
}

// Función para mostrar mensaje de error en el perfil
function mostrarErrorPerfil(mensaje) {
    const perfilContenido = document.getElementById('perfilContenido');
    if (perfilContenido) {
        perfilContenido.innerHTML = `<div class="alert alert-danger">${mensaje}</div>`;
    }
}

// Función básica para convertir Markdown a HTML
function convertirMarkdownAHTML(markdown) {
    if (!markdown) return '';
    
    // Convertir encabezados
    let html = markdown
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^#### (.+)$/gm, '<h4>$1</h4>');
    
    // Convertir negritas
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Convertir listas
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.+<\/li>\n)+/g, '<ul>$&</ul>');
    
    // Convertir párrafos
    html = html.replace(/\n\n/g, '<br><br>');
    
    return html;
}

// Función para exportar el perfil como PDF
function exportarPerfilPDF() {
    // Obtener documento actual
    const perfilDocumento = document.getElementById('perfilDocumento');
    const documento = perfilDocumento.textContent.replace('Documento: ', '').trim();
    
    if (!documento) {
        console.error('No se pudo determinar el documento para exportar');
        return;
    }
    
    // En una implementación real, esto redireccionaría a un endpoint para generar el PDF
    alert(`Exportando perfil a PDF para el documento: ${documento}`);
    window.open(`/dashboard/api/perfil/exportar-pdf/?documento=${documento}`, '_blank');
}

// Función para renderizar una línea de tiempo horizontal
function renderizarTimelineHorizontal(timeline) {
    const container = document.getElementById('timelineContainer');
    if (!container) {
        console.error("Elemento 'timelineContainer' no encontrado en el DOM");
        return;
    }
    
    if (!timeline || timeline.length === 0) {
        container.innerHTML = '<div class="timeline-no-events">No hay eventos disponibles para crear una línea de tiempo.</div>';
        return;
    }
    
    // Limpiar el contenedor
    container.innerHTML = '';
    
    // Crear leyenda de la línea de tiempo
    const leyenda = document.createElement('div');
    leyenda.className = 'timeline-legend';
    leyenda.innerHTML = `
        <div class="timeline-legend-item">
            <div class="timeline-legend-color timeline-legend-hechos"></div>
            <span>Fecha de hechos</span>
        </div>
        <div class="timeline-legend-item">
            <div class="timeline-legend-color timeline-legend-denuncia"></div>
            <span>Fecha de denuncia</span>
        </div>
    `;
    container.appendChild(leyenda);
    
    // Crear navegación de la línea de tiempo
    const navegacion = document.createElement('div');
    navegacion.className = 'timeline-navigation';
    navegacion.innerHTML = `
        <button id="btnScrollLeft" type="button">
            <i class="bi bi-arrow-left"></i> Anterior
        </button>
        <button id="btnScrollRight" type="button">
            Siguiente <i class="bi bi-arrow-right"></i>
        </button>
    `;
    container.appendChild(navegacion);
    
    // Crear contenedor de la línea de tiempo
    const timelineContainer = document.createElement('div');
    timelineContainer.className = 'timeline-horizontal-container';
    
    // Crear la línea de tiempo
    const timelineEl = document.createElement('div');
    timelineEl.className = 'timeline-horizontal';
    
    // Procesar eventos y ordenarlos por fecha
    timeline.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));
    
    // Crear eventos en la línea de tiempo
    timeline.forEach(evento => {
        const eventoEl = document.createElement('div');
        eventoEl.className = `timeline-event ${evento.tipo}`;
        
        // Formatear fecha para mostrar
        const fechaObj = new Date(evento.fecha + 'T12:00:00'); // Agregar mediodía para evitar problemas de zona horaria
        const fechaFormateada = fechaObj.toLocaleDateString('es-ES', { 
            year: 'numeric', month: 'long', day: 'numeric' 
        });
        
        // Definir el tipo de evento
        const tipoEvento = evento.tipo === 'hechos' ? 'Hechos' : 'Denuncia';
        
        // Contenido del evento
        eventoEl.innerHTML = `
            <div class="timeline-event-content">
                <div class="timeline-event-header">
                    <div class="timeline-date">${fechaFormateada}</div>
                    <div class="timeline-event-title">${tipoEvento}</div>
                </div>
                <div class="timeline-event-details">
                    <span class="timeline-event-tag tag-nunc">NUNC: ${evento.nunc}</span>
                    <span class="timeline-event-tag tag-delito">Delito: ${evento.delito}</span>
                </div>
            </div>
        `;
        
        timelineEl.appendChild(eventoEl);
    });
    
    // Agregar la línea de tiempo al contenedor
    timelineContainer.appendChild(timelineEl);
    container.appendChild(timelineContainer);
    
    // Implementar navegación con botones
    const btnScrollLeft = document.getElementById('btnScrollLeft');
    const btnScrollRight = document.getElementById('btnScrollRight');
    
    if (btnScrollLeft && btnScrollRight) {
        btnScrollLeft.addEventListener('click', () => {
            timelineContainer.scrollBy({ left: -300, behavior: 'smooth' });
        });
        
        btnScrollRight.addEventListener('click', () => {
            timelineContainer.scrollBy({ left: 300, behavior: 'smooth' });
        });
        
        // Actualizar estado de botones según la posición del scroll
        function actualizarEstadoBotones() {
            const scrollLeft = timelineContainer.scrollLeft;
            const maxScrollLeft = timelineContainer.scrollWidth - timelineContainer.clientWidth;
            
            btnScrollLeft.disabled = scrollLeft <= 0;
            btnScrollRight.disabled = scrollLeft >= maxScrollLeft;
        }
        
        timelineContainer.addEventListener('scroll', actualizarEstadoBotones);
        actualizarEstadoBotones(); // Estado inicial
    }
    
    // Destacar cronológicamente la primera ocurrencia de cada tipo de evento
    const primerosEventos = {};
    
    timeline.forEach(evento => {
        const tipo = evento.tipo;
        if (!primerosEventos[tipo] || new Date(evento.fecha) < new Date(primerosEventos[tipo].fecha)) {
            primerosEventos[tipo] = evento;
        }
    });
    
    // Resaltar el primer evento de cada tipo
    const eventos = document.querySelectorAll('.timeline-event');
    eventos.forEach((eventoEl, index) => {
        const evento = timeline[index];
        
        // Si es el primer evento de este tipo
        if (primerosEventos[evento.tipo] && evento.nunc === primerosEventos[evento.tipo].nunc && 
            evento.fecha === primerosEventos[evento.tipo].fecha) {
            eventoEl.classList.add('highlight');
        }
        
        // Agregar tooltip o información adicional
        const contenido = eventoEl.querySelector('.timeline-event-content');
        if (contenido) {
            contenido.title = `${evento.tipo === 'hechos' ? 'Hechos ocurridos' : 'Denuncia realizada'} el ${evento.fecha}\nNUNC: ${evento.nunc}\nDelito: ${evento.delito}`;
        }
    });
    
    // Centrar la línea de tiempo si no tiene muchos eventos
    if (timeline.length <= 4) {
        timelineEl.style.width = '100%';
        timelineEl.style.textAlign = 'center';
    }
}

// Función para crear gráfico de línea temporal con Chart.js
function crearGraficoTimeline(timeline) {
    const container = document.getElementById('timelineContainer');
    if (!container) {
        console.error("Elemento 'timelineContainer' no encontrado en el DOM");
        return;
    }
    
    // Organizar datos para el gráfico
    const fechas = [...new Set(timeline.map(item => item.fecha))].sort();
    
    // Crear puntos de datos para el gráfico
    const hechos = [];
    const denuncias = [];
    
    fechas.forEach(fecha => {
        const eventosHechos = timeline.filter(item => item.fecha === fecha && item.tipo === 'hechos');
        const eventosDenuncias = timeline.filter(item => item.fecha === fecha && item.tipo === 'denuncia');
        
        hechos.push({
            x: fecha,
            y: eventosHechos.length
        });
        
        denuncias.push({
            x: fecha,
            y: eventosDenuncias.length
        });
    });
    
    // Crear canvas para el gráfico
    const canvas = document.createElement('canvas');
    canvas.id = 'graficoTimeline';
    container.appendChild(canvas);
    
    // Verificar que Chart esté disponible
    if (typeof Chart === 'undefined') {
        console.error("La librería Chart.js no está disponible");
        container.innerHTML += '<div class="alert alert-warning mt-3">No se pudo cargar la visualización de gráfico porque Chart.js no está disponible.</div>';
        return;
    }
    
    // Crear gráfico
    try {
        new Chart(canvas, {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: 'Hechos',
                        data: hechos,
                        borderColor: '#dc3545',
                        backgroundColor: '#dc354580',
                        pointRadius: 6,
                        pointHoverRadius: 8
                    },
                    {
                        label: 'Denuncias',
                        data: denuncias,
                        borderColor: '#0d6efd',
                        backgroundColor: '#0d6efd80',
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month',
                            displayFormats: {
                                month: 'MMM YYYY'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Fecha'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Número de eventos'
                        },
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                const fecha = new Date(context[0].parsed.x);
                                return fecha.toLocaleDateString('es-ES', { 
                                    year: 'numeric', month: 'long', day: 'numeric' 
                                });
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error al crear el gráfico:", error);
        container.innerHTML += `<div class="alert alert-danger mt-3">Error al crear el gráfico: ${error.message}</div>`;
    }
}

// Función para exportar a CSV
function exportarCSV() {
    // Verificar si hay búsqueda activa
    if (!hayFiltrosActivos()) {
        alert('Debe realizar una búsqueda antes de exportar a CSV');
        return;
    }
    
    // Construir URL con todos los datos (sin paginación)
    let url = `/dashboard/api/personas/?por_pagina=1000`;
    
    // Agregar parámetros según el modo de búsqueda
    if (paginacionState.modoBusqueda === 'texto') {
        const inputBusqueda = document.getElementById('inputBusqueda');
        if (!inputBusqueda) {
            console.error("Elemento 'inputBusqueda' no encontrado en el DOM");
            return;
        }
        
        const busqueda = inputBusqueda.value.trim();
        url += `&busqueda=${encodeURIComponent(busqueda)}&modo=texto`;
    } else {
        // Obtener valores de los selectores de delitos
        const selectores = {
            'desaparicion': document.getElementById('selectDesaparicion'),
            'homicidio': document.getElementById('selectHomicidio'),
            'secuestro': document.getElementById('selectSecuestro'),
            'reclutamiento': document.getElementById('selectReclutamiento'),
            'rud': document.getElementById('selectRUD')
        };
        
        // Verificar que todos los selectores existan
        for (const [nombre, selector] of Object.entries(selectores)) {
            if (!selector) {
                console.error(`Elemento 'select${nombre.charAt(0).toUpperCase() + nombre.slice(1)}' no encontrado en el DOM`);
                return;
            }
        }
        
        url += '&modo=delitos';
        
        // Agregar parámetros para cada filtro de delito
        for (const [param, selector] of Object.entries(selectores)) {
            if (selector.value !== 'cualquiera') {
                url += `&${param}=${selector.value === 'si' ? 'true' : 'false'}`;
            }
        }
    }
    
    // Realizar petición para obtener todos los datos
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Crear contenido CSV
            let csvContent = "data:text/csv;charset=utf-8,";
            csvContent += "Documento,Nombre Completo,Desaparición Forzada,Homicidio,Secuestro,Reclutamiento Ilícito,RUD\n";
            
            data.personas.forEach(persona => {
                csvContent += `${persona.id},${persona.nombre},${persona.desaparicion},${persona.homicidio},${persona.secuestro},${persona.reclutamiento},${persona.rud}\n`;
            });
            
            // Crear enlace de descarga
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            
            // Nombre personalizado según el tipo de búsqueda
            let nombreArchivo = 'personas_';
            if (paginacionState.modoBusqueda === 'texto') {
                nombreArchivo += 'busqueda_texto';
            } else {
                nombreArchivo += 'filtro_delitos';
            }
            nombreArchivo += '_' + new Date().toISOString().split('T')[0] + '.csv';
            
            link.setAttribute("download", nombreArchivo);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            mostrarEstadoBusqueda('success', `Se ha exportado correctamente un total de ${data.total_registros} registros.`);
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarEstadoBusqueda('danger', 'Error al exportar datos. Por favor intente nuevamente.');
        })
}

// Función para renderizar tabla de noticias
function renderizarTablaNoticias(noticias, extraData) {
    const tabla = document.getElementById('tablaNoticias');
    if (!tabla) {
        console.error("Elemento 'tablaNoticias' no encontrado en el DOM");
        return;
    }
    
    tabla.innerHTML = '';
    
    if (noticias.length === 0) {
        const fila = document.createElement('tr');
        fila.innerHTML = `<td colspan="6" class="text-center">No se encontraron noticias criminales</td>`;
        tabla.appendChild(fila);
        return;
    }
    
    // Verificar si es una noticia de RUD (para mostrar encabezados específicos)
    const esRUD = noticias[0].fuente === 'RUD';
    
    // Actualizar encabezados de la tabla si es RUD
    const thead = tabla.closest('table').querySelector('thead tr');
    if (thead && esRUD) {
        thead.innerHTML = `
            <th>Radicado</th>
            <th>Fecha Desaparición</th>
            <th>Departamento</th>
            <th>Municipio</th>
            <th>Estado</th>
            <th>Fuente</th>
        `;
    } else if (thead) {
        // Restaurar encabezados originales si no es RUD
        thead.innerHTML = `
            <th>NUNC</th>
            <th>Fecha Hechos</th>
            <th>Fecha Denuncia</th>
            <th>Delito</th>
            <th>Unidad</th>
            <th>Fuente</th>
            <th>Estado</th>
            <th>Etapa</th>
        `;
    }
    
    // Si es RUD y tenemos datos extra, mostrar información de aparecidos vivos no registrados
    if (esRUD && extraData && typeof extraData.en_aparecidos_vivos !== 'undefined') {
        // Buscar un relato existente o crear uno nuevo
        let relatoNoticia = document.getElementById('relatoNoticia');
        
        // Crear un div para la información de aparecidos vivos
        const aparecidosVivosDivId = 'infoAparecidosVivos';
        let aparecidosVivosDiv = document.getElementById(aparecidosVivosDivId);
        
        if (!aparecidosVivosDiv) {
            aparecidosVivosDiv = document.createElement('div');
            aparecidosVivosDiv.id = aparecidosVivosDivId;
            aparecidosVivosDiv.className = 'border p-3 mb-3';
            
            // Insertar antes del relatoNoticia
            relatoNoticia.parentNode.insertBefore(aparecidosVivosDiv, relatoNoticia);
        }
        
        // Estilo para el cuadro de información
        const estilo = extraData.en_aparecidos_vivos ? 
            'bg-success text-white' : 'bg-secondary text-white';
        
        const mensaje = extraData.en_aparecidos_vivos ?
            'La persona SÍ se encuentra en la tabla de aparecidos vivos no registrados.' :
            'La persona NO se encuentra en la tabla de aparecidos vivos no registrados.';
        
        aparecidosVivosDiv.className = `border p-3 mb-3 ${estilo}`;
        aparecidosVivosDiv.innerHTML = `
            <h6>Estatus de Aparecidos Vivos</h6>
            <p class="mb-0">${mensaje}</p>
        `;
    }

    noticias.forEach(noticia => {
        const fila = document.createElement('tr');
        
        // HTML específico según si es RUD o no
        if (esRUD) {
            fila.innerHTML = `
                <td>${noticia.nunc}</td>
                <td>${noticia.fecha_hechos || 'No registrada'}</td>
                <td>${noticia.departamento || 'No registrado'}</td>
                <td>${noticia.municipio || 'No registrado'}</td>
                <td>${noticia.estado_desaparicion || 'No registrado'}</td>
                <td>${noticia.fuente}</td>
            `;
        } else {
            fila.innerHTML = `
                <td>${noticia.nunc}</td>
                <td>${noticia.fecha_hechos || 'No registrada'}</td>
                <td>${noticia.fecha_denuncia || 'No registrada'}</td>
                <td>${noticia.delito}</td>
                <td>${noticia.unidad}</td>
                <td>${noticia.fuente}</td>
                <td>${noticia.estado}</td>
                <td>${noticia.etapa}</td>
            `;
        }
        
        // Agregar evento para mostrar relato al hacer clic
        fila.addEventListener('click', function() {
            const relatoNoticia = document.getElementById('relatoNoticia');
            if (relatoNoticia) {
                // Para RUD, mostrar información adicional en el relato
                if (esRUD) {
                    const datosAdicionales = `
                        <p><strong>Barrio/Vereda:</strong> ${noticia.barrio_vereda || 'No registrado'}</p>
                        <p><strong>Sexo:</strong> ${noticia.sexo || 'No registrado'}</p>
                        <p><strong>Edad:</strong> ${noticia.edad || 'No registrada'}</p>
                        <p><strong>Estatura:</strong> ${noticia.estatura || 'No registrada'}</p>
                        <p><strong>Ancestro Racial:</strong> ${noticia.ancestro_racial || 'No registrado'}</p>
                        <p><strong>Señales Particulares:</strong> ${(noticia.relato || '').replace('Señales particulares: ', '')}</p>
                    `;
                    relatoNoticia.innerHTML = datosAdicionales;
                } else {
                    relatoNoticia.textContent = noticia.relato || 'No hay relato disponible.';
                }
            }
            
            // Quitar selección de otras filas y seleccionar esta
            document.querySelectorAll('#tablaNoticias tr').forEach(tr => tr.classList.remove('table-primary'));
            this.classList.add('table-primary');
        });
        
        tabla.appendChild(fila);
    });
    
    // Seleccionar primera fila por defecto para mostrar su relato
    if (noticias.length > 0) {
        const relatoNoticia = document.getElementById('relatoNoticia');
        if (relatoNoticia) {
            // Para RUD, mostrar información adicional en el relato
            if (esRUD) {
                const primerNoticia = noticias[0];
                const datosAdicionales = `
                    <p><strong>Barrio/Vereda:</strong> ${primerNoticia.barrio_vereda || 'No registrado'}</p>
                    <p><strong>Sexo:</strong> ${primerNoticia.sexo || 'No registrado'}</p>
                    <p><strong>Edad:</strong> ${primerNoticia.edad || 'No registrada'}</p>
                    <p><strong>Estatura:</strong> ${primerNoticia.estatura || 'No registrada'}</p>
                    <p><strong>Ancestro Racial:</strong> ${primerNoticia.ancestro_racial || 'No registrado'}</p>
                    <p><strong>Señales Particulares:</strong> ${(primerNoticia.relato || '').replace('Señales particulares: ', '')}</p>
                `;
                relatoNoticia.innerHTML = datosAdicionales;
            } else {
                relatoNoticia.textContent = noticias[0].relato || 'No hay relato disponible.';
            }
        }
        
        const primeraFila = document.querySelector('#tablaNoticias tr');
        if (primeraFila) {
            primeraFila.classList.add('table-primary');
        }
    }
}

// Función para abrir modal de línea de tiempo (versión actualizada)
function abrirModalTimeline(documento) {
    // Actualizar título del modal
    const modalTimelineLabel = document.getElementById('modalTimelineLabel');
    if (!modalTimelineLabel) {
        console.error("Elemento 'modalTimelineLabel' no encontrado en el DOM");
        return;
    }
    
    modalTimelineLabel.textContent = `Línea de Tiempo - Documento: ${documento}`;
    
    // Limpiar contenedor
    const timelineContainer = document.getElementById('timelineContainer');
    if (!timelineContainer) {
        console.error("Elemento 'timelineContainer' no encontrado en el DOM");
        return;
    }
    
    timelineContainer.innerHTML = '<div class="d-flex justify-content-center my-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>';
    
    // Mostrar modal
    const modalElement = document.getElementById('modalTimeline');
    if (!modalElement) {
        console.error("Elemento 'modalTimeline' no encontrado en el DOM");
        return;
    }
    
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Cargar datos
    fetch(`/dashboard/api/timeline/?documento=${documento}`)
        .then(response => response.json())
        .then(data => {
            // Usar la nueva función de línea de tiempo horizontal
            renderizarTimelineHorizontal(data.timeline);
        })
        .catch(error => {
            console.error('Error:', error);
            if (timelineContainer) {
                timelineContainer.innerHTML = `<div class="alert alert-danger">Error al cargar línea de tiempo: ${error}</div>`;
            }
        });
}