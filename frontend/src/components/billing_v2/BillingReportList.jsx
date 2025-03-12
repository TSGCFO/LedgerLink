import React from 'react';
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Tooltip,
  Box,
  Chip,
  CircularProgress
} from '@mui/material';
import { format } from 'date-fns';
import DownloadIcon from '@mui/icons-material/Download';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { billingV2Api } from '../../utils/api/billingV2Api';
import logger from '../../utils/logger';

/**
 * List of billing reports with selection and download functionality
 */
const BillingReportList = ({ 
  reports, 
  onReportSelected, 
  selectedReportId,
  loading = false
}) => {
  const handleDownload = async (reportId, e) => {
    e.stopPropagation();
    try {
      await billingV2Api.downloadBillingReport(reportId, 'csv');
    } catch (err) {
      logger.error('Error downloading report', err);
    }
  };
  
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };
  
  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMM d, yyyy');
    } catch (err) {
      return dateString;
    }
  };
  
  return (
    <Paper elevation={3} sx={{ height: '100%' }}>
      <Box sx={{ p: 2, borderBottom: '1px solid rgba(0, 0, 0, 0.12)' }}>
        <Typography variant="h6" component="h2">
          Billing Reports
        </Typography>
      </Box>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : reports.length === 0 ? (
        <Box sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary">
            No reports found. Generate a new report using the form above.
          </Typography>
        </Box>
      ) : (
        <List sx={{ overflow: 'auto', maxHeight: 'calc(100vh - 300px)' }}>
          {reports.map((report, index) => (
            <React.Fragment key={report.id}>
              {index > 0 && <Divider />}
              <ListItem disablePadding>
                <ListItemButton
                  selected={report.id === selectedReportId}
                  onClick={() => onReportSelected(report.id)}
                  sx={{ 
                    display: 'block',
                    '&.Mui-selected': {
                      backgroundColor: 'rgba(0, 0, 0, 0.04)',
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                    <Typography variant="subtitle1" noWrap>
                      {report.customer_name}
                    </Typography>
                    <Chip 
                      label={formatCurrency(report.total_amount)} 
                      color="primary" 
                      size="small" 
                      sx={{ ml: 1 }}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" noWrap>
                    {formatDate(report.start_date)} to {formatDate(report.end_date)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" component="div" sx={{ mt: 1 }}>
                    Created: {formatDate(report.created_at)}
                  </Typography>
                  
                  <ListItemSecondaryAction>
                    <Tooltip title="View Report">
                      <IconButton 
                        edge="end" 
                        aria-label="view" 
                        onClick={() => onReportSelected(report.id)}
                        size="small"
                      >
                        <VisibilityIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Download CSV">
                      <IconButton 
                        edge="end" 
                        aria-label="download" 
                        onClick={(e) => handleDownload(report.id, e)}
                        size="small"
                      >
                        <DownloadIcon />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItemButton>
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default BillingReportList;