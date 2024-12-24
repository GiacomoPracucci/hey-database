import { Message } from "./types";
import { FeedbackRequest } from "../../types";

interface MessageBubbleProps {
  message: Message;
  onFeedback?: (feedback: FeedbackRequest) => Promise<void>;
}

const MessageBubble = ({ message, onFeedback }: MessageBubbleProps) => {
  // se è un messaggio utente
  if (message.type === "user") {
    return (
      <div className="flex justify-end">
        <div className="bg-blue-600 text-white rounded-xl rounded-tr-none px-4 py-3 max-w-[85%] shadow-sm">
          {message.content}
        </div>
      </div>
    );
  }

  // se è un bot message è più complicata la questione
  return (
    <div className="flex justify-start">
      <div className="bg-gray-50 rounded-xl rounded-tl-none px-4 py-3 max-w-[85%] shadow-sm">
        {/* Se c'è un errore */}
        {message.error && (
          <div className="bg-red-50 border border-red-100 rounded-lg p-4 mb-4">
            <div className="flex items-start">
              <div className="text-red-500 text-xl">❌</div>
              <div className="ml-3">
                <div className="text-red-800 font-medium mb-1">
                  Si è verificato un errore:
                </div>
                <div className="text-red-600">{message.error}</div>
                {message.query && (
                  <div className="mt-3">
                    <div className="text-red-800 text-sm font-medium mb-1">
                      Query tentata:
                    </div>
                    <pre className="bg-white p-2 rounded border border-red-100 text-sm overflow-x-auto">
                      <code>{message.query}</code>
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Query SQL */}
        {!message.error && message.query && (
          <div className="mb-4">
            <div className="bg-blue-600 text-white rounded-lg overflow-hidden">
              <div className="px-4 py-2 bg-blue-700/50 flex justify-between items-center">
                <span className="text-sm font-medium">SQL</span>
                <div className="flex gap-2">
                  <button
                    className="p-1.5 hover:bg-blue-500 rounded transition-colors"
                    title="Copia query"
                    onClick={() =>
                      navigator.clipboard.writeText(message.query || "")
                    }
                  >
                    <i className="fas fa-copy text-sm"></i>
                  </button>
                  {onFeedback && message.explanation && (
                    <button
                      className="p-1.5 hover:bg-blue-500 rounded transition-colors"
                      title="Mark as correct answer"
                      onClick={() => {
                        if (
                          message.originalQuestion &&
                          message.query &&
                          message.explanation
                        ) {
                          onFeedback({
                            question: message.originalQuestion,
                            sql_query: message.query,
                            explanation: message.explanation,
                          });
                        }
                      }}
                    >
                      <i className="fas fa-thumbs-up text-sm"></i>
                    </button>
                  )}
                </div>
              </div>
              <pre className="p-4 overflow-x-auto">
                <code>{message.query}</code>
              </pre>
            </div>
          </div>
        )}

        {/* Spiegazione */}
        {message.explanation && (
          <div className="text-gray-600 italic mb-4">{message.explanation}</div>
        )}

        {/* Risultati */}
        {message.results && message.results.length > 0 && (
          <div className="overflow-x-auto bg-white rounded-lg border border-gray-200">
            <table className="w-full">
              <thead>
                <tr>
                  {Object.keys(message.results[0]).map((key) => (
                    <th
                      key={key}
                      className="px-4 py-2 bg-gray-50 text-left text-sm font-semibold text-gray-600 border-b border-gray-200"
                    >
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {message.results.map((row, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    {Object.values(row).map((value: any, j) => (
                      <td
                        key={j}
                        className="px-4 py-2 text-sm border-b border-gray-200 text-gray-600"
                      >
                        {value?.toString() || ""}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
