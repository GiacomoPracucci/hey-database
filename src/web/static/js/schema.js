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

    function formatTableLabel(table) {
        const lines = [];
        lines.push(table.name.toUpperCase());
        lines.push('─'.repeat(16));
        
        table.columns.forEach(col => {
            if (col.isPrimaryKey || col.isForeignKey) {
                const flags = [];
                if (col.isPrimaryKey) flags.push('🔑');
                if (col.isForeignKey) flags.push('🔗');
                
                let type = col.type.replace(/\([^)]*\)/g, '').substring(0, 12);
                const flagText = flags.length ? ` ${flags.join(' ')}` : '';
                lines.push(`${col.name} [${type}]${flagText}`);
            }
        });
        
        return lines.join('\n');
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

    async function loadSchemaData() {
        try {
            const response = await fetch('/schema/api/metadata');
            if (!response.ok) {
                throw new Error(`Failed to load schema data: ${response.statusText}`);
            }
            const result = await response.json();
            return result.data;
        } catch (error) {
            console.error('Error loading schema:', error);
            throw error;
        }
    }



    async function initializeGraph() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.style.display = 'flex';

        try {
            const response = await fetch('/schema/api/metadata');
            if (!response.ok) {
                throw new Error(`Failed to load schema data: ${response.statusText}`);
            }
            const result = await response.json();

            // Debug dei dati ricevuti
            console.log('Schema data:', result.data);

            globalSchemaData = result.data;
            const elements = createGraphElements(globalSchemaData);

            cy.elements().remove();
            cy.add(elements);

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

            layout.run();

            setupInteractivity(cy);
            setupSearch();
            setupZoomControls(cy);

            setTimeout(() => {
                cy.fit(50);
                cy.center();
                loadingIndicator.style.display = 'none';
            }, 50);

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