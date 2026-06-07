import TerminalChat from "@/components/chat/TerminalChat";

export default function AssistantPage() {
  return (
    <div className="space-y-4 h-full flex flex-col">
      <div>
        <h1 className="text-lg font-bold text-terminal-green tracking-wider">
          ASSISTANT
        </h1>
        <p className="text-xs text-terminal-muted mt-1">
          LLM-powered data warehouse exploration via MCP tools
        </p>
      </div>

      <div
        className="flex-1 bg-terminal-surface border border-terminal-border rounded overflow-hidden"
        style={{ minHeight: "400px" }}
      >
        <TerminalChat />
      </div>
    </div>
  );
}
