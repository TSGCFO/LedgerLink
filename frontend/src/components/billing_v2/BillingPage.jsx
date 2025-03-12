import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  Alert, 
  Snackbar,
  CircularProgress,
  Breadcrumbs,
  Link,
  Divider
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import ReceiptIcon from '@mui/icons-material/Receipt';
import BillingReportGenerator from './BillingReportGenerator';
import BillingReportList from './BillingReportList';
import BillingReportViewer from './BillingReportViewer';
import { billingV2Api } from '../../utils/api/billingV2Api';
import logger from '../../utils/logger';

/**
 * Main Billing V2 page component
 */
const BillingPage = () => {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState({
    reports: true,
    customers: true,
    selectedReport: false
  });
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });
  
  // Fetch reports on component mount
  useEffect(() => {
    fetchReports();
    fetchCustomers();
  }, []);
  
  const fetchReports = async () => {
    setLoading(prev => ({ ...prev, reports: true }));
    try {
      console.log('Fetching reports using billingV2Api:', billingV2Api);
      const response = await billingV2Api.getBillingReports();
      console.log('Reports API response:', response);
      
      // Make sure we have a valid response structure
      if (!response || typeof response !== 'object') {
        throw new Error('Invalid response format');
      }
      
      // Ensure data is an array, even if empty
      const reportData = Array.isArray(response.data) ? response.data : [];
      setReports(reportData);
      setError(null);
    } catch (err) {
      console.error('Error in fetchReports:', err);
      logger.error('Error fetching billing reports', err);
      
      if (err.status === 403 && err.message?.includes('CSRF')) {
        setError('CSRF verification failed. Please contact admin to add the domain to CSRF_TRUSTED_ORIGINS');
        showSnackbar('CSRF verification failed', 'error');
      } else if (err.status === 500) {
        setError('Server error: The billing reports API endpoint is not responding correctly');
        showSnackbar('Server error in reports API', 'error');
      } else {
        setError('Failed to load billing reports: ' + (err.message || 'Unknown error'));
        showSnackbar('Error loading reports', 'error');
      }
    } finally {
      setLoading(prev => ({ ...prev, reports: false }));
    }
  };
  
  const fetchCustomers = async () => {
    setLoading(prev => ({ ...prev, customers: true }));
    try {
      console.log('Importing customerApi');
      // Import the customer API with error catching
      let customerApi;
      try {
        const apiModule = await import('../../utils/apiClient');
        console.log('ApiClient module imported:', apiModule);
        
        if (!apiModule || !apiModule.customerApi) {
          throw new Error('CustomerApi not found in apiClient module');
        }
        
        customerApi = apiModule.customerApi;
      } catch (importErr) {
        console.error('Error importing customer API:', importErr);
        throw new Error(`Failed to import customer API: ${importErr.message}`);
      }
      
      console.log('Fetching customers using customerApi:', customerApi);
      const response = await customerApi.list();
      console.log('Customers API response:', response);
      
      // Ensure data is an array, even if empty
      const customerData = Array.isArray(response.data) ? response.data : [];
      setCustomers(customerData);
    } catch (err) {
      console.error('Error in fetchCustomers:', err);
      logger.error('Error fetching customers', err);
      showSnackbar('Error loading customers: ' + (err.message || 'Unknown error'), 'error');
    } finally {
      setLoading(prev => ({ ...prev, customers: false }));
    }
  };
  
  const handleReportGenerated = (newReport) => {
    // Add the new report to the reports list
    setReports(prevReports => [newReport, ...prevReports]);
    
    // Select the new report
    setSelectedReport(newReport);
    
    // Show success message
    showSnackbar('Report generated successfully', 'success');
    
    // Refresh the reports list to ensure we have the latest data
    fetchReports();
  };
  
  const handleReportSelected = async (reportId) => {
    // If already selected, do nothing
    if (selectedReport && selectedReport.id === reportId) return;
    
    setLoading(prev => ({ ...prev, selectedReport: true }));
    try {
      console.log('Selecting report with ID:', reportId);
      
      if (!reportId) {
        throw new Error('Invalid report ID');
      }
      
      console.log('Using billingV2Api to get report details:', billingV2Api);
      const response = await billingV2Api.getBillingReport(reportId);
      console.log('Report details response:', response);
      
      // Make sure we have a valid response structure
      if (!response || typeof response !== 'object') {
        throw new Error('Invalid response format for report details');
      }
      
      // Make sure data is an object
      if (!response.data || typeof response.data !== 'object') {
        throw new Error('Invalid report data structure');
      }
      
      setSelectedReport(response.data);
      setError(null);
    } catch (err) {
      console.error('Error in handleReportSelected:', err);
      logger.error('Error fetching billing report', err);
      setError('Failed to load billing report details: ' + (err.message || 'Unknown error'));
      showSnackbar('Error loading report details', 'error');
    } finally {
      setLoading(prev => ({ ...prev, selectedReport: false }));
    }
  };
  
  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };
  
  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };
  
  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 3, mb: 4 }}>
        <Breadcrumbs aria-label="breadcrumb">
          <Link 
            color="inherit" 
            href="/" 
            sx={{ display: 'flex', alignItems: 'center' }}
          >
            <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Home
          </Link>
          <Typography 
            color="text.primary"
            sx={{ display: 'flex', alignItems: 'center' }}
          >
            <ReceiptIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Billing System V2
          </Typography>
        </Breadcrumbs>
      </Box>
      
      <Typography variant="h4" component="h1" gutterBottom>
        Billing System V2
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Generate and manage billing reports for customers based on orders and services.
      </Typography>
      
      <Divider sx={{ my: 3 }} />
      
      {error && (
        <Alert severity="error" sx={{ my: 2 }}>
          {error}
        </Alert>
      )}
      
      <BillingReportGenerator 
        onReportGenerated={handleReportGenerated} 
        customers={customers}
        loading={loading.customers}
      />
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4} lg={3}>
          <BillingReportList
            reports={reports}
            onReportSelected={handleReportSelected}
            selectedReportId={selectedReport?.id}
            loading={loading.reports}
          />
        </Grid>
        
        <Grid item xs={12} md={8} lg={9}>
          <BillingReportViewer 
            report={selectedReport} 
            loading={loading.selectedReport}
          />
        </Grid>
      </Grid>
      
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          variant="filled"
          elevation={6}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default BillingPage;