// static/js/rules/sku-selector.js

class SkuSelector {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            customerServiceId: null,
            operator: null,
            onUpdate: null,
            ...options
        };

        this.skus = [];
        this.selectedSkus = new Set();
        this.searchTerm = '';

        this.init();
    }

    async init() {
        this.initializeElements();
        await this.loadSkus();
        this.setupEventListeners();
        this.updateOperatorHelp();
        this.render();
    }

    initializeElements() {
        this.searchInput = this.container.querySelector('#skuSearch');
        this.clearButton = this.container.querySelector('#clearSkuSearch');
        this.skuList = this.container.querySelector('#skuList');
        this.selectedTagsContainer = this.container.querySelector('#selectedSkuTags');
        this.selectedCount = this.container.querySelector('#selectedCount');
        this.hiddenInput = this.container.querySelector('#selectedSkusInput');
    }

    async loadSkus() {
        try {
            const response = await fetch(`/rules/api/customer-skus/${this.options.customerServiceId}/`);
            if (!response.ok) throw new Error('Failed to load SKUs');
            const data = await response.json();
            this.skus = data.skus;
        } catch (error) {
            console.error('Error loading SKUs:', error);
            this.showError('Failed to load SKUs');
        }
    }

    setupEventListeners() {
        // Search functionality
        this.searchInput.addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.filterSkus();
        });

        this.clearButton.addEventListener('click', () => {
            this.searchInput.value = '';
            this.searchTerm = '';
            this.filterSkus();
            this.searchInput.focus();
        });

        // SKU selection
        this.skuList.addEventListener('click', (e) => {
            const skuItem = e.target.closest('.sku-item');
            if (skuItem) {
                this.toggleSku(skuItem.dataset.sku);
            }
        });

        // Remove selected SKUs
        this.selectedTagsContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-sku')) {
                this.toggleSku(e.target.dataset.sku);
            }
        });
    }

    toggleSku(sku) {
        if (this.selectedSkus.has(sku)) {
            this.selectedSkus.delete(sku);
        } else {
            this.selectedSkus.add(sku);
        }

        this.updateSelection();

        if (this.options.onUpdate) {
            this.options.onUpdate(Array.from(this.selectedSkus));
        }
    }

    updateSelection() {
        // Update hidden input
        this.hiddenInput.value = Array.from(this.selectedSkus).join(';');

        // Update selected count
        this.selectedCount.textContent = this.selectedSkus.size;

        // Update SKU items
        this.container.querySelectorAll('.sku-item').forEach(item => {
            item.classList.toggle('selected', this.selectedSkus.has(item.dataset.sku));
        });

        // Update selected tags
        this.renderSelectedTags();

        // Update operator help
        this.updateOperatorHelp();
    }

    filterSkus() {
        const searchTerm = this.searchTerm.toLowerCase();
        this.container.querySelectorAll('.sku-item').forEach(item => {
            const sku = item.dataset.sku.toLowerCase();
            const description = item.dataset.description?.toLowerCase() || '';
            const matches = sku.includes(searchTerm) || description.includes(searchTerm);
            item.classList.toggle('d-none', !matches);
        });
    }

    render() {
        // Render SKU list
        this.skuList.innerHTML = this.skus.map(sku => `
            <div class="sku-item ${this.selectedSkus.has(sku.sku) ? 'selected' : ''}"
                 data-sku="${sku.sku}"
                 data-description="${sku.description || ''}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="fw-bold">${sku.sku}</div>
                        ${sku.description ? `<small class="text-muted">${sku.description}</small>` : ''}
                    </div>
                    <div class="form-check">
                        <input type="checkbox" class="form-check-input" 
                               ${this.selectedSkus.has(sku.sku) ? 'checked' : ''}>
                    </div>
                </div>
            </div>
        `).join('');

        this.renderSelectedTags();
    }

    renderSelectedTags() {
        this.selectedTagsContainer.innerHTML = Array.from(this.selectedSkus).map(sku => `
            <span class="badge bg-primary">
                ${sku}
                <button type="button" class="btn-close btn-close-white ms-2 remove-sku"
                        data-sku="${sku}" aria-label="Remove"></button>
            </span>
        `).join('');
    }

    updateOperatorHelp() {
        const helpTitle = this.container.querySelector('#operatorHelp');
        const helpDescription = this.container.querySelector('#operatorDescription');

        const operator = this.options.operator;
        if (operator === 'only_contains') {
            helpTitle.textContent = 'Only Contains';
            helpDescription.textContent = 'Order must ONLY contain SKUs from your selection. Any other SKUs will make this rule false.';
        } else if (operator === 'contains') {
            helpTitle.textContent = 'Contains';
            helpDescription.textContent = 'Order must contain AT LEAST ONE of the selected SKUs.';
        } else if (operator === 'ncontains') {
            helpTitle.textContent = 'Does Not Contain';
            helpDescription.textContent = 'Order must NOT contain ANY of the selected SKUs.';
        }
    }

    showError(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        this.container.insertBefore(alert, this.container.firstChild);
    }
}