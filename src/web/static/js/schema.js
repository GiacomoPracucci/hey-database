document.addEventListener('DOMContentLoaded', () => {
    const schemaViewer = document.getElementById('schemaViewer');
    let globalSchemaData = null;
    
    const cy = cytoscape({
        container: schemaViewer,
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#ffffff',
                    'border-width': 2,
                    'border-color': '#3498db',
                    'width': '180px',
                    'height': '60px',
                    'shape': 'roundrectangle',
                    'content': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif',
                    'font-size': '14px',
                    'font-weight': '500',
                    'text-wrap': 'wrap',
                    'text-max-width': '160px',
                    'padding': '10px',
                    'color': '#2c3e50',
                    'text-outline-color': '#ffffff',
                    'text-outline-width': 1,
                    'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
                    'overlay-opacity': 0
                }
            },
            {
                selector: 'node:hover',
                style: {
                    'border-width': 3,
                    'border-color': '#2980b9',
                    'background-color': '#f8f9fa',
                    'transition-property': 'border-width, border-color, background-color',
                    'transition-duration': '0.2s'
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'border-width': 3,
                    'border-color': '#2980b9',
                    'background-color': '#ebf5fb',
                    'box-shadow': '0 0 0 4px rgba(52, 152, 219, 0.2)'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#95a5a6',
                    'target-arrow-color': '#95a5a6',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'arrow-scale': 1.5,
                    'line-style': 'solid',
                    'target-distance-from-node': '10px',
                    'source-distance-from-node': '10px'
                }
            },
            {
                selector: 'edge:hover',
                style: {
                    'width': 3,
                    'line-color': '#3498db',
                    'target-arrow-color': '#3498db',
                    'transition-property': 'width, line-color, target-arrow-color',
                    'transition-duration': '0.2s',
                    'z-index': 999
                }
            },
            {
                selector: '.highlighted',
                style: {
                    'border-color': '#2980b9',
                    'border-width': 3,
                    'line-color': '#3498db',
                    'target-arrow-color': '#3498db',
                    'z-index': 999,
                    'transition-property': 'all',
                    'transition-duration': '0.2s'
                }
            },
            {
                selector: '.faded',
                style: {
                    'opacity': 0.4,
                    'transition-property': 'opacity',
                    'transition-duration': '0.2s'
                }
            }
        ]
    });

    function logObject(obj) {
        console.log(JSON.stringify(obj, null, 2));
    }

    function formatTableLabel(table) {
        const lines = [];
        
        // Nome della tabella in maiuscolo
        lines.push(table.name.toUpperCase());
        lines.push('─'.repeat(16)); // Separatore più corto
        
        // Aggiunge solo le colonne che sono chiavi primarie o chiavi esterne
        table.columns.forEach(col => {
            if (col.isPrimaryKey || col.isForeignKey) {
                const flags = [];
                if (col.isPrimaryKey) flags.push('🔑');  // Chiave primaria
                if (col.isForeignKey) flags.push('🔗');  // Foreign key
                
                // Formatta: nome [tipo] flags
                let type = col.type.replace(/\([^)]*\)/g, '').substring(0, 4); // Rimuove dimensioni dal tipo (es. VARCHAR(50) -> VARCHAR)
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
                        ${table.columns.map(col => `
                            <tr>
                                <td>${col.name}</td>
                                <td><code>${col.type}</code></td>
                                <td>
                                    ${col.isPrimaryKey ? '<span class="badge pk">PK</span>' : ''}
                                    ${col.isForeignKey ? '<span class="badge fk">FK</span>' : ''}
                                    ${!col.isNullable ? '<span class="badge required">Required</span>' : ''}
                                </td>
                            </tr>
                        `).join('')}
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

    // Il resto delle funzioni rimane lo stesso, ma aggiorniamo la creazione degli elementi
    function createGraphElements(schemaData) {
        if (!schemaData || !Array.isArray(schemaData.tables)) {
            throw new Error('Invalid schema data structure');
        }
    
        const elements = [];
    
        // Nodi (tabelle)
        schemaData.tables.forEach(table => {
            elements.push({
                group: 'nodes',
                data: {
                    id: table.name,
                    label: formatTableLabel(table),
                    tableData: table
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



    async function initializeGraph() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.style.display = 'flex';
        
        try {
            const response = await fetch('/schema/api/metadata');
            if (!response.ok) {
                throw new Error(`Failed to load schema data: ${response.statusText}`);
            }
            const result = await response.json();
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
            
            setTimeout(() => {
                cy.fit(50);
                cy.center();
                loadingIndicator.style.display = 'none';
            }, 600);
            
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