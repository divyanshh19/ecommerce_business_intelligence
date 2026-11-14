import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function KPICard({ 
  title, 
  value, 
  subtitle, 
  trend, 
  trendValue, 
  icon: Icon,
  color = 'blue' 
}) {
  const colorStyles = {
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    green: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
    red: 'bg-rose-50 text-rose-600 border-rose-100'
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm hover:shadow transition">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-lg border ${colorStyles[color] || colorStyles.blue}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline space-x-2">
        <span className="text-2xl font-bold text-slate-900 tracking-tight">{value}</span>
      </div>

      <div className="mt-2 flex items-center justify-between text-xs">
        <span className="text-slate-400">{subtitle}</span>
        {trendValue && (
          <span className={`inline-flex items-center font-medium px-1.5 py-0.5 rounded text-[11px] ${
            trend === 'up' 
              ? 'bg-emerald-50 text-emerald-700 font-semibold' 
              : trend === 'down' 
              ? 'bg-rose-50 text-rose-700 font-semibold' 
              : 'bg-slate-100 text-slate-600'
          }`}>
            {trend === 'up' && <TrendingUp className="w-3 h-3 mr-0.5 text-emerald-600" />}
            {trend === 'down' && <TrendingDown className="w-3 h-3 mr-0.5 text-rose-600" />}
            {trend === 'neutral' && <Minus className="w-3 h-3 mr-0.5 text-slate-400" />}
            {trendValue}
          </span>
        )}
      </div>
    </div>
  );
}
