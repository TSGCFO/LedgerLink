/* jshint esversion: 6 */

// State Management System
/**
 * Represents the application state management system.
 *
 * The `AppState` includes methods and properties to manage, persist, and notify changes in the
 * state of the application. It provides functionality such as maintaining the current
 * application state, notifying subscribers when the state changes, and persisting certain state
 * values to the browser's `localStorage`.
 *
 * Main features:
 * - Maintain and manage the application state using `state`.
 * - Allow external modules to subscribe to state changes via listeners.
 * - Automatically persist specific state values to `localStorage`.
 * - Provide methods to get and update the state.
 * - Support initialization and theme management for light/dark mode.
 *
 * Components:
 * - `state`: The application's core state object containing various stateful properties.
 * - `listeners`: An array of subscribed callback functions to notify when the state changes.
 * - `setState`: Updates the current state by merging new values and notifies subscribers.
 * - `getState`: Retrieves a shallow copy of the current state.
 * - `subscribe`: Allows external modules to subscribe to state changes and receive notifications.
 * - `notify`: Internal function to trigger all registered callbacks for state updates.
 * - `persist`: Persists the `darkMode` state to `localStorage` for retention across sessions.
 * - `initTheme`: Placeholder method to initialize the application theme.
 * - `setTheme`: Placeholder method to set the theme to light or dark.
 */
const AppState = {
    state: {
        darkMode: localStorage.getItem('darkMode') === 'true',
        sidebarOpen: window.innerWidth >= 1024,
        activeModals: [],
        loading: false,
        filters: {},
    },
    listeners: [],

    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.notify();
        this.persist();
    },

    getState() {
        return { ...this.state };
    },

    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    },

    notify() {
        this.listeners.forEach(listener => listener(this.state));
    },

    persist() {
        localStorage.setItem('darkMode', this.state.darkMode);
    },
    initTheme() {

    },
    setTheme(light) {

    }
};

// Theme Management
/**
 * ThemeManager is responsible for managing and applying the application's theme settings.
 * It allows toggling between dark and light modes based on application state.
 *
 * The ThemeManager provides methods to initialize theme settings, update the current theme,
 * and set up the theme toggle functionality.
 */
const ThemeManager = {
    init() {
        this.updateTheme(AppState.getState().darkMode);
        this.setupThemeToggle();
    },

    updateTheme(isDark) {
        document.documentElement.classList.toggle('dark', isDark);
        AppState.setState({ darkMode: isDark });
    },

    setupThemeToggle() {
        const toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.addEventListener('click', () => {
                this.updateTheme(!AppState.getState().darkMode);
            });
        }
    }
};

// Enhanced Toast Notification System
/**
 * The `Toast` object provides functionality to display toast notifications
 * in a web application. It supports multiple types of notifications (e.g.,
 * success, error, warning, info) with customizable message, type, and display
 * duration.
 *
 * Properties:
 * - `types`: Contains configuration for the supported toast types, including
 *    their associated icons and CSS classes for styling.
 *   - `success`: Configuration for success notifications, including a green
 *     icon and related styling classes.
 *   - `error`: Configuration for error notifications, including a red icon
 *     and related styling classes.
 *   - `warning`: Configuration for warning notifications, including a yellow
 *     icon and related styling classes.
 *   - `info`: Configuration for info notifications, including a blue icon and
 *     related styling classes.
 *
 * Methods:
 * - `show(message, type = 'info', duration = 5000)`: Displays a toast
 *   notification in the designated toast container.
 *   - `message`: The text content of the toast.
 *   - `type`: The type of toast to display (default is 'info').
 *     Must match one of the keys in the `types` property.
 *   - `duration`: The duration (in milliseconds) the toast should be displayed
 *     before it is automatically removed (default is 5000). A value of 0
 *     disables auto-removal.
 *
 * - `hideToast(toast)`: Handles the removal of a toast notification. It
 *   animates the removal process and then removes the toast element from
 *   the DOM.
 */
