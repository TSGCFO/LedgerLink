import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import TemplateSelector from './TemplateSelector';
import FileUploader from './FileUploader';
import ValidationProgress from './ValidationProgress';
import ErrorDisplay from './ErrorDisplay';
import ResultsSummary from './ResultsSummary';

const steps = ['Select Template', 'Upload File', 'Validation', 'Results'];

const BulkOperations = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [file, setFile] = useState(null);
  const [validationProgress, setValidationProgress] = useState(0);
  const [validationErrors, setValidationErrors] = useState([]);
  const [importSummary, setImportSummary] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setActiveStep(1);
  };

  const handleFileSelect = async (selectedFile) => {
    if (!selectedFile) return;

    // Client-side validation
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10MB limit');
      return;
    }

    const extension = selectedFile.name.split('.').pop().toLowerCase();
    if (!['csv', 'xlsx', 'xls'].includes(extension)) {
      setError('Unsupported file format. Please use CSV or Excel files.');
      return;
    }

    setFile(selectedFile);
    setError(null);
    setActiveStep(2);
    await validateFile(selectedFile);
  };

  const validateFile = async (selectedFile) => {
    setIsProcessing(true);
    setValidationProgress(0);
    setValidationErrors([]);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      // Start progress simulation
      const progressInterval = setInterval(() => {
        setValidationProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      const response = await fetch(`/api/v1/bulk-operations/import/${selectedTemplate.type}/`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      const result = await response.json();

      if (result.success) {
        setImportSummary(result.import_summary);
        setValidationProgress(100);
        setActiveStep(3);
      } else {
        setValidationErrors(result.errors || []);
        setError(result.error || 'Validation failed');
        setValidationProgress(100);
      }
    } catch (err) {
      setError('Error processing file: ' + err.message);
      setValidationProgress(100);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRetry = () => {
    setFile(null);
    setValidationErrors([]);
    setImportSummary(null);
    setError(null);
    setActiveStep(1);
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return <TemplateSelector onSelect={handleTemplateSelect} />;
      case 1:
        return (
          <FileUploader
            selectedTemplate={selectedTemplate}
            onFileSelect={handleFileSelect}
            error={error}
          />
        );
      case 2:
        return (
          <ValidationProgress
            progress={validationProgress}
            errors={validationErrors}
            isProcessing={isProcessing}
          />
        );
      case 3:
        return (
          <ResultsSummary
            summary={importSummary}
            errors={validationErrors}
            onRetry={handleRetry}
          />
        );
      default:
        return null;
    }
  };

  return (
    <ErrorDisplay>
      <Box sx={{ p: 3 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Bulk Operations
          </Typography>

          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {renderStepContent()}
        </Paper>
      </Box>
    </ErrorDisplay>
  );
};

export default BulkOperations;