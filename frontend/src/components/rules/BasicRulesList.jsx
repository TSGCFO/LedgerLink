import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  IconButton,
  Tooltip,
  Typography,
  Alert,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material';
import { useMaterialReactTable, MaterialReactTable } from 'material-react-table';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import rulesService from '../../services/rulesService';
import RuleBuilder from './RuleBuilder';

const BasicRulesList = ({ groupId }) => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingRule, setEditingRule] = useState(null);
  const [showRuleBuilder, setShowRuleBuilder] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState({ open: false, ruleId: null });

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
      accessorKey: 'adjustment_amount',
      header: 'Adjustment Amount',
      Cell: ({ row }) => (
        <Typography>
          {row.original.adjustment_amount ? `$${row.original.adjustment_amount}` : 'N/A'}
        </Typography>
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
            onClick={() => handleDeleteConfirm(row.original.id)}
          >
            <DeleteIcon />
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
      const fetchedRules = await rulesService.getRules(groupId);
      setRules(fetchedRules);
      setError(null);
    } catch (err) {
      console.error('Error fetching basic rules:', err);
      // Check if it's a connection error
      if (err.message && (
          err.message.includes('connect to the server') ||
          err.message.includes('Network error') ||
          err.message.includes('Failed to fetch')
      )) {
        setError('Cannot connect to the server. Please make sure the backend is running.');
      } else if (err.status === 404) {
        setError(`Basic rules endpoint not found. There may be an API path mismatch. Check the /api/v1/rules/group/${groupId}/rules/ endpoint.`);
      } else if (err.status === 500) {
        setError('Server error processing this request. This might be due to incorrect API paths or route configuration.');
      } else {
        setError(`Failed to fetch basic rules: ${err.message || 'Unknown error'}. Please try again.`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async (ruleData) => {
    try {
      await rulesService.createRule(groupId, ruleData);
      await fetchRules();
      setShowRuleBuilder(false);
    } catch (err) {
      setError('Failed to create rule. Please try again.');
      console.error('Error creating rule:', err);
    }
  };

  const handleUpdateRule = async (id, ruleData) => {
    try {
      await rulesService.updateRule(id, ruleData);
      await fetchRules();
      setEditingRule(null);
    } catch (err) {
      setError('Failed to update rule. Please try again.');
      console.error('Error updating rule:', err);
    }
  };

  const handleDeleteConfirm = (id) => {
    setDeleteConfirm({ open: true, ruleId: id });
  };

  const handleDeleteCancel = () => {
    setDeleteConfirm({ open: false, ruleId: null });
  };

  const handleDeleteRule = async () => {
    try {
      const id = deleteConfirm.ruleId;
      await rulesService.deleteRule(id);
      await fetchRules();
      setDeleteConfirm({ open: false, ruleId: null });
    } catch (err) {
      setError('Failed to delete rule. Please try again.');
      console.error('Error deleting rule:', err);
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
          Create Rule
        </Button>
      </Box>

      {!loading && rules.length === 0 && !error ? (
        <Box sx={{ p: 4, textAlign: 'center', border: '1px dashed', borderColor: 'grey.300', borderRadius: 1 }}>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            No basic rules found for this group.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Click the "Create Rule" button to add a new rule.
          </Typography>
        </Box>
      ) : (
        <MaterialReactTable table={table} />
      )}

      {showRuleBuilder && (
        <RuleBuilder
          groupId={groupId}
          onSubmit={handleCreateRule}
          onCancel={() => setShowRuleBuilder(false)}
        />
      )}

      {editingRule && (
        <RuleBuilder
          groupId={groupId}
          initialData={editingRule}
          onSubmit={handleUpdateRule}
          onCancel={() => setEditingRule(null)}
        />
      )}

      <Dialog
        open={deleteConfirm.open}
        onClose={handleDeleteCancel}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Confirm Delete
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete this rule? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteRule} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BasicRulesList;