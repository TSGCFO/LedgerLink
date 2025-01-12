// static/js/rules/rule-group.js
class RuleGroup {
    constructor() {
        this.initializeDeleteModals();
        this.initializeTooltips();
    }

    initializeDeleteModals() {
        // Delete rule modal
        const deleteRuleModal = document.getElementById('deleteRuleModal');
        if (deleteRuleModal) {
            deleteRuleModal.addEventListener('show.bs.modal', (event) => {
                const button = event.relatedTarget;
                const ruleId = button.getAttribute('data-rule-id');
                const deleteForm = document.getElementById('deleteRuleForm');
                deleteForm.action = `/rules/rule/${ruleId}/delete/`;
            });
        }

        // Delete advanced rule modal
        const deleteAdvancedRuleModal = document.getElementById('deleteAdvancedRuleModal');
        if (deleteAdvancedRuleModal) {
            deleteAdvancedRuleModal.addEventListener('show.bs.modal', (event) => {
                const button = event.relatedTarget;
                const ruleId = button.getAttribute('data-rule-id');
                const deleteForm = document.getElementById('deleteAdvancedRuleForm');
                deleteForm.action = `/rules/advanced-rule/${ruleId}/delete/`;
            });
        }
    }

    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new RuleGroup();
});