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
    // For CSV downloads, use a different approach
    if (data.output_format === 'csv') {
      // Get CSRF token
      const csrfToken = document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
        
      // Make a direct fetch request to handle the file download
      const response = await fetch('/api/v1/billing-v2/reports/generate/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json'  // This was missing - causing 415 error
        },
        body: JSON.stringify(data),
        credentials: 'include',
      });
      
      // Check if response is ok
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }
      
      // Get the filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'billing_report.csv';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+?)"/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      }
      
      // Create a blob from the response and download it
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      
      return { success: true };
    }
    
    // For other formats, use the normal request function
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
  },

  /**
   * Get customer services for a specific customer
   * @param {number} customerId - Customer ID
   * @returns {Promise} Promise with response
   */
  getCustomerServices: async (customerId) => {
    if (!customerId) {
      throw new Error('Customer ID is required');
    }
    return request(`/api/v1/billing-v2/reports/customer-services/${customerId}/`, {}, false);
  },
  
  /**
   * Check progress of a report generation
   * @param {Object} params - Parameters matching the report generation request
   * @returns {Promise} Promise with response
   */
  getReportProgress: async (params) => {
    if (!params.customer_id || !params.start_date || !params.end_date) {
      throw new Error('Missing required parameters: customer_id, start_date, end_date');
    }
    
    const queryParams = new URLSearchParams();
    queryParams.append('customer_id', params.customer_id);
    queryParams.append('start_date', params.start_date);
    queryParams.append('end_date', params.end_date);
    
    // Add a cache-busting timestamp to prevent browser caching
    queryParams.append('_t', Date.now());
    
    return request(`/api/v1/billing-v2/reports/progress/?${queryParams.toString()}`, {
      // Add no-cache headers to prevent caching of progress responses
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    }, false);
  }
};

export default billingV2Api;