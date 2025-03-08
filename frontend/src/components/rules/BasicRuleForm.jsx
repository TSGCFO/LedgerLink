import React, { useState, useEffect } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Tooltip,
  IconButton,
  FormHelperText,
} from '@mui/material';
import {
  Info as InfoIcon,
  Help as HelpIcon,
} from '@mui/icons-material';
import PropTypes from 'prop-types';
import { validateRuleValue } from '../../utils/validationUtils';

// Help text constants
const HELP_TEXTS = {
  field: 'Select the order field to evaluate. This determines what aspect of the order will be checked.',
  operator: 'Choose how to compare the field value. Different fields support different operators.',
  value: 'Enter the value to compare against. Format depends on the selected field and operator.',
};

/**
 * Component for basic rule form fields (field, operator, value)
 */
const BasicRuleForm = ({
  field,
  operator,
  value,
  availableFields,
  availableOperators,
  onChange,
  errors = {},
}) => {
  const [localErrors, setLocalErrors] = useState({});

  // Handle field change
  const handleFieldChange = (e) => {
    onChange('field', e.target.value);
  };

  // Handle operator change
  const handleOperatorChange = (e) => {
    onChange('operator', e.target.value);
  };

  // Handle value change
  const handleValueChange = (e) => {
    onChange('value', e.target.value);
  };

  // Client-side validation
  useEffect(() => {
    if (field && operator && value) {
      const { isValid, message } = validateRuleValue(field, operator, value);
      setLocalErrors(prev => ({
        ...prev,
        value: isValid ? null : message
      }));
    }
  }, [field, operator, value]);

  return (
    <Box display="flex" gap={2}>
      <FormControl fullWidth required error={!!errors.field}>
        <InputLabel>Field</InputLabel>
        <Select
          name="field"
          value={field || ''}
          onChange={handleFieldChange}
          label="Field"
        >
          {availableFields.map((fieldOption) => (
            <MenuItem key={fieldOption.value} value={fieldOption.value}>
              {fieldOption.label}
              <Tooltip title={fieldOption.description || ''}>
                <IconButton size="small">
                  <InfoIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </MenuItem>
          ))}
        </Select>
        <FormHelperText>
          {errors.field || (
            <Tooltip title={HELP_TEXTS.field}>
              <IconButton size="small">
                <HelpIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </FormHelperText>
      </FormControl>

      <FormControl fullWidth required disabled={!field} error={!!errors.operator}>
        <InputLabel>Operator</InputLabel>
        <Select
          name="operator"
          value={operator || ''}
          onChange={handleOperatorChange}
          label="Operator"
        >
          {availableOperators.map((op) => (
            <MenuItem key={op.value} value={op.value}>
              {op.label}
            </MenuItem>
          ))}
        </Select>
        <FormHelperText>
          {errors.operator || (
            <Tooltip title={HELP_TEXTS.operator}>
              <IconButton size="small">
                <HelpIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </FormHelperText>
      </FormControl>

      <TextField
        fullWidth
        required
        label="Value"
        name="value"
        value={value || ''}
        onChange={handleValueChange}
        disabled={!operator}
        error={!!errors.value || !!localErrors.value}
        helperText={errors.value || localErrors.value || (
          <Typography component="span" variant="caption">
            For multiple values, separate with semicolons (;)
            <Tooltip title={HELP_TEXTS.value}>
              <IconButton size="small">
                <HelpIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Typography>
        )}
      />
    </Box>
  );
};

BasicRuleForm.propTypes = {
  field: PropTypes.string,
  operator: PropTypes.string,
  value: PropTypes.string,
  availableFields: PropTypes.array.isRequired,
  availableOperators: PropTypes.array.isRequired,
  onChange: PropTypes.func.isRequired,
  errors: PropTypes.object,
};

export default BasicRuleForm;