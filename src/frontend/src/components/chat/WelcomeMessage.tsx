const WelcomeMessage = () => {
  const tips = [
    "Ask for information about available data",
    "Request specific SQL queries",
    "Explore relationships between tables",
  ];

  return (
    <div className="flex justify-center">
      <div className="bg-white p-8 rounded-lg border border-gray-200 text-center max-w-fit">
        <h3 className="text-xl font-semibold text-blue-900 mb-4">
          👋 Welcome to your SQL Assistant!
        </h3>
        <p className="text-gray-700 mb-5">
          I'm here to help you explore and query the database.
        </p>
        <ul className="space-y-3 text-left mb-5">
          {tips.map((tip) => (
            <li key={tip} className="flex items-center space-x-2 text-gray-600">
              <span>•</span>
              <span>{tip}</span>
            </li>
          ))}
        </ul>
        <p className="text-blue-600 text-sm">
          💡 Tip: start by asking "Show me available tables" or "What data can I
          query?"
        </p>
      </div>
    </div>
  );
};

export default WelcomeMessage;
