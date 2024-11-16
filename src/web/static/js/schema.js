document.addEventListener('DOMContentLoaded', () => {
    const schemaViewer = document.getElementById('schemaViewer');
    let globalSchemaData = null;
    
    const cy = cytoscape({
        container: schemaViewer,
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#f8f9fa',
                    'border-width': 2,
                    'border-color': '#2c3e50',
                    'width': '250px',
                    'shape': 'rectangle',
                    'content': 'data(label)',
                    'text-wrap': 'wrap',
                    'text-max-width': '230px',
                    'font-family': 'monospace',
                    'font-size': '12px',
                    'padding': '15px',
                    'text-valign': 'center',
                    'text-halign': 'center',
                }
            },
            {
                // Stile per i nodi quando ci passi sopra il mouse
                selector: ':hover',
                style: {
                    'border-width': 3,
                    'border-color': '#3498db',
                    'background-color': '#ecf0f1'
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
                    'arrow-scale': 1.5
                }
            },
            {
                // Stile per le relazioni quando ci passi sopra il mouse
                selector: 'edge:active',
                style: {
                    'width': 4,
                    'line-color': '#3498db',
                    'target-arrow-color': '#3498db'
                }
            },
            {
                // Stile per evidenziare elementi connessi
                selector: '.highlighted',
                style: {
                    'border-color': '#3498db',
                    'border-width': 3,
                    'line-color': '#3498db',
                    'target-arrow-color': '#3498db'
                }
            },
            {
                // Stile per elementi non evidenziati
                selector: '.faded',
                style: {
                    'opacity': 0.4
                }
            }
        ]
    });

    function formatTableLabel(table) {
        const lines = [];
        
        // Nome della tabella in maiuscolo
        lines.push(table.name.toUpperCase());
        lines.push('═'.repeat(30)); // Separatore più evidente
        
        // Aggiunge le colonne con dettagli
        table.columns.forEach(col => {
            const flags = [];
            if (col.isPrimaryKey) flags.push('🔑');  // Chiave primaria
            if (col.isForeignKey) flags.push('🔗');  // Foreign key
            if (!col.isNullable) flags.push('*');   // Required
            
            // Formatta: nome [tipo] flags
            const type = col.type.replace(/\([^)]*\)/g, ''); // Rimuove dimensioni dal tipo (es. VARCHAR(50) -> VARCHAR)
            const flagText = flags.length ? ` ${flags.join(' ')}` : '';
            lines.push(`${col.name} [${type}]${flagText}`);
        });
        
        return lines.join('\n');
    }

    function getTableRelationships(tableName) {
        if (!globalSchemaData || !globalSchemaData.relationships) {
            return [];
        }
        
        const relationships = [];
        globalSchemaData.relationships.forEach(rel => {
            if (rel.fromTable === tableName) {
                relationships.push({
                    type: 'outgoing',
                    from: tableName,
                    to: rel.toTable,
                    columns: `${rel.fromColumn} → ${rel.toColumn}`,
                    relationType: rel.type
                });
            }
            if (rel.toTable === tableName) {
                relationships.push({
                    type: 'incoming',
                    from: rel.fromTable,
                    to: tableName,
                    columns: `${rel.fromColumn} → ${rel.toColumn}`,
                    relationType: rel.type
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
                <small>Columns: ${rel.columns}</small>
                <small>Type: ${rel.relationType}</small>
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
                }
            });
        });
    
        // Archi (relazioni)
        if (Array.isArray(schemaData.relationships)) {
            console.log('Processing relationships:', schemaData.relationships);  // debug
            schemaData.relationships.forEach((rel, index) => {
                elements.push({
                    group: 'edges',
                    data: {
                        id: `edge-${index}`,
                        source: rel.fromTable,
                        target: rel.toTable,
                        relationship: rel.type,
                        // Aggiungiamo anche le informazioni sulle colonne
                        fromColumn: rel.fromColumn,
                        toColumn: rel.toColumn
                    }
                });
            });
        }
    
        console.log('Created elements:', elements);  // debug
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
            globalSchemaData = result.data; // Salviamo i dati globalmente
            
            const elements = createGraphElements(globalSchemaData);
            
            cy.elements().remove();
            cy.add(elements);
            
            const layout = cy.layout({
                name: 'dagre',
                rankDir: 'TB',
                rankSep: 80,
                nodeSep: 50,
                padding: 50,
                animate: false,
                nodeDimensionsIncludeLabels: true
            });
            
            layout.run();
            
            setupInteractivity(cy);
            
            setTimeout(() => {
                cy.fit(50);
                cy.center();
            }, 100);
            
        } catch (error) {
            console.error('Error in graph initialization:', error);
            loadingIndicator.innerHTML = `
                <div class="error-message">
                    Failed to load schema: ${error.message}
                </div>
            `;
        } finally {
            loadingIndicator.style.display = 'none';
        }
    }

    // Inizializzazione
    initializeGraph();
});