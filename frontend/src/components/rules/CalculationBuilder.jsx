import React, { useState } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  IconButton,
  Button,
  Tooltip,
  Paper,
  Chip,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Help as HelpIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material';
import PropTypes from 'prop-types';
import { validateCalculation } from '../../utils/validationUtils';

// Help text constants
const HELP_TEXTS = {
  calculations: 'Define how to calculate the final price when this rule applies.',
  caseTiers: 'Set up pricing tiers based on the number of cases in an order.',
  excludedSkus: 'List any SKUs that should not be counted in case calculations.',
};

// Helper component to visualize tier configuration
const TierVisualizer = ({ tiers }) => {
  if (!tiers || !Array.isArray(tiers) || tiers.length === 0) {
    return (
      <Alert severity="warning" sx={{ mb: 2 }}>
        No tiers configured yet
      </Alert>
    );
  }
  
  // Sort tiers by min value
  const sortedTiers = [...tiers].sort((a, b) => parseFloat(a.min) - parseFloat(b.min));
  
  // Find the maximum value for visualization scaling
  const maxValue = Math.max(...sortedTiers.map(tier => parseFloat(tier.max)));
  
  return (
    <Box sx={{ mt: 2, mb: 3 }}>
      <Typography variant="subtitle2" gutterBottom>
        Tier Visualization
      </Typography>
      
      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
        {sortedTiers.map((tier, index) => {
          const min = parseFloat(tier.min);
          const max = parseFloat(tier.max);
          const multiplier = parseFloat(tier.multiplier);
          
          // Calculate position and width for visual representation
          const startPos = (min / maxValue) * 100;
          const width = ((max - min + 1) / maxValue) * 100;
          
          return (
            <Box key={index} sx={{ mb: 1 }}>
              <Typography variant="caption" color="text.secondary">
                {min} to {max} cases 
                <Chip 
                  label={`${multiplier}x`} 
                  size="small" 
                  color="primary" 
                  sx={{ ml: 1, height: 20 }} 
                />
              </Typography>
              
              <Box sx={{ position: 'relative', height: 18, bgcolor: 'grey.100', borderRadius: 1, mt: 0.5 }}>
                <Box 
                  sx={{
                    position: 'absolute',
                    left: `${startPos}%`,
                    width: `${width}%`,
                    height: '100%',
                    bgcolor: `rgba(25, 118, 210, ${0.3 + (multiplier / 10)})`,
                    borderRadius: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                />
              </Box>
            </Box>
          );
        })}
        
        {/* Axis */}
        <Box sx={{ mt: 1, position: 'relative', height: 16 }}>
          <LinearProgress 
            variant="determinate" 
            value={100} 
            sx={{ 
              height: 1, 
              bgcolor: 'grey.300',
              '& .MuiLinearProgress-bar': {
                bgcolor: 'grey.500',
              }
            }} 
          />
          <Box sx={{ position: 'absolute', left: 0, top: 4, fontSize: 10 }}>0</Box>
          <Box sx={{ position: 'absolute', right: 0, top: 4, fontSize: 10 }}>{maxValue}</Box>
        </Box>
        
        <Typography variant="caption" color="text.secondary" align="center" sx={{ display: 'block', mt: 1 }}>
          Number of Cases
        </Typography>
      </Paper>
    </Box>
  );
};

/**
 * Component for building calculation configurations for advanced rules
 */
const CalculationBuilder = ({ 
  calculations, 
  tierConfig, 
  calculationTypes,
  onCalculationChange, 
  onCalculationAdd, 
  onCalculationRemove,
  onTierChange,
  onTierAdd,
  onTierRemove,
  onExcludedSkusChange,
  errors = {}
}) => {
  // Client-side validation
  const validateCalculationField = (calculation) => {
    const { isValid, message } = validateCalculation(calculation);
    return isValid ? null : message;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          Calculations
        </Typography>
        <Button
          startIcon={<AddIcon />}
          onClick={onCalculationAdd}
        >
          Add Calculation
        </Button>
      </Box>

      {calculations.map((calc, index) => {
        const error = errors[`calculation_${index}`] || 
                     (calc.type && validateCalculationField(calc));
        
        return (
          <Box key={index} display="flex" gap={2} mb={2}>
            <FormControl fullWidth error={!!error}>
              <InputLabel>Type</InputLabel>
              <Select
                value={calc.type || ''}
                onChange={(e) => onCalculationChange(index, 'type', e.target.value)}
                label="Type"
              >
                {Object.entries(calculationTypes).map(([value, label]) => (
                  <MenuItem key={value} value={value}>
                    {label}
                  </MenuItem>
                ))}
              </Select>
              {error && <Typography color="error" variant="caption">{error}</Typography>}
            </FormControl>

            {calc.type === 'case_based_tier' ? (
              <Box sx={{ width: '100%' }}>
                <Typography variant="subtitle2" gutterBottom>
                  Case-Based Tiers
                  <Tooltip title={HELP_TEXTS.caseTiers}>
                    <IconButton size="small">
                      <HelpIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Typography>
                
                {tierConfig.ranges.map((tier, tierIndex) => {
                  const isLastTier = tierIndex === tierConfig.ranges.length - 1;
                  const nextTier = !isLastTier ? tierConfig.ranges[tierIndex + 1] : null;
                  const hasOverlap = nextTier && parseFloat(tier.max) >= parseFloat(nextTier.min);
                  const hasGap = nextTier && parseFloat(tier.max) + 1 < parseFloat(nextTier.min);
                  
                  return (
                    <Box key={tierIndex} display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2} 
                         sx={{ 
                           p: 1, 
                           border: '1px solid', 
                           borderColor: hasOverlap ? 'error.main' : hasGap ? 'warning.main' : 'transparent',
                           borderRadius: 1
                         }}>
                      <TextField
                        label="Min Cases"
                        type="number"
                        value={tier.min}
                        onChange={(e) => onTierChange(tierIndex, 'min', e.target.value)}
                        size="small"
                        error={!!errors[`tier_${tierIndex}_min`] || hasOverlap}
                        helperText={errors[`tier_${tierIndex}_min`]}
                        sx={{ flexGrow: 1 }}
                      />
                      <TextField
                        label="Max Cases"
                        type="number"
                        value={tier.max}
                        onChange={(e) => onTierChange(tierIndex, 'max', e.target.value)}
                        size="small"
                        error={!!errors[`tier_${tierIndex}_max`] || hasOverlap || hasGap}
                        helperText={errors[`tier_${tierIndex}_max`] || 
                                  (hasOverlap ? 'Overlaps with next tier' : 
                                  (hasGap ? 'Gap before next tier' : ''))}
                        sx={{ flexGrow: 1 }}
                      />
                      <TextField
                        label="Price Multiplier"
                        type="number"
                        value={tier.multiplier}
                        onChange={(e) => onTierChange(tierIndex, 'multiplier', e.target.value)}
                        size="small"
                        inputProps={{ step: '0.1' }}
                        error={!!errors[`tier_${tierIndex}_multiplier`]}
                        helperText={errors[`tier_${tierIndex}_multiplier`]}
                        sx={{ flexGrow: 1 }}
                      />
                      <Box display="flex" alignItems="center" justifyContent="center">
                        <IconButton
                          color="error"
                          onClick={() => onTierRemove(tierIndex)}
                          disabled={tierConfig.ranges.length <= 1}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </Box>
                  );
                })}
                
                <Button
                  startIcon={<AddIcon />}
                  onClick={onTierAdd}
                  size="small"
                  sx={{ mt: 1 }}
                >
                  Add Tier
                </Button>
                
                {/* Visual representation of tiers */}
                {tierConfig.ranges.length > 0 && (
                  <TierVisualizer tiers={tierConfig.ranges} />
                )}

                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Excluded SKUs
                    <Tooltip title={HELP_TEXTS.excludedSkus}>
                      <IconButton size="small">
                        <HelpIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Typography>
                  <TextField
                    fullWidth
                    label="Excluded SKUs"
                    value={tierConfig.excluded_skus.join(';')}
                    onChange={onExcludedSkusChange}
                    helperText="Enter SKUs separated by semicolons (;)"
                    size="small"
                    error={!!errors.excluded_skus}
                  />
                </Box>
              </Box>
            ) : (
              <TextField
                fullWidth
                label="Value"
                type="number"
                value={calc.value || ''}
                onChange={(e) => onCalculationChange(index, 'value', e.target.value)}
                inputProps={{ step: '0.01' }}
                error={!!errors[`calculation_${index}_value`]}
                helperText={errors[`calculation_${index}_value`]}
              />
            )}

            <IconButton
              color="error"
              onClick={() => onCalculationRemove(index)}
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        );
      })}
    </Box>
  );
};

CalculationBuilder.propTypes = {
  calculations: PropTypes.array.isRequired,
  tierConfig: PropTypes.object.isRequired,
  calculationTypes: PropTypes.object.isRequired,
  onCalculationChange: PropTypes.func.isRequired,
  onCalculationAdd: PropTypes.func.isRequired,
  onCalculationRemove: PropTypes.func.isRequired,
  onTierChange: PropTypes.func.isRequired,
  onTierAdd: PropTypes.func.isRequired,
  onTierRemove: PropTypes.func.isRequired,
  onExcludedSkusChange: PropTypes.func.isRequired,
  errors: PropTypes.object,
};

export default CalculationBuilder;