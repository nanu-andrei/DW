"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import MessageBubble from "./MessageBubble";
import {
  fetchAssets,
  fetchAssetDetails,
  fetchDataSources,
  fetchDataSourceDetails,
  fetchTimeSeries,
  fetchTotals,
  triggerIngestion,
} from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const HELP_TEXT = `Available commands:
  list assets          - List all asset IDs in the warehouse
  list sources         - List all data source IDs
  asset <id>           - Show details for a specific asset
  source <id>          - Show details for a specific data source
  data <assetId> <sourceId> <start> <end>
                       - Fetch time series data
  totals               - Show aggregation results
  ingest <ticker1> [ticker2] ...
                       - Ingest data from Yahoo Finance
  help                 - Show this help message`;

export default function TerminalChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Nanu Financial DW Assistant v0.1\nType 'help' for available commands.\n\nConnected to backend API.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const addMessage = (role: "user" | "assistant", content: string) => {
    setMessages((prev) => [...prev, { role, content, timestamp: new Date() }]);
  };

  const processCommand = async (cmd: string) => {
    const parts = cmd.trim().split(/\s+/);
    const command = parts[0]?.toLowerCase();

    try {
      if (command === "help") {
        return HELP_TEXT;
      }

      if (command === "list") {
        const sub = parts[1]?.toLowerCase();
        if (sub === "assets") {
          const res = (await fetchAssets(0, 50)) as any;
          if (!res.items || res.items.length === 0) {
            return "No assets found. Try ingesting data first:\n  ingest BTC-USD ETH-USD AAPL";
          }
          const header = `Assets (${res.total} total):\n${"─".repeat(40)}`;
          const rows = res.items.map((id: string, i: number) => `  ${i + 1}. ${id}`).join("\n");
          return `${header}\n${rows}\n${"─".repeat(40)}\nShowing ${res.items.length} of ${res.total}`;
        }
        if (sub === "sources" || sub === "datasources") {
          const res = (await fetchDataSources(0, 50)) as any;
          if (!res.items || res.items.length === 0) {
            return "No data sources found.";
          }
          const header = `Data Sources (${res.total} total):\n${"─".repeat(40)}`;
          const rows = res.items.map((id: string, i: number) => `  ${i + 1}. ${id}`).join("\n");
          return `${header}\n${rows}`;
        }
        return "Unknown list command. Try: list assets, list sources";
      }

      if (command === "asset") {
        const assetId = parts.slice(1).join(" ");
        if (!assetId) return "Usage: asset <assetId>";
        const versions = (await fetchAssetDetails(assetId)) as any[];
        if (!versions || versions.length === 0) {
          return `Asset '${assetId}' not found.`;
        }
        const latest = versions[0];
        let out = `Asset: ${latest.id}\n${"─".repeat(40)}`;
        out += `\n  Name:        ${latest.name}`;
        out += `\n  Description: ${latest.description}`;
        out += `\n  Updated:     ${new Date(latest.system_date).toLocaleString()}`;
        out += `\n  Versions:    ${versions.length}`;
        if (latest.attributes && Object.keys(latest.attributes).length > 0) {
          out += `\n  Attributes:`;
          for (const [k, v] of Object.entries(latest.attributes)) {
            out += `\n    ${k}: ${v}`;
          }
        }
        return out;
      }

      if (command === "source") {
        const sourceId = parts.slice(1).join(" ");
        if (!sourceId) return "Usage: source <dataSourceId>";
        const versions = (await fetchDataSourceDetails(sourceId)) as any[];
        if (!versions || versions.length === 0) {
          return `Data source '${sourceId}' not found.`;
        }
        const latest = versions[0];
        let out = `Data Source: ${latest.id}\n${"─".repeat(40)}`;
        out += `\n  Name:        ${latest.name}`;
        out += `\n  Description: ${latest.description}`;
        out += `\n  Updated:     ${new Date(latest.system_date).toLocaleString()}`;
        if (latest.attributes && latest.attributes.length > 0) {
          out += `\n  Attributes:  ${latest.attributes.join(", ")}`;
        }
        return out;
      }

      if (command === "data") {
        if (parts.length < 5) {
          return "Usage: data <assetId> <dataSourceId> <startDate> <endDate>\nExample: data YFINANCE/BTC-USD YFINANCE 2023-01-01 2023-06-30";
        }
        const [, assetId, sourceId, startDate, endDate] = parts;
        const res = (await fetchTimeSeries(assetId, sourceId, startDate, endDate, true)) as any;
        if (!res.data.records || res.data.records.length === 0) {
          return "No records found for the given parameters.";
        }
        let out = `Time Series: ${res.data.assetId}\n`;
        out += `Source: ${res.data.datasourceId}\n`;
        out += `${"─".repeat(60)}\n`;

        // Show first 10 records as a table
        const records = res.data.records.slice(0, 10);
        const cols = Object.keys(records[0].values);
        out += `Date       | ${cols.map((c: string) => c.padEnd(12)).join("| ")}\n`;
        out += `${"─".repeat(60)}\n`;
        for (const r of records) {
          const vals = cols.map((c: string) => {
            const v = r.values[c];
            return typeof v === "number" ? v.toFixed(2).padStart(12) : String(v || "-").padEnd(12);
          });
          out += `${r.businessDate} | ${vals.join("| ")}\n`;
        }
        if (res.data.records.length > 10) {
          out += `\n... and ${res.data.records.length - 10} more records`;
        }
        if (res.attributes) {
          out += `\nAttributes: ${res.attributes.join(", ")}`;
        }
        return out;
      }

      if (command === "totals") {
        const res = (await fetchTotals()) as any[];
        if (!res || res.length === 0) {
          return "No aggregation results found. Run an aggregation job from the Analytics page.";
        }
        let out = `Aggregation Totals\n${"─".repeat(50)}\n`;
        out += `${"Asset".padEnd(30)} ${"Year".padEnd(6)} Count\n`;
        out += `${"─".repeat(50)}\n`;
        for (const r of res) {
          out += `${r.asset_id.padEnd(30)} ${String(r.business_date_year).padEnd(6)} ${r.cnt}\n`;
        }
        return out;
      }

      if (command === "ingest") {
        const tickers = parts.slice(1);
        if (tickers.length === 0) {
          return "Usage: ingest <ticker1> [ticker2] ...\nExample: ingest BTC-USD ETH-USD AAPL";
        }
        addMessage("assistant", `Ingesting ${tickers.join(", ")}...`);
        const res = (await triggerIngestion(tickers)) as any;
        return `Ingestion complete:\n  Fetched: ${res.fetched}\n  Stored:  ${res.stored}\n  Skipped: ${res.skipped}\n  Errors:  ${res.errors}\n  Status:  ${res.status}`;
      }

      return `Unknown command: '${command}'. Type 'help' for available commands.`;
    } catch (e) {
      return `Error: ${e instanceof Error ? e.message : String(e)}`;
    }
  };

  const handleSubmit = async () => {
    if (!input.trim() || loading) return;

    const cmd = input.trim();
    addMessage("user", cmd);
    setInput("");
    setLoading(true);

    try {
      const response = await processCommand(cmd);
      addMessage("assistant", response);
    } catch (e) {
      addMessage(
        "assistant",
        `Error: ${e instanceof Error ? e.message : String(e)}`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col h-full bg-terminal-bg">
      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {loading && (
          <div className="text-terminal-muted text-sm animate-pulse">
            Processing...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-terminal-border p-3">
        <div className="flex items-center gap-2">
          <span className="text-terminal-green font-bold">&gt;</span>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command... (try 'help')"
            className="flex-1 bg-transparent text-terminal-text text-sm outline-none placeholder:text-terminal-muted/50"
            disabled={loading}
          />
          {input && (
            <span className="text-terminal-green cursor-blink">|</span>
          )}
        </div>
      </div>
    </div>
  );
}
