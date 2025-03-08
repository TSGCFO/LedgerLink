import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Grid,
  Paper,
  TextField,
  Typography,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import rulesService from '../../services/rulesService';

/**
 * Interactive Rule Testing Component
 * 
 * Allows users to test a rule against sample order data to see if it matches
 * and what calculation results would be produced.
 */
const DEFAULT_SAMPLE_DATA = {
  // Default sample order data
  weight_lb: '10',
  total_item_qty: '5',
  packages: '1',
  line_items: '2',
  volume_cuft: '2.5',
  reference_number: 'ORD-12345',
  ship_to_name: 'John Doe',
  ship_to_company: 'ACME Corp',
  ship_to_city: 'New York',
  ship_to_state: 'NY',
  ship_to_country: 'US',
  carrier: 'UPS',
  sku_quantity: '{"SKU-123": 2, "SKU-456": 3}',
  notes: 'Test order notes'
};

const RuleTester = ({ rule }) => {
  const [sampleData, setSampleData] = useState({ ...DEFAULT_SAMPLE_DATA });
  
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSampleData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleTestRule = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // First, validate the rule is complete
      if (!rule.field || !rule.operator || !rule.value) {
        setError('Rule is missing required fields. Complete the rule definition first.');
        setLoading(false);
        return;
      }
      
      // Parse any JSON fields
      const parsedData = { ...sampleData };
      
      // Handle SKU quantity specially
      if (parsedData.sku_quantity) {
        try {
          // Check if it's already valid JSON
          const parsed = JSON.parse(parsedData.sku_quantity);
          // Keep it as a string since that's what the API expects
        } catch (e) {
          // If not valid JSON, try to convert it to JSON
          try {
            // Format expected: SKU-1:2;SKU-2:3 -> {"SKU-1": 2, "SKU-2": 3}
            if (parsedData.sku_quantity.includes(':')) {
              const entries = parsedData.sku_quantity.split(';')
                .map(entry => entry.trim())
                .filter(Boolean)
                .map(entry => {
                  const [sku, qty] = entry.split(':').map(part => part.trim());
                  return [sku, parseInt(qty) || 0];
                });
              
              parsedData.sku_quantity = JSON.stringify(Object.fromEntries(entries));
            } else {
              throw new Error('Invalid SKU quantity format');
            }
          } catch (conversionError) {
            setError('Invalid SKU quantity format. Use format: SKU-1:2;SKU-2:3 or valid JSON like {"SKU-123": 2}');
            setLoading(false);
            return;
          }
        }
      }
      
      // Check for case_based_tier calculations and validate against provided test data
      if (rule.calculations && rule.calculations.some(calc => calc.type === 'case_based_tier')) {
        // Check if SKU quantity is provided for testing case-based tiers
        if (!parsedData.sku_quantity || parsedData.sku_quantity === '{}') {
          setError('To test case-based tier rules, you must provide SKU quantities. Enter SKUs and quantities in the SKU Quantities field.');
          setLoading(false);
          return;
        }
      }
      
      // Convert numeric fields to numbers
      const numericFields = ['weight_lb', 'total_item_qty', 'packages', 'volume_cuft', 'line_items'];
      for (const field of numericFields) {
        if (parsedData[field] && parsedData[field] !== '') {
          try {
            parsedData[field] = parseFloat(parsedData[field]);
            if (isNaN(parsedData[field])) {
              throw new Error(`Invalid number for ${field}`);
            }
          } catch (e) {
            setError(`Invalid number for ${field}. Please enter a valid numeric value.`);
            setLoading(false);
            return;
          }
        }
      }
      
      // Make the API call
      try {
        const result = await rulesService.testRule(rule, parsedData);
        setTestResult(result);
      } catch (apiError) {
        // Handle API connection errors separately
        if (apiError.message && apiError.message.includes('connect to the server')) {
          setError('Unable to connect to the server. API service may not be running.');
        } else {
          setError(apiError.message || 'Failed to test rule. Please check your inputs and try again.');
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to test rule. Please check your inputs and try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const renderCalculationResults = () => {
    if (!testResult || !testResult.calculation_result) {
      // If rule matches but no calculation result, show a message
      if (testResult && testResult.matches) {
        return (
          <Box mt={2}>
            <Typography variant="h6">Calculation Results</Typography>
            <Paper elevation={2} sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">
                Rule matches, but no calculations were defined or applied.
              </Typography>
            </Paper>
          </Box>
        );
      }
      return null;
    }
    
    // Check if we have calculation details
    const hasDetails = testResult.calculation_result.details && 
                      Array.isArray(testResult.calculation_result.details) && 
                      testResult.calculation_result.details.length > 0;
    
    return (
      <Box mt={2}>
        <Typography variant="h6">Calculation Results</Typography>
        <Paper elevation={2} sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
          {hasDetails ? (
            <>
              {/* Show each calculation step */}
              {testResult.calculation_result.details.map((detail, index) => (
                <Box key={index} mb={1} display="flex" alignItems="center">
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      backgroundColor: 'rgba(0,0,0,0.05)', 
                      px: 1, 
                      py: 0.5, 
                      borderRadius: 1,
                      width: '100%'
                    }}
                  >
                    {detail.description}
                  </Typography>
                </Box>
              ))}
              <Divider sx={{ my: 1 }} />
            </>
          ) : (
            <Typography variant="body2" sx={{ mb: 2 }} color="text.secondary">
              No detailed calculation steps available.
            </Typography>
          )}
          
          {/* Show the total amount */}
          <Box 
            display="flex" 
            justifyContent="space-between" 
            alignItems="center"
            sx={{ 
              backgroundColor: 'primary.main', 
              color: 'white', 
              p: 1, 
              borderRadius: 1 
            }}
          >
            <Typography variant="subtitle1" fontWeight="bold">
              Total Calculated Amount:
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              ${testResult.calculation_result.total.toFixed(2)}
            </Typography>
          </Box>
        </Paper>
      </Box>
    );
  };

  const renderConditionResults = () => {
    if (!testResult || !testResult.conditions_results) return null;
    
    // Add a condition for the base rule (field, operator, value)
    const allConditions = {
      ...testResult.conditions_results,
      [`Base condition (${rule.field} ${rule.operator} ${rule.value})`]: 
        testResult.matches || (testResult.reason ? false : true)
    };
    
    return (
      <Box mt={2}>
        <Typography variant="h6">Condition Evaluation</Typography>
        <Paper elevation={2} sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
          {Object.entries(allConditions).map(([condition, result], index) => (
            <Box key={index} mb={1} display="flex" alignItems="center">
              <Box 
                component="span" 
                sx={{ 
                  width: 10, 
                  height: 10, 
                  borderRadius: '50%', 
                  bgcolor: result ? 'success.main' : 'error.main',
                  mr: 1 
                }} 
              />
              <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center' }}>
                <span style={{ fontWeight: index === 0 ? 'bold' : 'normal' }}>
                  {condition}:
                </span>
                <span style={{ 
                  marginLeft: '4px', 
                  color: result ? '#2e7d32' : '#d32f2f',
                  fontWeight: 'bold'
                }}>
                  {result ? 'Matches ✓' : 'Does not match ✗'}
                </span>
              </Typography>
            </Box>
          ))}
        </Paper>
      </Box>
    );
  };
  
  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Rule Tester
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Test your rule against sample order data to see if it matches and how it would calculate.
        </Typography>
        
        <Divider sx={{ my: 2 }} />
        
        <Accordion defaultExpanded>
          <AccordionSummary>
            <Typography variant="subtitle1" fontWeight="medium">Sample Order Data</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Configure sample order data to test how your rule would evaluate against real-world scenarios
              </Typography>
            </Box>
            
            <Grid container spacing={2}>
              {/* Numeric Fields Section */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom sx={{ borderBottom: '1px solid #eee', pb: 0.5, mb: 1 }}>
                  Numeric Values
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  label="Weight (lbs)"
                  name="weight_lb"
                  value={sampleData.weight_lb}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                  type="number"
                  InputProps={{ inputProps: { min: 0, step: 0.1 } }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  label="Total Items"
                  name="total_item_qty"
                  value={sampleData.total_item_qty}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                  type="number"
                  InputProps={{ inputProps: { min: 0 } }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  label="Packages"
                  name="packages"
                  value={sampleData.packages}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                  type="number"
                  InputProps={{ inputProps: { min: 0 } }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  label="Line Items"
                  name="line_items"
                  value={sampleData.line_items}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                  type="number"
                  InputProps={{ inputProps: { min: 0 } }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  label="Volume (cu. ft.)"
                  name="volume_cuft"
                  value={sampleData.volume_cuft}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                  type="number"
                  InputProps={{ inputProps: { min: 0, step: 0.1 } }}
                />
              </Grid>
              
              {/* Shipping Information Section */}
              <Grid item xs={12} sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom sx={{ borderBottom: '1px solid #eee', pb: 0.5, mb: 1 }}>
                  Shipping Information
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  label="Reference #"
                  name="reference_number"
                  value={sampleData.reference_number}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  label="Ship To Name"
                  name="ship_to_name"
                  value={sampleData.ship_to_name}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  label="Ship To Company"
                  name="ship_to_company"
                  value={sampleData.ship_to_company}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  label="Ship To City"
                  name="ship_to_city"
                  value={sampleData.ship_to_city}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  label="Ship To State"
                  name="ship_to_state"
                  value={sampleData.ship_to_state}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  label="Ship To Country"
                  name="ship_to_country"
                  value={sampleData.ship_to_country}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  label="Carrier"
                  name="carrier"
                  value={sampleData.carrier}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                />
              </Grid>
              
              {/* SKU & Notes Section */}
              <Grid item xs={12} sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom sx={{ borderBottom: '1px solid #eee', pb: 0.5, mb: 1 }}>
                  SKUs & Notes
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  label="SKU Quantities"
                  name="sku_quantity"
                  value={sampleData.sku_quantity}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                  helperText="Format: {'SKU-123': 2, 'SKU-456': 3} or SKU-1:2;SKU-2:3"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Notes"
                  name="notes"
                  value={sampleData.notes}
                  onChange={handleInputChange}
                  fullWidth
                  margin="normal"
                  size="small"
                  multiline
                  rows={2}
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
        
        <Box mt={3} display="flex" justifyContent="center" gap={2}>
          <Button
            variant="outlined"
            color="secondary"
            onClick={() => {
              setSampleData({ ...DEFAULT_SAMPLE_DATA });
              setTestResult(null);
              setError(null);
            }}
            disabled={loading}
          >
            Reset Data
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleTestRule}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
            sx={{ minWidth: '150px' }}
          >
            {loading ? 'Testing...' : 'Test Rule'}
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        
        {testResult && (
          <Box mt={3}>
            <Paper 
              elevation={3}
              sx={{ 
                p: 2, 
                bgcolor: testResult.matches ? 'success.light' : 'error.light',
                color: testResult.matches ? 'white' : 'white'
              }}
            >
              <Typography variant="h6" fontWeight="bold">
                {testResult.matches 
                  ? '✅ Rule Matches' 
                  : '❌ Rule Does Not Match'}
              </Typography>
              {testResult.reason && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  <strong>Reason:</strong> {testResult.reason}
                </Typography>
              )}
            </Paper>
            
            {renderConditionResults()}
            {renderCalculationResults()}
            
            {/* Add debugging information */}
            <Accordion sx={{ mt: 3 }}>
              <AccordionSummary>
                <Typography>Debug Information</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="subtitle2" gutterBottom>Rule Data:</Typography>
                <Box 
                  component="pre" 
                  sx={{ 
                    bgcolor: '#f5f5f5', 
                    p: 1, 
                    borderRadius: 1,
                    overflow: 'auto',
                    fontSize: '0.75rem'
                  }}
                >
                  {JSON.stringify(rule, null, 2)}
                </Box>
                
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>Sample Data:</Typography>
                <Box 
                  component="pre" 
                  sx={{ 
                    bgcolor: '#f5f5f5', 
                    p: 1, 
                    borderRadius: 1,
                    overflow: 'auto',
                    fontSize: '0.75rem'
                  }}
                >
                  {JSON.stringify(sampleData, null, 2)}
                </Box>
                
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>Response Data:</Typography>
                <Box 
                  component="pre" 
                  sx={{ 
                    bgcolor: '#f5f5f5', 
                    p: 1, 
                    borderRadius: 1,
                    overflow: 'auto',
                    fontSize: '0.75rem'
                  }}
                >
                  {JSON.stringify(testResult, null, 2)}
                </Box>
              </AccordionDetails>
            </Accordion>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default RuleTester;