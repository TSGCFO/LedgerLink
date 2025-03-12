import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Box,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  IconButton,
  Tooltip,
  Card,
  CardContent
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DownloadIcon from '@mui/icons-material/Download';
import PrintIcon from '@mui/icons-material/Print';
import { format } from 'date-fns';
import { billingV2Api } from '../../utils/api/billingV2Api';
import logger from '../../utils/logger';

/**
 * Detailed view of a billing report
 */
const BillingReportViewer = ({ report, loading = false }) => {
  const [expandedOrder, setExpandedOrder] = useState(null);
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (!report) {
    return (
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="body1" color="text.secondary">
          Select a report from the list to view details.
        </Typography>
      </Paper>
    );
  }
  
  const handleDownload = async (format) => {
    try {
      await billingV2Api.downloadBillingReport(report.id, format);
    } catch (err) {
      logger.error(`Error downloading report as ${format}`, err);
    }
  };
  
  const handlePrint = () => {
    window.print();
  };
  
  const handleAccordionChange = (orderId) => (event, isExpanded) => {
    setExpandedOrder(isExpanded ? orderId : null);
  };
  
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };
  
  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMMM d, yyyy');
    } catch (err) {
      return dateString;
    }
  };
  
  // Calculate totals
  const totalOrders = report.orders ? report.orders.length : 0;
  
  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, flexWrap: 'wrap' }}>
        <Typography variant="h5" component="h2">
          Billing Report #{report.id}
        </Typography>
        
        <Box>
          <Tooltip title="Print Report">
            <IconButton onClick={handlePrint} sx={{ mr: 1 }}>
              <PrintIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload('csv')}
            size="small"
            sx={{ mr: 1 }}
          >
            CSV
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload('json')}
            size="small"
          >
            JSON
          </Button>
        </Box>
      </Box>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Customer Information
              </Typography>
              <Typography variant="body1">
                <strong>Customer:</strong> {report.customer_name}
              </Typography>
              <Typography variant="body1">
                <strong>Customer ID:</strong> {report.customer_id}
              </Typography>
              <Typography variant="body1">
                <strong>Report Generated:</strong> {formatDate(report.created_at)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Billing Period
              </Typography>
              <Typography variant="body1">
                <strong>Start Date:</strong> {formatDate(report.start_date)}
              </Typography>
              <Typography variant="body1">
                <strong>End Date:</strong> {formatDate(report.end_date)}
              </Typography>
              <Typography variant="body1">
                <strong>Total Amount:</strong> {formatCurrency(report.total_amount)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Service Totals */}
      <Typography variant="h6" gutterBottom>
        Service Totals
      </Typography>
      <TableContainer component={Paper} variant="outlined" sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Service</TableCell>
              <TableCell align="right">Amount</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(report.service_totals || {}).map(([serviceId, data]) => (
              <TableRow key={serviceId}>
                <TableCell>{data.service_name}</TableCell>
                <TableCell align="right">{formatCurrency(data.amount)}</TableCell>
              </TableRow>
            ))}
            <TableRow>
              <TableCell>
                <Typography variant="subtitle1"><strong>Total</strong></Typography>
              </TableCell>
              <TableCell align="right">
                <Typography variant="subtitle1"><strong>{formatCurrency(report.total_amount)}</strong></Typography>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
      
      {/* Order Details */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Order Details
        </Typography>
        <Chip label={`${totalOrders} Orders`} color="primary" />
      </Box>
      
      {report.orders && report.orders.map((order) => (
        <Accordion 
          key={order.order_id} 
          expanded={expandedOrder === order.order_id}
          onChange={handleAccordionChange(order.order_id)}
          sx={{ mb: 1 }}
        >
          <AccordionSummary 
            expandIcon={<ExpandMoreIcon />}
            aria-controls={`order-${order.order_id}-content`}
            id={`order-${order.order_id}-header`}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
              <Typography>
                Order #{order.order_id} - {order.reference_number}
              </Typography>
              <Box>
                <Chip 
                  label={formatDate(order.order_date)}
                  size="small"
                  sx={{ mr: 1 }}
                  variant="outlined"
                />
                <Chip 
                  label={formatCurrency(order.total_amount)}
                  size="small"
                  color="primary"
                />
              </Box>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Service</TableCell>
                    <TableCell align="right">Amount</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {order.service_costs && order.service_costs.map((service, index) => (
                    <TableRow key={index}>
                      <TableCell>{service.service_name}</TableCell>
                      <TableCell align="right">{formatCurrency(service.amount)}</TableCell>
                    </TableRow>
                  ))}
                  <TableRow>
                    <TableCell>
                      <Typography variant="subtitle2"><strong>Total</strong></Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="subtitle2"><strong>{formatCurrency(order.total_amount)}</strong></Typography>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>
      ))}
    </Paper>
  );
};

export default BillingReportViewer;