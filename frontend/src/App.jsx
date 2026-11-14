import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import ExecutiveOverview from './pages/ExecutiveOverview';
import CustomerIntelligence from './pages/CustomerIntelligence';
import ProductAnalytics from './pages/ProductAnalytics';
import OperationsAnalytics from './pages/OperationsAnalytics';
import PaymentAnalytics from './pages/PaymentAnalytics';
import DataQuality from './pages/DataQuality';
import { fetchDashboardOverview, exportReportFile } from './services/api';

const pageTitles = {
  'overview': {
    title: 'Executive Performance Overview',
    subtitle: 'High-level business KPIs, longitudinal revenue growth, category performance, and geographical distribution'
  },
  'customers': {
    title: 'Customer Intelligence & RFM Segmentation',
    subtitle: 'Recency, Frequency, and Monetary quintile classification, repeat purchase dynamics, and retention playbooks'
  },
  'products': {
    title: 'Product Catalog & Category Performance',
    subtitle: 'Top revenue drivers, demand elasticity, price tier concentration, and lowest-velocity SKU diagnostics'
  },
  'operations': {
    title: 'Logistics & Operational Efficiency',
    subtitle: 'Door-to-door transit velocity, regional SLA bottlenecks, and empirical delivery delay impact on satisfaction'
  },
  'payments': {
    title: 'Payment Gateway & Installment Analytics',
    subtitle: 'Payment rail market share, financing duration analysis, and ticket economics'
  },
  'data-quality': {
    title: 'Data Quality Audit & Automated Reporting',
    subtitle: 'Transparent data health scoring, referential integrity verification, and one-click export center'
  }
};

export default function App() {
  const [activePage, setActivePage] = useState('overview');
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    state: '',
    category: ''
  });

  const [overviewData, setOverviewData] = useState(null);
  const [overviewLoading, setOverviewLoading] = useState(true);

  // Fetch overview whenever global filters change
  useEffect(() => {
    setOverviewLoading(true);
    const params = {};
    if (filters.startDate) params.start_date = filters.startDate;
    if (filters.endDate) params.end_date = filters.endDate;
    if (filters.state) params.state = filters.state;
    if (filters.category) params.category = filters.category;

    fetchDashboardOverview(params)
      .then(res => {
        setOverviewData(res);
        setOverviewLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch dashboard overview:", err);
        setOverviewLoading(false);
      });
  }, [filters]);

  const handleResetFilters = () => {
    setFilters({
      startDate: '',
      endDate: '',
      state: '',
      category: ''
    });
  };

  const handleExportPDF = () => {
    exportReportFile('pdf');
  };

  const currentPage = pageTitles[activePage] || pageTitles.overview;

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
      {/* Sidebar Navigation */}
      <Sidebar 
        activePage={activePage} 
        setActivePage={setActivePage} 
        onExportPDF={handleExportPDF}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Filter & Header Bar */}
        <Navbar 
          filters={filters} 
          setFilters={setFilters} 
          activePageTitle={currentPage.title}
          activePageSubtitle={currentPage.subtitle}
          onReset={handleResetFilters}
        />

        {/* Dynamic Page Container */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-7xl mx-auto">
            {activePage === 'overview' && (
              <ExecutiveOverview 
                data={overviewData} 
                loading={overviewLoading} 
                onSelectCategory={(cat) => setFilters(prev => ({ ...prev, category: cat }))}
              />
            )}
            {activePage === 'customers' && (
              <CustomerIntelligence filters={filters} />
            )}
            {activePage === 'products' && (
              <ProductAnalytics filters={filters} />
            )}
            {activePage === 'operations' && (
              <OperationsAnalytics filters={filters} />
            )}
            {activePage === 'payments' && (
              <PaymentAnalytics filters={filters} />
            )}
            {activePage === 'data-quality' && (
              <DataQuality />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
