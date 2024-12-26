import { PropsWithChildren } from "react";
import { Link, useLocation } from "react-router-dom";

/*
In React, ogni componente può ricevere dei "children", cioè degli elementi React che vengono passati come parte della props del componente. 
In TypeScript, è necessario tipizzare correttamente questi children.
PropsWithChildren è un tipo generico fornito da React che aggiunge automaticamente la tipizzazione per i children a un tipo di props personalizzato. 
Di solito, quando si definisce un componente con TypeScript, puoi tipizzare le props in modo esplicito, 
ma se si vuole che il componente possa anche accettare i children, usare PropsWithChildren è un modo molto comodo di farlo.
*/

const Layout = ({ children }: PropsWithChildren) => {
  const location = useLocation();

  // Helper per determinare se un link è attivo
  const isActive = (path: string) => location.pathname === path;

  // Helper per il titolo della pagina
  const getPageTitle = () => {
    switch (location.pathname) {
      case "/":
        return "Welcome";
      case "/chat":
        return "SQL Chat";
      case "/schema":
        return "Entity Relationship Diagram";
      default:
        return "";
    }
  };

  return (
    <div className="w-full h-full">
      <header className="fixed top-0 left-0 right-0 bg-brand-500 bg-blue-900 shadow-md">
        {/* Navbar principale */}
        <nav className="h-[60px] max-w-[1500px] mx-auto px-6 flex items-center">
          {/* Brand */}
          <Link
            to="/"
            className="flex items-center text-white text-xl font-medium mr-12"
          >
            <i className="fas fa-database mr-3 text-[1.3rem]"></i>
            <span className="brand-text">Hey, Database!</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-2 mr-auto">
            <Link
              to="/chat"
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors
                  ${
                    isActive("/chat")
                      ? "text-white bg-blue-800"
                      : "text-blue-300 hover:text-white hover:bg-blue-800"
                  }`}
            >
              <i className="fas fa-comments"></i>
              <span>Chat</span>
            </Link>
            <Link
              to="/schema"
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors
                  ${
                    isActive("/schema")
                      ? "text-white bg-blue-800"
                      : "text-blue-300 hover:text-white hover:bg-blue-800"
                  }`}
            >
              <i className="fas fa-project-diagram"></i>
              <span>Schema</span>
            </Link>
          </div>

          {/* Page Title */}
          <div className="text-white text-lg font-medium mr-6 pr-6 border-r border-blue-800">
            {getPageTitle()}
          </div>

          {/* Placeholder for page-specific actions */}
          <div className="flex items-center gap-3">
            {/* Le azioni contestuali verranno inserite qui dai componenti figli */}
          </div>
        </nav>

        {/* Optional contextual toolbar */}
        {/* Verrà gestito dai componenti figli */}
      </header>

      {/* Main Content */}
      <main className="w-full h-full pt-[15px]">{children}</main>
    </div>
  );
};

export default Layout;
