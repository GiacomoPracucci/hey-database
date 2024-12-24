import { useState } from "react";
import { Message } from "./types";
import { MessageBubble, WelcomeMessage, ChatInput } from ".";

const ChatContainer = () => {
  const [messages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = (message: string) => {
    // Temporaneamente solo log
    console.log("Sending message:", message);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Area Messaggi */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <WelcomeMessage />

        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
      </div>

      {/* Input Area */}
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatContainer;
