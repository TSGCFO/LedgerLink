import { getAccessToken, refreshAccessToken, logout } from './auth';
import logger from './logger';

const API_BASE_URL = '/api/v1';

/**
 * Generic request handler with error handling and token management
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function request(endpoint, options = {}, useBaseUrl = true) {
  const url = useBaseUrl ? `${API_BASE_URL}${endpoint}` : endpoint;
  const token = getAccessToken();
  const csrfToken = getCookie('csrftoken');

  const headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken,
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers,
  };

  const requestOptions = {
    ...options,
    headers,
    credentials: 'include',
    mode: 'cors',
  };

  try {
    logger.logApiRequest(options.method || 'GET', url, requestOptions);
    const response = await fetch(url, requestOptions);
    
    // Log redirect responses
    if (response.status >= 300 && response.status < 400) {
      logger.info(`Redirect response received: ${response.status}`, {
        location: response.headers.get('location'),
        status: response.status
      });
      return { success: true };
    }
    
    if (response.status === 401) {
      logger.warn('Authentication failed, attempting token refresh', {
        url,
        originalStatus: response.status
      });
      
      try {
        const newToken = await refreshAccessToken();
        logger.info('Token refresh successful, retrying original request');
        
        // Retry the request with new token
        const retryOptions = {
          ...requestOptions,
          headers: {
            ...requestOptions.headers,
            'Authorization': `Bearer ${newToken}`,
          },
        };
        
        logger.logApiRequest(`${options.method || 'GET'} (Retry)`, url, retryOptions);
        const retryResponse = await fetch(url, retryOptions);
        const data = await retryResponse.json();
        logger.logApiResponse(`${options.method || 'GET'} (Retry)`, url, retryResponse, data);

        if (!retryResponse.ok) {
          const error = {
            status: retryResponse.status,
            message: data.detail || 'An error occurred',
            data: data
          };
          logger.error('Retry request failed after token refresh', error);
          throw error;
        }

        return data;
      } catch (refreshError) {
        logger.error('Token refresh failed, logging out user', refreshError);
        logout();
        throw {
          status: 401,
          message: 'Session expired. Please log in again.',
          originalError: refreshError
        };
      }
    }

    // Handle redirect responses (302, 301, etc.) as successful operations
    if (response.status >= 300 && response.status < 400) {
      return { success: true };
    }

    try {
      const data = await response.json();
      logger.logApiResponse(options.method || 'GET', url, response, data);

      if (!response.ok) {
        const error = {
          status: response.status,
          message: data.detail || data.message || 'An error occurred',
          data: data
        };
        logger.error(`API Error Response: ${response.status}`, error);
        throw error;
      }

      return data;
    } catch (jsonError) {
      // For successful responses that don't return JSON
      if (response.ok) {
        logger.info('Non-JSON success response', {
          status: response.status,
          url: url
        });
        return { success: true };
      }
      // For error responses that don't return JSON
      const error = {
        status: response.status,
        message: 'Invalid response from server',
        originalError: jsonError
      };
      logger.error('JSON Parsing Error', error);
      throw error;
    }
  } catch (error) {
    logger.logApiError(options.method || 'GET', url, error);
    throw error;
  }
}

/**
 * Rules API endpoints
 */
export const rulesApi = {
  // Rule Groups
  listGroups: () => request('/rules/api/groups/'),
  getGroup: (id) => request(`/rules/group/${id}/`),
  createGroup: (data) => request('/rules/api/groups/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  updateGroup: (id, data) => request(`/rules/group/${id}/edit/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  deleteGroup: (id) => request(`/rules/group/${id}/delete/api/`, {
    method: 'DELETE',
  }),

  // Basic Rules
  listRules: (groupId) => request(`/rules/group/${groupId}/rules/`),
  createRule: (groupId, data) => request(`/rules/group/${groupId}/rule/create/api/`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  updateRule: (id, data) => request(`/rules/rule/${id}/edit/api/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  deleteRule: (id) => request(`/rules/rule/${id}/delete/api/`, {
    method: 'DELETE',
  }),

  // Advanced Rules
  listAdvancedRules: (groupId) => request(`/rules/group/${groupId}/advanced-rules/`),
  createAdvancedRule: (groupId, data) => request(`/rules/group/${groupId}/advanced-rule/create/`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  updateAdvancedRule: (id, data) => request(`/rules/advanced-rule/${id}/edit/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  deleteAdvancedRule: (id) => request(`/rules/advanced-rule/${id}/delete/`, {
    method: 'DELETE',
  }),

  // Utility Endpoints
  getOperatorChoices: (field) => request(`/rules/operators/?field=${field}`),
  validateConditions: (conditions) => request('/rules/validate-conditions/', {
    method: 'POST',
    body: JSON.stringify({ conditions }),
  }),
  validateCalculations: (calculations) => request('/rules/validate-calculations/', {
    method: 'POST',
    body: JSON.stringify({ calculations }),
  }),
  getConditionsSchema: () => request('/rules/conditions-schema/'),
  getCalculationsSchema: () => request('/rules/calculations-schema/'),
  getAvailableFields: () => request('/rules/fields/'),
  getCalculationTypes: () => request('/rules/calculation-types/'),
  validateRuleValue: (data) => request('/rules/validate-rule-value/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getCustomerSkus: (groupId) => request(`/rules/group/${groupId}/skus/`),
};

/**
 * Customer API endpoints
 */
export const customerApi = {
  list: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.search) queryParams.append('search', params.search);
    if (params.business_type) queryParams.append('business_type', params.business_type);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return request(`/customers/${query}`);
  },
  get: (id) => request(`/customers/${id}/`),
  create: (data) => request('/customers/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => request(`/customers/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => request(`/customers/${id}/`, {
    method: 'DELETE',
  }),
};

