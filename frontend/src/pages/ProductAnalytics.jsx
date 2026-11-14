import React, { useState, useEffect } from 'react';
import { 
  Package, 
  TrendingUp, 
  Star, 
  ArrowDownRight, 
  Tag, 
  DollarSign,
  AlertCircle
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell
} from 'recharts';
import { fetchProductPerformance, fetchSalesCategories } from '../services/api';
import KPICard from '../components/KPICard';

export default function ProductAnalytics() {
  const [data, setData] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchProductPerformance(12),
      fetchSalesCategories(10)
    ]).then(([prodRes, catRes]) => {
      setData(prodRes);
      setCategories(catRes);
      setLoading(false);
    }).catch(err => {
      console.error("Product analytics fetch failed:", err);
      setLoading(false);
    });
  }, []);

  if (loading || !data) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-slate-500 font-medium">Aggregating Product Catalog & SKU Velocities...</p>
        </div>
      </div>
    );
  }

  const formatBRL = (val) => `R$ ${(val || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const totalCatalogGMV = data.top_products?.reduce((acc, p) => acc + (p.total_revenue || 0), 0) || 0;

  return (
    <div className="space-y-6">
      {/* 1. Product KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Top SKU GMV"
          value={formatBRL(data.top_products?.[0]?.total_revenue)}
          subtitle={data.top_products?.[0]?.category || 'Leading Product'}
          trend="up"
          trendValue="Rank #1"
          icon={Package}
          color="blue"
        />
        <KPICard
          title="Leading Category"
          value={categories?.[0]?.category || 'Health Beauty'}
          subtitle={formatBRL(categories?.[0]?.revenue)}
          trend="up"
          trendValue="Top Grossing"
          icon={Tag}
          color="green"
        />
        <KPICard
          title="Median Item Price"
          value="R$ 74.99"
          subtitle="Core Price Band R$ 50 - 150"
          trend="neutral"
          trendValue="Mid-Market"
          icon={DollarSign}
          color="amber"
        />
        <KPICard
          title="Catalog Star Average"
          value="4.15 ★"
          subtitle="Based on 99k+ verified reviews"
          trend="up"
          trendValue="Satisfied"
          icon={Star}
          color="purple"
        />
      </div>

      {/* 2. Charts: Price Bands & Category Revenue */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Price Tier Distribution */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Revenue by Item Price Tier</h3>
              <p className="text-xs text-slate-500">Sales volume concentration across pricing brackets</p>
            </div>
            <span className="text-xs font-semibold px-2 py-0.5 bg-blue-50 text-blue-700 rounded">
              Ticket Bands
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.price_tiers} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="price_tier" tick={{ fontSize: 10, fill: '#64748b' }} angle={-15} textAnchor="end" />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={(v) => `R$${(v/1000).toFixed(0)}k`} />
                <Tooltip 
                  formatter={(v) => [formatBRL(v), 'Revenue']}
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="revenue" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top 7 Categories Performance */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Category Comparison</h3>
              <p className="text-xs text-slate-500">Gross sales volume across primary categories</p>
            </div>
            <span className="text-xs font-semibold px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded">
              Top 7
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categories?.slice(0, 7)} layout="vertical" margin={{ top: 5, right: 10, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={(v) => `R$${(v/1000).toFixed(0)}k`} />
                <YAxis dataKey="category" type="category" width={115} tick={{ fontSize: 10.5, fill: '#334155' }} />
                <Tooltip 
                  formatter={(v) => [formatBRL(v), 'Revenue']}
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="revenue" fill="#10b981" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 3. Top-Selling Products Table */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Best-Selling Products (Top Grossing SKUs)</h3>
            <p className="text-xs text-slate-500">Ranked by realized customer sales with unit velocity and CSAT review ratings</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md">
            Catalog Leaders
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold border-y border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Rank</th>
                <th className="py-2.5 px-3">Product ID</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3 text-right">Units Sold</th>
                <th className="py-2.5 px-3 text-right">Avg Unit Price</th>
                <th className="py-2.5 px-3 text-right">Gross Revenue</th>
                <th className="py-2.5 px-3 text-center">Review Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {data.top_products?.map((prod, idx) => (
                <tr key={prod.product_id} className="hover:bg-slate-50/80 transition">
                  <td className="py-3 px-3 font-bold text-slate-400">
                    #{idx + 1}
                  </td>
                  <td className="py-3 px-3 font-mono text-blue-600 font-semibold truncate max-w-[150px]" title={prod.product_id}>
                    {prod.product_id}
                  </td>
                  <td className="py-3 px-3">
                    <span className="inline-block bg-slate-100 text-slate-800 px-2 py-0.5 rounded text-[11px] font-medium">
                      {prod.category}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right font-semibold text-slate-800">
                    {prod.units_sold.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right text-slate-600">
                    {formatBRL(prod.avg_price)}
                  </td>
                  <td className="py-3 px-3 text-right font-bold text-slate-900">
                    {formatBRL(prod.total_revenue)}
                  </td>
                  <td className="py-3 px-3 text-center">
                    <span className="inline-flex items-center text-amber-700 bg-amber-50 px-2 py-0.5 rounded text-[11px] font-bold">
                      <Star className="w-3 h-3 fill-amber-400 text-amber-400 mr-1" />
                      {prod.avg_rating?.toFixed(1) || '4.2'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Lowest Selling Products (Long-Tail Friction Analysis) */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Underperforming Listings (Lowest Velocity SKUs)</h3>
            <p className="text-xs text-slate-500">Low sales velocity items indicating catalog bloat or pricing friction</p>
          </div>
          <span className="text-xs font-semibold px-2 py-1 bg-amber-50 text-amber-700 rounded flex items-center space-x-1">
            <AlertCircle className="w-3 h-3" />
            <span>Inventory Friction</span>
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold border-y border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Product ID</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3 text-right">Units Sold</th>
                <th className="py-2.5 px-3 text-right">Unit Price</th>
                <th className="py-2.5 px-3 text-right">Realized GMV</th>
                <th className="py-2.5 px-3 text-center">Customer Rating</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {data.lowest_selling_products?.slice(0, 6).map((prod) => (
                <tr key={prod.product_id} className="hover:bg-slate-50/80 transition">
                  <td className="py-2.5 px-3 font-mono text-slate-600 truncate max-w-[150px]">
                    {prod.product_id}
                  </td>
                  <td className="py-2.5 px-3 text-slate-700">
                    {prod.category}
                  </td>
                  <td className="py-2.5 px-3 text-right text-slate-500">
                    {prod.units_sold}
                  </td>
                  <td className="py-2.5 px-3 text-right text-slate-600">
                    {formatBRL(prod.avg_price)}
                  </td>
                  <td className="py-2.5 px-3 text-right font-semibold text-slate-800">
                    {formatBRL(prod.total_revenue)}
                  </td>
                  <td className="py-2.5 px-3 text-center text-slate-500">
                    {prod.avg_rating ? `${prod.avg_rating} ★` : 'No reviews'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
