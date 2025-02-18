import { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Divider,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  CheckCircle as PassIcon,
  Cancel as FailIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

const sampleOrder = {
  reference_number: 'ORD123456',
  ship_to_name: 'John Doe',
  ship_to_company: 'ACME Corp',
  ship_to_city: 'New York',
  ship_to_state: 'NY',
  ship_to_country: 'USA',
  weight_lb: 25.5,
  line_items: 3,
  sku_quantity: JSON.stringify([
    { sku: 'SKU123', quantity: 2 },
    { sku: 'SKU456', quantity: 1 }
  ]),
  total_item_qty: 3,
  packages: 2,
  notes: 'Handle with care',
  carrier: 'UPS',
  volume_cuft: 5.2
};

const RulePreview = ({ onClose }) => {
  const [orderData, setOrderData] = useState(JSON.stringify(sampleOrder, null, 2));
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleTestRules = () => {
    try {
      // Parse order data but not used yet - will be used when connected to backend
      JSON.parse(orderData);
      
      // Simulate rule evaluation
      const evaluationResults = [
        {
          group: 'Service A Rules',
          logic: 'AND',
          passed: true,
          rules: [
            {
              description: 'Weight > 20 lb',
              field: 'weight_lb',
              operator: 'gt',
              value: '20',
              passed: true,
              adjustment: 10.00
            },
            {
              description: 'Shipping to USA',
              field: 'ship_to_country',
              operator: 'eq',
              value: 'USA',
              passed: true,
              adjustment: 5.00
            }
          ],
          totalAdjustment: 15.00
        },
        {
          group: 'Service B Rules',
          logic: 'OR',
          passed: false,
          rules: [
            {
              description: 'Contains SKU789',
              field: 'sku_quantity',
              operator: 'contains',
              value: 'SKU789',
              passed: false,
              adjustment: 0
            }
          ],
          totalAdjustment: 0
        }
      ];

      setResults(evaluationResults);
      setError('');
    } catch (err) {
      setError('Invalid order data format');
      setResults(null);
    }
  };

  const handleReset = () => {
    setOrderData(JSON.stringify(sampleOrder, null, 2));
    setResults(null);
    setError('');
  };

  const renderRuleResult = (rule) => (
    <ListItem key={rule.description}>
      <ListItemIcon>
        {rule.passed ? (
          <PassIcon color="success" />
        ) : (
          <FailIcon color="error" />
        )}
      </ListItemIcon>
      <ListItemText
        primary={rule.description}
        secondary={`${rule.field} ${rule.operator} ${rule.value}`}
      />
      {rule.passed && rule.adjustment > 0 && (
        <Chip
          label={`$${rule.adjustment.toFixed(2)}`}
          color="primary"
          size="small"
        />
      )}
    </ListItem>
  );

  const renderGroupResult = (group) => (
    <Paper key={group.group} sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
          {group.group}
        </Typography>
        <Tooltip title={`Logic: ${group.logic}`}>
          <InfoIcon sx={{ mr: 1 }} color="action" />
        </Tooltip>
        {group.passed ? (
          <Chip label="Passed" color="success" size="small" />
        ) : (
          <Chip label="Failed" color="error" size="small" />
        )}
      </Box>
      <List dense>
        {group.rules.map(renderRuleResult)}
      </List>
      {group.totalAdjustment > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
          <Typography variant="subtitle2" color="primary">
            Total Adjustment: ${group.totalAdjustment.toFixed(2)}
          </Typography>
        </Box>
      )}
    </Paper>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Rule Preview
      </Typography>
      <Divider sx={{ mb: 3 }} />

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="subtitle1">Test Order Data</Typography>
              <IconButton onClick={handleReset} size="small">
                <RefreshIcon />
              </IconButton>
            </Box>
            <TextField
              fullWidth
              multiline
              rows={12}
              value={orderData}
              onChange={(e) => setOrderData(e.target.value)}
              error={!!error}
              helperText={error}
            />
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                onClick={handleTestRules}
                disabled={!orderData}
              >
                Test Rules
              </Button>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Evaluation Results
            </Typography>
            {results ? (
              <>
                {results.map(renderGroupResult)}
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Summary
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Paper sx={{ p: 1, textAlign: 'center' }} elevation={0}>
                        <Typography variant="body2" color="text.secondary">
                          Total Groups
                        </Typography>
                        <Typography variant="h6">
                          {results.length}
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={6}>
                      <Paper sx={{ p: 1, textAlign: 'center' }} elevation={0}>
                        <Typography variant="body2" color="text.secondary">
                          Total Adjustment
                        </Typography>
                        <Typography variant="h6" color="primary">
                          ${results.reduce((sum, group) => sum + group.totalAdjustment, 0).toFixed(2)}
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>
                </Box>
              </>
            ) : (
              <Alert severity="info">
                Enter order data and click Test Rules to see evaluation results
              </Alert>
            )}
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
        <Button onClick={onClose}>
          Close
        </Button>
      </Box>
    </Box>
  );
};

RulePreview.propTypes = {
  onClose: PropTypes.func.isRequired
};

export default RulePreview;