const Toast = {
    types: {
        success: {
            icon: `<svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                   </svg>`,
            class: 'border-green-500 bg-green-50 dark:bg-green-900/50'
        },
        error: {
            icon: `<svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                   </svg>`,
            class: 'border-red-500 bg-red-50 dark:bg-red-900/50'
        },
        warning: {
            icon: `<svg class="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                   </svg>`,
            class: 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/50'
        },
        info: {
            icon: `<svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                   </svg>`,
            class: 'border-blue-500 bg-blue-50 dark:bg-blue-900/50'
        }
    },

    show(message, type = 'info', duration = 5000) {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        const typeConfig = this.types[type];

        toast.className = `
            flex items-center w-full max-w-sm p-4 mb-4 rounded-lg shadow-lg border-l-4
            transform transition-all duration-300 ease-in-out
            ${typeConfig.class}
        `;

        toast.innerHTML = `
            <div class="flex-shrink-0">
                ${typeConfig.icon}
            </div>
            <div class="ml-3 text-sm font-normal text-gray-700 dark:text-gray-300">
                ${message}
            </div>
            <button type="button" class="ml-auto -mx-1.5 -my-1.5 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 inline-flex h-8 w-8 text-gray-500 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-600">
                <span class="sr-only">Close</span>
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>
        `;

        // Add to container
        container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('translate-x-0', 'opacity-100');
        });

        // Setup close button
        const closeButton = toast.querySelector('button');
        closeButton.addEventListener('click', () => this.hideToast(toast));

        // Auto remove
        if (duration > 0) {
            setTimeout(() => this.hideToast(toast), duration);
        }
    },

    hideToast(toast) {
        toast.classList.add('opacity-0', 'translate-x-full');
        setTimeout(() => toast.remove(), 300);
    }
};

// Enhanced Modal System
/**
 * Modal Utility for Dynamically Rendering and Managing Modals
 *
 * The `Modal` object provides a simple interface for dynamically creating, showing,
 * and controlling modal dialogs in JavaScript. It includes methods for displaying
 * modals with custom content, handling user actions with callbacks, and cleaning
 * up DOM elements after dismissal.
 *
 * ## Overview
 * The `Modal` object contains three main methods:
 * 1. `show(options)`: Displays a modal dialog based on the provided options.
 * 2. `hide(modal, onClose)`: Closes a specific modal and cleans up the DOM.
 * 3. `hideAll()`: Closes all currently open modals.
 *
 * ## Example Usage
 * ```javascript
 * Modal.show({
 *   title: 'Confirmation',
 *   content: '<p>Are you sure you want to proceed?</p>',
 *   size: 'md',
 *   onClose: () => console.log('Modal closed'),
 *   onConfirm: () => console.log('Confirmed!')
 * });
 * ```
 */
