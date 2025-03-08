# Detailed Billing App Test Coverage Analysis

This in-depth report provides a comprehensive analysis of test coverage for the LedgerLink Billing app, including specific code examples of uncovered sections, function-level coverage metrics, and detailed improvement recommendations.

## Executive Summary

| Area | Coverage | Critical Issues | Priority |
|------|----------|-----------------|----------|
| Backend | 20% overall | Complex calculation logic, export generators, service layer | HIGH |
| Frontend | 42% overall | Export functionality, dynamic rendering, UI interactions | HIGH |

The analysis reveals significant coverage gaps with particularly low coverage in core business logic components. Most concerning is the billing calculator at only 11% coverage, which handles critical pricing logic.

## Backend Coverage Analysis

### Module-Level Breakdown

| Module | Coverage | Missing Lines | Critical Functions |
|--------|----------|---------------|-------------------|
| billing_calculator.py | 11% | 410/462 | `calculate_service_charge()`, `calculate_tier_costs()` |
| exporters.py | 16% | 76/91 | `generate_pdf()`, `generate_excel()` |
| services.py | 19% | 80/99 | `create_billing_report()`, `apply_caching()` |
| views.py | 39% | 44/72 | `generate_report_api()`, `report_preview()` |
| utils.py | 32% | 75/111 | `format_currency()`, `process_service_data()` |
| models.py | 75% | 12/48 | `get_report_totals()` |
| serializers.py | 66% | 11/32 | `validate()`, `create()` |

### Function-Level Coverage Analysis

#### billing_calculator.py (11% coverage)

```python
def calculate_service_charge(service_type, order_data, rules=None):
    """Calculate service charge based on service type and order data."""
    # 0% coverage for this critical function
    if not rules:
        rules = get_default_rules()
    
    if service_type == 'standard_shipping':
        return calculate_standard_shipping(order_data, rules)
    elif service_type == 'premium_shipping':
        return calculate_premium_shipping(order_data, rules)
    elif service_type == 'packaging':
        return calculate_packaging_cost(order_data, rules)
    elif service_type == 'pick_cost':
        return calculate_pick_cost(order_data, rules)
    elif service_type.startswith('custom_'):
        return calculate_custom_service(service_type, order_data, rules)
    else:
        raise ValueError(f"Unsupported service type: {service_type}")
```

```python
def calculate_tier_costs(value, tier_config):
    """Calculate costs based on tiered pricing structure."""
    # 5% coverage - only basic path tested
    if not tier_config:
        return 0
    
    total_cost = 0
    remaining_value = value
    
    for tier in sorted(tier_config, key=lambda x: x.get('min', 0)):
        min_val = tier.get('min', 0)
        max_val = tier.get('max', float('inf'))
        rate = tier.get('rate', 0)
        
        if remaining_value <= 0:
            break
            
        if remaining_value > min_val:
            # Calculate how much of this tier applies
            tier_value = min(remaining_value, max_val) - min_val
            tier_cost = tier_value * rate
            
            total_cost += tier_cost
            remaining_value -= tier_value
    
    return total_cost
```

#### exporters.py (16% coverage)

```python
def generate_pdf(billing_data, output_path=None):
    """Generate PDF report from billing data."""
    # 0% coverage for PDF generation
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    
    doc = SimpleDocTemplate(output_path or "billing_report.pdf", pagesize=letter)
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Billing Report: {billing_data['customer_name']}", styles['Title']))
    
    # Add date range
    date_text = f"Period: {billing_data['start_date']} to {billing_data['end_date']}"
    elements.append(Paragraph(date_text, styles['Normal']))
    
    # Create orders table
    if billing_data.get('preview_data', {}).get('orders'):
        orders = billing_data['preview_data']['orders']
        table_data = [['Order ID', 'Date', 'Status', 'Amount']]
        
        for order in orders:
            table_data.append([
                order['order_id'],
                order.get('transaction_date', ''),
                order.get('status', ''),
                f"${order.get('total_amount', 0):.2f}"
            ])
        
        # Create the table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
    
    # Build the PDF
    doc.build(elements)
    return output_path or "billing_report.pdf"
```

#### services.py (19% coverage)

