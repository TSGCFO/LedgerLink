import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  IconButton,
  Tooltip,
  Typography,
  Alert,
  Chip,
} from '@mui/material';
import { useMaterialReactTable, MaterialReactTable } from 'material-react-table';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Code as CodeIcon,
} from '@mui/icons-material';
import rulesService from '../../services/rulesService';
import AdvancedRuleBuilder from './AdvancedRuleBuilder';

const AdvancedRulesList = ({ groupId }) => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingRule, setEditingRule] = useState(null);
  const [showRuleBuilder, setShowRuleBuilder] = useState(false);

  const formatConditions = (conditions) => {
    if (!conditions || Object.keys(conditions).length === 0) {
      return 'No conditions';
    }
    return Object.entries(conditions).map(([field, criteria]) => (
      <Chip
        key={field}
        label={`${field}: ${Object.entries(criteria).map(([op, val]) => `${op}=${val}`).join(', ')}`}
        size="small"
        sx={{ m: 0.5 }}
      />
    ));
  };

  const formatCalculations = (calculations) => {
    if (!calculations || calculations.length === 0) {
      return 'No calculations';
    }
    return calculations.map((calc, index) => (
      <Chip
        key={index}
        label={`${calc.type}: ${calc.value}`}
        size="small"
        sx={{ m: 0.5 }}
      />
    ));
  };

  const columns = [
    {
      accessorKey: 'field',
      header: 'Field',
      Cell: ({ row }) => {
        const fieldMap = Object.fromEntries(
          row.original.FIELD_CHOICES?.map(([value, label]) => [value, label]) || []
        );
        return <Typography fontWeight="medium">{fieldMap[row.original.field] || row.original.field}</Typography>;
      },
      size: 150,
    },
    {
      accessorKey: 'operator',
      header: 'Operator',
      Cell: ({ row }) => {
        const operatorMap = Object.fromEntries(
          row.original.OPERATOR_CHOICES?.map(([value, label]) => [value, label]) || []
        );
        return (
          <Chip 
            label={operatorMap[row.original.operator] || row.original.operator} 
            size="small" 
            variant="outlined"
            color="primary"
          />
        );
      },
      size: 120,
    },
    {
      accessorKey: 'value',
      header: 'Value',
      Cell: ({ row }) => (
        <Typography 
          sx={{ 
            fontFamily: 'monospace', 
            bgcolor: 'grey.100', 
            px: 1, 
            py: 0.5, 
            borderRadius: 1,
            display: 'inline-block'
          }}
        >
          {row.original.value}
        </Typography>
      ),
      size: 150,
    },
    {
      accessorKey: 'conditions',
      header: 'Conditions',
      Cell: ({ row }) => {
        const conditionEntries = Object.entries(row.original.conditions || {});
        if (conditionEntries.length === 0) {
          return (
            <Typography variant="body2" color="text.secondary" fontStyle="italic">
              No additional conditions
            </Typography>
          );
        }
        return (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {formatConditions(row.original.conditions)}
          </Box>
        );
      },
      size: 200,
    },
    {
      accessorKey: 'calculations',
      header: 'Calculations',
      Cell: ({ row }) => {
        // Check for case-based tier calculations
        const hasCaseTiers = row.original.calculations?.some(calc => calc.type === 'case_based_tier');
        
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {formatCalculations(row.original.calculations)}
            </Box>
            
            {hasCaseTiers && (
              <Chip 
                label="Case-Based Tier Pricing" 
                size="small" 
                color="secondary"
                variant="outlined"
                sx={{ alignSelf: 'flex-start' }}
              />
            )}
          </Box>
        );
      },
      size: 200,
    },
  ];

  const table = useMaterialReactTable({
    columns,
    data: rules,
    enableRowActions: true,
    positionActionsColumn: 'last',
    muiTableContainerProps: { sx: { maxHeight: '500px' } },
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    muiTableProps: {
      sx: {
        tableLayout: 'auto',
      },
    },
    renderRowActions: ({ row }) => (
      <Box sx={{ display: 'flex', gap: '1rem' }}>
        <Tooltip title="Edit">
          <IconButton onClick={() => setEditingRule(row.original)}>
            <EditIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete">
          <IconButton
            color="error"
            onClick={() => handleDeleteRule(row.original.id)}
          >
            <DeleteIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="View JSON">
          <IconButton
            onClick={() => {
              console.log('Advanced Rule Details:', {
                conditions: row.original.conditions,
                calculations: row.original.calculations
              });
            }}
          >
            <CodeIcon />
          </IconButton>
        </Tooltip>
      </Box>
    ),
    initialState: {
      sorting: [{ id: 'field', desc: false }],
      pagination: { pageSize: 10 },
    },
    state: {
      isLoading: loading,
    },
  });

  useEffect(() => {
    if (groupId) {
      fetchRules();
    }
  }, [groupId]);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const fetchedRules = await rulesService.getAdvancedRules(groupId);
      setRules(fetchedRules);
      setError(null);
    } catch (err) {
      console.error('Error fetching advanced rules:', err);
      // Check if it's a connection error
      if (err.message && (
          err.message.includes('connect to the server') ||
          err.message.includes('Network error') ||
          err.message.includes('Failed to fetch')
      )) {
        setError('Cannot connect to the server. Please make sure the backend is running.');
      } else if (err.status === 404) {
        setError(`Advanced rules endpoint not found. There may be an API path mismatch. Check the /api/v1/rules/group/${groupId}/advanced-rules/ endpoint.`);
      } else if (err.status === 500) {
        setError('Server error processing this request. This might be due to incorrect API paths or route configuration. Check server logs for more details.');
      } else {
        setError(`Failed to fetch advanced rules: ${err.message || 'Unknown error'}. Please try again.`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async (ruleData) => {
    try {
      await rulesService.createAdvancedRule(groupId, ruleData);
      await fetchRules();
      setShowRuleBuilder(false);
    } catch (err) {
      setError('Failed to create advanced rule. Please try again.');
      console.error('Error creating advanced rule:', err);
    }
  };

  const handleUpdateRule = async (id, ruleData) => {
    try {
      await rulesService.updateAdvancedRule(id, ruleData);
      await fetchRules();
      setEditingRule(null);
    } catch (err) {
      setError('Failed to update advanced rule. Please try again.');
      console.error('Error updating advanced rule:', err);
    }
  };

  const handleDeleteRule = async (id) => {
    try {
      await rulesService.deleteAdvancedRule(id);
      await fetchRules();
    } catch (err) {
      setError('Failed to delete advanced rule. Please try again.');
      console.error('Error deleting advanced rule:', err);
    }
  };

  return (
    <Box>
      <Box mb={2} display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          {error && (
            <Alert 
              severity="error" 
              sx={{ mb: 2, maxWidth: '600px' }}
              action={
                <Button 
                  color="inherit" 
                  size="small" 
                  onClick={() => fetchRules()}
                >
                  Retry
                </Button>
              }
            >
              {error}
            </Alert>
          )}
        </Box>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setShowRuleBuilder(true)}
        >
          Create Advanced Rule
        </Button>
      </Box>

      {!loading && rules.length === 0 && !error ? (
        <Box sx={{ p: 4, textAlign: 'center', border: '1px dashed', borderColor: 'grey.300', borderRadius: 1 }}>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            No advanced rules found for this group.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Click the "Create Advanced Rule" button to add a new rule.
          </Typography>
        </Box>
      ) : (
        <MaterialReactTable table={table} />
      )}

      {showRuleBuilder && (
        <AdvancedRuleBuilder
          groupId={groupId}
          onSubmit={handleCreateRule}
          onCancel={() => setShowRuleBuilder(false)}
        />
      )}

      {editingRule && (
        <AdvancedRuleBuilder
          groupId={groupId}
          initialData={editingRule}
          onSubmit={handleUpdateRule}
          onCancel={() => setEditingRule(null)}
        />
      )}
    </Box>
  );
};

export default AdvancedRulesList;