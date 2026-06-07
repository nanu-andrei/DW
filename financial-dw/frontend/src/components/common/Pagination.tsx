interface PaginationProps {
  offset: number;
  limit: number;
  total: number;
  onPageChange: (newOffset: number) => void;
}

export default function Pagination({
  offset,
  limit,
  total,
  onPageChange,
}: PaginationProps) {
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="flex items-center justify-between px-4 py-2 text-xs text-terminal-muted border-t border-terminal-border">
      <span>
        {total === 0
          ? "No results"
          : `Showing ${offset + 1}-${Math.min(offset + limit, total)} of ${total}`}
      </span>
      <div className="flex gap-2">
        <button
          onClick={() => onPageChange(Math.max(0, offset - limit))}
          disabled={offset === 0}
          className="px-2 py-1 border border-terminal-border rounded disabled:opacity-30 hover:border-terminal-cyan transition-colors"
        >
          Prev
        </button>
        <span className="px-2 py-1">
          {currentPage} / {totalPages}
        </span>
        <button
          onClick={() => onPageChange(offset + limit)}
          disabled={offset + limit >= total}
          className="px-2 py-1 border border-terminal-border rounded disabled:opacity-30 hover:border-terminal-cyan transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  );
}
