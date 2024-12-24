import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/chat/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
        secure: false,
      },
      "/schema/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});

/*

  // aggiugniamo la configurazione del proxy
  // serve per coordinarsi/comunicare correttamente con il server Flask
  // questo perchè avremo il server flask per il back + il server vite per il front
il CORS è un meccanismo di sicurezza che permette o blocca le richieste tra origini diverse (cross-origin) in un'applicazione web. 
Definisce se un sito web (dominio A) può fare richieste HTTP (ad esempio, chiamate API) verso un altro sito web (dominio B). 
Per motivi di sicurezza, i browser impediscono di default che il codice di una pagina web esegua richieste verso un dominio diverso da quello da cui proviene la pagina.
Il CORS è un insieme di intestazioni HTTP che vengono utilizzate per controllare l'accesso tra origini diverse e consentire o negare richieste tra queste.
*/
