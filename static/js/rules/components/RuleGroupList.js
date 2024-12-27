import { ApiService } from '../utils/api.js';
import { validateRuleGroup } from '../utils/validation.js';
import { RuleGroupCard } from './RuleGroupCard.js';
import { FilterModal } from './FilterModal.js';

/**
 * RuleGroupList Component
 * @class RuleGroupList
 * @description Manages the list of rule groups, including filtering and sorting
 */
export class RuleGroupList {
    constructor() {
        this.initialize();
        this.bindEvents();
        this.loadRuleGroups();
    }

    /**
     * Initialize component properties and sub-components
     * @private
     */
    initialize() {
        // Initialize properties
        this.filterModal = new FilterModal({
            onApply: filters => this.applyFilters(filters)
        });

        // Cache DOM elements
        this.elements = {
            container: document.querySelector('.rule-groups-container'),
            searchForm: document.getElementById('searchForm'),
            filterBtn: document.getElementById('filterBtn'),
            deleteModal: document.getElementById('deleteModal'),
            pagination: document.querySelector('.pagination')
        };

        // Initialize state
        this.state = {
            filters: new URLSearchParams(window.location.search),
            selectedGroups: new Set(),
            loading: false
        };
    }

    /**
     * Bind event listeners
     * @private
     */
    bindEvents() {
        // Search form submission
        this.elements.searchForm?.addEventListener('submit', e => {
            e.preventDefault();
            this.handleSearch(new FormData(e.target));
        });

        // Filter button click
        this.elements.filterBtn?.addEventListener('click', () => {
            this.filterModal.show();
        });

        // Delete confirmation
        this.elements.deleteModal?.addEventListener('show.bs.modal', e => {
            const button = e.relatedTarget;
            const groupId = button.dataset.groupId;
            this.setupDeleteConfirmation(groupId);
        });

        // Pagination clicks
        this.elements.pagination?.addEventListener('click', e => {
            if (e.target.matches('.page-link')) {
                e.preventDefault();
                this.handlePagination(e.target.href);
            }
        });

        // Column sorting
        document.querySelectorAll('.column-header[data-sortable="true"]').forEach(header => {
            header.addEventListener('click', () => this.handleSort(header));
        });
    }

    /**
     * Load rule groups with current filters
     * @private
     * @async
     */
    async loadRuleGroups() {
        try {
            this.setLoading(true);
            const params = this.buildQueryParams();
            const data = await ApiService.get('/rule-groups/', params);
            this.updateRuleGroups(data);
        } catch (error) {
            this.handleError(error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Handle search form submission
     * @private
     * @param {FormData} formData - Form data from search form
     */
    handleSearch(formData) {
        const searchParams = new URLSearchParams();
        for (const [key, value] of formData) {
            if (value) searchParams.append(key, value);
        }
        this.updateUrl(searchParams);
        this.loadRuleGroups();
    }

    /**
     * Apply filters from filter modal
     * @private
     * @param {Object} filters - Filter configuration
     */
    applyFilters(filters) {
        const searchParams = new URLSearchParams(this.state.filters);
        Object.entries(filters).forEach(([key, value]) => {
            if (value) {
                searchParams.set(key, value);
            } else {
                searchParams.delete(key);
            }
        });
        this.updateUrl(searchParams);
        this.loadRuleGroups();
    }

    /**
     * Handle column sorting
     * @private
     * @param {HTMLElement} header - Header element clicked
     */
    handleSort(header) {
        const field = header.dataset.field;
        const currentDirection = header.dataset.direction || 'asc';
        const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';

        // Update URL params
        const searchParams = new URLSearchParams(this.state.filters);
        searchParams.set('sort', field);
        searchParams.set('direction', newDirection);

        this.updateUrl(searchParams);
        this.loadRuleGroups();
    }

    /**
     * Handle pagination click
     * @private
     * @param {string} url - Pagination URL
     */
    handlePagination(url) {
        const searchParams = new URLSearchParams(new URL(url).search);
        this.updateUrl(searchParams);
        this.loadRuleGroups();
    }

    /**
     * Set up delete confirmation modal
     * @private
     * @param {string} groupId - ID of rule group to delete
     */
    setupDeleteConfirmation(groupId) {
        const form = this.elements.deleteModal.querySelector('#deleteForm');
        form.action = `/rules/rule-groups/${groupId}/delete/`;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                await ApiService.post(`/rule-groups/${groupId}/delete/`);
                this.removeRuleGroup(groupId);
                bootstrap.Modal.getInstance(this.elements.deleteModal).hide();
            } catch (error) {
                this.handleError(error);
            }
        });
    }

    /**
     * Update URL with new search params
     * @private
     * @param {URLSearchParams} searchParams - New search parameters
     */
    updateUrl(searchParams) {
        const newUrl = `${window.location.pathname}?${searchParams.toString()}`;
        window.history.pushState({}, '', newUrl);
        this.state.filters = searchParams;
    }

    /**
     * Update rule groups display
     * @private
     * @param {Object} data - Rule groups data from API
     */
    updateRuleGroups(data) {
        if (!this.elements.container) return;

        // Clear existing content
        this.elements.container.innerHTML = '';

        // Add new rule groups
        if (data.results?.length) {
            data.results.forEach(ruleGroup => {
                const card = new RuleGroupCard(ruleGroup);
                this.elements.container.appendChild(card.element);
            });
        } else {
            this.showEmptyState();
        }

        // Update pagination if needed
        if (data.pagination) {
            this.updatePagination(data.pagination);
        }
    }

    /**
     * Show empty state when no rule groups exist
     * @private
     */
    showEmptyState() {
        const emptyState = document.createElement('div');
        emptyState.className = 'alert alert-info text-center';
        emptyState.innerHTML = `
            <h4 class="alert-heading">No Rule Groups Found</h4>
            <p>There are no rule groups matching your criteria.</p>
            <hr>
            <p class="mb-0">
                <a href="/rules/rule-groups/new/" class="alert-link">Create a new rule group</a>
            </p>
        `;
        this.elements.container.appendChild(emptyState);
    }

    /**
     * Handle API and other errors
     * @private
     * @param {Error} error - Error object
     */
    handleError(error) {
        console.error('Rule Group List Error:', error);
        const message = error.message || 'An error occurred while processing your request.';

        // Show error message to user
        const toast = new bootstrap.Toast(document.createElement('div'));
        toast.element.className = 'toast align-items-center text-white bg-danger border-0';
        toast.element.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        document.body.appendChild(toast.element);
        toast.show();
    }

    /**
     * Set loading state
     * @private
     * @param {boolean} loading - Loading state
     */
    setLoading(loading) {
        this.state.loading = loading;
        if (loading) {
            this.elements.container.classList.add('loading');
        } else {
            this.elements.container.classList.remove('loading');
        }
    }

    /**
     * Build query parameters for API request
     * @private
     * @returns {Object} Query parameters
     */
    buildQueryParams() {
        const params = {};
        for (const [key, value] of this.state.filters) {
            params[key] = value;
        }
        return params;
    }
}