import { useRef, useEffect } from "react";
import { MessageBubble, WelcomeMessage, ChatInput } from ".";
import useChat from "../../hooks/useChat";

const ChatContainer = () => {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    sendFeedback,
    clearMessages,
  } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    await sendMessage(message);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header con bottone clear */}
      <div className="p-4 border-b border-gray-200 flex justify-between items-center">
        <div></div> {/* Spacer per mantenere il bottone a destra */}
        <button
          onClick={clearMessages}
          className="text-gray-500 hover:text-gray-700 transition-colors p-2 rounded-lg hover:bg-gray-100"
          title="Clear chat"
        >
          <i className="fas fa-trash"></i>
        </button>
      </div>

      {/* Area messaggi */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <WelcomeMessage />

        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onFeedback={sendFeedback}
          />
        ))}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="px-6 py-2 bg-red-50 border-t border-red-100">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatContainer;
