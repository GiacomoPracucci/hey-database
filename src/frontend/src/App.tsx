import { Routes, Route } from "react-router-dom";
import { Layout } from "./components/layout";
import HomePage from "./pages/HomePage";
import ChatPage from "./pages/ChatPage";
import SchemaPage from "./pages/SchemaPage";
import "./App.css";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/schema" element={<SchemaPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
