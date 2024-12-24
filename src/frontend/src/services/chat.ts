import {
  ChatMessage,
  ChatResponse,
  FeedbackRequest,
  FeedbackResponse,
} from "../types";

class ChatService {
  private static readonly CHAT_ENDPOINT = "/chat/api/chat";
  private static readonly FEEDBACK_ENDPOINT = "/chat/api/feedback";

  /**
   * Invia un messaggio all'API della chat
   * @param message - Il messaggio da inviare
   * @returns La risposta dal server
   * @throws Error se la chiamata fallisce
   */
  static async sendMessage(message: string): Promise<ChatResponse> {
    try {
      console.log("Sending message to API:", message);
      const response = await fetch(this.CHAT_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message } as ChatMessage),
      });

      console.log("Response status:", response.status);
      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response:", errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data as ChatResponse;
    } catch (error) {
      console.error("Error in sendMessage:", error);
      throw error instanceof Error
        ? error
        : new Error("Unknown error occurred while sending message");
    }
  }

  /**
   * Invia feedback positivo per una risposta
   * @param feedback - I dettagli del feedback
   * @returns True se il feedback è stato salvato con successo
   * @throws Error se la chiamata fallisce
   */
  static async sendFeedback(feedback: FeedbackRequest): Promise<boolean> {
    try {
      const response = await fetch(this.FEEDBACK_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(feedback),
      });

      const data = (await response.json()) as FeedbackResponse;

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Error saving feedback");
      }

      return true;
    } catch (error) {
      throw error instanceof Error
        ? error
        : new Error("Unknown error occurred while sending feedback");
    }
  }
}

export default ChatService;