/**
 * Customer Services API endpoints
 */
export const customerServiceApi = {
  list: async (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.search) queryParams.append('search', params.search);
    if (params.customer) queryParams.append('customer', params.customer);
    if (params.service) queryParams.append('service', params.service);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    const response = await request(`/customer-services/${query}`);
    return {
      success: true,
      data: response.data || []
    };
  },
  get: (id) => request(`/customer-services/${id}/`),
  create: (data) => request('/customer-services/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => request(`/customer-services/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => request(`/customer-services/${id}/`, {
    method: 'DELETE',
  }),
  addSkus: (id, data) => request(`/customer-services/${id}/add_skus/`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};

/**
 * Services API endpoints
 */
export const serviceApi = {
  list: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.search) queryParams.append('search', params.search);
    if (params.charge_type) queryParams.append('charge_type', params.charge_type);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return request(`/services/${query}`);
  },
  get: (id) => request(`/services/${id}/`),
  create: (data) => request('/services/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => request(`/services/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => request(`/services/${id}/`, {
    method: 'DELETE',
  }),
  getChargeTypes: () => request('/services/charge_types/'),
};

/**
 * Products API endpoints
 */
export const productApi = {
  list: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.search) queryParams.append('search', params.search);
    if (params.customer) queryParams.append('customer', params.customer);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return request(`/products/${query}`);
  },
  getStats: () => request('/products/stats/'),
  get: (id) => request(`/products/${id}/`),
  create: (data) => request('/products/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => request(`/products/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => request(`/products/${id}/`, {
    method: 'DELETE',
  }),
  getSkusByCustomer: (customerId) => request(`/products/?customer=${customerId}`),
};

/**
 * Orders API endpoints
 */
export const orderApi = {
  list: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.search) queryParams.append('search', params.search);
    if (params.status) queryParams.append('status', params.status);
    if (params.priority) queryParams.append('priority', params.priority);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return request(`/orders/${query}`);
  },
  get: (id) => request(`/orders/${id}/`),
  create: (data) => request('/orders/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => request(`/orders/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => request(`/orders/${id}/`, {
    method: 'DELETE',
  }),
  cancel: (id) => request(`/orders/${id}/cancel/`, {
    method: 'POST',
  }),
  getChoices: () => request('/orders/choices/'),
  getStatusCounts: () => request('/orders/status_counts/'),
};

/**
 * Inserts API endpoints
 */
export const insertApi = {
  list: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.search) queryParams.append('search', params.search);
    if (params.customer) queryParams.append('customer', params.customer);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return request(`/inserts/${query}`);
  },
  get: (id) => request(`/inserts/${id}/`),
  create: (data) => request('/inserts/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => request(`/inserts/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => request(`/inserts/${id}/`, {
    method: 'DELETE',
  }),
  getStats: () => request('/inserts/stats/'),
  updateQuantity: (id, quantity, operation) => request(`/inserts/${id}/update_quantity/`, {
    method: 'POST',
    body: JSON.stringify({ quantity, operation }),
  }),
};

/**
 * US Shipping API endpoints
 */
export const usShippingApi = {
  list: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.search) queryParams.append('search', params.search);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return request(`/shipping/us/${query}`);
  },
  get: (id) => request(`/shipping/us/${id}/`),
  create: (data) => request('/shipping/us/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => request(`/shipping/us/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => request(`/shipping/us/${id}/`, {
    method: 'DELETE',
  }),
  // Add missing methods
  getStatuses: () => request('/shipping/us/statuses/'),
};

/**
 * CAD Shipping API endpoints
 */
export const cadShippingApi = {
  list: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.search) queryParams.append('search', params.search);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return request(`/shipping/cad/${query}`);
  },
  get: (id) => request(`/shipping/cad/${id}/`),
  create: (data) => request('/shipping/cad/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => request(`/shipping/cad/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => request(`/shipping/cad/${id}/`, {
    method: 'DELETE',
  }),
  // Add missing method
  getCarriers: () => request('/shipping/cad/carriers/'),
};

export const handleApiError = (error) => {
  if (!error) {
    logger.error('Unknown API error', { error: 'No error object provided' });
    return 'An unknown error occurred.';
  }

  // Handle network errors
  if (error instanceof TypeError && error.message === 'Failed to fetch') {
    logger.error('Network Error', {
      type: 'NetworkError',
      message: error.message,
      stack: error.stack
    });
    return 'Network error. Please check your connection.';
  }

  // Log detailed error information
  const errorDetails = {
    status: error.status,
    message: error.message,
    originalError: error.originalError || null,
    data: error.data || null,
    stack: error.stack || null
  };

  switch (error.status) {
    case 404:
      logger.error('Resource Not Found', errorDetails);
      return 'The requested resource was not found.';
    case 401:
      logger.error('Authentication Error', errorDetails);
      return 'Please log in to continue.';
    case 403:
      logger.error('Authorization Error', errorDetails);
      return 'You do not have permission to perform this action.';
    case 400:
      logger.error('Bad Request', errorDetails);
      return error.message || 'Invalid request. Please check your input.';
    case 500:
      logger.error('Server Error', errorDetails);
      return 'Server error. Please try again later.';
    default:
      logger.error('Unexpected API Error', errorDetails);
      return error.message || 'An unexpected error occurred. Please try again later.';
  }
};

export default {
  customerApi,
  customerServiceApi,
  serviceApi,
  productApi,
  orderApi,
  insertApi,
  cadShippingApi,
  usShippingApi,
  rulesApi,
  handleApiError,
};