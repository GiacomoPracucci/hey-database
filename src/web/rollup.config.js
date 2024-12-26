import resolve from "@rollup/plugin-node-resolve";
import terser from "@rollup/plugin-terser";

const external = ["cytoscape", "cytoscape-dagre", "dagre"];

// Configurazione di base per entrambe le pagine
const commonConfig = {
  plugins: [
    resolve(),
    terser({
      format: {
        comments: false,
      },
    }),
  ],
};

export default [
  // Bundle per la pagina chat
  {
    ...commonConfig,
    input: "static/js/pages/chat-page.js",
    output: {
      dir: "static/dist",
      format: "es",
      sourcemap: true,
      entryFileNames: "chat.bundle.js",
    },
  },
  // Bundle per la pagina schema
  {
    ...commonConfig,
    input: "static/js/pages/schema-page.js",
    external,
    output: {
      dir: "static/dist",
      format: "es",
      sourcemap: true,
      entryFileNames: "schema.bundle.js",
      globals: {
        cytoscape: "cytoscape",
        "cytoscape-dagre": "cytoscapeDagre",
        dagre: "dagre",
      },
    },
  },
];
