import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

export const fetchDashboardOverview = async (params = {}) => {
  const response = await apiClient.get('/dashboard/overview', { params });
  return response.data;
};

export const fetchSalesTrends = async (params = {}) => {
  const response = await apiClient.get('/sales/trends', { params });
  return response.data;
};

export const fetchSalesCategories = async (limit = 25) => {
  const response = await apiClient.get('/sales/categories', { params: { limit } });
  return response.data;
};

export const fetchCustomerSegments = async () => {
  const response = await apiClient.get('/customers/segments');
  return response.data;
};

export const fetchCustomerRFM = async () => {
  const response = await apiClient.get('/customers/rfm');
  return response.data;
};

export const fetchProductPerformance = async (limit = 15) => {
  const response = await apiClient.get('/products/performance', { params: { limit } });
  return response.data;
};

export const fetchDeliveryOperations = async (params = {}) => {
  const response = await apiClient.get('/operations/delivery', { params });
  return response.data;
};

export const fetchPaymentAnalysis = async () => {
  const response = await apiClient.get('/payments/analysis');
  return response.data;
};

export const fetchReviewAnalysis = async () => {
  const response = await apiClient.get('/reviews/analysis');
  return response.data;
};

export const fetchDataQuality = async () => {
  const response = await apiClient.get('/data-quality');
  return response.data;
};

export const exportReportFile = (format = 'pdf') => {
  window.open(`${API_BASE_URL}/reports/export?format=${format}`, '_blank');
};

export default apiClient;
