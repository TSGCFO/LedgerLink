/* jshint esversion: 9 */
import $ from 'jquery';
import 'datatables.net';

export class DataTableEnhanced {
    constructor(element, options = {}) {
        this.element = element;
        this.options = this.mergeOptions(options);
        this.init();
    }

    // Merges default options with user-provided options
    mergeOptions(options) {
        return {
            responsive: true, // Enables responsive design
            dom: '<"flex flex-col sm:flex-row justify-between items-center"<"flex-none"B><"flex-grow"f>>rt<"flex flex-col sm:flex-row justify-between items-center"<"flex-none"l><"flex-grow"p>>', // Layout
            buttons: [
                { extend: 'copy', className: 'export-button' },
                { extend: 'excel', className: 'export-button' },
                { extend: 'pdf', className: 'export-button' },
                { extend: 'print', className: 'export-button' },
            ], // Export buttons
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous",
                },
            }, // Language customization
            ...options, // Overrides default options with user-provided ones
        };
    }

    // Initializes the DataTable with the specified options
    init() {
        this.instance = $(this.element).DataTable(this.options);
        this.setupCustomStyles();
        this.setupResponsiveHandling();
    }

    // Adds custom styles to DataTable elements
    setupCustomStyles() {
        // Style dropdowns
        $(this.element).closest('.dataTables_wrapper').find('.dataTables_length select').addClass(
            'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'
        );

        // Style search input
        $(this.element).closest('.dataTables_wrapper').find('.dataTables_filter input').addClass(
            'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'
        );

        // Style export buttons
        $('.export-button').addClass(
            'block w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900'
        );
    }

    // Adjusts table layout on window resize
    setupResponsiveHandling() {
        window.addEventListener('resize', () => {
            this.instance.columns.adjust().draw();
        });
    }

    // Refreshes the table data
    refresh() {
        this.instance.ajax.reload();
    }

    // Destroys the DataTable instance
    destroy() {
        this.instance.destroy();
    }
}
