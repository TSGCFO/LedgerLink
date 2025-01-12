// static/js/rules/advanced-rule.js
class AdvancedRuleForm {
    constructor() {
        this.form = document.getElementById('advancedRuleForm');
        this.conditionsEditor = null;
        this.calculationsEditor = null;
        this.fieldSelect = document.getElementById('id_field');
        this.operatorSelect = document.getElementById('id_operator');

        this.init();
    }

    init() {
        this.initializeJSONEditors();
        this.initializeFieldDependencies();
        this.initializeCalculationTypes();
        this.initializeValidationButtons();
        this.initializeFormSubmission();
    }

    initializeJSONEditors() {
        // Initialize JSON editor for conditions
        this.conditionsEditor = new JSONEditor(
            document.getElementById('id_conditions'),
            {
                mode: 'code',
                modes: ['code', 'tree'],
                onChangeText: () => this.validateConditions()
            }
        );

        // Initialize JSON editor for calculations
        this.calculationsEditor = new JSONEditor(
            document.getElementById('id_calculations'),
            {
                mode: 'code',
                modes: ['code', 'tree'],
                onChangeText: () => this.validateCalculations()
            }
        );
    }

    async initializeFieldDependencies() {
        this.fieldSelect.addEventListener('change', async () => {
            const field = this.fieldSelect.value;
            try {
                const response = await fetch(`/rules/api/operators/?field=${field}`);
                const data = await response.json();

                this.operatorSelect.innerHTML = data.operators
                    .map(op => `<option value="${op.value}">${op.label}</option>`)
                    .join('');
            } catch (error) {
                console.error('Error fetching operators:', error);
            }
        });
    }

    initializeCalculationTypes() {
        document.querySelectorAll('.calculation-type').forEach(el => {
            el.addEventListener('click', () => {
                const type = el.dataset.type;
                const currentCalcs = this.calculationsEditor.get() || [];

                currentCalcs.push({
                    type: type,
                    value: 0
                });

                this.calculationsEditor.set(currentCalcs);
                this.validateCalculations();
            });
        });
    }

    initializeValidationButtons() {
        document.getElementById('validateConditions')
            .addEventListener('click', () => this.validateConditions());
        document.getElementById('validateCalculations')
            .addEventListener('click', () => this.validateCalculations());
    }

    async validateConditions() {
        const conditions = this.conditionsEditor.get();
        const indicator = document.querySelector('#id_conditions')
            .nextElementSibling;

        try {
            const response = await fetch('/rules/api/advanced-rule/validate-conditions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ conditions })
            });

            const data = await response.json();

            if (data.valid) {
                this.showValidation(indicator, true);
                this.showPreview('conditions', conditions);
            } else {
                this.showValidation(indicator, false);
                this.hidePreview('conditions');
            }
        } catch (error) {
            console.error('Validation error:', error);
            this.showValidation(indicator, false);
        }
    }

    async validateCalculations() {
        const calculations = this.calculationsEditor.get();
        const indicator = document.querySelector('#id_calculations')
            .nextElementSibling;

        try {
            const response = await fetch('/rules/api/advanced-rule/validate-calculations/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ calculations })
            });

            const data = await response.json();

            if (data.valid) {
                this.showValidation(indicator, true);
                this.showPreview('calculations', calculations);
            } else {
                this.showValidation(indicator, false);
                this.hidePreview('calculations');
            }
        } catch (error) {
            console.error('Validation error:', error);
            this.showValidation(indicator, false);
        }
    }

    showValidation(indicator, isValid) {
        indicator.innerHTML = isValid
            ? '<i class="bi bi-check-circle-fill text-success"></i>'
            : '<i class="bi bi-x-circle-fill text-danger"></i>';
        indicator.classList.remove('d-none');
    }

    showPreview(type, data) {
        const preview = document.getElementById(`${type}Preview`);
        const content = document.getElementById(`${type}PreviewContent`);

        content.innerHTML = type === 'conditions'
            ? this.formatConditionsPreview(data)
            : this.formatCalculationsPreview(data);

        preview.classList.remove('d-none');
    }

    hidePreview(type) {
        document.getElementById(`${type}Preview`).classList.add('d-none');
    }

    formatConditionsPreview(conditions) {
        return Object.entries(conditions)
            .map(([field, criteria]) => `
                <div class="mb-2">
                    <strong>${field}:</strong>
                    ${Object.entries(criteria)
                        .map(([op, val]) => `${op} ${val}`)
                        .join(', ')}
                </div>
            `).join('');
    }

    formatCalculationsPreview(calculations) {
        return calculations
            .map(calc => `
                <div class="mb-2">
                    <span class="badge bg-secondary">${calc.type}</span>
                    <strong class="ms-2">$${calc.value}</strong>
                </div>
            `).join('');
    }

    initializeFormSubmission() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();

            try {
                // Update hidden form fields
                document.getElementById('id_conditions').value =
                    JSON.stringify(this.conditionsEditor.get());
                document.getElementById('id_calculations').value =
                    JSON.stringify(this.calculationsEditor.get());

                // Submit the form
                this.form.submit();
            } catch (error) {
                console.error('Form submission error:', error);
                alert('Please fix the validation errors before submitting.');
            }
        });
    }
}

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AdvancedRuleForm();
});