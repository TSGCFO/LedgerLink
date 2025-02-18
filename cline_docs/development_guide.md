# LedgerLink Development Guide

[Previous content remains the same until the "Best Practices" section...]

## Best Practices

1. Code Review
   - Required for all changes
   - Focus on maintainability
   - Check for test coverage
   - Verify documentation

2. Performance
   - Optimize database queries
   - Minimize API calls
   - Implement caching where appropriate
   - Monitor frontend bundle size

3. Accessibility
   - WCAG 2.1 compliance
   - Keyboard navigation
   - Screen reader support
   - Color contrast requirements

4. Error Handling
   - Consistent error messages
   - Proper error logging
   - User-friendly error displays
   - Recovery procedures

## Bulk Operations Development

### Template Generation
1. Field Definition Pattern
   ```python
   def _get_field_definition():
       return {
           'field_name': {
               'type': 'string|integer|decimal|choice|json',
               'required': True|False,
               'description': 'Field description',
               'choices': [('value', 'label')],  # For choice fields
               'default': 'default_value'  # Optional
           }
       }
   ```

2. Validation Implementation
   ```python
   def validate_field(self, value):
       if pd.isna(value) or value is None or value == '' or value == 'nan':
           if self.default:
               return self.default
           if self.required:
               raise ValidationError("This field is required")
           return None
       
       # Field-specific validation
       if self.field_type == 'choice':
           if value not in [choice[0] for choice in self.choices]:
               raise ValidationError(f"'{value}' is not a valid choice")
   ```

### File Processing
1. Client-side Validation
   ```jsx
   const validateFile = async (file) => {
     const errors = [];
     
     // Size validation
     if (file.size > 10 * 1024 * 1024) {
       errors.push('File size exceeds 10MB limit');
     }

     // Format validation
     const extension = file.name.split('.').pop().toLowerCase();
     if (!['csv', 'xlsx', 'xls'].includes(extension)) {
       errors.push('Unsupported file format');
     }

     // Content validation for CSV
     if (extension === 'csv') {
       const text = await file.text();
       const lines = text.split('\n');
       if (lines.length > 1000) {
         errors.push('File exceeds maximum row limit');
       }
     }

     return errors;
   };
   ```

2. Progress Tracking
   ```jsx
   const [progress, setProgress] = useState(0);
   const [validationErrors, setValidationErrors] = useState([]);
   
   // Progress simulation
   const progressInterval = setInterval(() => {
     setProgress(prev => {
       if (prev >= 90) {
         clearInterval(progressInterval);
         return 90;
       }
       return prev + 10;
     });
   }, 500);
   ```

### Error Handling
1. Row-level Errors
   ```python
   def process_row(self, row_data, row_number):
       errors = {}
       for field, value in row_data.items():
           try:
               self.validate_field(field, value)
           except ValidationError as e:
               errors[field] = str(e)
       
       if errors:
           return {
               'row': row_number,
               'errors': errors
           }
       return None
   ```

2. Error Display
   ```jsx
   const ValidationErrors = ({ errors }) => (
     <Alert severity="error">
       <Typography variant="subtitle2">
         Validation Errors:
       </Typography>
       <List dense>
         {errors.map((error, index) => (
           <ListItem key={index}>
             <ListItemIcon>
               <ErrorIcon color="error" />
             </ListItemIcon>
             <ListItemText
               primary={`Row ${error.row}`}
               secondary={Object.entries(error.errors)
                 .map(([field, msgs]) => `${field}: ${msgs.join(', ')}`)
                 .join('; ')}
             />
           </ListItem>
         ))}
       </List>
     </Alert>
   );
   ```

### Testing Requirements
1. Template Tests
   ```python
   def test_template_generation(self):
       template = TemplateGenerator.get_template('orders')
       self.assertIn('transaction_id', template.fields)
       self.assertTrue(template.fields['transaction_id'].required)
       self.assertEqual(template.fields['status'].default, 'draft')
   ```

2. Validation Tests
   ```python
   def test_field_validation(self):
       serializer = OrderBulkSerializer()
       
       # Test NaN handling
       self.assertEqual(
           serializer.validate_status('nan'),
           'draft'
       )
       
       # Test invalid choice
       with self.assertRaises(ValidationError):
           serializer.validate_status('invalid_status')
   ```

3. File Processing Tests
   ```python
   def test_file_processing(self):
       processor = BulkFileProcessor()
       result = processor.process_file('test.csv')
       
       self.assertEqual(result.total_rows, 5)
       self.assertEqual(result.successful, 3)
       self.assertEqual(result.failed, 2)
       self.assertEqual(len(result.errors), 2)
   ```

### API Documentation
1. Bulk Import Endpoint
   ```
   POST /api/v1/bulk-operations/import/{type}/
   
   Request:
   - Multipart form data with file

   Response (Success):
   {
     "success": true,
     "import_summary": {
       "total_rows": number,
       "successful": number,
       "failed": number
     }
   }

   Response (Error):
   {
     "success": false,
     "errors": [
       {
         "row": number,
         "errors": {
           "field": ["error messages"]
         }
       }
     ]
   }
   ```

2. Template Info Endpoint
   ```
   GET /api/v1/bulk-operations/templates/template-info/{type}/
   
   Response:
   {
     "success": true,
     "data": {
       "fields": ["field_names"],
       "required_fields": ["required_field_names"],
       "field_types": {
         "field_name": "type"
       }
     }
   }
   ```

### Performance Considerations
1. File Processing
   - Use chunked processing for large files
   - Implement background tasks for long operations
   - Add proper timeout handling
   - Monitor memory usage

2. Database Operations
   - Use bulk_create for efficient imports
   - Implement transaction management
   - Add proper indexing
   - Monitor query performance

3. Frontend Performance
   - Implement progressive loading
   - Add proper error boundaries
   - Optimize re-renders
   - Monitor bundle size