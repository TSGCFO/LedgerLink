import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Paper,
  Divider,
} from '@mui/material';

const HELP_CONTENT = {
  basic_rules: {
    title: 'Basic Rules Guide',
    description: 'Basic rules are simple conditions that check a single aspect of an order.',
    examples: [
      {
        title: 'Weight-based Rule',
        description: 'Add $10 when order weight is over 50 lbs',
        setup: {
          field: 'weight_lb',
          operator: 'gt',
          value: '50',
          adjustment: '10.00'
        }
      },
      {
        title: 'SKU-specific Rule',
        description: 'Add $5 when order contains SKU-123',
        setup: {
          field: 'sku_quantity',
          operator: 'contains',
          value: 'SKU-123',
          adjustment: '5.00'
        }
      },
      {
        title: 'Quantity-based Rule',
        description: 'Add $0.50 per item when total quantity exceeds 100',
        setup: {
          field: 'total_item_qty',
          operator: 'gt',
          value: '100',
          adjustment: '0.50'
        }
      }
    ]
  },
  advanced_rules: {
    title: 'Advanced Rules Guide',
    description: 'Advanced rules combine multiple conditions and support complex pricing calculations.',
    examples: [
      {
        title: 'Case-based Tier Pricing',
        description: 'Apply different multipliers based on the number of cases',
        setup: {
          conditions: {
            'sku_quantity': { 'contains': 'CASE-SKU' }
          },
          calculations: [
            { type: 'case_based_tier' }
          ],
          tier_config: {
            ranges: [
              { min: 1, max: 10, multiplier: 1.0 },
              { min: 11, max: 50, multiplier: 0.9 },
              { min: 51, max: 100, multiplier: 0.8 }
            ]
          }
        }
      },
      {
        title: 'Multiple Conditions with Percentage',
        description: 'Add 15% when order is heavy AND ships internationally',
        setup: {
          field: 'weight_lb',
          operator: 'gt',
          value: '100',
          conditions: {
            'ship_to_country': { 'ne': 'USA' }
          },
          calculations: [
            { type: 'percentage', value: '15' }
          ]
        }
      }
    ]
  },
  case_tiers: {
    title: 'Case-based Tier Configuration',
    description: 'Learn how to set up pricing tiers based on the number of cases in an order.',
    steps: [
      'Define tier ranges with minimum and maximum case counts',
      'Set price multipliers for each tier (e.g., 1.0 for full price, 0.9 for 10% discount)',
      'Optionally exclude specific SKUs from case counting',
      'The system will automatically calculate cases based on product case sizes'
    ],
    tips: [
      'Ensure tier ranges don\'t overlap',
      'Consider starting with 2-3 tiers and adjust based on business needs',
      'Use excluded SKUs for products that shouldn\'t affect tier calculation',
      'Verify that product case sizes are correctly set up'
    ]
  }
};

const RuleHelpDialog = ({ open, onClose, topic = 'basic_rules' }) => {
  const content = HELP_CONTENT[topic];

  const renderExample = (example) => (
    <Paper sx={{ p: 2, mb: 2 }} key={example.title}>
      <Typography variant="subtitle1" gutterBottom>
        {example.title}
      </Typography>
      <Typography color="text.secondary" paragraph>
        {example.description}
      </Typography>
      <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
        <Typography variant="caption" component="pre">
          {JSON.stringify(example.setup, null, 2)}
        </Typography>
      </Box>
    </Paper>
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {content.title}
      </DialogTitle>
      <DialogContent>
        <Typography paragraph>
          {content.description}
        </Typography>

        <Divider sx={{ my: 2 }} />

        {content.examples && (
          <>
            <Typography variant="h6" gutterBottom>
              Examples
            </Typography>
            {content.examples.map(renderExample)}
          </>
        )}

        {content.steps && (
          <>
            <Typography variant="h6" gutterBottom>
              Setup Steps
            </Typography>
            <List>
              {content.steps.map((step, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`${index + 1}. ${step}`} />
                </ListItem>
              ))}
            </List>
          </>
        )}

        {content.tips && (
          <>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Tips & Best Practices
            </Typography>
            <List>
              {content.tips.map((tip, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`• ${tip}`} />
                </ListItem>
              ))}
            </List>
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default RuleHelpDialog; 