import { Routes, Route } from "react-router-dom"; // gestiamo il routing multipagina tramite react router dom
import HomePage from "./pages/HomePage";
import ChatPage from "./pages/ChatPage";
import SchemaPage from "./pages/SchemaPage";
import "./App.css";

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/chat" element={<ChatPage />} />
      <Route path="/schema" element={<SchemaPage />} />
    </Routes>
  );
}

export default App;
