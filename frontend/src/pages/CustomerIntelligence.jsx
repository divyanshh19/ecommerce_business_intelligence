import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Repeat, 
  Wallet, 
  Target, 
  Award, 
  AlertTriangle,
  Info,
  Clock,
  ArrowRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { fetchCustomerRFM } from '../services/api';
import KPICard from '../components/KPICard';

const SEGMENT_COLORS = {
  'Champions': '#10b981',           // Emerald
  'Loyal Customers': '#3b82f6',     // Blue
  'Potential Loyalists': '#06b6d4', // Cyan
  'New Customers': '#8b5cf6',       // Purple
  'Promising': '#f59e0b',           // Amber
  'Need Attention': '#ec4899',      // Pink
  'High-Value At Risk': '#f97316',  // Orange
  'At Risk': '#ef4444',             // Red
  'Lost Customers': '#64748b'       // Slate
};

const STRATEGIES = {
  'Champions': 'Reward with exclusive VIP early access, no-threshold free shipping, and ambassador referral codes.',
  'Loyal Customers': 'Upsell complementary product categories and incentivize reviews with bonus loyalty points.',
  'Potential Loyalists': 'Trigger automated 20-day post-delivery cross-sell sequences with personalized discounts.',
  'New Customers': 'Provide warm onboarding lifecycle nurture; deliver an exclusive second-purchase voucher valid for 30 days.',
  'Promising': 'Showcase trending community favorites and offer low-threshold bundle deals to build purchasing habit.',
  'Need Attention': 'Conduct customer sentiment surveys, diagnose satisfaction bottlenecks, and offer time-limited reactivations.',
  'High-Value At Risk': 'High past spenders going dormant! Trigger personal re-engagement emails with substantial discount codes.',
  'At Risk': 'Automate multi-channel win-back campaigns highlighting new arrivals in previously browsed categories.',
  'Lost Customers': 'Run low-cost reactivation tests or suppress high-cost retargeting ads to optimize acquisition CAC.'
};

