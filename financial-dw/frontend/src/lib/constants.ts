export const APP_NAME = "NANU";
export const APP_TITLE = "Nanu Financial Data Warehouse";

export const NAV_ITEMS = [
  { name: "Dashboard", path: "/", icon: "LayoutDashboard" },
  { name: "Assets", path: "/assets", icon: "Database" },
  { name: "Data Sources", path: "/data-sources", icon: "Server" },
  { name: "Explorer", path: "/explorer", icon: "LineChart" },
  { name: "Analytics", path: "/analytics", icon: "BarChart3" },
  { name: "Assistant", path: "/assistant", icon: "Terminal" },
] as const;
