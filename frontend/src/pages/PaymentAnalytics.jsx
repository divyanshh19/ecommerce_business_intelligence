import React, { useState, useEffect } from 'react';
import { 
  CreditCard, 
  Wallet, 
  FileText, 
  Layers, 
  TrendingUp, 
  DollarSign,
  PieChart as PieIcon
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
import { fetchPaymentAnalysis } from '../services/api';
import KPICard from '../components/KPICard';

const METHOD_COLORS = {
  'credit_card': '#2563eb', // Blue
  'boleto': '#059669',      // Emerald
  'voucher': '#d97706',     // Amber
  'debit_card': '#7c3aed'   // Purple
};

export default function PaymentAnalytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPaymentAnalysis()
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(err => {
        console.error("Payment fetch failed:", err);
        setLoading(false);
      });
  }, []);

  if (loading || !data) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-slate-500 font-medium">Aggregating Payment Rails & Installment Financed Transactions...</p>
        </div>
      </div>
    );
  }

  const formatBRL = (val) => `R$ ${(val || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const totalPaymentGMV = data.methods?.reduce((acc, m) => acc + (m.total_payment_value || 0), 0) || 0;
  const creditCardMethod = data.methods?.find(m => m.payment_type === 'credit_card');

  const pieData = data.methods?.map(m => ({
    name: m.payment_type?.replace('_', ' ').toUpperCase(),
    value: m.total_payment_value,
    share: m.gmv_share_pct,
    color: METHOD_COLORS[m.payment_type] || '#94a3b8'
  })) || [];

  return (
    <div className="space-y-6">
      {/* 1. Payment KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Payment Volume"
          value={formatBRL(totalPaymentGMV)}
          subtitle="Processed Gross Volume"
          trend="up"
          trendValue="103k Transactions"
          icon={DollarSign}
          color="blue"
        />
        <KPICard
          title="Credit Card Dominance"
          value={`${creditCardMethod?.gmv_share_pct || 75.8}%`}
          subtitle={formatBRL(creditCardMethod?.total_payment_value)}
          trend="up"
          trendValue="Primary Rail"
          icon={CreditCard}
          color="green"
        />
        <KPICard
          title="Boleto Bancário Share"
          value="19.0%"
          subtitle="Cash Voucher Alternative"
          trend="neutral"
          trendValue="Bank Slip"
          icon={FileText}
          color="amber"
        />
        <KPICard
          title="Avg Card Financing"
          value="3.5x Installments"
          subtitle="Median 3.0 Months Term"
          trend="up"
          trendValue="Credit Driven"
          icon={Layers}
          color="purple"
        />
      </div>

      {/* 2. Visualizations: Method Share & Installments */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Payment Rail Share Donut */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">Payment Method GMV Share</h3>
                <p className="text-xs text-slate-500">Gross revenue breakdown by checkout gateway</p>
              </div>
              <PieIcon className="w-4 h-4 text-blue-600" />
            </div>

            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(val, name) => [formatBRL(val), name]}
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-2 mt-2 pt-3 border-t border-slate-100">
            {pieData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></span>
                  <span className="font-medium text-slate-700">{item.name}</span>
                </div>
                <div className="flex items-center space-x-2 font-bold text-slate-900">
                  <span>{formatBRL(item.value)}</span>
                  <span className="text-slate-400 font-normal">({item.share}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Credit Card Installments Distribution */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Credit Card Installments Breakdown</h3>
              <p className="text-xs text-slate-500">Frequency distribution of financing duration (1x up to 10x+ installments)</p>
            </div>
            <span className="text-xs font-semibold px-2 py-0.5 bg-blue-50 text-blue-700 rounded">
              Installment Terms
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.installments_distribution?.slice(0, 10)} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="payment_installments" tick={{ fontSize: 11, fill: '#64748b' }} tickFormatter={(v) => `${v}x`} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickFormatter={(v) => `${(v/1000).toFixed(0)}k`} />
                <Tooltip 
                  formatter={(val, name) => [name === 'count' ? `${val.toLocaleString()} orders` : formatBRL(val), name === 'count' ? 'Order Volume' : 'Total Financed']}
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} name="count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 3. Detailed Payment Methods Table */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Payment Gateway Performance & Unit Economics</h3>
            <p className="text-xs text-slate-500">Transaction counts, total volume, financing terms, and ticket values</p>
          </div>
          <span className="text-xs font-semibold px-2 py-1 bg-slate-100 text-slate-700 rounded">
            4 Methods
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold border-y border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Payment Method</th>
                <th className="py-2.5 px-3 text-right">Transactions</th>
                <th className="py-2.5 px-3 text-right">Txn Share %</th>
                <th className="py-2.5 px-3 text-right">Total GMV (R$)</th>
                <th className="py-2.5 px-3 text-right">GMV Share %</th>
                <th className="py-2.5 px-3 text-right">Avg Ticket (AOV)</th>
                <th className="py-2.5 px-3 text-center">Avg Financing Term</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {data.methods?.map((m) => (
                <tr key={m.payment_type} className="hover:bg-slate-50/80 transition">
                  <td className="py-3 px-3 font-bold text-slate-900 flex items-center space-x-2">
                    <span 
                      className="w-2.5 h-2.5 rounded-full shrink-0" 
                      style={{ backgroundColor: METHOD_COLORS[m.payment_type] || '#64748b' }}
                    ></span>
                    <span className="capitalize">{m.payment_type.replace('_', ' ')}</span>
                  </td>
                  <td className="py-3 px-3 text-right font-semibold text-slate-800">
                    {m.transaction_count?.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right text-slate-600">
                    {m.transaction_share_pct}%
                  </td>
                  <td className="py-3 px-3 text-right font-bold text-blue-600">
                    {formatBRL(m.total_payment_value)}
                  </td>
                  <td className="py-3 px-3 text-right font-bold text-slate-900">
                    {m.gmv_share_pct}%
                  </td>
                  <td className="py-3 px-3 text-right text-slate-700 font-semibold">
                    {formatBRL(m.avg_ticket_value)}
                  </td>
                  <td className="py-3 px-3 text-center font-bold text-slate-800">
                    {m.payment_type === 'credit_card' ? `${m.avg_installments}x Months` : '1.0x (Instant)'}
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