export default function CustomerIntelligence() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSegment, setSelectedSegment] = useState(null);

  useEffect(() => {
    fetchCustomerRFM()
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(err => {
        console.error("RFM fetch failed:", err);
        setLoading(false);
      });
  }, []);

  if (loading || !data) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-slate-500 font-medium">Evaluating RFM Quintiles & Customer Segments...</p>
        </div>
      </div>
    );
  }

  const formatBRL = (val) => `R$ ${(val || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const pieData = data.segments?.map(s => ({
    name: s.customer_segment,
    value: s.customer_count,
    color: SEGMENT_COLORS[s.customer_segment] || '#94a3b8'
  })) || [];

  return (
    <div className="space-y-6">
      {/* 1. Customer Intelligence KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KPICard
          title="Total Customers"
          value={data.total_unique_customers?.toLocaleString()}
          subtitle="Distinct Individual Buyers"
          trend="neutral"
          trendValue="Empirical Base"
          icon={Users}
          color="blue"
        />
        <KPICard
          title="Repeat Customers"
          value={data.repeat_customers_count?.toLocaleString()}
          subtitle="Purchased >= 2 Times"
          trend="neutral"
          trendValue="Cohort Core"
          icon={Repeat}
          color="purple"
        />
        <KPICard
          title="Repeat Purchase Rate"
          value={`${data.repeat_purchase_rate_pct}%`}
          subtitle="Benchmarking 15-25%"
          trend="down"
          trendValue="Primary Focus"
          icon={Target}
          color="amber"
        />
        <KPICard
          title="Average Spend / Buyer"
          value={formatBRL(data.average_customer_spend)}
          subtitle="Cumulative Ticket"
          trend="up"
          trendValue="Gross Value"
          icon={Wallet}
          color="green"
        />
        <KPICard
          title="Lifetime Value Proxy"
          value={formatBRL(data.clv_proxy)}
          subtitle="Spend × Frequency"
          trend="up"
          trendValue="Realized CLV"
          icon={Award}
          color="blue"
        />
      </div>

      {/* 2. Analytical Context Banner */}
      <div className="bg-blue-50/70 border border-blue-200 rounded-xl p-4 flex items-start space-x-3 text-xs text-blue-900">
        <Info className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">E-Commerce RFM Segmentation Methodology & Analytical Assumptions:</span>
          <p className="mt-1 text-blue-800 leading-relaxed">
            In the Olist dataset, ~97% of buyers placed a single order during the 2016-2018 window. Rather than treating single-order buyers as homogeneous, our model cross-classifies buyers into <b>Potential Loyalists</b> (high monetary spend, recent purchase) vs <b>Lost Customers</b> (low spend, purchased over 365 days ago). Recency is anchored to <b>September 4, 2018</b> (the empirical platform cutoff date).
          </p>
        </div>
      </div>

      {/* 3. RFM Visualizations Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Segment Size & Revenue Contribution */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Customer Segment Revenue Contribution</h3>
              <p className="text-xs text-slate-500">Gross realized merchandise revenue by behavioral RFM cohort</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md">
              Segment Revenue
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.segments} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis 
                  dataKey="customer_segment" 
                  tick={{ fontSize: 10, fill: '#475569' }} 
                  angle={-25} 
                  textAnchor="end" 
                  interval={0}
                />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickFormatter={(v) => `R$${(v/1000).toFixed(0)}k`} />
                <Tooltip 
                  formatter={(val) => [formatBRL(val), 'Segment Revenue']}
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="total_segment_revenue" radius={[4, 4, 0, 0]}>
                  {data.segments?.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={SEGMENT_COLORS[entry.customer_segment] || '#3b82f6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Segment Share Donut */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Segment Share</h3>
            <p className="text-xs text-slate-500">Proportion of total customer base</p>

            <div className="h-56 w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(val, name) => [`${val.toLocaleString()} (${((val / data.total_unique_customers) * 100).toFixed(1)}%)`, name]}
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-1 text-[11px] text-slate-600 mt-2">
            {pieData.slice(0, 6).map((item) => (
              <div key={item.name} className="flex items-center space-x-1.5 truncate">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }}></span>
                <span className="truncate">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 4. Actionable Customer Segment Matrix */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Actionable RFM Cohort Matrix & Marketing Playbooks</h3>
            <p className="text-xs text-slate-500">Operational benchmarks, average spend, and prescriptive retention strategies</p>
          </div>
          <span className="text-xs font-semibold px-2 py-1 bg-blue-50 text-blue-700 rounded">
            9 Cohorts
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold border-y border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Segment Name</th>
                <th className="py-2.5 px-3 text-right">Customer Count</th>
                <th className="py-2.5 px-3 text-right">Base Share</th>
                <th className="py-2.5 px-3 text-right">Avg Recency</th>
                <th className="py-2.5 px-3 text-right">Avg Ticket</th>
                <th className="py-2.5 px-3 text-right">Total Revenue</th>
                <th className="py-2.5 px-3">Prescriptive Marketing Strategy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {data.segments?.map((seg) => {
                const color = SEGMENT_COLORS[seg.customer_segment] || '#64748b';
                return (
                  <tr key={seg.customer_segment} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-3">
                      <span 
                        className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold text-white shadow-xs"
                        style={{ backgroundColor: color }}
                      >
                        {seg.customer_segment}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right font-bold text-slate-900">
                      {seg.customer_count?.toLocaleString()}
                    </td>
                    <td className="py-3 px-3 text-right text-slate-600">
                      {seg.percentage_of_customers}%
                    </td>
                    <td className="py-3 px-3 text-right text-slate-700">
                      {seg.avg_recency_days} days
                    </td>
                    <td className="py-3 px-3 text-right font-semibold text-slate-800">
                      {formatBRL(seg.avg_customer_spend)}
                    </td>
                    <td className="py-3 px-3 text-right font-bold text-blue-600">
                      {formatBRL(seg.total_segment_revenue)}
                    </td>
                    <td className="py-3 px-3 text-slate-600 text-[11px] max-w-[320px] leading-relaxed">
                      {STRATEGIES[seg.customer_segment] || 'Engage with targeted marketing flows.'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
