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
        return <Typography>{fieldMap[row.original.field] || row.original.field}</Typography>;
      },
    },
    {
      accessorKey: 'operator',
      header: 'Operator',
      Cell: ({ row }) => {
        const operatorMap = Object.fromEntries(
          row.original.OPERATOR_CHOICES?.map(([value, label]) => [value, label]) || []
        );
        return <Typography>{operatorMap[row.original.operator] || row.original.operator}</Typography>;
      },
    },
    {
      accessorKey: 'value',
      header: 'Value',
    },
    {
      accessorKey: 'conditions',
      header: 'Conditions',
      Cell: ({ row }) => (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          {formatConditions(row.original.conditions)}
        </Box>
      ),
    },
    {
      accessorKey: 'calculations',
      header: 'Calculations',
      Cell: ({ row }) => (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          {formatCalculations(row.original.calculations)}
        </Box>
      ),
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
      setError('Failed to fetch advanced rules. Please try again.');
      console.error('Error fetching advanced rules:', err);
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
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box mb={2} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setShowRuleBuilder(true)}
        >
          Create Advanced Rule
        </Button>
      </Box>

      <MaterialReactTable table={table} />

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