const Modal = {
    modalStack: [],

    /**
     * Dynamically creates and displays a modal dialog with customizable content, title, size, and actions.
     *
     * This method adds a modal dialog to the document's body, allowing users to specify modal content,
     * header title, modal size, and callback functions for confirmation and cancellation. It also
     * applies classes for smooth transitions and allows customization for responsive layouts.
     *
     * @param {Object} options - Configuration options for the modal.
     * @param {string} options.content - The HTML string or text to display as the modal's body content.
     * @param {string} [options.title] - The title of the modal. If not provided, the title section will be omitted.
     * @param {string} [options.size='md'] - The size of the modal. Valid values are: `sm`, `md`, `lg`, `xl`, `2xl`, or `full`.
     * @param {Function} [options.onClose] - A callback function executed when the modal is closed or canceled.
     * @param {Function} [options.onConfirm] - A callback function executed when the confirm button is clicked.
     * @return {void} This function does not return any value as it directly manipulates the DOM to display the modal.
     *
     * @example
     * // Example 1: Basic Usage with title and confirmation
     * show({
     *   content: '<p>This is a modal content</p>',
     *   title: 'Modal Title',
     *   size: 'lg',
     *   onClose: () => console.log('Modal closed'),
     *   onConfirm: () => console.log('Confirmed!')
     * });
     *
     * // Example 2: Modal without title and confirmation
     * show({
     *   content: '<p>Content without title and confirm</p>',
     * });
     *
     * @example
     * // Example 3: Modal with a different size
     * show({
     *   content: '<p>Extra large modal content</p>',
     *   size: '2xl',
     *   onClose: () => alert('Modal closed'),
     * });
     *
     * @detailedExplanation
     * 1. **Extract Properties**: The function takes an object parameter `options` and destructures it
     *    to access `content`, `title`, `size`, `onClose`, and `onConfirm`. If `size` is not provided,
     *    it defaults to `md`.
     *
     * 2. **Create Modal DOM**: A `div` element is dynamically created, and multiple classes are added
     *    for styling, animation, and accessibility attributes such as role and aria properties.
     *
     * 3. **Size Handling**: Based on the `size` provided in options, it applies appropriate inner container
     *    classes to control modal size (`sm`, `md`, `lg`, `xl`, etc.).
     *
     * 4. **Event Listeners**:
     *    - **Backdrop Click**: Clicking the backdrop triggers `onClose`.
     *    - **Cancel Button**: If `onClose` callback is defined, it is called when clicking the cancel button.
     *    - **Confirm Button**: On clicking confirm, if `onConfirm` is defined, it gets executed. On any button click
     *      (cancel/confirm), the modal is removed by invoking `this.hide()`.
     *
     * 5. **Animation & Scroll Prevention**:
     *    - Prevents background scrolling by setting `document.body.style.overflow` to hidden.
     *    - Applies animation classes using `requestAnimationFrame` for smooth modal transition effects.
     *
     * 6. **Modal Stack**: Adds the created modal to an internal `this.modalStack` array, useful for
     *    managing multiple modals or preventing interaction with previously opened ones.
     *
     * 7. **Edge Cases**:
     *    - If `size` is provided but invalid, the modal uses default `md` size classes.
     *    - If both `onClose` and `onConfirm` are not provided, the modal still works, but without specific callback behavior.
     *    - Ensure `content` is safely formatted to avoid potential cross-site scripting (XSS) issues.
     *
     * @bestPractices
     * - Always provide `onClose` to clean up resources or reset state when the modal closes.
     * - Use meaningful and safe content strings or HTML to avoid security vulnerabilities like XSS.
     * - Ensure that accessible attributes (`aria-modal`, `aria-labelledby`, etc.) are preserved for proper accessibility.
     * - Keep modal content concise to avoid overwhelming the user.
     */
    show(options) {
        const { content, title, size = 'md', onClose, onConfirm } = options;

        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 z-50 overflow-y-auto';
        modal.setAttribute('aria-labelledby', 'modal-title');
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');

        const sizeClasses = {
            sm: 'sm:max-w-sm',
            md: 'sm:max-w-md',
            lg: 'sm:max-w-lg',
            xl: 'sm:max-w-xl',
            '2xl': 'sm:max-w-2xl',
            full: 'sm:max-w-full sm:m-4'
        };

        /**
         * Updates the inner HTML of a modal element with the provided content.
         *
         * This function is utilized to dynamically set or update the content of a modal in the DOM.
         * It locates a modal by its `id` and updates its HTML content using the `innerHTML` property.
         *
         * ## Parameters
         * @param {string} modalId - The id of the modal element that needs to be updated.
         *                          Must be a valid HTML `id` string corresponding to an element in the DOM.
         * @param {string} content - The HTML content to be inserted into the modal.
         *                          Can be plain text, HTML string, or sanitized input to secure against XSS attacks.
         *
         * ## Returns
         * @returns {void} - This function does not return anything. It updates the DOM directly.
         *
         * ## Example Usage
         * ```
         * // Update the modal with a success message
         * updateModalContent('successModal', '<h1>Success!</h1><p>Your operation was completed successfully.</p>');
         *
         * // Clear the modal content
         * updateModalContent('myModal', '');
         * ```
         *
         * ## Detailed Explanation
         * 1. The function takes in two arguments: `modalId` (string) and `content` (string).
         * 2. It uses `document.getElementById` to locate the modal element in the DOM by its `id`.
         * 3. If the element exists, the `innerHTML` property of the modal is updated with the given `content`.
         * 4. If `content` contains HTML, it will be rendered as such in the modal.
         *
         * ## Notes on Best Practices
         * - **Sanitizing Input:** If user-generated content is passed to this function, it should be sanitized to prevent XSS attacks.
         * - **Element Existence:** Ensure the modal element with the given `modalId` exists in the DOM before calling the function. If not, you should handle it with a fallback or error message.
         * - **Accessibility:** When updating modal content dynamically, ensure that screen readers are updated to reflect the changes for better accessibility compliance.
         *
         * ## Edge Cases
         * - If the `modalId` does not match any element in the DOM, the function will silently fail. Consider adding a check for element existence.
         * - Passing `null` or `undefined` for `content` will cause the modal's existing content to be cleared.
         *
         * ## Full Example:
         * ```
         * // Example 1: Displaying an alert message in a modal
         * const alertMessage = '<div class="alert alert-warning">This is a warning!</div>';
         * updateModalContent('alertModal', alertMessage);
         *
         * // Example 2: Resetting a modal's content
         * updateModalContent('infoModal', '');
         *
         * // Example 3: Handling dynamic data
         * const userName = 'John Doe';
         * const message = `<h1>Hello, ${userName}!</h1><p>Welcome to our platform.</p>`;
         * updateModalContent('welcomeModal', message);
         *
         * // Error Handling (checking if modalId exists manually):
         * const modalId = 'nonExistentModal';
         * if (document.getElementById(modalId)) {
         *     updateModalContent(modalId, '<p>This will run only if the modal exists.</p>');
         * } else {
         *     console.error(`Modal with id "${modalId}" not found.`);
         * }
         * ```
         */
        modal.innerHTML = `
            <div class="flex min-h-screen items-center justify-center p-4 text-center sm:p-0">
                <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
                
                <div class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 w-full ${sizeClasses[size]}">
                    ${title ? `
                        <div class="bg-gray-50 dark:bg-gray-800 px-4 py-3 sm:px-6 border-b border-gray-200 dark:border-gray-700">
                            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-100" id="modal-title">
                                ${title}
                            </h3>
                        </div>
                    ` : ''}
                    
                    <div class="bg-white dark:bg-gray-900 px-4 py-3 sm:px-6">
                        ${content}
                    </div>

                    ${onConfirm ? `
                        <div class="bg-gray-50 dark:bg-gray-800 px-4 py-3 sm:px-6 border-t border-gray-200 dark:border-gray-700 flex flex-row-reverse gap-2">
                            <button type="button" class="confirm-btn inline-flex justify-center rounded-md border border-transparent bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
                                Confirm
                            </button>
                            <button type="button" class="cancel-btn inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
                                Cancel
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.modalStack.push(modal);

        // Setup event listeners
        /**
         * Variable: backdrop
         *
         * This variable represents a reference to a DOM element within the `modal` component. It is used to
         * select an element with the class name `bg-opacity-75` that is a child of the `modal` element.
         * The `backdrop` variable is typically used when you need to manipulate the backdrop of the modal,
         * such as showing, hiding, or modifying its style dynamically using JavaScript.
         *
         * ## Usage
         * The `querySelector` method is used here, which allows you to select the first element that matches
         * the specified CSS selector. This method is useful for querying specific elements within a complex
         * DOM structure.
         *
         * ## Example Workflow
         * 1. Access a modal in your HTML.
         * 2. Locate the element with the `bg-opacity-75` class within that modal.
         * 3. Store this specific element in the variable `backdrop` and manipulate it as needed.
         *
         * ## Example HTML Structure
         * ```html
         * <div class="modal" id="exampleModal">
         *   <div class="content">
         *     <div class="bg-opacity-75"></div>
         *   </div>
         * </div>
         * ```
         *
         * ## Example JavaScript
         * ```javascript
         * const modal = document.getElementById('exampleModal'); // Access modal element by ID
         * const backdrop = modal.querySelector('.bg-opacity-75'); // Find element with the `bg-opacity-75` class
         *
         * // Example: Change the backdrop's background color to black when the modal is visible.
         * backdrop.style.backgroundColor = 'black';
         *
         * // Example: Hide the backdrop by setting `display` to none.
         * backdrop.style.display = 'none';
         *
         * // Example: Show the backdrop by resetting display.
         * backdrop.style.display = 'block';
         * ```
         *
         * ## Explanation of Code
         * - `modal.querySelector('.bg-opacity-75')`:
         *   This queries the DOM using the `querySelector` method to locate the first child element
         *   of `modal` that matches the `.bg-opacity-75` CSS selector. The result is an element
         *   object reference that can be used to dynamically manipulate its properties or styles.
         *
         * ## Best Practices
         * - **Ensure Unique Selectors**: Ensure the class `.bg-opacity-75` is unique within the modal
         *   context to avoid unintended behavior caused by selecting the wrong element.
         * - **Check for Null Values**: The `querySelector` method returns `null` if no matching
         *   element is found. Always validate that `backdrop` is not `null` before attempting any
         *   operations to prevent runtime errors.
         *   ```javascript
         *   if (backdrop) {
         *     // Safe to manipulate the element
         *     backdrop.style.opacity = '0.5';
         *   } else {
         *     console.error('Backdrop element not found.');
         *   }
         *   ```
         * - **Separation of Concerns**: Store references to DOM elements at the top of your
         *   script or in initialization functions to reduce repeated `querySelector` calls.
         *
         * ## Edge Cases
         * - If the `modal` variable is not properly assigned (e.g., `null` or undefined), accessing `querySelector`
         *   will throw a runtime error. Verify the `modal` variable before calling `querySelector`.
         * - If multiple elements with the `.bg-opacity-75` class exist, only the first occurrence will be selected.
         *   For selecting multiple elements, consider using `querySelectorAll`.
         *
         * ## Additional Notes:
         * - The `.bg-opacity-75` class controls the transparency level of the backdrop element, as indicated in its
         *   CSS class name. Adjustments to style properties like opacity can impact the visual appearance of the modal.
         */
        const backdrop = modal.querySelector('.bg-opacity-75');
        const cancelBtn = modal.querySelector('.cancel-btn');
        const confirmBtn = modal.querySelector('.confirm-btn');

        backdrop.addEventListener('click', () => this.hide(modal, onClose));
        if (cancelBtn) cancelBtn.addEventListener('click', () => this.hide(modal, onClose));
        if (confirmBtn) confirmBtn.addEventListener('click', () => {
            if (onConfirm) onConfirm();
            this.hide(modal, onClose);
        });

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        // Animation
        requestAnimationFrame(() => {
            backdrop.classList.add('opacity-100');
            modal.querySelector('.transform').classList.add('translate-y-0', 'opacity-100', 'sm:scale-100');
        });
    },

    hide(modal, onClose) {
        const backdrop = modal.querySelector('.bg-opacity-75');
        const content = modal.querySelector('.transform');

        backdrop.classList.remove('opacity-100');
        content.classList.remove('translate-y-0', 'opacity-100', 'sm:scale-100');
        content.classList.add('opacity-0', 'translate-y-4', 'sm:translate-y-0', 'sm:scale-95');

        setTimeout(() => {
            modal.remove();
            this.modalStack.pop();
            if (this.modalStack.length === 0) {
                document.body.style.overflow = '';
            }
            if (onClose) onClose();
        }, 300);
    },

    hideAll() {
        [...this.modalStack].forEach(modal => this.hide(modal));
    }
};

