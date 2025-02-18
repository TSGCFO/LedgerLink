import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
} from '@mui/material';
import RuleGroupsList from './RuleGroupsList';
import BasicRulesList from './BasicRulesList';
import AdvancedRulesList from './AdvancedRulesList';
import RuleGroupForm from './RuleGroupForm';
import rulesService from '../../services/rulesService';

const RulesDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [ruleGroups, setRuleGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showGroupForm, setShowGroupForm] = useState(false);

  // Initial data load
  useEffect(() => {
    fetchRuleGroups();
  }, []);

  // Refresh data when returning to groups tab
  useEffect(() => {
    if (activeTab === 0) {
      // Small delay to ensure proper state update
      const timer = setTimeout(() => {
        fetchRuleGroups();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [activeTab]);

  const fetchRuleGroups = async () => {
    try {
      setLoading(true);
      const groups = await rulesService.getRuleGroups();
      setRuleGroups(groups);
      setError(null);
    } catch (err) {
      setError('Failed to fetch rule groups. Please try again.');
      console.error('Error fetching rule groups:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    // Reset error state on tab change
    setError(null);
    
    // Update active tab
    setActiveTab(newValue);
    
    // Handle tab-specific logic
    if (newValue === 0) {
      // When switching to groups tab, maintain selection but refresh data
      setLoading(true);
      fetchRuleGroups().finally(() => {
        setLoading(false);
      });
    }
  };

  const handleGroupSelect = (group) => {
    setSelectedGroup(group);
  };

  const handleGroupCreate = async (groupData) => {
    try {
      await rulesService.createRuleGroup(groupData);
      await fetchRuleGroups();
      setShowGroupForm(false);
    } catch (err) {
      setError('Failed to create rule group. Please try again.');
      console.error('Error creating rule group:', err);
    }
  };

  const handleGroupUpdate = async (id, groupData) => {
    try {
      await rulesService.updateRuleGroup(id, groupData);
      await fetchRuleGroups();
    } catch (err) {
      setError('Failed to update rule group. Please try again.');
      console.error('Error updating rule group:', err);
    }
  };

  const handleGroupDelete = async (id) => {
    try {
      setLoading(true);
      await rulesService.deleteRuleGroup(id);
      const updatedGroups = await rulesService.getRuleGroups();
      setRuleGroups(updatedGroups);
      setSelectedGroup(null);
      setError(null);
    } catch (err) {
      setError('Failed to delete rule group. Please try again.');
      console.error('Error deleting rule group:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Rules Management
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ mb: 4 }}>
        <Tabs value={activeTab} onChange={handleTabChange} centered>
          <Tab label="Rule Groups" />
          <Tab label="Basic Rules" disabled={!selectedGroup} />
          <Tab label="Advanced Rules" disabled={!selectedGroup} />
        </Tabs>
      </Paper>

      <Box sx={{ display: activeTab === 0 ? 'block' : 'none' }}>
        <RuleGroupsList
          groups={ruleGroups}
          onSelect={handleGroupSelect}
          onUpdate={handleGroupUpdate}
          onDelete={handleGroupDelete}
          onCreateNew={() => setShowGroupForm(true)}
        />
        {showGroupForm && (
          <RuleGroupForm
            onSubmit={handleGroupCreate}
            onCancel={() => setShowGroupForm(false)}
          />
        )}
      </Box>

      <Box sx={{ display: activeTab === 1 ? 'block' : 'none' }}>
        {selectedGroup && <BasicRulesList groupId={selectedGroup.id} />}
      </Box>

      <Box sx={{ display: activeTab === 2 ? 'block' : 'none' }}>
        {selectedGroup && <AdvancedRulesList groupId={selectedGroup.id} />}
      </Box>
    </Container>
  );
};

export default RulesDashboard;