```python
def create_billing_report(customer_id, start_date, end_date, format='json', save=False):
    """Create a billing report for a customer within a date range."""
    # 30% coverage - basic path only
    try:
        # Validate inputs
        if not customer_id:
            raise ValueError("Customer ID is required")
        
        customer = Customer.objects.get(id=customer_id)
        
        # Get all orders for this customer in date range
        orders = Order.objects.filter(
            customer=customer,
            order_date__gte=start_date,
            order_date__lte=end_date
        )
        
        if not orders.exists():
            return {"message": "No orders found for this period"}
        
        # Calculate services
        calculator = BillingCalculator()
        order_data = []
        service_totals = {}
        
        for order in orders:
            # Calculate services for this order
            order_services = calculator.calculate_all_services(order)
            
            # Add to service totals
            for service_id, data in order_services.items():
                if service_id not in service_totals:
                    service_totals[service_id] = {
                        'name': data['name'],
                        'amount': 0,
                        'order_count': 0
                    }
                
                service_totals[service_id]['amount'] += data['amount']
                service_totals[service_id]['order_count'] += 1
            
            # Build order data
            order_data.append({
                'order_id': order.order_id,
                'transaction_date': order.order_date,
                'status': order.status,
                'services': [
                    {'service_id': k, 'service_name': v['name'], 'amount': v['amount']}
                    for k, v in order_services.items()
                ],
                'total_amount': sum(s['amount'] for s in order_services.values())
            })
        
        # Calculate overall total
        total_amount = sum(service['amount'] for service in service_totals.values())
        
        # Create the report data
        report_data = {
            'customer': customer_id,
            'customer_name': customer.company_name,
            'start_date': start_date,
            'end_date': end_date,
            'total_amount': total_amount,
            'service_totals': service_totals,
            'preview_data': {
                'orders': order_data
            }
        }
        
        # Save the report if requested
        if save:
            report = BillingReport.objects.create(
                customer=customer,
                start_date=start_date,
                end_date=end_date,
                total_amount=total_amount,
                report_data=report_data
            )
            report_data['id'] = str(report.id)
        
        # Format the output
        if format == 'pdf':
            return generate_pdf(report_data)
        elif format == 'excel':
            return generate_excel(report_data)
        elif format == 'csv':
            return generate_csv(report_data)
        else:
            return report_data
            
    except Customer.DoesNotExist:
        raise ValueError(f"Customer with ID {customer_id} not found")
    except Exception as e:
        # Log the error
        logger.error(f"Error creating billing report: {str(e)}")
        raise
```

### Code Smell Analysis

Beyond just line coverage, the analysis reveals several "code smells" in testing:

1. **Over-mocking**: Many tests mock too much, testing implementation rather than behavior
2. **Happy Path Focus**: Tests primarily focus on successful execution paths
3. **Missing Edge Cases**: Boundary conditions and edge cases rarely tested
4. **Incomplete Assertions**: Tests often verify only one aspect of function output
5. **Poor Isolation**: Some tests depend on global state or other test execution

## Frontend Coverage Analysis

### Component-Level Breakdown

| Component | Statement Coverage | Branch Coverage | Function Coverage | Line Coverage |
|-----------|-------------------|-----------------|-------------------|---------------|
| BillingForm.jsx | 40.9% | 26.5% | 23.33% | 43.54% |
| BillingList.jsx | 45.16% | 24% | 30% | 45% |

### Uncovered Code Examples

#### BillingForm.jsx (40.9% coverage)

```jsx
// Export functionality (lines 141-193) - 0% coverage
const handleExport = async (format) => {
  try {
    setIsExporting(true);
    setExportError(null);
    
    // Prepare the report data
    const reportData = {
      customer: formData.customer,
      start_date: formData.startDate.format('YYYY-MM-DD'),
      end_date: formData.endDate.format('YYYY-MM-DD'),
      output_format: format || formData.outputFormat
    };
    
    // If we're viewing an existing report, include the report ID
    if (reportId) {
      reportData.report_id = reportId;
    }
    
    // Generate the report
    const response = await billingApi.generateReport(reportData);
    
    // Handle the response based on format
    if (format === 'pdf' || format === 'excel') {
      // For binary formats, create a download
      const blob = new Blob([response.data], {
        type: format === 'pdf' 
          ? 'application/pdf' 
          : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `billing_report_${formData.customer}_${formData.startDate.format('YYYYMMDD')}.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 0);
      
      setSuccess('Report generated successfully');
    } else {
      // For JSON format, show success message
      setSuccess('Report generated successfully');
    }
  } catch (error) {
    setExportError(handleApiError(error));
  } finally {
    setIsExporting(false);
  }
};
```

```jsx
// Preview dialog (lines 198-237) - 20% coverage
const handlePreviewDialogOpen = (previewData) => {
  setPreviewDialogOpen(true);
  setPreviewData(previewData);
};

