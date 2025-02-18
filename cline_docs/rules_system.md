# Rules System Documentation

## Overview
The Rules System is a core component of LedgerLink that manages business rules for customer services. It supports both basic and advanced rules with comprehensive CRUD operations.

## API Endpoints

### Rule Deletion
```
DELETE /rules/rule/{id}/delete/api/

Response (Success):
{
  "success": true,
  "message": "Rule deleted successfully",
  "group_id": number
}

Response (Error):
{
  "error": "Error message"
}

Status Codes:
- 200: Success
- 404: Rule not found
- 500: Server error
```

## Frontend Implementation

### Navigation and State Management
```jsx
// RulesDashboard.jsx - Component Rendering
<Box sx={{ display: activeTab === 0 ? 'block' : 'none' }}>
  <RuleGroupsList {...props} />
</Box>

// State Management
useEffect(() => {
  fetchRuleGroups();  // Initial data load
}, []);

useEffect(() => {
  if (activeTab === 0) {
    const timer = setTimeout(() => {
      fetchRuleGroups();
    }, 100);
    return () => clearTimeout(timer);
  }
}, [activeTab]);

const handleTabChange = (event, newValue) => {
  setError(null);
  setActiveTab(newValue);
  if (newValue === 0) {
    setLoading(true);
    fetchRuleGroups().finally(() => {
      setLoading(false);
    });
  }
};
```

Key Features:
- Uses CSS display property to maintain component state
- Separate initial data load and tab switch handling
- Proper loading states during data fetches
- Error state management during tab switches
- Maintains component state while switching tabs
- Prevents unnecessary component remounts
- Improves performance and user experience

### Rule Deletion Component
```jsx
// Confirmation Dialog Pattern
<Dialog open={deleteConfirm.open} onClose={handleDeleteCancel}>
  <DialogTitle>Confirm Delete</DialogTitle>
  <DialogContent>
    <DialogContentText>
      Are you sure you want to delete this rule? This action cannot be undone.
    </DialogContentText>
  </DialogContent>
  <DialogActions>
    <Button onClick={handleDeleteCancel}>Cancel</Button>
    <Button onClick={handleDeleteRule} color="error" variant="contained">
      Delete
    </Button>
  </DialogActions>
</Dialog>
```

### Error Handling
```javascript
try {
  await rulesService.deleteRule(id);
  await fetchRules(); // Refresh the list
  setDeleteConfirm({ open: false, ruleId: null });
} catch (error) {
  setError('Failed to delete rule. Please try again.');
  logger.error('Error deleting rule:', error);
}
```

## Implementation Guidelines

### Frontend
1. User Interface
   - Use confirmation dialogs for destructive actions
   - Show loading states during API calls
   - Display user-friendly error messages
   - Update UI state after successful deletion

2. Error Handling
   - Log detailed error information
   - Handle all possible error cases:
     * Rule not found (404)
     * Server errors (500)
     * Network errors
   - Provide clear recovery actions
   - Maintain consistent error message format

3. State Management
   - Update local state after successful deletion
   - Handle loading states properly
   - Manage confirmation dialog state
   - Refresh rule list after deletion

### Backend
1. API Implementation
   - Validate rule existence
   - Handle cascade deletion properly
   - Provide meaningful error messages
   - Return sufficient information for UI updates

2. Error Handling
   - Log all deletion attempts
   - Include relevant context in logs
   - Handle database errors gracefully
   - Return appropriate HTTP status codes

3. Security
   - Validate request parameters
   - Handle edge cases
   - Prevent unauthorized deletions
   - Maintain audit trail

## Testing Requirements

1. Frontend Tests
   - Test confirmation dialog behavior
   - Verify error handling
   - Check loading states
   - Validate UI updates

2. Backend Tests
   - Test successful deletion
   - Test error cases
   - Verify cascade deletion
   - Check error responses

3. Integration Tests
   - End-to-end deletion flow
   - Error scenario handling
   - State management
   - API response handling