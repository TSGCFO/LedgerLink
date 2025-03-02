import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AdvancedRuleBuilder from '../AdvancedRuleBuilder';
import rulesService from '../../../services/rulesService';

// Mocking the rulesService
jest.mock('../../../services/rulesService', () => ({
  getAvailableFields: jest.fn(),
  getOperatorChoices: jest.fn(),
  getCalculationTypes: jest.fn(),
  getConditionsSchema: jest.fn(),
  validateRuleValue: jest.fn(),
  validateConditions: jest.fn(),
  validateCalculations: jest.fn()
}));

describe('AdvancedRuleBuilder', () => {
  const mockGroupId = 'test-group-123';
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    // Default mock implementations
    rulesService.getAvailableFields.mockResolvedValue({
      'sku_quantity': { label: 'SKU Quantity', type: 'object' },
      'weight_lb': { label: 'Weight (lb)', type: 'number' }
    });
    
    rulesService.getOperatorChoices.mockResolvedValue({
      operators: [
        { value: 'contains', label: 'Contains' },
        { value: 'gt', label: 'Greater than' }
      ]
    });
    
    rulesService.getCalculationTypes.mockResolvedValue({
      'flat_fee': 'Flat Fee',
      'percentage': 'Percentage',
      'case_based_tier': 'Case-Based Tier'
    });
    
    rulesService.getConditionsSchema.mockResolvedValue({
      'fields': {
        'weight_lb': { 'type': 'number' },
        'sku_quantity': { 'type': 'object' }
      }
    });
    
    rulesService.validateRuleValue.mockResolvedValue(true);
    rulesService.validateConditions.mockResolvedValue(true);
    rulesService.validateCalculations.mockResolvedValue(true);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders case-based tier fields when case_based_tier type is selected', async () => {
    // Render the component
    render(
      <AdvancedRuleBuilder
        groupId={mockGroupId}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    );

    // Wait for the form to load
    await waitFor(() => {
      expect(rulesService.getAvailableFields).toHaveBeenCalled();
      expect(rulesService.getCalculationTypes).toHaveBeenCalled();
    });

    // Fill in basic rule details
    const fieldSelect = screen.getByLabelText(/Field/i);
    fireEvent.change(fieldSelect, { target: { value: 'sku_quantity' } });

    await waitFor(() => {
      expect(rulesService.getOperatorChoices).toHaveBeenCalledWith('sku_quantity');
    });

    const operatorSelect = screen.getByLabelText(/Operator/i);
    fireEvent.change(operatorSelect, { target: { value: 'contains' } });

    const valueInput = screen.getByLabelText(/Value/i);
    fireEvent.change(valueInput, { target: { value: 'SKU1' } });

    // Navigate to calculations step
    const continueButton = screen.getByText(/Continue/i);
    fireEvent.click(continueButton);
    // Second step to calculations
    fireEvent.click(continueButton);

    // Add a calculation
    const addCalculationButton = screen.getByText(/Add Calculation/i);
    fireEvent.click(addCalculationButton);

    // Select case_based_tier type
    const typeSelect = screen.getByLabelText(/Type/i);
    fireEvent.change(typeSelect, { target: { value: 'case_based_tier' } });

    // Check that tier fields are rendered
    await waitFor(() => {
      expect(screen.getByText(/Case-Based Tiers/i)).toBeInTheDocument();
      expect(screen.getAllByLabelText(/Min Cases/i).length).toBeGreaterThan(0);
      expect(screen.getAllByLabelText(/Max Cases/i).length).toBeGreaterThan(0);
      expect(screen.getAllByLabelText(/Price Multiplier/i).length).toBeGreaterThan(0);
      expect(screen.getByLabelText(/Excluded SKUs/i)).toBeInTheDocument();
    });

    // Test adding a new tier
    const addTierButton = screen.getByText(/Add Tier/i);
    fireEvent.click(addTierButton);

    await waitFor(() => {
      // Should now have one more tier than before
      const minCasesFields = screen.getAllByLabelText(/Min Cases/i);
      expect(minCasesFields.length).toBeGreaterThan(4); // Default 4 + 1 new
    });
  });

  test('form submission includes tier_config at root level', async () => {
    // Initial data with case-based tier
    const initialData = {
      id: 'test-rule-123',
      field: 'sku_quantity',
      operator: 'contains',
      value: 'SKU1',
      calculations: [
        { type: 'case_based_tier', value: 1.0 }
      ],
      tier_config: {
        ranges: [
          { min: 1, max: 3, multiplier: 1.0 },
          { min: 4, max: 6, multiplier: 2.0 }
        ],
        excluded_skus: ['SKU3']
      }
    };

    // Render with initial data
    render(
      <AdvancedRuleBuilder
        groupId={mockGroupId}
        initialData={initialData}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    );

    // Wait for the form to load
    await waitFor(() => {
      expect(rulesService.getAvailableFields).toHaveBeenCalled();
    });

    // Submit the form
    const submitButton = screen.getByText(/Update/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalled();
      const formData = mockOnSubmit.mock.calls[0][1]; // Second arg to onSubmit is the form data
      
      // Check that tier_config exists at the root level
      expect(formData.tier_config).toBeDefined();
      expect(formData.tier_config.ranges).toHaveLength(2);
      expect(formData.tier_config.excluded_skus).toContain('SKU3');
      
      // Check that calculations don't have duplicate tier_config
      expect(formData.calculations[0].tier_config).toBeUndefined();
    });
  });
});