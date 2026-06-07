"use client";

import { useEffect, useState } from "react";

export default function Header() {
  const [time, setTime] = useState("");

  useEffect(() => {
    const update = () => {
      setTime(new Date().toLocaleTimeString("en-US", { hour12: false }));
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  const tickerItems = [
    { symbol: "BTC/USD", price: "43,250.00", change: "+2.4%" },
    { symbol: "ETH/USD", price: "2,280.50", change: "+1.8%" },
    { symbol: "LTC/USD", price: "72.30", change: "-0.5%" },
    { symbol: "SPX", price: "5,120.00", change: "+0.3%" },
  ];

  return (
    <header className="flex items-center h-10 px-4 bg-terminal-surface border-b border-terminal-border text-xs gap-4">
      {/* Ticker */}
      <div className="flex gap-6 overflow-hidden flex-shrink-0">
        {tickerItems.map((item) => (
          <div key={item.symbol} className="flex gap-2 whitespace-nowrap">
            <span className="text-terminal-cyan">{item.symbol}</span>
            <span className="text-terminal-text">{item.price}</span>
            <span
              className={
                item.change.startsWith("+")
                  ? "text-terminal-green"
                  : "text-terminal-red"
              }
            >
              {item.change}
            </span>
          </div>
        ))}
      </div>

      {/* Search */}
      <div className="flex-1 max-w-xs">
        <input
          type="text"
          placeholder="Search assets, sources..."
          className="w-full bg-terminal-bg border border-terminal-border rounded px-2 py-1 text-xs text-terminal-text placeholder:text-terminal-muted/50 focus:border-terminal-cyan outline-none"
        />
      </div>

      {/* Clock */}
      <div className="text-terminal-muted font-mono" suppressHydrationWarning>
        {time}
      </div>
    </header>
  );
}
