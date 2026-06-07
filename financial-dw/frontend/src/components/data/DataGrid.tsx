"use client";

interface Column {
  key: string;
  label: string;
  width?: string;
  render?: (value: any, row: any) => React.ReactNode;
}

interface DataGridProps {
  columns: Column[];
  rows: any[];
  onRowClick?: (row: any) => void;
  emptyMessage?: string;
}

export default function DataGrid({
  columns,
  rows,
  onRowClick,
  emptyMessage = "No data available",
}: DataGridProps) {
  if (rows.length === 0) {
    return (
      <div className="flex items-center justify-center p-8 text-terminal-muted text-sm">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="overflow-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-terminal-border">
            {columns.map((col) => (
              <th
                key={col.key}
                className="text-left px-3 py-2 text-terminal-muted font-normal uppercase tracking-wider"
                style={{ width: col.width }}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={i}
              onClick={() => onRowClick?.(row)}
              className={`border-b border-terminal-border/50 transition-colors ${
                onRowClick
                  ? "cursor-pointer hover:bg-terminal-bg/50"
                  : ""
              }`}
            >
              {columns.map((col) => (
                <td key={col.key} className="px-3 py-2 text-terminal-text">
                  {col.render
                    ? col.render(row[col.key], row)
                    : row[col.key] ?? "-"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
