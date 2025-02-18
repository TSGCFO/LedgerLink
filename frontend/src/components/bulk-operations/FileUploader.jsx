import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Description as FileIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

const FileUploader = ({ selectedTemplate, onFileSelect, error }) => {
  const [dragActive, setDragActive] = useState(false);
  const [validating, setValidating] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [clientValidationErrors, setClientValidationErrors] = useState([]);
  const fileInputRef = useRef(null);

  const validateFile = async (file) => {
    setValidating(true);
    setClientValidationErrors([]);
    const errors = [];

    // Size validation
    if (file.size > 10 * 1024 * 1024) {
      errors.push('File size exceeds 10MB limit');
    }

    // Format validation
    const extension = file.name.split('.').pop().toLowerCase();
    if (!['csv', 'xlsx', 'xls'].includes(extension)) {
      errors.push('Unsupported file format. Please use CSV or Excel files.');
    }

    // Basic content validation for CSV files
    if (extension === 'csv') {
      try {
        const text = await file.text();
        const lines = text.split('\n');
        if (lines.length > 1000) {
          errors.push('File exceeds maximum row limit of 1000');
        }

        // Header validation
        if (lines.length > 0) {
          const headers = lines[0].split(',').map(h => h.trim());
          const missingRequired = selectedTemplate.requiredFields.filter(
            field => !headers.includes(field)
          );
          if (missingRequired.length > 0) {
            errors.push(`Missing required columns: ${missingRequired.join(', ')}`);
          }
        }
      } catch (err) {
        errors.push('Error reading file content');
      }
    }

    setValidating(false);
    setClientValidationErrors(errors);

    if (errors.length === 0) {
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await validateFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = async (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      await validateFile(e.target.files[0]);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  const getFieldDescription = (field, type) => {
    const fields = selectedTemplate.fields || {};
    const fieldDef = fields[field] || {};

    if (type === 'choice' && fieldDef.choices) {
      return (
        <Box>
          <Typography variant="body2" color="text.primary">
            Valid choices:
          </Typography>
          <List dense>
            {fieldDef.choices.map(([value, label]) => (
              <ListItem key={value}>
                <ListItemText 
                  primary={value}
                  secondary={label}
                />
              </ListItem>
            ))}
          </List>
          {fieldDef.description && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {fieldDef.description}
            </Typography>
          )}
        </Box>
      );
    }

    if (fieldDef.description) {
      return fieldDef.description;
    }

    if (type === 'json') {
      return 'JSON object (e.g., {"SKU1": 5, "SKU2": 3})';
    }

    if (type === 'datetime') {
      return 'Date and time (YYYY-MM-DD HH:MM:SS)';
    }

    if (type === 'date') {
      return 'Date (YYYY-MM-DD)';
    }

    if (type === 'decimal') {
      return 'Decimal number';
    }

    if (type === 'integer') {
      return 'Whole number';
    }

    return type;
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Upload {selectedTemplate.name} File
      </Typography>

      <Paper
        sx={{
          p: 3,
          border: '2px dashed',
          borderColor: dragActive ? 'primary.main' : 'grey.300',
          bgcolor: dragActive ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          mb: 3,
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleChange}
          style={{ display: 'none' }}
        />

        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
        >
          {validating ? (
            <CircularProgress sx={{ mb: 2 }} />
          ) : (
            <CloudUploadIcon sx={{ fontSize: 48, mb: 2, color: 'primary.main' }} />
          )}

          <Typography variant="h6" gutterBottom>
            {validating
              ? 'Validating file...'
              : 'Drag and drop your file here or click to browse'}
          </Typography>

          <Typography variant="body2" color="text.secondary">
            Supported formats: CSV, XLSX, XLS (Max 10MB)
          </Typography>
        </Box>
      </Paper>

      {selectedFile && (
        <Box mt={2}>
          <List>
            <ListItem>
              <ListItemIcon>
                <FileIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary={selectedFile.name}
                secondary={`${(selectedFile.size / 1024 / 1024).toFixed(2)} MB`}
              />
              <CheckCircleIcon color="success" />
            </ListItem>
          </List>
        </Box>
      )}

      {clientValidationErrors.length > 0 && (
        <Alert severity="error" sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Validation Errors:
          </Typography>
          <List dense>
            {clientValidationErrors.map((error, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <ErrorIcon color="error" fontSize="small" />
                </ListItemIcon>
                <ListItemText primary={error} />
              </ListItem>
            ))}
          </List>
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          Field Requirements
        </Typography>
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Field Name</TableCell>
                <TableCell>Required</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Description</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.entries(selectedTemplate.fieldTypes).map(([field, type]) => (
                <TableRow key={field}>
                  <TableCell>{field}</TableCell>
                  <TableCell>
                    {selectedTemplate.requiredFields.includes(field) ? (
                      <CheckCircleIcon color="success" fontSize="small" />
                    ) : 'Optional'}
                  </TableCell>
                  <TableCell>{type}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                      <Typography variant="body2">
                        {getFieldDescription(field, type)}
                      </Typography>
                      {selectedTemplate.fields?.[field]?.description && (
                        <Tooltip title={selectedTemplate.fields[field].description}>
                          <InfoIcon 
                            color="info" 
                            fontSize="small" 
                            sx={{ ml: 1, cursor: 'help' }}
                          />
                        </Tooltip>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>

      {selectedFile && !clientValidationErrors.length && (
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => onFileSelect(selectedFile)}
          >
            Next: Validate File
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default FileUploader;