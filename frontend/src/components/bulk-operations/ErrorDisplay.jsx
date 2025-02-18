import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Error as ErrorIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

class ErrorDisplay extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Bulk Operations Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 3 }}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <ErrorIcon color="error" sx={{ mr: 2, fontSize: 40 }} />
              <Typography variant="h5" color="error">
                Something went wrong
              </Typography>
            </Box>

            <Alert severity="error" sx={{ mb: 3 }}>
              {this.state.error?.message || 'An unexpected error occurred'}
            </Alert>

            <List>
              <ListItem>
                <ListItemIcon>
                  <ErrorIcon color="error" />
                </ListItemIcon>
                <ListItemText
                  primary="Error Details"
                  secondary={this.state.error?.stack}
                />
              </ListItem>
            </List>

            <Box mt={3}>
              <Button
                variant="contained"
                startIcon={<RefreshIcon />}
                onClick={() => window.location.reload()}
              >
                Reload Page
              </Button>
            </Box>
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorDisplay;