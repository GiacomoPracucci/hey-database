import { useState } from "react";

const ChatContainer = () => {
  // stato temporaneo per testing layout
  const [messages] = useState<any[]>([]);

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Area Messaggi */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {/* Messaggio di benvenuto - poi diventerà un componente separato */}
        <div className="flex justify-center">
          <div className="bg-white p-8 rounded-lg border border-gray-200 text-center max-w-fit">
            <h3 className="text-xl font-semibold text-blue-900 mb-4">
              👋 Welcome to your SQL Assistant!
            </h3>
            <p className="text-gray-700 mb-5">
              I'm here to help you explore and query the database.
            </p>
            <ul className="space-y-3 text-left mb-5">
              <li className="flex items-center space-x-2 text-gray-600">
                <span>•</span>
                <span>Ask for information about available data</span>
              </li>
              <li className="flex items-center space-x-2 text-gray-600">
                <span>•</span>
                <span>Request specific SQL queries</span>
              </li>
              <li className="flex items-center space-x-2 text-gray-600">
                <span>•</span>
                <span>Explore relationships between tables</span>
              </li>
            </ul>
            <p className="text-blue-600 text-sm">
              💡 Tip: start by asking "Show me available tables" or "What data
              can I query?"
            </p>
          </div>
        </div>

        {/* Area per i messaggi dinamici - temporaneamente vuota */}
        {messages.map(() => null)}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-6">
        <div className="flex gap-3 max-w-4xl mx-auto">
          <textarea
            placeholder="Write your question here..."
            rows={1}
            className="flex-1 resize-none rounded-lg border border-gray-200 p-3 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
          />
          <button className="bg-blue-600 text-white px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
            <i className="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatContainer;
