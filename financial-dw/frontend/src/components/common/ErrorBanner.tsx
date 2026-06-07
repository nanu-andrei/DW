interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div className="flex items-center gap-3 p-3 bg-terminal-red/10 border border-terminal-red/30 rounded text-sm">
      <span className="text-terminal-red font-bold">ERR</span>
      <span className="text-terminal-text flex-1">{message}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-3 py-1 text-xs bg-terminal-surface border border-terminal-border rounded hover:border-terminal-cyan transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  );
}
