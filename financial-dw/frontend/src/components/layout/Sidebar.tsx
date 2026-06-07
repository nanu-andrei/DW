"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Database,
  Server,
  LineChart,
  BarChart3,
  Terminal,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const navItems = [
  { name: "Dashboard", path: "/", icon: LayoutDashboard },
  { name: "Assets", path: "/assets", icon: Database },
  { name: "Data Sources", path: "/data-sources", icon: Server },
  { name: "Explorer", path: "/explorer", icon: LineChart },
  { name: "Analytics", path: "/analytics", icon: BarChart3 },
  { name: "Assistant", path: "/assistant", icon: Terminal },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <aside
      className={`flex flex-col h-screen bg-terminal-surface border-r border-terminal-border transition-all duration-200 ${
        collapsed ? "w-16" : "w-60"
      }`}
    >
      {/* Logo */}
      <div className="flex items-center h-14 px-4 border-b border-terminal-border">
        {!collapsed && (
          <span className="text-terminal-green font-bold text-lg tracking-widest">
            NANU
          </span>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="ml-auto text-terminal-muted hover:text-terminal-text transition-colors"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4">
        {navItems.map((item) => {
          const isActive =
            item.path === "/"
              ? pathname === "/"
              : pathname.startsWith(item.path);
          const Icon = item.icon;
          return (
            <Link
              key={item.path}
              href={item.path}
              className={`flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                isActive
                  ? "text-terminal-green bg-terminal-green/10 border-r-2 border-terminal-green"
                  : "text-terminal-muted hover:text-terminal-text hover:bg-terminal-bg"
              }`}
            >
              <Icon size={18} />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-terminal-border text-xs text-terminal-muted">
        {!collapsed && <span>Acme Ltd DW v0.1</span>}
      </div>
    </aside>
  );
}
