import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Tooltip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Info as InfoIcon,
  NavigateNext as NavigateNextIcon,
} from '@mui/icons-material';

const TemplateSelector = ({ onSelect }) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/v1/bulk-operations/templates/');
      const result = await response.json();

      if (result.success) {
        setTemplates(result.data.templates);
      } else {
        setError(result.error || 'Failed to fetch templates');
      }
    } catch (err) {
      setError('Error loading templates: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateSelect = async (template) => {
    try {
      // Fetch template info before selection
      const response = await fetch(`/api/v1/bulk-operations/templates/template-info/${template.type}/`);
      const result = await response.json();

      if (result.success) {
        const templateWithInfo = {
          ...template,
          fields: result.data.fields,
          requiredFields: result.data.requiredFields,
          fieldTypes: result.data.fieldTypes,
        };
        setSelectedTemplate(templateWithInfo);
      } else {
        setError(result.error || 'Failed to fetch template information');
      }
    } catch (err) {
      setError('Error loading template information: ' + err.message);
    }
  };

  const handleDownloadTemplate = async (templateType, event) => {
    event.stopPropagation();
    try {
      const response = await fetch(`/api/v1/bulk-operations/templates/${templateType}/download/`);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to download template');
      }

      // Create a blob from the response
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${templateType}_template.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Error downloading template: ' + err.message);
    }
  };

  const handleNext = () => {
    if (selectedTemplate) {
      onSelect(selectedTemplate);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Select a Template
      </Typography>
      <Grid container spacing={2}>
        {templates.map((template) => (
          <Grid item xs={12} sm={6} md={4} key={template.type}>
            <Card
              sx={{
                cursor: 'pointer',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'scale(1.02)',
                },
                bgcolor: selectedTemplate?.type === template.type ? 'action.selected' : 'background.paper',
              }}
              onClick={() => handleTemplateSelect(template)}
            >
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6" component="div">
                    {template.name}
                  </Typography>
                  <Tooltip title="Download Template">
                    <Button
                      size="small"
                      startIcon={<DownloadIcon />}
                      onClick={(e) => handleDownloadTemplate(template.type, e)}
                    >
                      Template
                    </Button>
                  </Tooltip>
                </Box>
                <Typography color="text.secondary" sx={{ mt: 1 }}>
                  {template.description}
                </Typography>
                {template.fieldCount && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {template.fieldCount} fields
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {selectedTemplate && (
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            color="primary"
            endIcon={<NavigateNextIcon />}
            onClick={handleNext}
          >
            Next: Upload File
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default TemplateSelector;