// Form Handler with Advanced Validation
/**
 *
 */
class FormHandler {
    constructor(form) {
        this.form = form;
        this.init();
    }

    init() {
        this.setupValidation();
        this.setupSubmission();
        this.setupDynamicFields();
    }

    setupValidation() {
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => this.validateField(field));
        });
    }

    setupDynamicFields() {
        this.form.querySelectorAll('[data-dependent-field]').forEach(field => {
            const sourceField = this.form.querySelector(`#${field.dataset.dependentField}`);
            if (sourceField) {
                sourceField.addEventListener('change', () => this.updateDependentField(field, sourceField));
            }
        });
    }

    validateField(field) {
        const validations = {
            required: value => value.trim() !== '',
            email: value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
            minLength: (value, param) => value.length >= parseInt(param),
            maxLength: (value, param) => value.length <= parseInt(param),
            pattern: (value, param) => new RegExp(param).test(value),
            match: (value, param) => value === this.form.querySelector(`#${param}`).value
        };

        let isValid = true;
        const errorMessages = [];

        // Get validation rules from data attributes
        Object.entries(field.dataset).forEach(([key, value]) => {
            if (key.startsWith('validate')) {
                const ruleName = key.replace('validate', '').toLowerCase();
                if (validations[ruleName] && !validations[ruleName](field.value, value)) {
                    isValid = false;
                    errorMessages.push(field.dataset[`${key}Message`] || `Validation failed for ${ruleName}`);
                }
            }
        });

        this.updateFieldStatus(field, isValid, errorMessages);
        return isValid;
    }

    updateFieldStatus(field, isValid, messages = []) {
        // Remove existing status classes
        field.classList.remove(
            'border-red-500', 'border-green-500',
            'focus:border-red-500', 'focus:border-green-500',
            'focus:ring-red-500', 'focus:ring-green-500'
        );

        // Remove existing feedback element
        const existingFeedback = field.parentNode.querySelector('.feedback-message');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Add new status classes and feedback
        if (field.value) {
            const statusClasses = isValid
                ? ['border-green-500', 'focus:border-green-500', 'focus:ring-green-500']
                : ['border-red-500', 'focus:border-red-500', 'focus:ring-red-500'];

            field.classList.add(...statusClasses);

            if (!isValid && messages.length > 0) {
                const feedback = document.createElement('div');
                feedback.className = 'feedback-message text-sm text-red-500 mt-1';
                feedback.textContent = messages.join('. ');
                field.parentNode.appendChild(feedback);
            }
        }
    }

    async setupSubmission() {
        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (this.validateForm()) {
                try {
                    AppState.setState({ loading: true });
                    const formData = new FormData(this.form);
                    const response = await this.submitForm(formData);
                    this.handleResponse(response);
                } catch (error) {
                    this.handleError(error);
                } finally {
                    AppState.setState({ loading: false });
                }
            }
        });
    }

    validateForm() {
        let isValid = true;
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        return isValid;
    }

    async submitForm(formData) {
        const response = await fetch(this.form.action, {
            method: this.form.method || 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.getCsrfToken()
            }
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        return response.json();
    }

    handleResponse(response) {
        if (response.success) {
            Toast.show(response.message || 'Success!', 'success');
            if (response.redirect) {
                window.location.href = response.redirect;
            }
            if (response.reload) {
                window.location.reload();
            }
        } else {
            Toast.show(response.message || 'An error occurred', 'error');
        }
    }

    handleError(error) {
        Toast.show(error.message || 'An error occurred', 'error');
        console.error('Form submission error:', error);
    }

    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : null;
    }
}

