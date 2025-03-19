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
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import PropTypes from 'prop-types';
import { validateConditions } from '../../utils/validationUtils';

/**
 * Component for building condition configurations for advanced rules
 */
const ConditionBuilder = ({ 
  conditions, 
  fields,
  operators,
  onConditionAdd, 
  onConditionChange, 
  onConditionRemove,
  errors = {}
}) => {
  const [error, setError] = useState(null);
  
  // Client-side validation
  const validateCondition = (field, operator, value) => {
    const condition = { [field]: { [operator]: value } };
    const { isValid, message } = validateConditions(condition);
    return isValid ? null : message;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          Additional Conditions
        </Typography>
        <Button
          startIcon={<AddIcon />}
          onClick={onConditionAdd}
        >
          Add Condition
        </Button>
      </Box>

      {Object.entries(conditions).length === 0 ? (
        <Box sx={{ 
          p: 3, 
          border: '1px dashed', 
          borderColor: 'grey.400', 
          borderRadius: 1,
          textAlign: 'center',
          mb: 2
        }}>
          <Typography variant="body2" color="text.secondary">
            No additional conditions added yet. Click "Add Condition" to create more specific rule criteria.
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            Additional conditions allow you to create more complex rules by requiring multiple criteria to be met.
          </Typography>
        </Box>
      ) : (
        Object.entries(conditions).map(([field, criteria], index) => {
          const [operator, value] = Object.entries(criteria)[0] || ['', ''];
          const fieldError = errors[`condition_${index}`] || 
                       (field && operator && validateCondition(field, operator, value));
          
          return (
            <Box key={index} display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2} 
                 sx={{ 
                   p: 1, 
                   border: '1px solid', 
                   borderColor: fieldError ? 'error.light' : 'transparent',
                   borderRadius: 1
                 }}>
              <FormControl fullWidth error={!!errors[`condition_${index}_field`]}>
                <InputLabel>Field</InputLabel>
                <Select
                  value={field}
                  onChange={(e) => onConditionChange(field, e.target.value, operator, value)}
                  label="Field"
                >
                  {fields.map((f) => (
                    <MenuItem key={f.value} value={f.value}>
                      {f.label}
                    </MenuItem>
                  ))}
                </Select>
                {errors[`condition_${index}_field`] && (
                  <Typography color="error" variant="caption">
                    {errors[`condition_${index}_field`]}
                  </Typography>
                )}
              </FormControl>

              <FormControl fullWidth error={!!errors[`condition_${index}_operator`]}>
                <InputLabel>Operator</InputLabel>
                <Select
                  value={operator}
                  onChange={(e) => onConditionChange(field, field, e.target.value, value)}
                  label="Operator"
                >
                  {operators.map((op) => (
                    <MenuItem key={op.value} value={op.value}>
                      {op.label}
                    </MenuItem>
                  ))}
                </Select>
                {errors[`condition_${index}_operator`] && (
                  <Typography color="error" variant="caption">
                    {errors[`condition_${index}_operator`]}
                  </Typography>
                )}
              </FormControl>

              <TextField
                fullWidth
                label="Value"
                value={value}
                onChange={(e) => onConditionChange(field, field, operator, e.target.value)}
                error={!!errors[`condition_${index}_value`]}
                helperText={errors[`condition_${index}_value`]}
              />

              <Box display="flex" alignItems="center" justifyContent={{ xs: 'flex-end', sm: 'center' }}>
                <IconButton
                  color="error"
                  onClick={() => onConditionRemove(field)}
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            </Box>
          );
        })
      )}
      
      {/* Display warning for conditions_warning */}
      {errors.conditions_warning && (
        <Typography color="warning.main" sx={{ mt: 1, display: 'block', fontStyle: 'italic' }}>
          {errors.conditions_warning}
        </Typography>
      )}
      
      {error && (
        <Typography color="error" variant="caption" sx={{ mt: 1, display: 'block' }}>
          {error}
        </Typography>
      )}
    </Box>
  );
};

ConditionBuilder.propTypes = {
  conditions: PropTypes.object.isRequired,
  fields: PropTypes.array.isRequired,
  operators: PropTypes.array.isRequired,
  onConditionAdd: PropTypes.func.isRequired,
  onConditionChange: PropTypes.func.isRequired,
  onConditionRemove: PropTypes.func.isRequired,
  errors: PropTypes.object,
};

export default ConditionBuilder;