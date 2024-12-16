document.addEventListener('DOMContentLoaded', () => {
    const schemaViewer = document.getElementById('schemaViewer');
    let globalSchemaData = null;

    const schemaStyles = [
        {
            selector: 'node',
            style: {
                'background-color': '#ffffff',
                'border-width': 1,
                'border-color': '#e2e8f0',
                'border-opacity': 1,
                'shape': 'roundrectangle',
                'width': 'label',
                'height': 'label',
                'padding': '20px',
                'text-wrap': 'wrap',
                'text-max-width': '280px',
                'text-valign': 'center',
                'text-halign': 'center',
                'font-family': 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
                'font-size': '14px',
                'color': '#2d3748',
                'text-margin-y': 5,
                'compound-sizing-wrt-labels': 'include',
                'min-width': '200px',
                'min-height': '50px',
                'corner-radius': '8px',
                'background-opacity': 1,
                'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
                'label': function(ele) {
                    const data = ele.data();
                    if (!data.tableData) return '';

                    const lines = [];
                    // Table header
                    lines.push(data.tableData.name.toUpperCase());
                    lines.push('─'.repeat(Math.min(data.tableData.name.length * 1.5, 30)));

                    // Filtra solo PK e FK
                    if (data.tableData.columns) {
                        const keyColumns = data.tableData.columns.filter(col =>
                            col.isPrimaryKey || col.isForeignKey
                        );

                        keyColumns.forEach(col => {
                            let line = col.name;

                            // Add key indicators
                            if (col.isPrimaryKey) line += ' 🔑';
                            if (col.isForeignKey) line += ' 🔗';

                            // Add type with clean format
                            const cleanType = col.type.replace(/\([^)]*\)/g, '').toLowerCase();
                            line += ` [${cleanType}]`;

                            lines.push(line);
                        });

                        // Add indicator if there are more columns
                        const hiddenColumns = data.tableData.columns.length - keyColumns.length;
                        if (hiddenColumns > 0) {
                            lines.push(`... +${hiddenColumns} more columns`);
                        }
                    }

                    return lines.join('\n');
                }
            }
        },
        {
            selector: 'edge',
            style: {
                'width': 1.5,
                'line-color': '#a0aec0',
                'line-style': 'dashed',
                'curve-style': 'bezier',
                'target-arrow-color': '#a0aec0',
                'target-arrow-shape': 'triangle',
                'arrow-scale': 1,
                'source-endpoint': 'outside-to-node',
                'target-endpoint': 'outside-to-node'
            }
        },
        {
            selector: '.highlighted',
            style: {
                'border-color': '#3182ce',
                'border-width': 2,
                'border-opacity': 1,
                'background-color': '#ebf8ff',
                'transition-property': 'all',
                'transition-duration': '0.2s'
            }
        },
        {
            selector: ':selected',
            style: {
                'border-color': '#3182ce',
                'border-width': 2,
                'border-opacity': 1,
                'background-color': '#ebf8ff',
                'box-shadow': '0 0 0 3px rgba(49, 130, 206, 0.3)'
            }
        },
        {
            selector: 'node:hover',
            style: {
                'border-color': '#3182ce',
                'border-width': 1.5,
                'background-color': '#f7fafc',
                'transition-property': 'all',
                'transition-duration': '0.2s'
            }
        },
        {
            selector: '.faded',
            style: {
                'opacity': 0.25
            }
        },
        {
            selector: '.search-match',
            style: {
                'border-color': '#3182ce',
                'border-width': 2,
                'background-color': '#ebf8ff',
                'z-index': 999
            }
        }
    ];

    function createGraphElements(schemaData) {
        if (!schemaData || !Array.isArray(schemaData.tables)) {
            throw new Error('Invalid schema data structure');
        }

        const elements = [];

        // Pre-process per identificare le foreign keys
        const foreignKeys = new Set();
        schemaData.tables.forEach(table => {
            if (Array.isArray(table.relationships)) {
                table.relationships.forEach(rel => {
                    rel.fromColumns.forEach(col => {
                        foreignKeys.add(`${table.name}.${col}`);
                    });
                });
            }
        });

        // Nodi (tabelle)
        schemaData.tables.forEach(table => {
            // Aggiungiamo l'informazione sulle FK alle colonne
            const tableData = {...table};
            if (tableData.columns) {
                tableData.columns = tableData.columns.map(col => ({
                    ...col,
                    isForeignKey: foreignKeys.has(`${table.name}.${col.name}`)
                }));
            }

            elements.push({
                group: 'nodes',
                data: {
                    id: table.name,
                    tableData: tableData
                },
                classes: ['table-node']
            });

            // Relazioni
            if (Array.isArray(table.relationships)) {
                table.relationships.forEach((rel, index) => {
                    elements.push({
                        group: 'edges',
                        data: {
                            id: `edge-${table.name}-${rel.toTable}-${index}`,
                            source: table.name,
                            target: rel.toTable,
                            relationship: rel.type,
                            fromColumns: rel.fromColumns,
                            toColumns: rel.toColumns
                        }
                    });
                });
            }
        });

        return elements;
    }

    // Inizializzazione di Cytoscape
    const cy = cytoscape({
        container: schemaViewer,
        style: schemaStyles,
        wheelSensitivity: 0.2,
    });

    // Funzione di ricerca
    function searchTables(searchTerm) {
        if (!searchTerm) {
            // Reset della visualizzazione se la ricerca è vuota
            cy.elements().removeClass('faded highlighted search-match');
            cy.elements().style('opacity', 1);
            return;
        }

        searchTerm = searchTerm.toLowerCase();
        
        // Trova i nodi che corrispondono al termine di ricerca
        const matchingNodes = cy.nodes().filter(node => {
            const tableData = node.data('tableData');
            if (!tableData) return false;
            
            // Cerca nel nome della tabella
            if (tableData.name.toLowerCase().includes(searchTerm)) return true;
            
            // Cerca nei nomi delle colonne e nei tipi
            return tableData.columns.some(col => 
                col.name.toLowerCase().includes(searchTerm) ||
                col.type.toLowerCase().includes(searchTerm)
            );
        });

        if (matchingNodes.length > 0) {
            // Evidenzia i nodi corrispondenti e le loro relazioni
            cy.elements().addClass('faded').style('opacity', 0.2);
            matchingNodes.removeClass('faded').addClass('search-match').style('opacity', 1);
            
            // Evidenzia anche le relazioni dirette tra i nodi corrispondenti
            const connectedEdges = matchingNodes.edgesWith(matchingNodes);
            connectedEdges.removeClass('faded').style('opacity', 1);
            
            // Centra la vista sui nodi trovati
            cy.animate({
                fit: {
                    eles: matchingNodes,
                    padding: 50
                },
                duration: 500,
                easing: 'ease-out'
            });
        }
    }

    // Setup del campo di ricerca
    function setupSearch() {
        // Usiamo l'input esistente nell'HTML
        const searchInput = document.getElementById('schemaSearch');
        
        if (searchInput) {
            // Event listener con debounce per la ricerca
            let debounceTimer;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    searchTables(e.target.value.trim());
                }, 300);
            });

            // Event listener per il reset della ricerca con il tasto ESC
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    searchInput.value = '';
                    searchTables('');
                    searchInput.blur();
                }
            });
        }
    }

    function setupZoomControls(cy) {
        // Zoom step (quanto zoom per click - 1.2 significa 20% in più o in meno)
        const ZOOM_STEP = 1.2;
        
        // Zoom In
        document.getElementById('zoomIn').addEventListener('click', () => {
            cy.animate({
                zoom: cy.zoom() * ZOOM_STEP,
                duration: 200,
                easing: 'ease-out'
            });
        });
        
        // Zoom Out
        document.getElementById('zoomOut').addEventListener('click', () => {
            cy.animate({
                zoom: cy.zoom() / ZOOM_STEP,
                duration: 200,
                easing: 'ease-out'
            });
        });
        
        // Fit to View
        document.getElementById('zoomFit').addEventListener('click', () => {
            cy.animate({
                fit: {
                    padding: 50
                },
                duration: 300,
                easing: 'ease-out'
            });
        });
    }

 
    function getTableRelationships(tableName) {
        if (!globalSchemaData || !Array.isArray(globalSchemaData.tables)) {
            return [];
        }
        
        const relationships = [];
        
        // Cerca la tabella corrente
        const currentTable = globalSchemaData.tables.find(t => t.name === tableName);
        
        // Aggiungi relazioni in uscita
        if (currentTable && Array.isArray(currentTable.relationships)) {
            currentTable.relationships.forEach(rel => {
                relationships.push({
                    type: 'outgoing',
                    from: tableName,
                    to: rel.toTable,
                    fromColumns: rel.fromColumns,
                    toColumns: rel.toColumns
                });
            });
        }
        
        // Cerca relazioni in entrata da altre tabelle
        globalSchemaData.tables.forEach(table => {
            if (Array.isArray(table.relationships)) {
                table.relationships.forEach(rel => {
                    if (rel.toTable === tableName) {
                        relationships.push({
                            type: 'incoming',
                            from: table.name,
                            to: tableName,
                            fromColumns: rel.fromColumns,
                            toColumns: rel.toColumns
                        });
                    }
                });
            }
        });
        
        return relationships;
    }

    function formatRelationship(rel) {
        const arrow = rel.type === 'outgoing' ? '→' : '←';
        const direction = rel.type === 'outgoing' ? 
            `${rel.from} ${arrow} ${rel.to}` :
            `${rel.from} ${arrow} ${rel.to}`;
        
        return `
            <div class="relationship-item">
                <div>${direction}</div>
                <small>Columns: ${rel.fromColumns.join(', ')} → ${rel.toColumns.join(', ')}</small>
                <small>Type: N-1</small>
            </div>
        `;
    }

    function updateTableDetails(node) {
        const table = node.data('tableData');
        const detailsPanel = document.getElementById('tableDetails');
        const detailsTitle = detailsPanel.querySelector('.details-title');
        const detailsContent = detailsPanel.querySelector('.details-content');
        const relationships = getTableRelationships(table.name);

        // Aggiorna il titolo
        detailsTitle.textContent = table.name;

        // Aggiorna il contenuto
        detailsContent.innerHTML = `
            <div class="section">
                <h4>Columns</h4>
                <table class="details-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Properties</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${table.columns.map(col => {
            const properties = [];
            if (col.isPrimaryKey) properties.push('<span class="badge pk">PK</span>');
            if (col.isForeignKey) properties.push('<span class="badge fk">FK</span>');
            if (!col.isNullable) properties.push('<span class="badge required">Required</span>');

            return `
                                <tr class="${col.isPrimaryKey || col.isForeignKey ? 'key-column' : ''}">
                                    <td>${col.name}</td>
                                    <td><code>${col.type}</code></td>
                                    <td>${properties.join(' ')}</td>
                                </tr>
                            `;
        }).join('')}
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h4>Relationships</h4>
                <div class="relationships-list">
                    ${relationships.length ?
            relationships.map(rel => formatRelationship(rel)).join('') :
            '<div class="relationship-item">No relationships found</div>'
        }
                </div>
            </div>
            
            <div class="section">
                <h4>Sample Query</h4>
                <div class="query-container">
                    <pre><code>SELECT *
FROM ${table.name}
LIMIT 5;</code></pre>
                </div>
            </div>
        `;

        detailsPanel.classList.remove('hidden');
    }

    // Aggiungi questi stili CSS dinamicamente
    const style = document.createElement('style');
    style.textContent = `
        .key-column {
            background-color: #f7fafc;
        }
        
        .details-table tr.key-column td {
            font-weight: 500;
        }
    `;
    document.head.appendChild(style);

    function setupInteractivity(cy) {
        // Hover effects
        cy.on('mouseover', 'node', function(e) {
            const node = e.target;
            const connectedEdges = node.connectedEdges();
            const connectedNodes = connectedEdges.connectedNodes();
            
            cy.elements()
              .difference(connectedEdges.union(connectedNodes).union(node))
              .addClass('faded');
            
            connectedEdges.addClass('highlighted');
            connectedNodes.addClass('highlighted');
        });

        cy.on('mouseout', 'node', function(e) {
            cy.elements().removeClass('faded highlighted');
        });

        // Click su nodo per mostrare i dettagli
        cy.on('click', 'node', function(e) {
            const node = e.target;
            updateTableDetails(node);
        });

        // Handler per chiusura pannello dettagli
        const closeButton = document.querySelector('.table-details .close-button');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                document.getElementById('tableDetails').classList.add('hidden');
            });
        }
    }



    // Funzioni di analisi della rete
    function analyzeNetworkMetrics(cy) {
        // Calcolo della degree centrality
        const degreeCentrality = {};
        cy.nodes().forEach(node => {
            degreeCentrality[node.id()] = node.degree();
        });

        // Calcolo della betweenness centrality
        const betweennessCentrality = cy.elements().bc();

        // Calcolo delle componenti connesse
        const components = [];
        let unvisited = cy.nodes().toArray();

        while (unvisited.length > 0) {
            const component = [];
            const queue = [unvisited[0]];

            while (queue.length > 0) {
                const node = queue.shift();
                if (unvisited.includes(node)) {
                    component.push(node);
                    unvisited = unvisited.filter(n => n !== node);

                    node.neighborhood().nodes().forEach(neighbor => {
                        if (unvisited.includes(neighbor)) {
                            queue.push(neighbor);
                        }
                    });
                }
            }

            components.push(component);
        }

        return {
            degreeCentrality,
            betweennessCentrality,
            components
        };
    }

    // Layout intelligente basato sulle metriche
    function applySmartLayout(cy) {
        const metrics = analyzeNetworkMetrics(cy);
        const components = metrics.components;

        // Resetta gli stili prima di applicare il nuovo layout
        cy.nodes().style({
            'border-width': 1,
            'border-color': '#e2e8f0'
        });

        // Se abbiamo una singola componente grande
        if (components.length === 1 && components[0].length > 10) {
            // Usa layout gerarchico per grafi grandi e connessi
            cy.layout({
                name: 'dagre',
                rankDir: 'TB',
                rankSep: 100,
                nodeSep: 80,
                padding: 50,
                animate: true,
                animationDuration: 500,
                fit: true
            }).run();
        } else if (components.length > 1) {
            // Per multiple componenti, disponi ogni componente separatamente
            components.forEach(component => {
                const componentCy = cy.collection(component);

                componentCy.layout({
                    name: 'cose',
                    animate: true,
                    animationDuration: 500,
                    fit: false,
                    padding: 50,
                    nodeRepulsion: 400000,
                    componentSpacing: 150
                }).run();
            });

            // Dopo aver disposto le componenti, fai il fit della vista
            setTimeout(() => {
                cy.fit(50);
            }, 600);
        } else {
            // Per grafi piccoli usa CoSE
            cy.layout({
                name: 'cose',
                animate: true,
                animationDuration: 500,
                fit: true,
                padding: 50,
                nodeRepulsion: 400000
            }).run();
        }

        // Evidenzia i nodi più connessi
        const maxDegree = Math.max(...Object.values(metrics.degreeCentrality));
        cy.nodes().forEach(node => {
            const degree = metrics.degreeCentrality[node.id()];
            const intensity = degree / maxDegree;
            if (intensity > 0.7) { // Solo per i nodi più connessi
                node.style({
                    'border-width': 2,
                    'border-color': '#3182ce'
                });
            }
        });
    }

    // Funzione per evidenziare i nodi centrali
    function highlightCentralNodes(cy) {
        const metrics = analyzeNetworkMetrics(cy);

        // Normalizza i valori di betweenness
        const betweennessValues = Object.values(metrics.betweennessCentrality.betweenness());
        const maxBetweenness = Math.max(...betweennessValues);

        cy.nodes().forEach(node => {
            const betweenness = metrics.betweennessCentrality.betweenness(node);
            const normalizedBetweenness = betweenness / maxBetweenness;

            // Applica stili basati sulla centralità
            node.style({
                'border-width': 1 + (normalizedBetweenness * 2),
                'border-color': `rgb(49, 130, 206, ${0.5 + normalizedBetweenness * 0.5})`
            });
        });
    }

    // Aggiungi controlli per la visualizzazione
    function addVisualizationControls() {
        try {
            // Verifica se esiste già un contenitore per i controlli
            let controlsContainer = document.querySelector('.context-toolbar');

            // Se non esiste, crealo
            if (!controlsContainer) {
                controlsContainer = document.createElement('div');
                controlsContainer.className = 'context-toolbar';

                // Trova un punto appropriato dove inserirlo
                const schemaViewer = document.getElementById('schemaViewer');
                if (!schemaViewer) {
                    console.error('Schema viewer element not found');
                    return; // Exit early if we can't find the schema viewer
                }

                schemaViewer.parentNode.insertBefore(controlsContainer, schemaViewer);
            }

            // Crea il contenitore dei controlli di visualizzazione
            const controls = document.createElement('div');
            controls.className = 'visualization-controls';

            // Prepara il contenuto HTML
            controls.innerHTML = `
            <div class="control-group">
                <button id="autoArrangeBtn" class="btn btn-secondary">
                    <i class="fas fa-project-diagram"></i>
                    Auto Arrange
                </button>
                <select id="layoutSelect" class="select">
                    <option value="dagre">Hierarchical View</option>
                    <option value="cose">Organic View</option>
                    <option value="concentric">Circular View</option>
                    <option value="grid">Grid View</option>
                </select>
            </div>
        `;

            // Aggiungi i controlli al contenitore
            controlsContainer.appendChild(controls);

            // Aggiungi gli stili
            const style = document.createElement('style');
            style.textContent = `
            .context-toolbar {
                display: flex;
                align-items: center;
                padding: 0.5rem 1.5rem;
                background-color: var(--background-color);
                border-bottom: 1px solid var(--border-color);
            }
            
            .visualization-controls {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .control-group {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .btn-secondary {
                background-color: var(--background-color);
                border: 1px solid var(--border-color);
                padding: 0.5rem 1rem;
                border-radius: 0.375rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                cursor: pointer;
                transition: all 0.2s;
                color: var(--text-color);
            }
            
            .btn-secondary:hover {
                background-color: var(--hover-color);
                border-color: var(--primary-color);
            }
            
            .select {
                padding: 0.5rem;
                border: 1px solid var(--border-color);
                border-radius: 0.375rem;
                background-color: var(--background-color);
                min-width: 200px;
                color: var(--text-color);
            }

            .select:focus {
                outline: none;
                border-color: var(--primary-color);
            }
        `;
            document.head.appendChild(style);

            // Aggiungi gli event listener dopo che gli elementi sono stati aggiunti al DOM
            const autoArrangeBtn = document.getElementById('autoArrangeBtn');
            const layoutSelect = document.getElementById('layoutSelect');

            if (autoArrangeBtn) {
                autoArrangeBtn.addEventListener('click', () => {
                    applySmartLayout(cy);
                });
            } else {
                console.error('Auto Arrange button not found');
            }

            if (layoutSelect) {
                layoutSelect.addEventListener('change', (e) => {
                    const layoutName = e.target.value;
                    applyLayout(cy, layoutName);
                });
            } else {
                console.error('Layout select not found');
            }

        } catch (error) {
            console.error('Error adding visualization controls:', error);
        }
    }


    // Funzione per applicare un layout specifico
    function applyLayout(cy, layoutName) {
        const layoutConfig = {
            dagre: {
                name: 'dagre',
                rankDir: 'TB',
                rankSep: 100,
                nodeSep: 80,
                padding: 50
            },
            cose: {
                name: 'cose',
                idealEdgeLength: 150,
                nodeOverlap: 20,
                refresh: 20,
                padding: 30,
                randomize: false,
                componentSpacing: 150,
                nodeRepulsion: 400000,
                edgeElasticity: 100,
                nestingFactor: 5,
                gravity: 80,
                numIter: 1000
            },
            concentric: {
                name: 'concentric',
                minNodeSpacing: 100,
                concentric: node => node.degree(),
                levelWidth: () => 1
            },
            grid: {
                name: 'grid',
                padding: 50
            }
        };

        const layout = cy.layout({
            ...layoutConfig[layoutName],
            animate: true,
            animationDuration: 500,
            animationEasing: 'ease-in-out'
        });

        layout.run();
    }


    async function initializeGraph() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.style.display = 'flex';

        try {
            const result = await fetch('/schema/api/metadata');
            if (!result.ok) {
                throw new Error(`Failed to load schema data: ${result.statusText}`);
            }
            const data = await result.json();

            globalSchemaData = data.data;
            const elements = createGraphElements(globalSchemaData);

            cy.elements().remove();
            cy.add(elements);

            // Prima esegui il layout
            const layout = cy.layout({
                name: 'dagre',
                rankDir: 'TB',
                rankSep: 100,
                nodeSep: 80,
                padding: 50,
                animate: true,
                animationDuration: 500,
                animationEasing: 'ease-in-out',
                nodeDimensionsIncludeLabels: true
            });

            await layout.run();

            // Poi aggiungi i controlli
            setupInteractivity(cy);
            setupSearch();
            setupZoomControls(cy);
            addVisualizationControls();  // Ora dovrebbe funzionare correttamente

            cy.fit(50);
            cy.center();
            loadingIndicator.style.display = 'none';

        } catch (error) {
            console.error('Error in graph initialization:', error);
            loadingIndicator.innerHTML = `
            <div class="error-message">
                Failed to load schema: ${error.message}
            </div>
        `;
        }
    }

    // Inizializzazione
    initializeGraph();
});