import React from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

const ValidationProgress = ({ progress, errors, isProcessing }) => {
  const getStatusColor = () => {
    if (isProcessing) return 'primary';
    return errors.length > 0 ? 'error' : 'success';
  };

  const getStatusText = () => {
    if (isProcessing) return 'Validating...';
    return errors.length > 0 ? 'Validation Failed' : 'Validation Complete';
  };

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
        File Validation
      </Typography>

      <Paper sx={{ p: 3 }}>
        <Box display="flex" alignItems="center" mb={2}>
          {isProcessing ? (
            <CircularProgress size={24} sx={{ mr: 2 }} />
          ) : (
            <Box sx={{ mr: 2 }}>
              {errors.length > 0 ? (
                <ErrorIcon color="error" />
              ) : (
                <CheckCircleIcon color="success" />
              )}
            </Box>
          )}
          <Typography variant="subtitle1" color={getStatusColor()}>
            {getStatusText()}
          </Typography>
        </Box>

        <LinearProgress
          variant="determinate"
          value={progress}
          color={getStatusColor()}
          sx={{ mb: 2, height: 8, borderRadius: 4 }}
        />

        <Box display="flex" justifyContent="space-between" mb={2}>
          <Typography variant="body2" color="text.secondary">
            {progress}% Complete
          </Typography>
          {errors.length > 0 && (
            <Typography variant="body2" color="error">
              {errors.length} {errors.length === 1 ? 'Error' : 'Errors'} Found
            </Typography>
          )}
        </Box>

        {isProcessing && (
          <Box mb={2}>
            <Alert severity="info">
              Validating file contents and processing data. This may take a few moments...
            </Alert>
          </Box>
        )}

        {!isProcessing && errors.length > 0 && (
          <Box>
            <Typography variant="subtitle2" gutterBottom color="error">
              Validation Errors:
            </Typography>
            <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
              <List dense>
                {errors.map((error, index) => renderError(error, index))}
              </List>
            </Paper>
            <Alert severity="warning" sx={{ mt: 2 }}>
              Please correct these errors and try uploading again.
            </Alert>
          </Box>
        )}

        {!isProcessing && errors.length === 0 && progress === 100 && (
          <Alert severity="success">
            File validation successful. Processing data...
          </Alert>
        )}
      </Paper>
    </Box>
  );
};

export default ValidationProgress;