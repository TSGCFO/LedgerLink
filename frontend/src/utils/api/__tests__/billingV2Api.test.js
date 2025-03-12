import { billingV2Api } from '../billingV2Api';
import { request } from '../../apiClient';

// Mock the request function
jest.mock('../../apiClient', () => {
  return {
    request: jest.fn().mockImplementation(() => {
      return Promise.resolve({
        success: true,
        data: [{ id: '123e4567-e89b-12d3-a456-426614174000' }]
      });
    })
  };
});

describe('billingV2Api module', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should export necessary methods', () => {
    // Verify all required methods are exported
    expect(billingV2Api.getBillingReports).toBeDefined();
    expect(billingV2Api.getBillingReport).toBeDefined();
    expect(billingV2Api.generateBillingReport).toBeDefined();
    expect(billingV2Api.downloadBillingReport).toBeDefined();
    expect(billingV2Api.getCustomerSummary).toBeDefined();
  });

  it('should call request with correct URL path for getBillingReports', async () => {
    await billingV2Api.getBillingReports();
    expect(request).toHaveBeenCalledWith('/api/v2/reports/', {}, false);
  });

  it('should call request with correct URL path for getBillingReport', async () => {
    const reportId = '123e4567-e89b-12d3-a456-426614174000';
    await billingV2Api.getBillingReport(reportId);
    expect(request).toHaveBeenCalledWith(`/api/v2/reports/${reportId}/`, {}, false);
  });

  it('should call request with correct URL path for generateBillingReport', async () => {
    const data = {
      customer_id: 1,
      start_date: '2023-01-01',
      end_date: '2023-01-31'
    };
    await billingV2Api.generateBillingReport(data);
    expect(request).toHaveBeenCalledWith('/api/v2/reports/generate/', {
      method: 'POST',
      body: JSON.stringify(data),
    }, false);
  });

  it('should use the correct URL format for getCustomerSummary', async () => {
    await billingV2Api.getCustomerSummary();
    expect(request).toHaveBeenCalledWith('/api/v2/reports/customer-summary/', {}, false);
    
    await billingV2Api.getCustomerSummary(1);
    expect(request).toHaveBeenCalledWith('/api/v2/reports/customer-summary/?customer_id=1', {}, false);
  });
});