// DataTable Enhancement
/**
 * A utility class for enhancing DataTables with custom styling, responsive support,
 * and extended export functionality using Tailwind CSS and DataTables plugin.
 */
class DataTableEnhanced {
    constructor(element, options = {}) {
        this.element = element;
        this.options = this.mergeOptions(options);
        this.init();
    }

    mergeOptions(options) {
        return {
            responsive: true,
            dom: '<"flex flex-col sm:flex-row justify-between items-center"<"flex-none mb-4 sm:mb-0"B><"flex-grow"f>>rt<"flex flex-col sm:flex-row justify-between items-center"<"flex-none mb-4 sm:mb-0"l><"flex-grow"p>>',
            buttons: [
                {
                    extend: 'collection',
                    text: 'Export',
                    buttons: [
                        { extend: 'copy', className: 'export-button' },
                        { extend: 'excel', className: 'export-button' },
                        { extend: 'pdf', className: 'export-button' },
                        { extend: 'print', className: 'export-button' }
                    ],
                    className: 'export-collection-button'
                }
            ],
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            },
            ...options
        };
    }

    init() {
        this.instance = $(this.element).DataTable(this.options);
        this.setupCustomStyles();
        this.setupResponsiveHandling();
    }

    setupCustomStyles() {
        // Add Tailwind classes to DataTable elements
        $(this.element).closest('.dataTables_wrapper').find('.dataTables_length select').addClass(
            'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'
        );

        $(this.element).closest('.dataTables_wrapper').find('.dataTables_filter input').addClass(
            'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm'
        );

        // Style export buttons
        $('.export-collection-button').addClass(
            'inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
        );

        $('.export-button').addClass(
            'block w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900'
        );
    }

    setupResponsiveHandling() {
        window.addEventListener('resize', () => {
            this.instance.columns.adjust().draw();
        });
    }

    refresh() {
        this.instance.ajax.reload();
    }

    destroy() {
        this.instance.destroy();
    }
}

