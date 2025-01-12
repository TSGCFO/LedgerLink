// static/js/rules/json-editor.js

class JsonEditor {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            mode: 'code',
            modes: ['code', 'tree'],
            search: true,
            ...options
        };
        this.editor = null;
        this.init();
    }

    init() {
        // Create editor instance
        this.editor = new JSONEditor(this.container, {
            ...this.options,
            onChange: () => this.handleChange(),
            onValidate: (json) => this.handleValidation(json)
        });

        // Set initial value if provided
        if (this.options.initialValue) {
            this.setValue(this.options.initialValue);
        }

        // Add custom event listeners
        this.setupEventListeners();
    }

    setValue(value) {
        try {
            const parsedValue = typeof value === 'string' ? JSON.parse(value) : value;
            this.editor.set(parsedValue);
        } catch (error) {
            console.error('Error setting JSON value:', error);
            this.showError('Invalid JSON format');
        }
    }

    getValue() {
        try {
            return this.editor.get();
        } catch (error) {
            console.error('Error getting JSON value:', error);
            return null;
        }
    }

    getValidValue() {
        try {
            return this.editor.get();
        } catch (error) {
            return null;
        }
    }

    handleChange() {
        try {
            const value = this.editor.get();
            this.container.dispatchEvent(new CustomEvent('json-editor-change', {
                detail: { value, isValid: true }
            }));
        } catch (error) {
            this.container.dispatchEvent(new CustomEvent('json-editor-change', {
                detail: { error: error.message, isValid: false }
            }));
        }
    }

    handleValidation(json) {
        const errors = [];

        // Perform basic JSON validation
        if (json === undefined || json === null) {
            errors.push({
                type: 'validation',
                message: 'Value is required'
            });
        }

        // Validate based on editor mode
        if (this.options.mode === 'code') {
            try {
                JSON.parse(JSON.stringify(json));
            } catch (error) {
                errors.push({
                    type: 'validation',
                    message: 'Invalid JSON format'
                });
            }
        }

        // Custom schema validation if provided
        if (this.options.schema) {
            const schemaErrors = this.validateSchema(json, this.options.schema);
            errors.push(...schemaErrors);
        }

        return errors;
    }

    validateSchema(json, schema) {
        const errors = [];

        try {
            // Basic type checking
            if (schema.type === 'object' && typeof json !== 'object') {
                errors.push({
                    type: 'validation',
                    message: 'Value must be an object'
                });
            }

            if (schema.type === 'array' && !Array.isArray(json)) {
                errors.push({
                    type: 'validation',
                    message: 'Value must be an array'
                });
            }

            // Required properties
            if (schema.required && Array.isArray(schema.required)) {
                for (const prop of schema.required) {
                    if (!(prop in json)) {
                        errors.push({
                            type: 'validation',
                            message: `Missing required property: ${prop}`
                        });
                    }
                }
            }

            // Property validations
            if (schema.properties) {
                for (const [prop, propSchema] of Object.entries(schema.properties)) {
                    if (prop in json) {
                        // Recursive validation for nested objects
                        if (propSchema.type === 'object') {
                            errors.push(...this.validateSchema(json[prop], propSchema));
                        }
                        // Array validation
                        else if (propSchema.type === 'array') {
                            if (Array.isArray(json[prop])) {
                                if (propSchema.items) {
                                    json[prop].forEach((item, index) => {
                                        errors.push(...this.validateSchema(item, propSchema.items)
                                            .map(error => ({
                                                ...error,
                                                message: `${prop}[${index}]: ${error.message}`
                                            })));
                                    });
                                }
                            }
                        }
                    }
                }
            }
        } catch (error) {
            errors.push({
                type: 'validation',
                message: `Schema validation error: ${error.message}`
            });
        }

        return errors;
    }

    setupEventListeners() {
        // Add editor-specific event listeners
        if (this.options.mode === 'code') {
            this.setupCodeModeListeners();
        } else if (this.options.mode === 'tree') {
            this.setupTreeModeListeners();
        }
    }

    setupCodeModeListeners() {
        const editor = this.editor;

        // Add auto-formatting on blur
        editor.aceEditor.container.addEventListener('blur', () => {
            try {
                const value = editor.get();
                editor.set(value);
            } catch (e) {
                // Ignore formatting errors on invalid JSON
            }
        });

        // Add custom keyboard shortcuts
        editor.aceEditor.commands.addCommand({
            name: 'formatJson',
            bindKey: {win: 'Ctrl-Shift-F', mac: 'Command-Shift-F'},
            exec: () => {
                try {
                    const value = editor.get();
                    editor.set(value);
                } catch (e) {
                    // Ignore formatting errors on invalid JSON
                }
            }
        });
    }

    setupTreeModeListeners() {
        // Tree mode specific event listeners
        this.container.addEventListener('click', (event) => {
            const target = event.target;

            // Handle expand/collapse all
            if (target.matches('.jsoneditor-expand-all')) {
                this.editor.expandAll();
            } else if (target.matches('.jsoneditor-collapse-all')) {
                this.editor.collapseAll();
            }
        });
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'jsoneditor-validation-errors';
        errorDiv.textContent = message;

        // Remove existing error messages
        const existingErrors = this.container.querySelectorAll('.jsoneditor-validation-errors');
        existingErrors.forEach(error => error.remove());

        // Add new error message
        this.container.appendChild(errorDiv);

        // Remove error after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    destroy() {
        if (this.editor) {
            this.editor.destroy();
        }
    }
}

// Make editor available globally
window.JsonEditor = JsonEditor;

// Initialize editors when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all JSON editors on the page
    document.querySelectorAll('[data-json-editor]').forEach(container => {
        const options = {
            mode: container.dataset.jsonEditorMode || 'code',
            schema: container.dataset.jsonEditorSchema ?
                JSON.parse(container.dataset.jsonEditorSchema) : undefined,
            initialValue: container.dataset.jsonEditorValue ?
                JSON.parse(container.dataset.jsonEditorValue) : undefined
        };

        new JsonEditor(container, options);
    });
});