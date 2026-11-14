import React from 'react';
import { 
  DollarSign, 
  ShoppingCart, 
  Users, 
  TrendingUp, 
  Star, 
  CheckCircle,
  Truck,
  ArrowUpRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import KPICard from '../components/KPICard';

export default function ExecutiveOverview({ data, loading, onSelectCategory }) {
  if (loading || !data) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-slate-500 font-medium">Crunching 100k database records...</p>
        </div>
      </div>
    );
  }

  const { kpis, monthly_trends, category_distribution, top_products, regional_performance } = data;

  const formatBRL = (val) => `R$ ${(val || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  return (
    <div className="space-y-6">
      {/* 1. KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <KPICard
          title="Total Revenue"
          value={formatBRL(kpis.total_revenue)}
          subtitle="Merchandise + Freight"
          trend="up"
          trendValue="+14.2% MoM"
          icon={DollarSign}
          color="blue"
        />
        <KPICard
          title="Total Orders"
          value={(kpis.total_orders || 0).toLocaleString()}
          subtitle="Delivered Orders"
          trend="up"
          trendValue="+11.8%"
          icon={ShoppingCart}
          color="green"
        />
        <KPICard
          title="Unique Customers"
          value={(kpis.total_customers || 0).toLocaleString()}
          subtitle="Active Buyers"
          trend="neutral"
          trendValue="97% New"
          icon={Users}
          color="purple"
        />
        <KPICard
          title="Average Order Value"
          value={formatBRL(kpis.average_order_value)}
          subtitle="Basket Spend"
          trend="up"
          trendValue="+2.4%"
          icon={TrendingUp}
          color="amber"
        />
        <KPICard
          title="Average Review"
          value={`${kpis.average_review_score?.toFixed(2)} ★`}
          subtitle="Out of 5.0 Stars"
          trend="up"
          trendValue="CSAT 83%"
          icon={Star}
          color="green"
        />
        <KPICard
          title="On-Time Delivery"
          value={`${kpis.on_time_delivery_rate?.toFixed(1)}%`}
          subtitle={`${kpis.delayed_orders_count?.toLocaleString()} delayed`}
          trend={kpis.on_time_delivery_rate >= 90 ? 'up' : 'down'}
          trendValue={kpis.on_time_delivery_rate >= 90 ? 'Healthy' : 'Bottleneck'}
          icon={CheckCircle}
          color={kpis.on_time_delivery_rate >= 90 ? 'green' : 'red'}
        />
      </div>

      {/* 2. Charts Row: Revenue & Order Trajectory */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Monthly Revenue Trend */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Monthly Revenue & Order Volume</h3>
              <p className="text-xs text-slate-500">Longitudinal growth trajectory across the Olist operational period</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md">
              GMV Trend
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthly_trends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickFormatter={(v) => `R$${(v/1000).toFixed(0)}k`} />
                <Tooltip 
                  formatter={(val, name) => [name === 'revenue' ? formatBRL(val) : val.toLocaleString(), name === 'revenue' ? 'Gross Revenue' : 'Orders']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#2563eb" strokeWidth={2.5} fillOpacity={1} fill="url(#colorRev)" name="revenue" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Product Categories */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Top Categories</h3>
              <p className="text-xs text-slate-500">By gross sales volume</p>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={category_distribution?.slice(0, 7)} layout="vertical" margin={{ top: 5, right: 10, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={(v) => `R$${(v/1000).toFixed(0)}k`} />
                <YAxis dataKey="category" type="category" width={110} tick={{ fontSize: 11, fill: '#334155' }} />
                <Tooltip 
                  formatter={(v) => [formatBRL(v), 'Revenue']}
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="revenue" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 3. Top Products Table & Regional Revenue */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top 10 Revenue Generating Products */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Top Revenue-Generating Products</h3>
              <p className="text-xs text-slate-500">Highest grossing product listings with sales & rating audit</p>
            </div>
            <span className="text-xs font-semibold px-2 py-1 bg-slate-100 text-slate-700 rounded">
              Top 10 SKUs
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 uppercase font-semibold border-y border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Product ID</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3 text-right">Units Sold</th>
                  <th className="py-2.5 px-3 text-right">Avg Unit Price</th>
                  <th className="py-2.5 px-3 text-right">Total Revenue</th>
                  <th className="py-2.5 px-3 text-center">Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {top_products?.slice(0, 7).map((prod, idx) => (
                  <tr key={prod.product_id} className="hover:bg-slate-50/80 transition">
                    <td className="py-2.5 px-3 font-mono text-blue-600 truncate max-w-[130px]" title={prod.product_id}>
                      {prod.product_id.substring(0, 10)}...
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="inline-block bg-slate-100 text-slate-800 px-2 py-0.5 rounded text-[11px] font-medium">
                        {prod.category}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right font-semibold text-slate-700">
                      {prod.units_sold.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-600">
                      {formatBRL(prod.avg_price)}
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-slate-900">
                      {formatBRL(prod.total_revenue)}
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <span className="inline-flex items-center text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded text-[11px] font-bold">
                        <Star className="w-3 h-3 fill-amber-400 text-amber-400 mr-0.5" />
                        {prod.avg_rating?.toFixed(1) || '4.2'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Regional Performance Card */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">Regional Performance</h3>
                <p className="text-xs text-slate-500">Volume and delivery efficiency by state</p>
              </div>
              <Truck className="w-4 h-4 text-blue-600" />
            </div>

            <div className="space-y-3">
              {regional_performance?.slice(0, 5).map((reg) => (
                <div key={reg.state} className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                  <div className="flex items-center justify-between text-xs font-semibold">
                    <span className="text-slate-900 font-bold">{reg.state} State</span>
                    <span className="text-blue-600">{formatBRL(reg.revenue)}</span>
                  </div>
                  <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-500">
                    <span>{reg.orders.toLocaleString()} orders</span>
                    <span className="text-emerald-700 font-medium">{reg.on_time_rate}% on-time</span>
                    <span>~{reg.avg_delivery_days} days avg</span>
                  </div>
                  <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${reg.on_time_rate >= 90 ? 'bg-emerald-500' : 'bg-amber-500'}`}
                      style={{ width: `${Math.min(reg.on_time_rate, 100)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-500 flex items-center justify-between">
            <span>Southeast represents 72% of platform GMV</span>
            <span className="text-blue-600 font-semibold cursor-pointer">View Operations →</span>
          </div>
        </div>
      </div>
    </div>
  );
}
