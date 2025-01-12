// static/js/rules/advanced-rule-builder.js

class AdvancedRuleBuilder {
    constructor() {
        // Initialize components
        this.initializeComponents();
        // Bind event handlers
        this.bindEvents();
        // Set up validation
        this.setupValidation();
    }

    initializeComponents() {
        // Step navigation
        this.currentStep = 1;
        this.totalSteps = 4;
        this.steps = {
            baseRule: document.getElementById('baseRuleStep'),
            conditions: document.getElementById('conditionsStep'),
            calculations: document.getElementById('calculationsStep'),
            review: document.getElementById('reviewStep')
        };
        this.stepIndicators = document.querySelectorAll('.step');

        // Navigation buttons
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.submitBtn = document.getElementById('submitBtn');

        // Form elements
        this.form = document.getElementById('advancedRuleForm');
        this.fieldSelect = document.getElementById('id_field');
        this.operatorSelect = document.getElementById('id_operator');
        this.valueInput = document.getElementById('id_value');
        this.adjustmentInput = document.getElementById('id_adjustment_amount');

        // Initialize condition builder
        this.conditionBuilder = new ConditionBuilder();

        // Initialize calculation selector
        this.calculationSelector = new CalculationSelector();
    }

    bindEvents() {
        // Navigation events
        this.prevBtn.addEventListener('click', () => this.navigateStep('prev'));
        this.nextBtn.addEventListener('click', () => this.navigateStep('next'));

        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));

        // Field dependencies
        this.fieldSelect.addEventListener('change', () => this.updateOperators());

        // Preview updates
        this.form.addEventListener('change', () => this.updatePreviews());
    }

    setupValidation() {
        this.validators = {
            baseRule: () => this.validateBaseRule(),
            conditions: () => this.validateConditions(),
            calculations: () => this.validateCalculations()
        };
    }

    navigateStep(direction) {
        if (direction === 'prev' && this.currentStep > 1) {
            this.showStep(this.currentStep - 1);
        } else if (direction === 'next' && this.currentStep < this.totalSteps) {
            if (this.validateCurrentStep()) {
                this.showStep(this.currentStep + 1);
            }
        }
    }

    showStep(stepNumber) {
        // Hide all steps
        Object.values(this.steps).forEach(step => step.classList.add('d-none'));

        // Show current step
        const stepKeys = Object.keys(this.steps);
        this.steps[stepKeys[stepNumber - 1]].classList.remove('d-none');

        // Update navigation
        this.updateNavigation(stepNumber);

        // Update indicators
        this.updateStepIndicators(stepNumber);

        // Update previews
        this.updatePreviews();

        this.currentStep = stepNumber;
    }

    updateNavigation(stepNumber) {
        this.prevBtn.style.display = stepNumber === 1 ? 'none' : 'block';
        this.nextBtn.style.display = stepNumber === this.totalSteps ? 'none' : 'block';
        this.submitBtn.classList.toggle('d-none', stepNumber !== this.totalSteps);
    }

    updateStepIndicators(currentStep) {
        this.stepIndicators.forEach((indicator, index) => {
            if (index + 1 < currentStep) {
                indicator.className = 'step completed';
            } else if (index + 1 === currentStep) {
                indicator.className = 'step active';
            } else {
                indicator.className = 'step';
            }
        });
    }

    updatePreviews() {
        if (this.currentStep === this.totalSteps) {
            this.updateReviewStep();
        } else {
            this.updateStepPreview(this.currentStep);
        }
    }

    updateStepPreview(step) {
        switch(step) {
            case 2:
                this.conditionBuilder.updatePreview();
                break;
            case 3:
                this.calculationSelector.updatePreview();
                break;
        }
    }

    updateReviewStep() {
        // Base Rule Review
        const baseRulePreview = document.getElementById('reviewBaseRule');
        baseRulePreview.innerHTML = this.getBaseRulePreviewHTML();

        // Conditions Review
        const conditionsPreview = document.getElementById('reviewConditions');
        conditionsPreview.innerHTML = this.conditionBuilder.getPreviewHTML();

        // Calculations Review
        const calculationsPreview = document.getElementById('reviewCalculations');
        calculationsPreview.innerHTML = this.calculationSelector.getPreviewHTML();
    }

    getBaseRulePreviewHTML() {
        const field = this.fieldSelect.options[this.fieldSelect.selectedIndex].text;
        const operator = this.operatorSelect.options[this.operatorSelect.selectedIndex].text;
        const value = this.valueInput.value;

        return `
            <div class="d-flex align-items-center mb-3">
                <span class="badge bg-primary me-2">Base Rule</span>
                <span>When <strong>${field}</strong> ${operator} <strong>${value}</strong></span>
            </div>
        `;
    }

    validateCurrentStep() {
        const validator = this.validators[Object.keys(this.steps)[this.currentStep - 1]];
        return validator ? validator() : true;
    }

    validateBaseRule() {
        if (!this.fieldSelect.value) {
            this.showError('Please select a field');
            return false;
        }
        if (!this.operatorSelect.value) {
            this.showError('Please select an operator');
            return false;
        }
        if (!this.valueInput.value) {
            this.showError('Please enter a value');
            return false;
        }
        return true;
    }

    validateConditions() {
        return this.conditionBuilder.validate();
    }

    validateCalculations() {
        if (!this.adjustmentInput.value && !this.calculationSelector.hasSelectedCalculations()) {
            this.showError('Please specify either a base adjustment amount or select additional calculations');
            return false;
        }
        return true;
    }

    async updateOperators() {
        const field = this.fieldSelect.value;
        try {
            const response = await fetch(`/rules/api/operators/?field=${field}`);
            const data = await response.json();

            this.operatorSelect.innerHTML = data.operators
                .map(op => `<option value="${op.value}">${op.label}</option>`)
                .join('');

            // Update value input type based on field
            this.updateValueInput(field);

        } catch (error) {
            console.error('Error fetching operators:', error);
            this.showError('Error loading operators');
        }
    }

    updateValueInput(field) {
        const numericFields = ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages'];
        if (numericFields.includes(field)) {
            this.valueInput.type = 'number';
            this.valueInput.step = '0.01';
        } else {
            this.valueInput.type = 'text';
            this.valueInput.removeAttribute('step');
        }
    }

    showError(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger border-0';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    async handleSubmit(e) {
        e.preventDefault();

        if (!this.validateForm()) {
            return;
        }

        try {
            // Update hidden fields
            document.getElementById('id_conditions').value =
                JSON.stringify(this.conditionBuilder.getConditions());
            document.getElementById('id_calculations').value =
                JSON.stringify(this.calculationSelector.getCalculations());

            // Submit form
            this.form.submit();

        } catch (error) {
            console.error('Error submitting form:', error);
            this.showError('Error saving rule');
        }
    }

    validateForm() {
        // Validate all steps
        for (let step = 1; step <= this.totalSteps; step++) {
            if (!this.validators[Object.keys(this.steps)[step - 1]]()) {
                this.showStep(step);
                return false;
            }
        }
        return true;
    }
}