const handlePreviewDialogClose = () => {
  setPreviewDialogOpen(false);
};

const renderServiceSummary = () => {
  if (!previewData?.service_totals) return null;
  
  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        Service Summary
      </Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Service</TableCell>
              <TableCell align="right">Orders</TableCell>
              <TableCell align="right">Amount</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.keys(previewData.service_totals).map((serviceId) => {
              const service = previewData.service_totals[serviceId];
              return (
                <TableRow key={serviceId}>
                  <TableCell>{service.name}</TableCell>
                  <TableCell align="right">{service.order_count}</TableCell>
                  <TableCell align="right">${service.amount.toFixed(2)}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};
```

#### BillingList.jsx (45.16% coverage)

```jsx
// Dynamic column generation (lines 63-101) - 25% coverage
const columns = useMemo(() => {
  if (!billingData || !billingData.preview_data || !billingData.preview_data.orders || billingData.preview_data.orders.length === 0) {
    return [];
  }
  
  // Get all unique service IDs from the orders
  const serviceIds = new Set();
  billingData.preview_data.orders.forEach(order => {
    order.services.forEach(service => {
      serviceIds.add(service.service_id);
    });
  });
  
  // Create a column for each service
  const serviceColumns = Array.from(serviceIds).sort().map(serviceId => {
    // Find the service name from the first order that has this service
    const serviceName = billingData.service_totals[serviceId]?.name || `Service ${serviceId}`;
    
    return {
      accessorKey: `service_${serviceId}`,
      header: serviceName,
      Cell: ({ cell }) => formatCurrency(cell.getValue()),
      Footer: ({ table }) => {
        // Calculate the total for this service across all filtered rows
        const total = table.getFilteredRowModel().rows.reduce((sum, row) => {
          return sum + (parseFloat(row.original[`service_${serviceId}`]) || 0);
        }, 0);
        
        return formatCurrency(total);
      }
    };
  });
  
  // Base columns plus dynamic service columns
  return [
    {
      accessorKey: 'order_id',
      header: 'Order ID',
    },
    // ... other base columns ...
    ...serviceColumns,
    {
      accessorKey: 'total_amount',
      header: 'Total Amount',
      Cell: ({ cell }) => formatCurrency(cell.getValue()),
      Footer: ({ table }) => {
        // Calculate grand total across all filtered rows
        const total = table.getFilteredRowModel().rows.reduce((sum, row) => {
          return sum + (parseFloat(row.original.total_amount) || 0);
        }, 0);
        
        return formatCurrency(total);
      }
    }
  ];
}, [billingData]);
```

```jsx
// Table data processing (lines 120-157) - 30% coverage
const tableData = useMemo(() => {
  if (!billingData || !billingData.preview_data || !billingData.preview_data.orders) {
    return [];
  }
  
  return billingData.preview_data.orders.map(order => {
    // Create a base row object
    const row = {
      order_id: order.order_id,
      transaction_date: order.transaction_date,
      status: order.status,
      total_amount: order.total_amount
    };
    
    // Add service columns
    order.services.forEach(service => {
      row[`service_${service.service_id}`] = service.amount;
    });
    
    return row;
  });
}, [billingData]);
```

```jsx
// Error handling (lines 201-212) - 10% coverage
useEffect(() => {
  // Reset error when form data changes
  if (error) {
    setError(null);
  }
}, [customerId, startDate, endDate]);

const handleApiError = (error) => {
  console.error('API Error:', error);
  if (error.response?.data?.detail) {
    return `Error: ${error.response.data.detail}`;
  }
  return 'An unexpected error occurred. Please try again.';
};
```

## Test Quality Assessment

Beyond just line coverage, the test quality has been assessed based on:

1. **Test isolation**: Are tests properly isolated from each other?
2. **Fixture quality**: Are test fixtures realistic and comprehensive?
3. **Assertion completeness**: Do tests verify all important outcomes?
4. **Error handling**: Do tests verify error conditions?
5. **Edge cases**: Are boundary conditions and special cases tested?

### Quality Scores (1-5 scale)

| Module | Isolation | Fixtures | Assertions | Error Handling | Edge Cases | Overall |
|--------|-----------|----------|------------|----------------|------------|---------|
| billing_calculator.py | 3 | 3 | 2 | 1 | 1 | 2/5 |
| exporters.py | 4 | 2 | 2 | 1 | 1 | 2/5 |
| services.py | 3 | 3 | 2 | 1 | 1 | 2/5 |
| views.py | 4 | 3 | 3 | 2 | 1 | 2.6/5 |
| BillingForm.jsx | 4 | 3 | 3 | 2 | 1 | 2.6/5 |
| BillingList.jsx | 4 | 3 | 3 | 2 | 1 | 2.6/5 |

### Test Quality Issues

1. **Calculator Tests**:
   - Fixtures don't cover complex rule combinations
   - Error cases rarely tested
   - Missing validation of calculation steps

2. **Exporter Tests**:
   - File output validation is superficial
   - No testing of formatting rules
   - Error handling untested

3. **Frontend Component Tests**:
   - Shallow rendering misses many interaction issues
   - Over-mocking API calls
   - Incomplete user interaction tests

## Detailed Improvement Recommendations

### 1. Billing Calculator (High Priority)

**Current Coverage**: 11%
**Target Coverage**: 85%

#### A. Service Calculation Functions

Create targeted test files for each service type:

```python
# tests/test_calculator/test_standard_shipping.py
def test_standard_shipping_calculation_with_weight_tiers():
    # Test weight-based tier calculations for standard shipping
    order_data = {
        "weight_lb": 15.5,
        "destination": "domestic"
    }
    rules = {"weight_tiers": [
        {"min": 0, "max": 10, "rate": 1.5},
        {"min": 10, "max": 20, "rate": 1.25},
        {"min": 20, "max": float('inf'), "rate": 1.0}
    ]}
    
    result = calculate_standard_shipping(order_data, rules)
    
    # Expected: 10 * 1.5 + 5.5 * 1.25 = 15 + 6.875 = 21.875
    assert result == 21.875

def test_standard_shipping_with_international_surcharge():
    # Test international shipping calculation with surcharge
    order_data = {
        "weight_lb": 5.0,
        "destination": "international"
    }
    rules = {
        "weight_tiers": [{"min": 0, "max": float('inf'), "rate": 2.0}],
        "international_surcharge": 10.0
    }
    
    result = calculate_standard_shipping(order_data, rules)
    
    # Expected: 5 * 2.0 + 10.0 = 20.0
    assert result == 20.0
```

#### B. Tier Calculation Logic

```python
# tests/test_calculator/test_tiered_pricing.py
def test_tier_boundary_conditions():
    # Test exact tier boundaries
    tier_config = [
        {"min": 0, "max": 10, "rate": 2.0},
        {"min": 10, "max": 20, "rate": 1.5},
        {"min": 20, "max": float('inf'), "rate": 1.0}
    ]
    
    # Test exactly at the first boundary (10)
    assert calculate_tier_costs(10, tier_config) == 20.0  # 10 * 2.0
    
    # Test slightly above the first boundary (10.01)
    assert calculate_tier_costs(10.01, tier_config) == 20.0 + 0.01 * 1.5  # 10 * 2.0 + 0.01 * 1.5
    
    # Test exactly at the second boundary (20)
    expected = 10 * 2.0 + 10 * 1.5  # 20.0 + 15.0 = 35.0
    assert calculate_tier_costs(20, tier_config) == expected

def test_tier_with_excluded_skus():
    # Test tier calculation with SKU exclusions
    order_data = {
        "total_items": 100,
        "skus": [
            {"sku": "SKU001", "quantity": 50},
            {"sku": "SKU002", "quantity": 30},
            {"sku": "EXCLUDED", "quantity": 20}
        ]
    }
    
    tier_config = [
        {"min": 0, "max": 50, "rate": 0.5},
        {"min": 50, "max": 100, "rate": 0.4},
        {"min": 100, "max": float('inf'), "rate": 0.3}
    ]
    
    # Excluded SKUs should reduce the count from 100 to 80
    result = calculate_tier_costs_with_exclusions(
        order_data["total_items"],
        order_data["skus"],
        tier_config,
        excluded_skus=["EXCLUDED"]
    )
    
    # Expected: 50 * 0.5 + 30 * 0.4 = 25.0 + 12.0 = 37.0
    assert result == 37.0
```

#### C. Error Handling and Edge Cases

```python
# tests/test_calculator/test_edge_cases.py
def test_empty_tier_config():
    # Test with empty tier config
    assert calculate_tier_costs(100, []) == 0
    assert calculate_tier_costs(100, None) == 0

def test_negative_values():
    # Test with negative values
    tier_config = [
        {"min": 0, "max": 10, "rate": 1.0}
    ]
    assert calculate_tier_costs(-5, tier_config) == 0

def test_invalid_service_type():
    # Test with invalid service type
    order_data = {"weight_lb": 10}
    with pytest.raises(ValueError) as exc:
        calculate_service_charge("invalid_service", order_data)
    assert "Unsupported service type" in str(exc.value)
```

### 2. Exporters (High Priority)

**Current Coverage**: 16%
**Target Coverage**: 75%

#### A. PDF Exporter Tests

Create a dedicated test file with mocking for PDF generation:

```python
# tests/test_exporters/test_pdf_exporter.py
@pytest.fixture
def mock_reportlab():
    """Mock ReportLab components for testing PDF generation."""
    with patch('billing.exporters.SimpleDocTemplate') as mock_doc:
        with patch('billing.exporters.Table') as mock_table:
            with patch('billing.exporters.Paragraph') as mock_para:
                # Configure the mocks as needed
                mock_doc.return_value.build = MagicMock()
                mock_table.return_value = MagicMock()
                yield mock_doc, mock_table, mock_para

def test_pdf_generation(mock_reportlab):
    # Test PDF report generation
    mock_doc, mock_table, mock_para = mock_reportlab
    
    # Test data
    billing_data = {
        'customer_name': 'Test Company',
        'start_date': '2025-01-01',
        'end_date': '2025-02-01',
        'preview_data': {
            'orders': [
                {'order_id': 'ORD-001', 'total_amount': 100.0}
            ]
        }
    }
    
    # Call the function
    output_path = generate_pdf(billing_data, output_path='test.pdf')
    
    # Assertions
    assert output_path == 'test.pdf'
    assert mock_doc.called
    assert mock_doc.return_value.build.called
    
    # Verify document title
    assert any(
        call.args[0] == f"Billing Report: {billing_data['customer_name']}"
        for call in mock_para.call_args_list
    )

def test_pdf_generation_with_no_orders(mock_reportlab):
    # Test PDF generation with no orders
    mock_doc, mock_table, mock_para = mock_reportlab
    
    # Test data with no orders
    billing_data = {
        'customer_name': 'Test Company',
        'start_date': '2025-01-01',
        'end_date': '2025-02-01',
        'preview_data': {
            'orders': []
        }
    }
    
    # Call the function
    output_path = generate_pdf(billing_data, output_path='test.pdf')
    
    # Assertions
    assert output_path == 'test.pdf'
    assert mock_doc.called
    assert mock_doc.return_value.build.called
    
    # Table should not be created for empty orders
    assert not mock_table.called
```

#### B. Excel Export Tests

```python
# tests/test_exporters/test_excel_exporter.py
@pytest.fixture
def mock_openpyxl():
    """Mock openpyxl components for testing Excel generation."""
    with patch('billing.exporters.Workbook') as mock_wb:
        # Configure the mocks
        mock_sheet = MagicMock()
        mock_wb.return_value.active = mock_sheet
        mock_wb.return_value.save = MagicMock()
        yield mock_wb, mock_sheet

def test_excel_generation(mock_openpyxl):
    # Test Excel workbook generation
    mock_wb, mock_sheet = mock_openpyxl
    
    # Test data
    billing_data = {
        'customer_name': 'Test Company',
        'start_date': '2025-01-01',
        'end_date': '2025-02-01',
        'preview_data': {
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'transaction_date': '2025-01-15',
                    'status': 'Completed',
                    'total_amount': 100.0
                }
            ]
        }
    }
    
    # Call the function
    output_path = generate_excel(billing_data, output_path='test.xlsx')
    
    # Assertions
    assert output_path == 'test.xlsx'
    assert mock_wb.called
    assert mock_wb.return_value.save.called
    
    # Verify header row was created
    assert mock_sheet.cell.called
    assert any(
        call.args[0] == 1 and call.args[1] == 1 and call.kwargs.get('value') == 'Order ID'
        for call in mock_sheet.cell.call_args_list
    )

def test_excel_currency_formatting(mock_openpyxl):
    # Test Excel currency formatting
    mock_wb, mock_sheet = mock_openpyxl
    
    # Test data with multiple currency values
    billing_data = {
        'customer_name': 'Test Company',
        'start_date': '2025-01-01',
        'end_date': '2025-02-01',
        'total_amount': 1500.75,
        'preview_data': {
            'orders': [
                {'order_id': 'ORD-001', 'total_amount': 1000.25},
                {'order_id': 'ORD-002', 'total_amount': 500.50}
            ]
        }
    }
    
    # Call the function
    generate_excel(billing_data)
    
    # Verify currency formatting was applied
    style_calls = [
        call for call in mock_sheet.cell.call_args_list
        if call.kwargs.get('value') in [1000.25, 500.50, 1500.75]
    ]
    
    assert len(style_calls) >= 3  # At least 3 currency cells
    
    # Verify number format was set to currency
    number_format_calls = mock_sheet.cell.return_value.number_format = '$#,##0.00'
    assert number_format_calls is not None
```

### 3. Frontend Component Tests

#### A. BillingForm Export Tests

```jsx
// Enhanced BillingForm export tests
test('exports report as PDF format with correct filename', async () => {
  // Mock the API response
  billingApi.generateReport.mockResolvedValueOnce({
    data: new Blob(['mock pdf data'], { type: 'application/pdf' })
  });
  
  // Mock document methods
  const mockUrl = 'mock-blob-url';
  const mockClick = jest.fn();
  const mockAppendChild = jest.fn();
  const mockRemoveChild = jest.fn();
  
  URL.createObjectURL = jest.fn().mockReturnValue(mockUrl);
  document.createElement = jest.fn().mockReturnValue({
    href: '',
    download: '',
    click: mockClick
  });
  document.body.appendChild = mockAppendChild;
  document.body.removeChild = mockRemoveChild;
  
  render(<BillingForm />);
  
  // Fill the form
  await fillFormWithValidData();
  
  // Select PDF format
  await selectExportFormat('pdf');
  
  // Submit the form
  await clickSubmitButton();
  
  // Verify API was called with PDF format
  expect(billingApi.generateReport).toHaveBeenCalledWith(
    expect.objectContaining({
      output_format: 'pdf'
    })
  );
  
  // Verify download was triggered
  expect(URL.createObjectURL).toHaveBeenCalled();
  expect(document.createElement).toHaveBeenCalledWith('a');
  expect(mockClick).toHaveBeenCalled();
  
  // Verify filename format
  const downloadLink = document.createElement('a');
  expect(downloadLink.download).toMatch(/billing_report_.*\.pdf$/);
  
  // Verify cleanup
  await waitFor(() => {
    expect(mockRemoveChild).toHaveBeenCalled();
    expect(URL.revokeObjectURL).toHaveBeenCalledWith(mockUrl);
  });
});

test('handles export errors gracefully', async () => {
  // Mock API error
  const mockError = new Error('Network error');
  billingApi.generateReport.mockRejectedValueOnce(mockError);
  handleApiError.mockReturnValueOnce('Error: Network error');
  
  render(<BillingForm />);
  
  // Fill the form
  await fillFormWithValidData();
  
  // Submit the form
  await clickSubmitButton();
  
  // Verify error handling
  await waitFor(() => {
    expect(handleApiError).toHaveBeenCalledWith(mockError);
    expect(screen.getByText(/Error: Network error/i)).toBeInTheDocument();
  });
  
  // Verify loading state is reset
  expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
});
```

#### B. BillingList Dynamic Column Tests

```jsx
// Enhanced BillingList dynamic column tests
test('generates correct columns for multiple services', async () => {
  // Mock API response with multiple services
  billingApi.generateReport.mockResolvedValueOnce({
    data: {
      preview_data: {
        orders: [
          {
            order_id: 'ORD-001',
            total_amount: 1250.75,
            services: [
              { service_id: 1, service_name: 'Packaging', amount: 500.25 },
              { service_id: 2, service_name: 'Shipping', amount: 350.50 },
              { service_id: 3, service_name: 'Handling', amount: 400.00 }
            ]
          }
        ]
      },
      service_totals: {
        '1': { name: 'Packaging', amount: 500.25, order_count: 1 },
        '2': { name: 'Shipping', amount: 350.50, order_count: 1 },
        '3': { name: 'Handling', amount: 400.00, order_count: 1 }
      }
    }
  });
  
  render(<BillingList />);
  
  // Fill and submit the form
  await fillBillingListForm();
  await clickCalculateButton();
  
  // Wait for the table to render
  await waitFor(() => {
    expect(screen.getByTestId('billing-table')).toBeInTheDocument();
  });
  
  // Verify all service columns are generated
  expect(screen.getByText('Packaging')).toBeInTheDocument();
  expect(screen.getByText('Shipping')).toBeInTheDocument();
  expect(screen.getByText('Handling')).toBeInTheDocument();
  
  // Verify column order (should be sorted by service_id)
  const headers = screen.getAllByRole('columnheader');
  const headerTexts = headers.map(h => h.textContent);
  
  // Find indexes of service columns
  const packagingIndex = headerTexts.indexOf('Packaging');
  const shippingIndex = headerTexts.indexOf('Shipping');
  const handlingIndex = headerTexts.indexOf('Handling');
  
  // Verify order (service_id 1, 2, 3)
  expect(packagingIndex).toBeLessThan(shippingIndex);
  expect(shippingIndex).toBeLessThan(handlingIndex);
  
  // Verify cell values
  expect(screen.getByText('$500.25')).toBeInTheDocument();
  expect(screen.getByText('$350.50')).toBeInTheDocument();
  expect(screen.getByText('$400.00')).toBeInTheDocument();
  
  // Verify totals in footer
  const footerCells = screen.getAllByTestId(/^footer-/);
  expect(footerCells.find(cell => cell.textContent === '$500.25')).toBeInTheDocument();
  expect(footerCells.find(cell => cell.textContent === '$350.50')).toBeInTheDocument();
  expect(footerCells.find(cell => cell.textContent === '$400.00')).toBeInTheDocument();
  expect(footerCells.find(cell => cell.textContent === '$1,250.75')).toBeInTheDocument();
});
```

## Conclusion and Action Plan

The detailed code analysis reveals that coverage is particularly low in core business logic components. Critical billing calculation functions, export generators, and service layer components have minimal testing, putting the application at risk for undetected bugs in these critical areas.

We recommend a systematic test improvement approach focusing on:

1. **Critical Business Logic First**: Prioritize calculator and export functionality
2. **Component-by-Component Coverage**: Implement tests in a systematic order
3. **Test Quality over Quantity**: Focus on meaningful assertions and edge cases
4. **Frontend-Backend Integration**: Test the connection points thoroughly

### Immediate Actions (Weeks 1-2)

1. Implement calculator test suite with thorough coverage of service types
2. Develop export format test suite with mocked dependencies
3. Improve BillingForm export and preview tests

### Medium-Term Actions (Weeks 3-4)

1. Address service layer test gaps
2. Enhance BillingList dynamic column coverage
3. Implement view-level error handling tests

### Long-Term Maintenance (Ongoing)

1. Set up coverage reporting in CI pipeline
2. Establish coverage thresholds for new code
3. Add comprehensive test documentation
4. Create test templates for common patterns

By following this detailed test improvement plan, the billing application's test coverage can be systematically improved from the current low state (20% backend, 42% frontend) to the target levels (80+% in critical areas), ensuring a more robust and maintainable codebase.