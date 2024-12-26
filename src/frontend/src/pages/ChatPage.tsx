import { ChatContainer } from "../components/chat";

export default function ChatPage() {
  return (
    // contenitore principale che occupa tutto lo spazio rimanente sotto la navbar
    <div className="flex-1 h-full flex flex-col p-6">
      <ChatContainer />
    </div>
  );
}
