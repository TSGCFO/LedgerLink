import { request } from '../apiClient';

/**
 * API client for Billing V2 endpoints
 */
export const billingV2Api = {
  /**
   * Get a list of billing reports (with optional filters)
   * @param {Object} filters - Filter parameters
   * @returns {Promise} Promise with response
   */
  getBillingReports: async (filters = {}) => {
    const queryParams = new URLSearchParams();
    
    if (filters.customerId) queryParams.append('customer_id', filters.customerId);
    if (filters.startDate) queryParams.append('start_date', filters.startDate);
    if (filters.endDate) queryParams.append('end_date', filters.endDate);
    if (filters.createdAfter) queryParams.append('created_after', filters.createdAfter);
    if (filters.createdBefore) queryParams.append('created_before', filters.createdBefore);
    if (filters.orderBy) queryParams.append('order_by', filters.orderBy);
    
    const queryString = queryParams.toString();
    return request(`/api/v1/billing-v2/reports/${queryString ? `?${queryString}` : ''}`, {}, false);
  },
  
  /**
   * Get a single billing report by ID
   * @param {number} reportId - Report ID
   * @returns {Promise} Promise with response
   */
  getBillingReport: async (reportId) => {
    return request(`/api/v1/billing-v2/reports/${reportId}/`, {}, false);
  },
  
  /**
   * Generate a new billing report
   * @param {Object} data - Report generation data
   * @returns {Promise} Promise with response
   */
  generateBillingReport: async (data) => {
    return request('/api/v1/billing-v2/reports/generate/', {
      method: 'POST',
      body: JSON.stringify(data),
    }, false);
  },
  
  /**
   * Download a report in specified format
   * @param {number} reportId - Report ID
   * @param {string} format - Format (csv, json, pdf)
   * @returns {Promise} Promise with response
   */
  downloadBillingReport: async (reportId, format = 'csv') => {
    // For direct file download, we need to use the browser's download capabilities
    const url = `/api/v1/billing-v2/reports/${reportId}/download/?format=${format}`;
    window.open(url, '_blank');
    return true;
  },
  
  /**
   * Get customer summary data
   * @param {number} customerId - Optional customer ID filter
   * @returns {Promise} Promise with response
   */
  getCustomerSummary: async (customerId = null) => {
    const queryParams = new URLSearchParams();
    if (customerId) queryParams.append('customer_id', customerId);
    
    const queryString = queryParams.toString();
    return request(`/api/v1/billing-v2/reports/customer-summary/${queryString ? `?${queryString}` : ''}`, {}, false);
  }
};

export default billingV2Api;