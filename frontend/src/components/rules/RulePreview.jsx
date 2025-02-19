import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';

const RulePreview = ({ rule }) => {
  const getFieldLabel = (field) => {
    const fieldMap = {
      'weight_lb': 'Weight (lb)',
      'line_items': 'Line Items',
      'total_item_qty': 'Total Quantity',
      'sku_quantity': 'SKU Quantity',
      // Add more field mappings
    };
    return fieldMap[field] || field;
  };

  const getOperatorLabel = (operator) => {
    const operatorMap = {
      'gt': 'is greater than',
      'lt': 'is less than',
      'eq': 'equals',
      'contains': 'contains',
      // Add more operator mappings
    };
    return operatorMap[operator] || operator;
  };

  const renderBasicRule = () => (
    <Typography>
      When <strong>{getFieldLabel(rule.field)}</strong>
      {' '}<em>{getOperatorLabel(rule.operator)}</em>{' '}
      <strong>{rule.value}</strong>
    </Typography>
  );

  const renderConditions = () => (
    <List dense>
      {Object.entries(rule.conditions || {}).map(([field, criteria], index) => {
        const [operator, value] = Object.entries(criteria)[0] || ['', ''];
        return (
          <ListItem key={index}>
            <ListItemText>
              AND <strong>{getFieldLabel(field)}</strong>
              {' '}<em>{getOperatorLabel(operator)}</em>{' '}
              <strong>{value}</strong>
            </ListItemText>
          </ListItem>
        );
      })}
    </List>
  );

  const renderCalculations = () => (
    <List dense>
      {(rule.calculations || []).map((calc, index) => (
        <ListItem key={index}>
          <ListItemText>
            {calc.type === 'case_based_tier' ? (
              <>Apply case-based pricing tiers:</>
            ) : (
              <>
                {calc.type === 'flat_fee' && `Add $${calc.value}`}
                {calc.type === 'percentage' && `Add ${calc.value}%`}
                {calc.type === 'per_unit' && `Add $${calc.value} per unit`}
              </>
            )}
          </ListItemText>
        </ListItem>
      ))}
    </List>
  );

  const renderTiers = () => {
    if (!rule.tier_config?.ranges?.length) return null;

    return (
      <Box mt={2}>
        <Typography variant="subtitle2" gutterBottom>
          Case-Based Tiers:
        </Typography>
        <List dense>
          {rule.tier_config.ranges.map((tier, index) => (
            <ListItem key={index}>
              <ListItemText>
                {tier.min} to {tier.max} cases: {tier.multiplier}x base price
              </ListItemText>
            </ListItem>
          ))}
        </List>
        {rule.tier_config.excluded_skus?.length > 0 && (
          <Box mt={1}>
            <Typography variant="subtitle2" gutterBottom>
              Excluded SKUs:
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {rule.tier_config.excluded_skus.map((sku, index) => (
                <Chip key={index} label={sku} size="small" />
              ))}
            </Box>
          </Box>
        )}
      </Box>
    );
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Rule Preview
      </Typography>
      <Divider sx={{ mb: 2 }} />
      
      <Box>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Basic Condition:
        </Typography>
        {renderBasicRule()}
      </Box>

      {rule.conditions && Object.keys(rule.conditions).length > 0 && (
        <Box mt={2}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Additional Conditions:
          </Typography>
          {renderConditions()}
        </Box>
      )}

      {rule.calculations && rule.calculations.length > 0 && (
        <Box mt={2}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Price Calculations:
          </Typography>
          {renderCalculations()}
          {renderTiers()}
        </Box>
      )}
    </Paper>
  );
};

export default RulePreview;