import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  Alert,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';

const ResultsSummary = ({ summary, errors, onRetry }) => {
  const [showErrors, setShowErrors] = useState(true);

  const getStatusColor = () => {
    if (!summary) return 'error';
    return summary.failed === 0 ? 'success' : 'warning';
  };

  const getStatusText = () => {
    if (!summary) return 'Import Failed';
    if (summary.failed === 0) return 'Import Successful';
    return 'Import Completed with Errors';
  };

  const renderSummaryCard = (title, value, icon, color) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" mb={1}>
          {icon}
          <Typography variant="h6" component="div" sx={{ ml: 1 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" color={color}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  const renderError = (error, index) => {
    const errorDetails = typeof error === 'string'
      ? { message: error }
      : {
          row: error.row,
          message: Object.entries(error.errors)
            .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
            .join('; '),
        };

    return (
      <ListItem key={index}>
        <ListItemIcon>
          <ErrorIcon color="error" />
        </ListItemIcon>
        <ListItemText
          primary={errorDetails.row ? `Row ${errorDetails.row}` : 'Error'}
          secondary={errorDetails.message}
        />
      </ListItem>
    );
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Import Results
      </Typography>

      <Paper sx={{ p: 3 }}>
        <Box display="flex" alignItems="center" mb={3}>
          {getStatusColor() === 'success' ? (
            <CheckCircleIcon color="success" sx={{ mr: 1 }} />
          ) : getStatusColor() === 'warning' ? (
            <WarningIcon color="warning" sx={{ mr: 1 }} />
          ) : (
            <ErrorIcon color="error" sx={{ mr: 1 }} />
          )}
          <Typography variant="h5" color={`${getStatusColor()}.main`}>
            {getStatusText()}
          </Typography>
        </Box>

        {summary && (
          <>
            <Grid container spacing={3} mb={3}>
              <Grid item xs={12} sm={4}>
                {renderSummaryCard(
                  'Total Rows',
                  summary.total_rows,
                  <CheckCircleIcon color="primary" />,
                  'primary.main'
                )}
              </Grid>
              <Grid item xs={12} sm={4}>
                {renderSummaryCard(
                  'Successful',
                  summary.successful,
                  <CheckCircleIcon color="success" />,
                  'success.main'
                )}
              </Grid>
              <Grid item xs={12} sm={4}>
                {renderSummaryCard(
                  'Failed',
                  summary.failed,
                  <ErrorIcon color="error" />,
                  'error.main'
                )}
              </Grid>
            </Grid>

            {summary.failed > 0 && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                Some records failed to import. Please review the errors below and try again with corrected data.
              </Alert>
            )}
          </>
        )}

        {errors && errors.length > 0 && (
          <Box>
            <Button
              startIcon={showErrors ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              onClick={() => setShowErrors(!showErrors)}
              sx={{ mb: 1 }}
            >
              {showErrors ? 'Hide' : 'Show'} Errors ({errors.length})
            </Button>
            <Collapse in={showErrors}>
              <Paper variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
                <List dense>
                  {errors.map((error, index) => renderError(error, index))}
                </List>
              </Paper>
            </Collapse>
          </Box>
        )}

        <Box mt={3}>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={onRetry}
            color="primary"
          >
            Upload Another File
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ResultsSummary;