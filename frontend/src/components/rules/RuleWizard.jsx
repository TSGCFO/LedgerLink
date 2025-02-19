import React, { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Stepper,
  Step,
  StepLabel,
  Typography,
  Paper,
  Alert,
} from '@mui/material';
import RuleGroupForm from './RuleGroupForm';
import BasicRulesList from './BasicRulesList';
import AdvancedRuleBuilder from './AdvancedRuleBuilder';

const steps = [
  {
    label: 'Choose Rule Type',
    description: 'Select whether you want to create basic rules or advanced rules',
  },
  {
    label: 'Create Rule Group',
    description: 'Set up a group to organize your rules',
  },
  {
    label: 'Add Rules',
    description: 'Create the specific rules for your group',
  },
  {
    label: 'Review',
    description: 'Review and confirm your rules',
  },
];

const RuleWizard = ({ open, onClose }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [ruleType, setRuleType] = useState(null);
  const [groupId, setGroupId] = useState(null);
  const [rules, setRules] = useState([]);

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleRuleTypeSelect = (type) => {
    setRuleType(type);
    handleNext();
  };

  const handleGroupCreated = (newGroupId) => {
    setGroupId(newGroupId);
    handleNext();
  };

  const handleRulesCreated = (newRules) => {
    setRules(newRules);
    handleNext();
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box display="flex" flexDirection="column" gap={3} p={3}>
            <Typography variant="h6" gutterBottom>
              What type of rules do you want to create?
            </Typography>
            
            <Paper
              elevation={3}
              sx={{
                p: 3,
                cursor: 'pointer',
                '&:hover': { bgcolor: 'action.hover' },
              }}
              onClick={() => handleRuleTypeSelect('basic')}
            >
              <Typography variant="h6" gutterBottom>
                Basic Rules
              </Typography>
              <Typography color="text.secondary">
                Simple rules for common scenarios. Best for:
                <ul>
                  <li>Checking order weight or quantity</li>
                  <li>Matching specific SKUs</li>
                  <li>Basic price adjustments</li>
                </ul>
              </Typography>
            </Paper>

            <Paper
              elevation={3}
              sx={{
                p: 3,
                cursor: 'pointer',
                '&:hover': { bgcolor: 'action.hover' },
              }}
              onClick={() => handleRuleTypeSelect('advanced')}
            >
              <Typography variant="h6" gutterBottom>
                Advanced Rules
              </Typography>
              <Typography color="text.secondary">
                Complex rules with multiple conditions. Best for:
                <ul>
                  <li>Case-based pricing tiers</li>
                  <li>Multiple conditions</li>
                  <li>Complex calculations</li>
                </ul>
              </Typography>
            </Paper>
          </Box>
        );

      case 1:
        return (
          <Box p={3}>
            <Typography variant="h6" gutterBottom>
              Create a Rule Group
            </Typography>
            <Typography color="text.secondary" paragraph>
              A rule group helps organize related rules and determines how they work together.
            </Typography>
            <RuleGroupForm onSubmit={handleGroupCreated} />
          </Box>
        );

      case 2:
        return (
          <Box p={3}>
            <Typography variant="h6" gutterBottom>
              Add Rules to Your Group
            </Typography>
            <Typography color="text.secondary" paragraph>
              Now let's create the specific rules that will determine when and how to adjust pricing.
            </Typography>
            {ruleType === 'basic' ? (
              <BasicRulesList groupId={groupId} onRulesCreated={handleRulesCreated} />
            ) : (
              <AdvancedRuleBuilder groupId={groupId} onSubmit={handleRulesCreated} />
            )}
          </Box>
        );

      case 3:
        return (
          <Box p={3}>
            <Typography variant="h6" gutterBottom>
              Review Your Rules
            </Typography>
            <Alert severity="success">
              Your rules have been created successfully! Here's a summary:
            </Alert>
            {/* Add rule summary display here */}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Create New Rules
      </DialogTitle>
      <DialogContent>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => (
            <Step key={step.label}>
              <StepLabel>
                <Typography variant="subtitle1">{step.label}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {step.description}
                </Typography>
              </StepLabel>
              {activeStep === index && (
                <Box mt={2}>
                  {renderStepContent(index)}
                  <Box mt={2} display="flex" justifyContent="space-between">
                    <Button
                      disabled={activeStep === 0}
                      onClick={handleBack}
                    >
                      Back
                    </Button>
                    {activeStep === steps.length - 1 ? (
                      <Button
                        variant="contained"
                        color="primary"
                        onClick={onClose}
                      >
                        Finish
                      </Button>
                    ) : null}
                  </Box>
                </Box>
              )}
            </Step>
          ))}
        </Stepper>
      </DialogContent>
    </Dialog>
  );
};

export default RuleWizard;