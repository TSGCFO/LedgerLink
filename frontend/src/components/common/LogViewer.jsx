import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  IconButton,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Close as CloseIcon,
  DeleteOutline as DeleteIcon,
  FileDownload as DownloadIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import logger from '../../utils/logger';

/**
 * LogViewer component to display and manage captured logs
 */
const LogViewer = ({ open, onClose }) => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [filter, setFilter] = useState({
    level: 'all',
    search: '',
  });
  const [saveInProgress, setSaveInProgress] = useState(false);
  const [saveResult, setSaveResult] = useState(null);

  // Load logs initially and when the component is opened
  useEffect(() => {
    if (open) {
      refreshLogs();
    }
  }, [open]);

  // Apply filters when logs or filter changes
  useEffect(() => {
    applyFilters();
  }, [logs, filter]);

  const refreshLogs = () => {
    const allLogs = logger.getLogs();
    setLogs(allLogs);
  };

  const applyFilters = () => {
    let filtered = [...logs];

    // Filter by level
    if (filter.level !== 'all') {
      filtered = filtered.filter(log => log.level === filter.level);
    }

    // Filter by search term
    if (filter.search.trim()) {
      const searchLower = filter.search.toLowerCase();
      filtered = filtered.filter(log => {
        const messageMatch = log.message && log.message.toLowerCase().includes(searchLower);
        const dataMatch = log.data && log.data.toLowerCase().includes(searchLower);
        return messageMatch || dataMatch;
      });
    }

    setFilteredLogs(filtered);
  };

  const handleFilterChange = (name, value) => {
    setFilter(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleClearLogs = () => {
    if (window.confirm('Are you sure you want to clear all logs?')) {
      logger.clearLogs();
      setLogs([]);
    }
  };

  const handleExportLogs = () => {
    logger.exportLogs();
  };
  
  const handleSaveLogsToServer = async () => {
    try {
      setSaveInProgress(true);
      setSaveResult(null);
      
      const result = await logger.saveLogsToServer();
      
      setSaveResult(result);
      
      if (result.success) {
        // Show success message briefly
        setTimeout(() => {
          setSaveResult(null);
        }, 5000);
      }
    } catch (error) {
      setSaveResult({
        success: false,
        error: error.message || 'An unexpected error occurred'
      });
    } finally {
      setSaveInProgress(false);
    }
  };

  // Helper to format log level as a colored chip
  const getLevelChip = (level) => {
    let color = 'default';
    
    switch (level) {
      case 'ERROR':
        color = 'error';
        break;
      case 'WARN':
        color = 'warning';
        break;
      case 'INFO':
        color = 'info';
        break;
      case 'DEBUG':
        color = 'success';
        break;
      case 'LOG':
        color = 'primary';
        break;
      default:
        color = 'default';
    }
    
    return <Chip size="small" label={level} color={color} />;
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{ sx: { height: '80vh' } }}
    >
      <DialogTitle>
        Console Logs
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{ position: 'absolute', right: 8, top: 8 }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent dividers>
        {/* Filters and actions */}
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Level</InputLabel>
            <Select
              value={filter.level}
              label="Level"
              onChange={(e) => handleFilterChange('level', e.target.value)}
            >
              <MenuItem value="all">All Levels</MenuItem>
              <MenuItem value="ERROR">Error</MenuItem>
              <MenuItem value="WARN">Warning</MenuItem>
              <MenuItem value="INFO">Info</MenuItem>
              <MenuItem value="DEBUG">Debug</MenuItem>
              <MenuItem value="LOG">Log</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            label="Search"
            variant="outlined"
            size="small"
            value={filter.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            InputProps={{
              endAdornment: <SearchIcon color="action" />,
            }}
          />
          
          <Box sx={{ flexGrow: 1 }} />
          
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={refreshLogs}
          >
            Refresh
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleExportLogs}
          >
            Export
          </Button>
          
          <Button
            variant="outlined"
            color="primary"
            startIcon={saveInProgress ? <CircularProgress size={18} color="primary" /> : <SaveIcon />}
            onClick={handleSaveLogsToServer}
            disabled={saveInProgress || logs.length === 0}
          >
            Save to Server
          </Button>
          
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleClearLogs}
          >
            Clear All
          </Button>
        </Box>
        
        {/* Save result message */}
        {saveResult && (
          <Alert 
            severity={saveResult.success ? 'success' : 'error'} 
            sx={{ mb: 2 }}
            onClose={() => setSaveResult(null)}
          >
            {saveResult.success 
              ? `Successfully saved ${saveResult.log_count} logs to server (${saveResult.filename})`
              : `Error saving logs: ${saveResult.error}`
            }
          </Alert>
        )}
        
        {/* Log table */}
        {filteredLogs.length > 0 ? (
          <TableContainer component={Paper} sx={{ height: 'calc(100% - 60px)' }}>
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  <TableCell width="180px">Time</TableCell>
                  <TableCell width="100px">Level</TableCell>
                  <TableCell>Message</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredLogs.map((log, index) => (
                  <TableRow key={index} hover>
                    <TableCell sx={{ whiteSpace: 'nowrap' }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>{getLevelChip(log.level)}</TableCell>
                    <TableCell>
                      <Typography variant="body2" 
                        sx={{ 
                          whiteSpace: 'pre-wrap', 
                          wordBreak: 'break-word',
                          fontFamily: 'monospace'
                        }}
                      >
                        {log.message}
                      </Typography>
                      
                      {log.data && (
                        <Box 
                          sx={{ 
                            mt: 1, 
                            p: 1, 
                            backgroundColor: 'rgba(0,0,0,0.05)',
                            borderRadius: 1,
                            overflow: 'auto',
                            maxHeight: '200px',
                            fontFamily: 'monospace',
                            fontSize: '0.75rem'
                          }}
                        >
                          {typeof log.data === 'string' ? log.data : JSON.stringify(log.data, null, 2)}
                        </Box>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <Typography color="text.secondary">
              {logs.length === 0 ? 'No logs available' : 'No logs match the current filters'}
            </Typography>
          </Box>
        )}
      </DialogContent>
      
      <DialogActions>
        <Typography variant="caption" sx={{ mr: 2 }}>
          Displaying {filteredLogs.length} of {logs.length} logs
        </Typography>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default LogViewer;