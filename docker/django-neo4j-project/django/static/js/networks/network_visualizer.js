/**
 * NetworkVisualizer - Módulo para visualizar redes a partir de archivos Excel
 * Permite cargar archivos, procesar datos, visualizar redes y buscar nodos
 */
const NetworkVisualizer = (function() {
    // Variables privadas
    let config = {};
    let currentFileId = null;
    let network = null;
    let nodesDataset = null;
    let edgesDataset = null;
    let allNodes = null;
    let allEdges = null;
    let isLargeNetwork = false;
    let loadingStatus = {
        nodesLoaded: 0,
        edgesLoaded: 0,
        totalNodes: 0,
        totalEdges: 0
    };
    
    /**
     * Inicializa el visualizador con la configuración proporcionada
     * @param {Object} userConfig - Configuración del usuario (URLs, opciones)
     */
    function init(userConfig) {
        // Combinar configuración predeterminada con configuración del usuario
        config = Object.assign({
            canvasHeight: 750,
            nodeHighlightColor: '#ff9e00',
            nodeBorderHighlightColor: '#ff6d00',
            connectedNodeColor: '#c8e6c9',
            connectedNodeBorderColor: '#2e7d32',
            dimmedNodeColor: '#eeeeee',
            dimmedNodeBorderColor: '#cccccc',
            connectedEdgeColor: '#2e7d32',
            dimmedEdgeColor: '#dddddd',
            // Colores predeterminados para los nodos y bordes
            defaultNodeColor: '#97C2FC',
            defaultNodeBorderColor: '#2B7CE9',
            defaultEdgeColor: '#848484',
            defaultEdgeWidth: 1,
            // Configuración para redes grandes
            largeNetworkThreshold: 1000, // Número de nodos para considerar una red como "grande"
            batchSize: 5000, // Tamaño del lote para cargar nodos y bordes progresivamente
            progressUpdateInterval: 200 // Intervalo para actualizar el progreso (ms)
        }, userConfig);
        
        // Configurar manejadores de eventos
        setupEventHandlers();
    }
    
    /**
     * Configura los manejadores de eventos para los elementos de la interfaz
     */
    function setupEventHandlers() {
        // Formulario de carga de archivos
        $('#upload-form').submit(function(e) {
            e.preventDefault();
            uploadFile();
        });
        
        // Botón de búsqueda
        $('#search-btn').click(function() {
            const searchValue = $('#node-search').val().trim();
            if (searchValue) {
                searchNode(searchValue);
            }
        });
        
        // Campo de búsqueda (para tecla Enter)
        $('#node-search').keypress(function(e) {
            if (e.which === 13) {
                const searchValue = $('#node-search').val().trim();
                if (searchValue) {
                    searchNode(searchValue);
                }
                e.preventDefault();
            }
        });
        
        // Botón para restablecer vista
        $('#reset-view').on('click', function() {
            console.log("Reset View button clicked");
            resetNetworkView();
        });
        
        // Botón para centrar la red
        $('#center-network').on('click', function() {
            console.log("Center Network button clicked");
            centerNetwork();
        });

        // Botones para controlar la física de la red
        $('#toggle-physics').on('click', function() {
            togglePhysics();
        });

        // Botón para cambiar el modo de visualización
        $('#toggle-performance-mode').on('click', function() {
            togglePerformanceMode();
        });
        
        // Botón para descargar la imagen
        $('#download-image').on('click', function() {
            downloadNetworkImage();
        });
        
        // Ajustar altura del canvas al redimensionar la ventana
        $(window).resize(function() {
            adjustCanvasHeight();
        });
    }
    
    /**
     * Carga la red de manera estándar (todos los datos de una vez)
     * @param {number} fileId - ID del archivo procesado
     */
    function loadNetworkStandard(fileId) {
        showStatus('Cargando visualización...', 'info');
        
        // Fetch nodes and edges
        $.when(
            $.getJSON(`${config.urls.getNodesUrl}${fileId}/`),
            $.getJSON(`${config.urls.getEdgesUrl}${fileId}/`)
        ).done(function(nodesResponse, edgesResponse) {
            const nodes = nodesResponse[0];
            const edges = edgesResponse[0];
            
            allNodes = nodes;
            allEdges = edges;
            
            showStatus(`Datos cargados: ${nodes.length} nodos, ${edges.length} conexiones`, 'success');
            initializeNetwork(nodes, edges);
            $('#loading-progress-container').hide();
        }).fail(function(jqXHR, textStatus, errorThrown) {
            showStatus('Error al cargar los datos de la red', 'danger');
            console.error(textStatus, errorThrown);
            $('#loading-progress-container').hide();
        });
    }
    
    /**
     * Carga la red progresivamente en lotes
     * @param {number} fileId - ID del archivo procesado
     */
    function loadNetworkProgressively(fileId) {
        // Inicializar contenedores
        allNodes = [];
        allEdges = [];
        
        // Crear datasets vacíos
        nodesDataset = new vis.DataSet();
        edgesDataset = new vis.DataSet();
        
        // Inicializar el contenedor de red con datasets vacíos
        const container = document.getElementById('network-container');
        const data = {
            nodes: nodesDataset,
            edges: edgesDataset
        };
        
        // Usar opciones optimizadas para redes grandes
        const options = createNetworkOptions(true);
        network = new vis.Network(container, data, options);
        
        // Ajustar la altura del canvas
        adjustCanvasHeight();
        
        // Iniciar la carga progresiva
        loadNodesProgressively(fileId, 0);
        
        // Actualizar el progreso de carga
        updateLoadingProgressBar();
    }
    
    /**
     * Carga nodos progresivamente en lotes
     * @param {number} fileId - ID del archivo
     * @param {number} offset - Offset para la paginación
     */
    function loadNodesProgressively(fileId, offset) {
        const url = `${config.urls.getNodesUrl}${fileId}/?offset=${offset}&limit=${config.batchSize}`;
        
        $.getJSON(url)
            .done(function(nodes) {
                if (nodes.length > 0) {
                    // Agregar nodos al dataset y al array completo
                    nodesDataset.add(nodes);
                    allNodes = allNodes.concat(nodes);
                    
                    // Actualizar contador de nodos cargados
                    loadingStatus.nodesLoaded += nodes.length;
                    
                    // Mostrar progreso
                    const progress = Math.round((loadingStatus.nodesLoaded / loadingStatus.totalNodes) * 100);
                    $('#loading-progress-bar').css('width', `${progress}%`).attr('aria-valuenow', progress);
                    $('#loading-progress-text').text(`Cargando nodos: ${loadingStatus.nodesLoaded}/${loadingStatus.totalNodes} (${progress}%)`);
                    
                    // Cargar el siguiente lote si hay más nodos
                    if (nodes.length === config.batchSize) {
                        setTimeout(function() {
                            loadNodesProgressively(fileId, offset + config.batchSize);
                        }, 10); // Pequeña pausa para evitar bloquear la UI
                    } else {
                        // Comenzar a cargar bordes cuando se completen los nodos
                        $('#loading-progress-text').text('Nodos cargados. Cargando conexiones...');
                        loadEdgesProgressively(fileId, 0);
                    }
                } else {
                    // No hay más nodos, cargar bordes
                    $('#loading-progress-text').text('Nodos cargados. Cargando conexiones...');
                    loadEdgesProgressively(fileId, 0);
                }
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                showStatus('Error al cargar los nodos de la red', 'danger');
                console.error(textStatus, errorThrown);
                $('#loading-progress-container').hide();
            });
    }
    
    /**
     * Carga bordes progresivamente en lotes
     * @param {number} fileId - ID del archivo
     * @param {number} offset - Offset para la paginación
     */
    function loadEdgesProgressively(fileId, offset) {
        const url = `${config.urls.getEdgesUrl}${fileId}/?offset=${offset}&limit=${config.batchSize}`;
        
        $.getJSON(url)
            .done(function(edges) {
                if (edges.length > 0) {
                    // Agregar bordes al dataset y al array completo
                    edgesDataset.add(edges);
                    allEdges = allEdges.concat(edges);
                    
                    // Actualizar contador de bordes cargados
                    loadingStatus.edgesLoaded += edges.length;
                    
                    // Mostrar progreso
                    const progress = Math.round((loadingStatus.edgesLoaded / loadingStatus.totalEdges) * 100);
                    $('#loading-progress-bar').css('width', `${progress}%`).attr('aria-valuenow', progress);
                    $('#loading-progress-text').text(`Cargando conexiones: ${loadingStatus.edgesLoaded}/${loadingStatus.totalEdges} (${progress}%)`);
                    
                    // Cargar el siguiente lote si hay más bordes
                    if (edges.length === config.batchSize) {
                        setTimeout(function() {
                            loadEdgesProgressively(fileId, offset + config.batchSize);
                        }, 10); // Pequeña pausa para evitar bloquear la UI
                    } else {
                        // Finalizar la carga cuando se completen los bordes
                        finishNetworkLoading();
                    }
                } else {
                    // No hay más bordes, finalizar
                    finishNetworkLoading();
                }
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                showStatus('Error al cargar las conexiones de la red', 'danger');
                console.error(textStatus, errorThrown);
                $('#loading-progress-container').hide();
            });
    }
    
    /**
     * Actualiza la barra de progreso durante la carga
     */
    function updateLoadingProgressBar() {
        if (loadingStatus.nodesLoaded < loadingStatus.totalNodes || 
            loadingStatus.edgesLoaded < loadingStatus.totalEdges) {
            
            // Si todavía hay elementos por cargar, programar la siguiente actualización
            setTimeout(updateLoadingProgressBar, config.progressUpdateInterval);
        }
    }
    
    /**
     * Finaliza el proceso de carga de la red
     */
    function finishNetworkLoading() {
        // Ocultar la barra de progreso
        $('#loading-progress-container').fadeOut(1000);
        
        // Mostrar mensaje de finalización
        showStatus(`Red cargada: ${loadingStatus.nodesLoaded} nodos, ${loadingStatus.edgesLoaded} conexiones`, 'success');
        
        // Configurar eventos de la red
        setupNetworkEvents();
        
        // Centrar la red
        centerNetwork();
        
        // Desactivar la física después de la estabilización inicial
        network.on("stabilizationIterationsDone", function () {
            // Si es una red grande, deshabilitar la física automáticamente
            if (isLargeNetwork) {
                network.setOptions({ physics: false });
                $('#toggle-physics').text('Activar Física');
                $('#physics-status').text('Física: Desactivada');
            }
            
            // Centrar la red una vez que se haya estabilizado
            centerNetwork();
        });
    }
    
    /**
     * Inicializa la red con todos los datos cargados
     * @param {Array} nodes - Array de nodos
     * @param {Array} edges - Array de bordes
     */
    function initializeNetwork(nodes, edges) {
        // Create a vis.js network
        const container = document.getElementById('network-container');
        nodesDataset = new vis.DataSet(nodes);
        edgesDataset = new vis.DataSet(edges);
        
        const data = {
            nodes: nodesDataset,
            edges: edgesDataset
        };
        
        // Determinar si es una red grande basado en el número de nodos
        isLargeNetwork = (nodes.length > config.largeNetworkThreshold);
        if (isLargeNetwork) {
            $('#network-size-info').text(`Red grande: ${nodes.length} nodos, ${edges.length} conexiones`);
            $('#performance-controls').show();
        }
        
        const options = createNetworkOptions(isLargeNetwork);
        
        // Initialize the network
        network = new vis.Network(container, data, options);
        
        // Ajustar la altura del canvas después de inicializar la red
        adjustCanvasHeight();
        
        // Configurar eventos de la red
        setupNetworkEvents();
    }
    
    /**
     * Configura eventos de la red una vez cargada
     */
    function setupNetworkEvents() {
        // Adjust the view
        network.on("stabilizationIterationsDone", function () {
            // Si es una red grande, deshabilitar la física automáticamente
            if (isLargeNetwork) {
                network.setOptions({ physics: false });
                $('#toggle-physics').text('Activar Física');
                $('#physics-status').text('Física: Desactivada');
            }
            
            // Centrar la red una vez que se haya estabilizado
            centerNetwork();
        });
        
        // También centrar la red cuando esté completamente cargada
        network.once("afterDrawing", function() {
            centerNetwork();
        });

        // Registrar los manejadores de eventos de nuevo (por si acaso)
        $('#reset-view').off('click').on('click', function() {
            console.log("Reset View button clicked (after network load)");
            resetNetworkView();
        });
        
        $('#center-network').off('click').on('click', function() {
            console.log("Center Network button clicked (after network load)");
            centerNetwork();
        });

        // // Eventos para mostrar información sobre el nodo al hacer hover
        // network.on("hoverNode", function(params) {
        //     const nodeId = params.node;
        //     const node = nodesDataset.get(nodeId);
            
        //     // Mostrar tooltip con información del nodo
        //     $('#node-tooltip').html(`<strong>${node.label}</strong><br>Conexiones: ${network.getConnectedEdges(nodeId).length}`);
        //     $('#node-tooltip').css({
        //         display: 'block',
        //         left: params.event.center.x + 10,
        //         top: params.event.center.y + 10
        //     });
        // });

        // Eventos para mostrar información sobre el nodo al hacer hover
        network.on("hoverNode", function(params) {
            const nodeId = params.node;
            const node = nodesDataset.get(nodeId);
            
            if (!node) return; // Si el nodo no existe, salir
            
            // Mostrar tooltip con información del nodo
            const tooltipEl = document.getElementById('node-tooltip');
            if (tooltipEl) {
                tooltipEl.innerHTML = `<strong>${node.label || 'Sin etiqueta'}</strong><br>ID: ${node.id}<br>Conexiones: ${network.getConnectedEdges(nodeId).length}`;
                tooltipEl.style.display = 'block';
                tooltipEl.style.left = (params.event.center.x + 10) + 'px';
                tooltipEl.style.top = (params.event.center.y + 10) + 'px';
                
                // También imprimir en la consola para depuración
                console.log('Mostrando tooltip para nodo:', node.id, node.label);
            } else {
                console.error('Elemento tooltip no encontrado');
            }
        });

        network.on("blurNode", function() {
            const tooltipEl = document.getElementById('node-tooltip');
            if (tooltipEl) {
                tooltipEl.style.display = 'none';
            }
        });
        
        network.on("blurNode", function() {
            $('#node-tooltip').css('display', 'none');
        });
    }
    
    /**
     * Crea las opciones de configuración para la red vis.js
     * @param {boolean} isLargeNetwork - Indica si es una red grande
     * @returns {Object} Opciones para la red
     */
    function createNetworkOptions(isLargeNetwork = false) {
        const options = {
            nodes: {
                shape: 'dot',
                scaling: {
                    min: isLargeNetwork ? 8 : 12, // Valores más grandes
                    max: isLargeNetwork ? 30 : 40, // Valores más grandes
                    label: {
                        min: isLargeNetwork ? 12 : 14,
                        max: isLargeNetwork ? 20 : 30,
                        drawThreshold: 5, // Valor más bajo para que las etiquetas se vean más fácilmente
                        maxVisible: 30 // Valor más alto para ver más etiquetas
                    }
                },
                font: {
                    size: isLargeNetwork ? 10 : 18,
                    face: 'Tahoma'
                },
                color: {
                    background: config.defaultNodeColor,
                    border: config.defaultNodeBorderColor,
                    highlight: {
                        background: '#D2E5FF',
                        border: '#2B7CE9'
                    }
                }
            },
            // En la función createNetworkOptions, modifica las opciones de los bordes
            edges: {
                width: isLargeNetwork ? 0.5 : config.defaultEdgeWidth,
                selectionWidth: isLargeNetwork ? 1 : 2,
                color: {
                    color: config.defaultEdgeColor,
                    inherit: 'from'
                },
                smooth: {
                    type: isLargeNetwork ? 'continuous' : 'dynamic',
                    forceDirection: isLargeNetwork ? 'none' : 'horizontal',
                    roundness: isLargeNetwork ? 0.2 : 0.5
                },
                arrows: {
                    to: {
                        enabled: false,  // Desactivar flechas para indicar que es no dirigido
                        scaleFactor: isLargeNetwork ? 0.3 : 1
                    }
                }
            },
            physics: {
                enabled: true,
                stabilization: {
                    iterations: 1000, // Mayor número de iteraciones para mejor estabilización
                    updateInterval: 100,
                    fit: true,
                    onlyDynamicEdges: false,
                    enabled: true
                },
                barnesHut: {
                    gravitationalConstant: -2000, // Menos fuerza gravitacional
                    centralGravity: 0.1, // Menos gravedad central
                    springLength: 150,
                    springConstant: 0.01, // Mayor rigidez en los resortes
                    damping: 0.2, // Mayor amortiguación
                    avoidOverlap: 0.5 // Mayor evitación de superposición
                },
                solver: 'barnesHut',
                timestep: 0.3 // Paso de tiempo más grande para movimientos más lentos
            },
            interaction: {
                navigationButtons: true,
                keyboard: true,
                tooltipDelay: 200,
                hideEdgesOnDrag: true,
                hideEdgesOnZoom: isLargeNetwork,
                multiselect: true,
                hover: true,
                zoomView: true
            }
        };
        
        // Opciones adicionales para redes muy grandes
        if (isLargeNetwork) {
            options.layout = {
                improvedLayout: false
            };
            options.rendering = {
                hideEdgesOnViewport: true,
                hideNodesOnViewport: true
            };
        }
        
        return options;
    }
    
    /**
     * Cambia entre los modos de rendimiento normal y alto
     */
    function togglePerformanceMode() {
        const currentMode = $('#toggle-performance-mode').text();
        
        if (currentMode.includes('Alto Rendimiento')) {
            // Cambiar a modo normal
            network.setOptions({
                nodes: {
                    scaling: {
                        min: isLargeNetwork ? 4 : 10,
                        max: isLargeNetwork ? 20 : 30
                    }
                },
                edges: {
                    width: isLargeNetwork ? 0.5 : config.defaultEdgeWidth,
                    hidden: false
                },
                interaction: {
                    hideEdgesOnZoom: isLargeNetwork
                }
            });
            $('#toggle-performance-mode').text('Modo Alto Rendimiento');
            $('#performance-mode-status').text('Modo: Normal');
        } else {
            // Cambiar a modo alto rendimiento
            network.setOptions({
                nodes: {
                    scaling: {
                        min: 2,
                        max: 10
                    }
                },
                edges: {
                    width: 0.1,
                    hidden: (allNodes.length > 5000)
                },
                interaction: {
                    hideEdgesOnZoom: true
                }
            });
            $('#toggle-performance-mode').text('Modo Normal');
            $('#performance-mode-status').text('Modo: Alto Rendimiento');
        }
    }
    
    /**
     * Activa o desactiva la física de la red
     */
    function togglePhysics() {
        const currentPhysics = network.physics.options.enabled;
        
        network.setOptions({
            physics: {
                enabled: !currentPhysics
            }
        });
        
        if (currentPhysics) {
            $('#toggle-physics').text('Activar Física');
            $('#physics-status').text('Física: Desactivada');
        } else {
            $('#toggle-physics').text('Desactivar Física');
            $('#physics-status').text('Física: Activada');
            
            // Si la red es grande, programar la desactivación después de un tiempo
            if (isLargeNetwork) {
                showStatus('La física se desactivará automáticamente después de 30 segundos para mejorar el rendimiento', 'info');
                setTimeout(function() {
                    if (network && network.physics.options.enabled) {
                        network.setOptions({ physics: false });
                        $('#toggle-physics').text('Activar Física');
                        $('#physics-status').text('Física: Desactivada');
                    }
                }, 30000);
            }
        }
    }
    
    /**
     * Busca un nodo en la red y lo resalta
     * @param {string} searchValue - Valor a buscar
     */
    function searchNode(searchValue) {
        if (!network || !nodesDataset) return;
        
        // Reset the highlighting
        resetNodeColors();
        
        // Find the node matching the search
        const searchLower = searchValue.toLowerCase();
        const foundNodes = nodesDataset.get({
            filter: function(node) {
                return node.label && node.label.toLowerCase().includes(searchLower);
            }
        });
        
        if (foundNodes.length > 0) {
            // Si se encuentran muchos nodos, mostrar advertencia
            if (foundNodes.length > 20) {
                showStatus(`Se encontraron ${foundNodes.length} nodos. Mostrando los primeros 20.`, 'warning');
                foundNodes.splice(20);
            }
            
            // Highlight the found node(s)
            const foundNodeIds = foundNodes.map(node => node.id);
            highlightConnectedNodes(foundNodeIds[0]); // Highlight first matching node
            
            // Focus on the node
            network.focus(foundNodeIds[0], {
                scale: 1.2,
                animation: true
            });
            network.selectNodes(foundNodeIds);
            
            // Show connected nodes in the sidebar
            displayConnectedNodes(foundNodeIds[0]);
            
            // Si hay más de un nodo encontrado, mostrar lista
            if (foundNodes.length > 1) {
                let otherNodesHtml = '<div class="mt-3"><strong>Otros nodos encontrados:</strong><ul class="other-nodes-list">';
                
                for (let i = 1; i < foundNodes.length; i++) {
                    otherNodesHtml += `<li class="other-found-node" data-node-id="${foundNodes[i].id}">${foundNodes[i].label}</li>`;
                }
                
                otherNodesHtml += '</ul></div>';
                $('#search-results').html(otherNodesHtml).show();
                
                // Agregar evento click a los nodos encontrados
                $('.other-found-node').click(function() {
                    const nodeId = $(this).data('node-id');
                    network.focus(nodeId, {
                        scale: 1.2,
                        animation: true
                    });
                    resetNodeColors();
                    highlightConnectedNodes(nodeId);
                    displayConnectedNodes(nodeId);
                });
            } else {
                $('#search-results').empty().hide();
            }
        } else {
            // No nodes found
            $('#connected-nodes').html('<p class="text-danger">No se encontraron nodos que coincidan con la búsqueda.</p>');
            $('#search-results').empty().hide();
        }
    }
    
    /**
     * Resalta los nodos conectados a un nodo específico
     * @param {string|number} nodeId - ID del nodo principal
     */
    function highlightConnectedNodes(nodeId) {
        if (!network || !nodesDataset || !edgesDataset) return;
        
        // Get all connected edges
        const connectedEdges = network.getConnectedEdges(nodeId);
        const connectedNodes = network.getConnectedNodes(nodeId);
        
        // Si hay demasiados nodos conectados, optimizar la actualización
        const updateBatchSize = 1000;
        
        // Update node colors
        if (connectedNodes.length > updateBatchSize) {
            // Actualizar por lotes para redes grandes
            let nodeUpdates = [];
            
            // Primero, atenuar todos los nodos
            allNodes.forEach(node => {
                nodeUpdates.push({ 
                    id: node.id, 
                    color: { 
                        background: config.dimmedNodeColor, 
                        border: config.dimmedNodeBorderColor 
                    } 
                });
                
                if (nodeUpdates.length >= updateBatchSize) {
                    nodesDataset.update(nodeUpdates);
                    nodeUpdates = [];
                }
            });
            
            if (nodeUpdates.length > 0) {
                nodesDataset.update(nodeUpdates);
                nodeUpdates = [];
            }
            
            // Luego, resaltar nodo principal
            nodesDataset.update({ 
                id: nodeId, 
                color: { 
                    background: config.nodeHighlightColor, 
                    border: config.nodeBorderHighlightColor 
                } 
            });
            
            // Finalmente, resaltar nodos conectados
            connectedNodes.forEach(connectedNodeId => {
                nodeUpdates.push({ 
                    id: connectedNodeId, 
                    color: { 
                        background: config.connectedNodeColor, 
                        border: config.connectedNodeBorderColor 
                    } 
                });
                
                if (nodeUpdates.length >= updateBatchSize) {
                    nodesDataset.update(nodeUpdates);
                    nodeUpdates = [];
                }
            });
            
            if (nodeUpdates.length > 0) {
                nodesDataset.update(nodeUpdates);
            }
        } else {
            // Método estándar para redes pequeñas
            nodesDataset.update(allNodes.map(node => {
                if (node.id === nodeId) {
                    // Main node (searched)
                    return { 
                        id: node.id, 
                        color: { 
                            background: config.nodeHighlightColor, 
                            border: config.nodeBorderHighlightColor 
                        } 
                    };
                } else if (connectedNodes.includes(node.id)) {
                    // Connected node - color verde claro
                    return { 
                        id: node.id, 
                        color: { 
                            background: config.connectedNodeColor, 
                            border: config.connectedNodeBorderColor 
                        } 
                    };
                } else {
                    // Other nodes (dimmed)
                    return { 
                        id: node.id, 
                        color: { 
                            background: config.dimmedNodeColor, 
                            border: config.dimmedNodeBorderColor 
                        } 
                    };
                }
            }));
        }
        
        // Optimizar actualización de bordes para redes grandes
        if (allEdges.length > 5000) {
            // Para redes muy grandes, simplemente ocultar los bordes no conectados
            network.setOptions({
                edges: {
                    hidden: false
                }
            });
            
            // Filtrar para mostrar solo bordes conectados
            const edgeFilter = edge => connectedEdges.includes(edge.id);
            network.setData({
                nodes: nodesDataset,
                edges: new vis.DataSet(allEdges.filter(edgeFilter))
            });
        } else {
            // Método estándar para actualizar colores de bordes
            edgesDataset.update(allEdges.map(edge => {
                if (connectedEdges.includes(edge.id)) {
                    return { 
                        id: edge.id, 
                        color: { 
                            color: config.connectedEdgeColor, 
                            highlight: config.connectedEdgeColor 
                        }, 
                        width: 2 
                    };
                } else {
                    return { 
                        id: edge.id, 
                        color: { 
                            color: config.dimmedEdgeColor, 
                            highlight: config.dimmedEdgeColor 
                        }, 
                        width: 1 
                    };
                }
            }));
        }
    }
    
    /**
     * Muestra los nodos conectados en el panel lateral
     * @param {string|number} nodeId - ID del nodo principal
     */
    function displayConnectedNodes(nodeId) {
        if (!network || !nodesDataset) return;
        
        const connectedNodes = network.getConnectedNodes(nodeId);
        const mainNode = nodesDataset.get(nodeId);
        
        if (!mainNode) {
            $('#connected-nodes').html('<p class="text-danger">No se pudo encontrar el nodo seleccionado.</p>');
            return;
        }
        
        if (connectedNodes.length === 0) {
            $('#connected-nodes').html(`<p class="node-main">${mainNode.label || 'Sin etiqueta'}</p><p class="text-muted">No tiene conexiones con otros nodos.</p>`);
            return;
        }
        
        let html = `<p class="node-main">${mainNode.label || 'Sin etiqueta'}</p>`;
        
        // Si hay demasiados nodos conectados, mostrar advertencia y limitar
        const maxNodesToShow = 100; // Limitar para evitar problemas de rendimiento
        
        if (connectedNodes.length > maxNodesToShow) {
            html += `<p class="text-warning">Este nodo tiene ${connectedNodes.length} conexiones. Mostrando las primeras ${maxNodesToShow}.</p>`;
        }
        
        html += '<ul class="node-connections">';
        
        // Obtener y ordenar los nodos conectados
        let connectedNodeObjects = nodesDataset.get(connectedNodes);
        
        // Ordenar por label para facilitar la búsqueda
        connectedNodeObjects.sort((a, b) => {
            if (!a.label) return 1;
            if (!b.label) return -1;
            return a.label.localeCompare(b.label);
        });
        
        // Limitar la cantidad si es necesario
        if (connectedNodeObjects.length > maxNodesToShow) {
            connectedNodeObjects = connectedNodeObjects.slice(0, maxNodesToShow);
        }
        
        // Crear la lista de nodos conectados
        for (const node of connectedNodeObjects) {
            html += `<li class="connected-node" data-node-id="${node.id}">${node.label || 'Sin etiqueta'}</li>`;
        }
        
        html += '</ul>';
        $('#connected-nodes').html(html);
        
        // Add click event for connected nodes in the list
        $('.connected-node').click(function() {
            const nodeId = $(this).data('node-id');
            network.focus(nodeId, {
                scale: 1.2,
                animation: true
            });
            resetNodeColors();
            highlightConnectedNodes(nodeId);
            displayConnectedNodes(nodeId);
        });
    }
    
    /**
     * Restablece los colores de los nodos a su estado original
     */
    function resetNodeColors() {
        if (!nodesDataset || !edgesDataset) return;
        
        // Para redes grandes, usar un enfoque optimizado de actualización por lotes
        if (allNodes.length > 5000) {
            const batchSize = 1000;
            let batch = [];
            
            // Actualizar nodos por lotes
            for (let i = 0; i < allNodes.length; i++) {
                batch.push({ 
                    id: allNodes[i].id, 
                    color: { 
                        background: config.defaultNodeColor, 
                        border: config.defaultNodeBorderColor 
                    } 
                });
                
                if (batch.length >= batchSize || i === allNodes.length - 1) {
                    nodesDataset.update(batch);
                    batch = [];
                }
            }
            
            // Si había una visualización filtrada, restaurar todos los bordes
            if (network && isLargeNetwork) {
                network.setData({
                    nodes: nodesDataset,
                    edges: edgesDataset
                });
            }
            
            // Para redes muy grandes, solo actualizar las propiedades de visualización
            if (allEdges.length > 10000) {
                network.setOptions({
                    edges: {
                        color: {
                            color: config.defaultEdgeColor,
                            highlight: '#848484'
                        },
                        width: config.defaultEdgeWidth,
                        hidden: false
                    }
                });
            } else {
                // Actualizar bordes por lotes
                batch = [];
                for (let i = 0; i < allEdges.length; i++) {
                    batch.push({ 
                        id: allEdges[i].id, 
                        color: { 
                            color: config.defaultEdgeColor 
                        }, 
                        width: config.defaultEdgeWidth 
                    });
                    
                    if (batch.length >= batchSize || i === allEdges.length - 1) {
                        edgesDataset.update(batch);
                        batch = [];
                    }
                }
            }
        } else {
            // Método estándar para redes pequeñas
            nodesDataset.update(allNodes.map(node => {
                return { 
                    id: node.id, 
                    color: { 
                        background: config.defaultNodeColor, 
                        border: config.defaultNodeBorderColor 
                    } 
                };
            }));
            
            edgesDataset.update(allEdges.map(edge => {
                return { 
                    id: edge.id, 
                    color: { 
                        color: config.defaultEdgeColor 
                    }, 
                    width: config.defaultEdgeWidth 
                };
            }));
        }
        
        // Desseleccionar todos los nodos
        if (network) {
            network.unselectAll();
        }
    }
    
    /**
     * Función para centrar la red y mostrar todos los nodos
     */
    function centerNetwork() {
        if (!network) return;
        
        // Para redes grandes, usar animación más corta
        const animationDuration = isLargeNetwork ? 1000 : 2000;
        
        network.fit({
            animation: {
                duration: animationDuration,
                easingFunction: 'easeInOutQuad'
            }
        });
    }
    
    /**
     * Restablece la vista de la red a su estado original
     */
    function resetNetworkView() {
        console.log("resetNetworkView called");
        if (!network) {
            console.log("No network object found");
            return;
        }
        
        // Mostrar estado de procesamiento
        showStatus('Restableciendo vista...', 'info');
        
        // Para redes grandes, usar setTimeout para evitar bloquear la UI
        if (isLargeNetwork && allNodes.length > 10000) {
            setTimeout(function() {
                // Restablecer colores
                resetNodeColors();
                
                // Restaurar opciones de visualización por defecto
                network.setOptions(createNetworkOptions(isLargeNetwork));
                
                // Centrar la red
                centerNetwork();
                
                // Actualizar controles de UI
                $('#toggle-physics').text(network.physics.options.enabled ? 'Desactivar Física' : 'Activar Física');
                $('#physics-status').text(`Física: ${network.physics.options.enabled ? 'Activada' : 'Desactivada'}`);
                $('#toggle-performance-mode').text('Modo Alto Rendimiento');
                $('#performance-mode-status').text('Modo: Normal');
                
                // Limpiar panel lateral y búsqueda
                $('#connected-nodes').html('<p class="text-muted">Busca un nodo para ver sus conexiones</p>');
                $('#node-search').val('');
                $('#search-results').empty().hide();
                
                showStatus('Vista restablecida', 'success');
                console.log("Reset view complete");
            }, 50);
        } else {
            // Proceso estándar para redes pequeñas
            // Restablecer colores
            resetNodeColors();
            
            // Centrar la red
            centerNetwork();
            
            // Limpiar panel lateral
            $('#connected-nodes').html('<p class="text-muted">Busca un nodo para ver sus conexiones</p>');
            $('#node-search').val('');
            $('#search-results').empty().hide();
            
            showStatus('Vista restablecida', 'success');
            console.log("Reset view complete");
        }
    }
    
    /**
     * Ajusta la altura del canvas de la red
     */
    function adjustCanvasHeight() {
        if (!network) return;
        
        // Si es una red grande, usar toda la altura disponible
        const height = isLargeNetwork ? 
            Math.max($(window).height() - $('#network-container').offset().top - 50, config.canvasHeight) : 
            config.canvasHeight;
        
        // Asegurarse de que el canvas dentro de vis-network tenga la altura correcta
        $('.vis-network canvas').css('height', height + 'px');
    }
    
    /**
     * Muestra un mensaje de estado
     * @param {string} message - Mensaje a mostrar
     * @param {string} type - Tipo de mensaje (success, info, warning, danger)
     * @param {number} [autoHideDelay=0] - Tiempo en ms para ocultar automáticamente (0 = no ocultar)
     */
    function showStatus(message, type, autoHideDelay = 0) {
        const statusDiv = $('#upload-status');
        statusDiv.removeClass('alert-success alert-info alert-warning alert-danger');
        statusDiv.addClass(`alert-${type}`);
        statusDiv.text(message);
        statusDiv.show();
        
        // También mostrar en el área de estado de red para mayor visibilidad
        if ($('#network-status-message').length) {
            $('#network-status-message').text(message).removeClass().addClass(`text-${type}`);
        }
        
        // Auto-ocultar después del tiempo especificado
        if (autoHideDelay > 0) {
            setTimeout(function() {
                statusDiv.fadeOut();
            }, autoHideDelay);
        }
    }
    
    /**
     * Descarga la red actual como imagen PNG
     */
    function downloadNetworkImage() {
        if (!network) {
            showStatus('No hay ninguna red cargada para exportar', 'warning');
            return;
        }
        
        try {
            // Obtener la red como imagen
            const dataUrl = network.canvas.body.container.getElementsByTagName('canvas')[0].toDataURL('image/png');
            
            // Crear un enlace para descargar
            const downloadLink = document.createElement('a');
            downloadLink.href = dataUrl;
            downloadLink.download = 'network_visualization.png';
            
            // Agregar al documento temporalmente
            document.body.appendChild(downloadLink);
            
            // Hacer clic en el enlace
            downloadLink.click();
            
            // Eliminar el enlace
            document.body.removeChild(downloadLink);
            
            showStatus('Imagen descargada correctamente', 'success', 3000);
        } catch (error) {
            console.error('Error al descargar la imagen:', error);
            showStatus('Error al generar la imagen de la red', 'danger');
        }
    }

    /**
     * Carga la componente de red desde el API
     */
    function loadComponent() {
        showStatus('Cargando componente...', 'info');
        
        $.getJSON(config.componentUrl)
            .done(function(data) {
                if (data.error) {
                    showStatus('Error: ' + data.error, 'danger');
                    return;
                }
                
                // Guardar datos para uso posterior
                allNodes = data.nodes;
                allEdges = data.edges;
                
                // Actualizar información en la interfaz
                if ($('#info-component').length) {
                    $('#info-component').text(data.componente || '-');
                }
                if ($('#info-total-nodes').length) {
                    $('#info-total-nodes').text(data.node_count || '-');
                }
                if ($('#info-total-edges').length) {
                    $('#info-total-edges').text(data.edge_count || '-');
                }
                
                // Resaltar el nodo central si está definido
                if (config.centralNodeId) {
                    allNodes.forEach(node => {
                        if (node.id === config.centralNodeId) {
                            node.color = '#FF0000'; // Rojo para el nodo consultado
                            node.borderWidth = 3;
                            node.size = 20;
                        }
                    });
                }
                
                // Crear la red
                initializeNetwork(allNodes, allEdges);
                
                // Mostrar mensaje de éxito
                showStatus(`Componente cargada: ${data.node_count} nodos, ${data.edge_count} enlaces`, 'success');
                
                // Si se alcanzó el límite, mostrar aviso
                if (data.limit_reached) {
                    showStatus('Aviso: La componente completa puede ser más grande que lo visualizado', 'warning', 5000);
                }
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                showStatus('Error al cargar la componente: ' + textStatus, 'danger');
                console.error('Error al cargar la componente:', errorThrown);
            });
    }
    
    // Actualizar el API público para exponer la nueva función
    return {
        init: init,
        loadComponent: loadComponent,
        resetView: resetNetworkView,
        centerNetwork: centerNetwork,
        search: searchNode,
        downloadNetworkImage: downloadNetworkImage,
        togglePhysics: togglePhysics,
        togglePerformanceMode: togglePerformanceMode
    };
})();

// Verificación adicional para asegurarse de que el módulo está disponible
console.log("NetworkVisualizer API available:", 
    Boolean(NetworkVisualizer && 
            typeof NetworkVisualizer.resetView === 'function' && 
            typeof NetworkVisualizer.centerNetwork === 'function'));