import { useEffect, useRef } from "react";
import { MessageBubble, WelcomeMessage, ChatInput } from ".";
import useChat from "../../hooks/useChat";
import { FeedbackRequest } from "../../types";

const ChatContainer = () => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, isLoading, error, sendMessage, sendFeedback } = useChat();

  // Auto-scroll quando arrivano nuovi messaggi
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    await sendMessage(message);
  };

  const handleFeedback = async (feedback: FeedbackRequest) => {
    await sendFeedback(feedback);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Area Messaggi */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <WelcomeMessage />

        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onFeedback={handleFeedback}
          />
        ))}

        {/* Elemento per l'auto-scroll */}
        <div ref={messagesEndRef} />
      </div>

      {/* Mostra errore se presente */}
      {error && (
        <div className="px-6 py-2 bg-red-50 border-t border-red-100">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* Input Area */}
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatContainer;
