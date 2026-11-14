import React from 'react';
import { Filter, Calendar, RotateCcw, MapPin, Tag } from 'lucide-react';

const stateOptions = [
  { value: '', label: 'All Regions / States' },
  { value: 'SP', label: 'São Paulo (SP)' },
  { value: 'RJ', label: 'Rio de Janeiro (RJ)' },
  { value: 'MG', label: 'Minas Gerais (MG)' },
  { value: 'RS', label: 'Rio Grande do Sul (RS)' },
  { value: 'PR', label: 'Paraná (PR)' },
  { value: 'SC', label: 'Santa Catarina (SC)' },
  { value: 'BA', label: 'Bahia (BA)' },
  { value: 'DF', label: 'Distrito Federal (DF)' },
  { value: 'GO', label: 'Goiás (GO)' },
  { value: 'PE', label: 'Pernambuco (PE)' }
];

const categoryOptions = [
  { value: '', label: 'All Product Categories' },
  { value: 'Bed Bath Table', label: 'Bed Bath Table' },
  { value: 'Health Beauty', label: 'Health Beauty' },
  { value: 'Sports Leisure', label: 'Sports Leisure' },
  { value: 'Furniture Decor', label: 'Furniture Decor' },
  { value: 'Computers Accessories', label: 'Computers Accessories' },
  { value: 'Housewares', label: 'Housewares' },
  { value: 'Watches Gifts', label: 'Watches Gifts' },
  { value: 'Telephony', label: 'Telephony' },
  { value: 'Garden Tools', label: 'Garden Tools' },
  { value: 'Auto', label: 'Auto' }
];

export default function Navbar({ 
  filters, 
  setFilters, 
  activePageTitle, 
  activePageSubtitle,
  onReset 
}) {
  const handleDatePreset = (preset) => {
    if (preset === 'all') {
      setFilters(prev => ({ ...prev, startDate: '', endDate: '' }));
    } else if (preset === '2017') {
      setFilters(prev => ({ ...prev, startDate: '2017-01-01', endDate: '2017-12-31' }));
    } else if (preset === '2018') {
      setFilters(prev => ({ ...prev, startDate: '2018-01-01', endDate: '2018-08-31' }));
    } else if (preset === 'peak') {
      setFilters(prev => ({ ...prev, startDate: '2017-11-01', endDate: '2017-12-31' }));
    }
  };

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-4 sticky top-0 z-20 shadow-sm">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* Page Title & Breadcrumb */}
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">{activePageTitle}</h2>
          <p className="text-xs text-slate-500 mt-0.5">{activePageSubtitle}</p>
        </div>

        {/* Global Filter Bar */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Quick Date Presets */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs font-medium">
            <button
              onClick={() => handleDatePreset('all')}
              className={`px-2.5 py-1 rounded-md transition ${!filters.startDate && !filters.endDate ? 'bg-white text-blue-600 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'}`}
            >
              All Time
            </button>
            <button
              onClick={() => handleDatePreset('2017')}
              className={`px-2.5 py-1 rounded-md transition ${filters.startDate === '2017-01-01' ? 'bg-white text-blue-600 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'}`}
            >
              2017
            </button>
            <button
              onClick={() => handleDatePreset('2018')}
              className={`px-2.5 py-1 rounded-md transition ${filters.startDate === '2018-01-01' ? 'bg-white text-blue-600 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'}`}
            >
              2018 YTD
            </button>
          </div>

          {/* Date Range Inputs */}
          <div className="flex items-center space-x-1.5 bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-xs">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => setFilters(prev => ({ ...prev, startDate: e.target.value }))}
              className="bg-transparent outline-none text-slate-700 text-xs w-28 cursor-pointer"
              title="Start Date"
            />
            <span className="text-slate-400">to</span>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => setFilters(prev => ({ ...prev, endDate: e.target.value }))}
              className="bg-transparent outline-none text-slate-700 text-xs w-28 cursor-pointer"
              title="End Date"
            />
          </div>

          {/* State Filter */}
          <div className="flex items-center space-x-1.5 bg-white border border-slate-300 rounded-lg px-2 py-1 text-xs">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filters.state}
              onChange={(e) => setFilters(prev => ({ ...prev, state: e.target.value }))}
              className="bg-transparent outline-none text-slate-700 text-xs cursor-pointer"
            >
              {stateOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Category Filter */}
          <div className="flex items-center space-x-1.5 bg-white border border-slate-300 rounded-lg px-2 py-1 text-xs">
            <Tag className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filters.category}
              onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
              className="bg-transparent outline-none text-slate-700 text-xs cursor-pointer max-w-[140px]"
            >
              {categoryOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Reset Filters */}
          {(filters.startDate || filters.endDate || filters.state || filters.category) && (
            <button
              onClick={onReset}
              className="flex items-center space-x-1 text-xs text-rose-600 hover:text-rose-700 font-medium px-2 py-1 rounded hover:bg-rose-50 transition"
              title="Clear all active filters"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
