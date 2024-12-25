import { useRef, useEffect } from "react";
import { MessageBubble, WelcomeMessage, ChatInput, TypingIndicator } from ".";
import Toast from "../common/Toast";
import useChat from "../../hooks/useChat";
import useToast from "../../hooks/useToast";
import { FeedbackRequest } from "../../types";

const ChatContainer = () => {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    sendFeedback,
    clearMessages,
  } = useChat();
  const { toasts, showToast, removeToast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll quando arrivano nuovi messaggi o durante il loading
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSendMessage = async (message: string) => {
    await sendMessage(message);
  };

  const handleFeedback = async (feedback: FeedbackRequest) => {
    try {
      await sendFeedback(feedback);
      showToast("Thank you for your feedback!", "success", "fa-check");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";

      if (errorMessage.includes("vector_store_disabled")) {
        showToast(
          "Please enable vectorstore in config.yaml to use this feature",
          "warning",
          "fa-exclamation-triangle"
        );
      } else {
        showToast(errorMessage, "error", "fa-times");
      }
    }
  };

  return (
    <>
      <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        {/* Header con bottone clear */}
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <div></div>
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
              onFeedback={handleFeedback}
            />
          ))}

          {isLoading && <TypingIndicator />}

          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className="px-6 py-2 bg-red-50 border-t border-red-100">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-gray-200">
          <div className="px-6 py-4">
            <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
          </div>
        </div>
      </div>

      {/* Toast notifications */}
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          icon={toast.icon}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </>
  );
};

export default ChatContainer;
