import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // aggiugniamo la configurazione del proxy
  // serve per coordinarsi/comunicare correttamente con il server Flask
  // questo perchè avremo il server flask per il back + il server vite per il front
  server: {
    proxy: {
      "/chat": {
        target: "http://localhost:5000", // url del server flask, le chiamate a /chat vengono reindirizzate a http://localhost:5000/chat/*
        changeOrigin: true, // per evitare problemi CORS (Cross-Origin Resource Sharing) durante lo sviluppo
      },
      "/schema": {
        target: "http://localhost:5000", // idem per schema
        changeOrigin: true,
      },
    },
  },
});

/*
il CORS è un meccanismo di sicurezza che permette o blocca le richieste tra origini diverse (cross-origin) in un'applicazione web. 
Definisce se un sito web (dominio A) può fare richieste HTTP (ad esempio, chiamate API) verso un altro sito web (dominio B). 
Per motivi di sicurezza, i browser impediscono di default che il codice di una pagina web esegua richieste verso un dominio diverso da quello da cui proviene la pagina.
Il CORS è un insieme di intestazioni HTTP che vengono utilizzate per controllare l'accesso tra origini diverse e consentire o negare richieste tra queste.
*/
