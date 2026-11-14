import React from 'react';
import { 
  BarChart3, 
  Users, 
  Package, 
  Truck, 
  CreditCard, 
  ShieldCheck, 
  FileDown, 
  Database,
  TrendingUp
} from 'lucide-react';

const navItems = [
  { id: 'overview', label: 'Executive Overview', icon: BarChart3, badge: 'KPIs' },
  { id: 'customers', label: 'Customer Intelligence', icon: Users, badge: 'RFM' },
  { id: 'products', label: 'Product Analytics', icon: Package },
  { id: 'operations', label: 'Operations & Logistics', icon: Truck },
  { id: 'payments', label: 'Payment Analytics', icon: CreditCard },
  { id: 'data-quality', label: 'Data Quality & Reports', icon: ShieldCheck, badge: '97.8%' }
];

export default function Sidebar({ activePage, setActivePage, onExportPDF }) {
  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 shrink-0">
      {/* Platform Branding */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight">Olist Analytics BI</h1>
            <p className="text-xs text-slate-400 font-medium">Enterprise Intelligence</p>
          </div>
        </div>
        <div className="mt-3 flex items-center justify-between bg-slate-800/60 rounded-md px-2.5 py-1 text-xs">
          <span className="flex items-center text-emerald-400 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse mr-1.5"></span>
            Live DB Active
          </span>
          <span className="text-slate-400">100k Orders</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2">
          Analytics Dashboards
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                  isActive ? 'bg-white/20 text-white' : 'bg-slate-800 text-blue-400'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Quick Action Footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/50 space-y-2">
        <button
          onClick={onExportPDF}
          className="w-full flex items-center justify-center space-x-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold py-2 px-3 rounded-lg border border-slate-700 transition"
        >
          <FileDown className="w-3.5 h-3.5 text-blue-400" />
          <span>Export Executive PDF</span>
        </button>
        <div className="text-[11px] text-slate-400 text-center flex items-center justify-center space-x-1">
          <Database className="w-3 h-3" />
          <span>PostgreSQL / MySQL / SQLite</span>
        </div>
      </div>
    </aside>
  );
}
