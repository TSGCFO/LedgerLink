import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  IconButton,
  Tooltip,
  Typography,
} from '@mui/material';
import { useMaterialReactTable, MaterialReactTable } from 'material-react-table';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import RuleGroupForm from './RuleGroupForm';

const RuleGroupsList = ({ groups, onSelect, onUpdate, onDelete, onCreateNew }) => {
  const [editingGroup, setEditingGroup] = useState(null);
  const [selectedGroupId, setSelectedGroupId] = useState(null);

  const columns = [
    {
      accessorKey: 'customer_service.name',
      header: 'Customer Service',
      Cell: ({ row }) => (
        <Typography>
          {row.original.customer_service?.name || 'N/A'}
        </Typography>
      ),
    },
    {
      accessorKey: 'logic_operator',
      header: 'Logic Operator',
      Cell: ({ row }) => {
        const logicMap = {
          'AND': 'All conditions must be true',
          'OR': 'Any condition can be true',
          'NOT': 'Condition must not be true',
          'XOR': 'Only one condition must be true',
          'NAND': 'At least one condition must be false',
          'NOR': 'None of the conditions must be true',
        };
        return (
          <Typography>
            {logicMap[row.original.logic_operator] || row.original.logic_operator}
          </Typography>
        );
      },
    },
    {
      accessorKey: 'rules',
      header: 'Rules Count',
      Cell: ({ row }) => (
        <Typography>
          {row.original.rules?.length || 0}
        </Typography>
      ),
    },
  ];

  const handleEdit = (group) => {
    setEditingGroup(group);
  };

  const handleUpdateComplete = async (groupData) => {
    await onUpdate(editingGroup.id, groupData);
    setEditingGroup(null);
  };

  const handleRowClick = (row) => {
    setSelectedGroupId(row.original.id);
    onSelect(row.original);
  };

  const [tableData, setTableData] = useState(groups || []);

  useEffect(() => {
    setTableData(groups || []);
  }, [groups]);

  const [rowSelection, setRowSelection] = useState({});

  useEffect(() => {
    setRowSelection({});
  }, [tableData]);

  const table = useMaterialReactTable({
    columns,
    data: tableData,
    enableRowActions: true,
    positionActionsColumn: 'last',
    muiTableContainerProps: { sx: { maxHeight: '500px' } },
    enableColumnResizing: true,
    columnResizeMode: "onChange",
    enablePagination: true,
    manualPagination: false,
    autoResetPageIndex: true,
    state: {
      rowSelection,
      isLoading: !groups
    },
    onRowSelectionChange: setRowSelection,
    enableRowSelection: false,
    muiTableProps: {
      sx: {
        tableLayout: 'auto',
      },
    },
    renderRowActions: ({ row }) => (
      <Box sx={{ display: 'flex', gap: '1rem' }}>
        <Tooltip title="Edit">
          <IconButton onClick={(e) => {
            e.stopPropagation(); // Prevent row selection when clicking edit
            handleEdit(row.original);
          }}>
            <EditIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete">
          <IconButton
            color="error"
            onClick={(e) => {
              e.stopPropagation(); // Prevent row selection when clicking delete
              onDelete(row.original.id);
            }}
          >
            <DeleteIcon />
          </IconButton>
        </Tooltip>
      </Box>
    ),
    muiTableBodyRowProps: ({ row }) => ({
      onClick: () => handleRowClick(row),
      sx: {
        cursor: 'pointer',
        backgroundColor: row.original.id === selectedGroupId ? 'rgba(25, 118, 210, 0.08)' : 'inherit',
        '&:hover': {
          backgroundColor: row.original.id === selectedGroupId 
            ? 'rgba(25, 118, 210, 0.12)' 
            : 'rgba(0, 0, 0, 0.04)',
        },
      },
    }),
    initialState: {
      pagination: { pageSize: 10 }
    },
    muiTablePaperProps: {
      elevation: 0,
      sx: {
        borderRadius: '8px',
        border: '1px solid rgba(224, 224, 224, 1)',
      },
    },
    muiTableHeadCellProps: {
      sx: {
        fontWeight: 'bold',
        backgroundColor: '#f5f5f5',
      },
    },
    displayColumnDefOptions: {
      'mrt-row-actions': {
        header: 'Actions',
        size: 100,
      },
    },
  });

  return (
    <Box>
      <Box mb={2} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={onCreateNew}
        >
          Create Rule Group
        </Button>
      </Box>

      <MaterialReactTable table={table} />

      {editingGroup && (
        <RuleGroupForm
          initialData={editingGroup}
          onSubmit={handleUpdateComplete}
          onCancel={() => setEditingGroup(null)}
        />
      )}
    </Box>
  );
};

export default RuleGroupsList;