class ConditionBuilder {
    constructor() {
        this.container = document.getElementById('conditionsList');
        this.addButton = document.getElementById('addConditionBtn');
        this.preview = document.getElementById('conditionsPreview');
        this.conditions = [];

        this.addButton.addEventListener('click', () => this.addCondition());
    }

    addCondition() {
        const condition = {
            id: Date.now(),
            field: '',
            operator: '',
            value: ''
        };

        this.conditions.push(condition);
        this.renderCondition(condition);
        this.updatePreview();
    }

    renderCondition(condition) {
        const conditionElement = document.createElement('div');
        conditionElement.className = 'condition-card';
        conditionElement.dataset.id = condition.id;

        conditionElement.innerHTML = `
            <div class="row g-3 align-items-center">
                <div class="col-md-4">
                    <select class="form-select field-select" data-id="${condition.id}">
                        <option value="">Select Field</option>
                        ${this.getFieldOptions()}
                    </select>
                </div>
                <div class="col-md-3">
                    <select class="form-select operator-select" data-id="${condition.id}">
                        <option value="">Select Operator</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <input type="text" class="form-control value-input" 
                           data-id="${condition.id}" placeholder="Enter value">
                </div>
                <div class="col-md-1">
                    <button type="button" class="btn btn-outline-danger btn-sm"
                            onclick="removeCondition(${condition.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;

        this.container.appendChild(conditionElement);
        this.bindConditionEvents(condition.id);
    }

    getFieldOptions() {
        // Get field options from the main field select
        const mainSelect = document.getElementById('id_field');
        return Array.from(mainSelect.options)
            .map(opt => `<option value="${opt.value}">${opt.text}</option>`)
            .join('');
    }

    bindConditionEvents(conditionId) {
        const fieldSelect = this.container.querySelector(`.field-select[data-id="${conditionId}"]`);
        fieldSelect.addEventListener('change', () => this.updateOperators(conditionId));
    }

    async updateOperators(conditionId) {
        const fieldSelect = this.container.querySelector(`.field-select[data-id="${conditionId}"]`);
        const operatorSelect = this.container.querySelector(`.operator-select[data-id="${conditionId}"]`);

        try {
            const response = await fetch(`/rules/api/operators/?field=${fieldSelect.value}`);
            const data = await response.json();

            operatorSelect.innerHTML = `
                <option value="">Select Operator</option>
                ${data.operators.map(op => `
                    <option value="${op.value}">${op.label}</option>
                `).join('')}
            `;

        } catch (error) {
            console.error('Error fetching operators:', error);
        }
    }

    removeCondition(conditionId) {
        this.conditions = this.conditions.filter(c => c.id !== conditionId);
        const element = this.container.querySelector(`[data-id="${conditionId}"]`);
        if (element) {
            element.remove();
        }
        this.updatePreview();
    }

    updatePreview() {
        if (this.conditions.length === 0) {
            this.preview.classList.add('d-none');
            return;
        }

        this.preview.classList.remove('d-none');
        const previewContent = document.getElementById('conditionsPreviewContent');

        previewContent.innerHTML = this.conditions.map(condition => {
            const fieldSelect = this.container.querySelector(`.field-select[data-id="${condition.id}"]`);
            const operatorSelect = this.container.querySelector(`.operator-select[data-id="${condition.id}"]`);
            const valueInput = this.container.querySelector(`.value-input[data-id="${condition.id}"]`);

            return `
                <div class="mb-2">
                    <span class="badge bg-secondary me-2">AND</span>
                    When <strong>${fieldSelect.options[fieldSelect.selectedIndex].text}</strong>
                    ${operatorSelect.options[operatorSelect.selectedIndex].text}
                    <strong>${valueInput.value}</strong>
                </div>
            `;
        }).join('');
    }

    validate() {
        return this.conditions.every(condition => {
            const fieldSelect = this.container.querySelector(`.field-select[data-id="${condition.id}"]`);
            const operatorSelect = this.container.querySelector(`.operator-select[data-id="${condition.id}"]`);
            const valueInput = this.container.querySelector(`.value-input[data-id="${condition.id}"]`);

            return fieldSelect.value && operatorSelect.value && valueInput.value;
        });
    }

    getConditions() {
        return this.conditions.map(condition => {
            const fieldSelect = this.container.querySelector(`.field-select[data-id="${condition.id}"]`);
            const operatorSelect = this.container.querySelector(`.operator-select[data-id="${condition.id}"]`);
            const valueInput = this.container.querySelector(`.value-input[data-id="${condition.id}"]`);

            return {
                field: fieldSelect.value,
                operator: operatorSelect.value,
                value: valueInput.value
            };
        });
    }

    getPreviewHTML() {
        if (this.conditions.length === 0) {
            return '<p class="text-muted mb-0">No additional conditions</p>';
        }

        return this.conditions.map(condition => {
            const fieldSelect = this.container.querySelector(`.field-select[data-id="${condition.id}"]`);
            const operatorSelect = this.container.querySelector(`.operator-select[data-id="${condition.id}"]`);
            const valueInput = this.container.querySelector(`.value-input[data-id="${condition.id}"]`);

            return `
                <div class="d-flex align-items-center mb-2">
                    <span class="badge bg-secondary me-2">AND</span>
                    <span>
                        When <strong>${fieldSelect.options[fieldSelect.selectedIndex].text}</strong>
                        ${operatorSelect.options[operatorSelect.selectedIndex].text}
                        <strong>${valueInput.value}</strong>
                    </span>
                </div>
            `;
        }).join('');
    }
}

class CalculationSelector {
    constructor() {
        this.container = document.querySelector('.calculation-type-cards');
        this.preview = document.getElementById('calculationsPreview');
        this.selectedCalculations = new Set();

        this.bindEvents();
    }

    bindEvents() {
        document.querySelectorAll('.calculation-type-card').forEach(card => {
            card.addEventListener('click', () => this.toggleCalculation(card));
        });
    }

    toggleCalculation(card) {
        card.classList.toggle('selected');
        const calculationType = card.dataset.type;

        if (card.classList.contains('selected')) {
            this.selectedCalculations.add(calculationType);
        } else {
            this.selectedCalculations.delete(calculationType);
        }

        this.updatePreview();
    }

    updatePreview() {
        if (this.selectedCalculations.size === 0) {
            this.preview.classList.add('d-none');
            return;
        }

        this.preview.classList.remove('d-none');
        const previewContent = document.getElementById('calculationsPreviewContent');

        previewContent.innerHTML = Array.from(this.selectedCalculations).map(type => `
            <div class="mb-2">
                <span class="badge bg-primary me-2">${type}</span>
                <span>${this.getCalculationDescription(type)}</span>
            </div>
        `).join('');
    }

    getCalculationDescription(type) {
        const descriptions = {
            'flat_fee': 'Add a fixed amount',
            'percentage': 'Add a percentage of the base price',
            'per_unit': 'Multiply by quantity',
            'weight_based': 'Multiply by weight',
            'volume_based': 'Multiply by volume',
            'tiered_percentage': 'Apply percentage based on value tiers',
            'product_specific': 'Apply specific rates per product'
        };
        return descriptions[type] || type;
    }

    hasSelectedCalculations() {
        return this.selectedCalculations.size > 0;
    }

    getCalculations() {
        return Array.from(this.selectedCalculations).map(type => ({
            type,
            value: 0 // Default value, can be updated later
        }));
    }

    getPreviewHTML() {
        const adjustmentInput = document.getElementById('id_adjustment_amount');
        const baseAdjustment = adjustmentInput.value ?
            `<div class="mb-3">
                <span class="badge bg-success me-2">Base Adjustment</span>
                <strong>$${adjustmentInput.value}</strong>
            </div>` : '';

        const additionalCalculations = this.selectedCalculations.size > 0 ?
            Array.from(this.selectedCalculations).map(type => `
                <div class="mb-2">
                    <span class="badge bg-primary me-2">${type}</span>
                    <span>${this.getCalculationDescription(type)}</span>
                </div>
            `).join('') :
            '<p class="text-muted mb-0">No additional calculations</p>';

        return baseAdjustment + additionalCalculations;
    }
}

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.advancedRuleBuilder = new AdvancedRuleBuilder();
});