// Utility Functions
/**
 * A collection of utility methods for common operations such as formatting, timing, and copying to clipboard.
 *
 * @namespace Utilities
 *
 * @property {function(number, string=): string} formatCurrency -
 * Formats a numerical amount into a currency string based on the provided currency code.
 * Defaults to 'USD' if no currency is specified.
 *
 * @property {function(Date|string|number, string=): string} formatDate -
 * Formats a date into a readable string using a specified format ('long', 'short', or 'time').
 * Defaults to 'long' format if not specified.
 *
 * @property {function(Function, number): Function} debounce -
 * Creates a debounced version of a function that delays invoking the function until
 * after a specified wait time has elapsed since the last invocation.
 *
 * @property {function(Function, number): Function} throttle -
 * Creates a throttled version of a function that ensures the function is invoked at most
 * once within the specified time limit.
 *
 * @property {function(string): void} copyToClipboard -
 * Copies the provided text to the system clipboard. Displays a success or failure toast message.
 *
 * @property {function(): string} generateUUID -
 * Generates a random UUID (Universally Unique Identifier) in the standard format.
 */
const Utilities = {
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    formatDate(date, format = 'long') {
        const options = {
            long: {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            },
            short: {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            },
            time: {
                hour: '2-digit',
                minute: '2-digit'
            }
        };
        return new Date(date).toLocaleDateString('en-US', options[format]);
    },

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func(...args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(
            () => Toast.show('Copied to clipboard!', 'success'),
            () => Toast.show('Failed to copy', 'error')
        );
    },

    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
};

// Initialize everything when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    ThemeManager.init();

    // Initialize all forms
    document.querySelectorAll('form').forEach(form => {
        new FormHandler(form);
    });

    // Initialize DataTables
    document.querySelectorAll('.datatable').forEach(table => {
        new DataTableEnhanced(table);
    });

    // Initialize Select2
    document.querySelectorAll('.select2').forEach(select => {
        $(select).select2({
            theme: 'tailwind',
            width: '100%'
        });
    });

    // Setup mobile menu
    const mobileMenuButton = document.querySelector('[data-mobile-menu-button]');
    const mobileMenu = document.querySelector('[data-mobile-menu]');
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            const isExpanded = mobileMenuButton.getAttribute('aria-expanded') === 'true';
            mobileMenuButton.setAttribute('aria-expanded', !isExpanded);
            mobileMenu.classList.toggle('hidden');
        });
    }
});

// Export functionality
export {
    AppState,
    ThemeManager,
    Toast,
    Modal,
    FormHandler,
    DataTableEnhanced,
    Utilities
};