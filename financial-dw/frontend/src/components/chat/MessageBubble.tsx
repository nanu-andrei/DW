interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] text-sm ${
          isUser
            ? "text-terminal-cyan"
            : "text-terminal-text"
        }`}
      >
        <div className="flex items-center gap-2 mb-1">
          <span
            className={`text-xs font-bold ${
              isUser ? "text-terminal-cyan" : "text-terminal-green"
            }`}
          >
            {isUser ? "YOU" : "SYS"}
          </span>
          <span className="text-xs text-terminal-muted">
            {message.timestamp.toLocaleTimeString("en-US", { hour12: false })}
          </span>
        </div>
        <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed">
          {message.content}
        </pre>
      </div>
    </div>
  );
}
