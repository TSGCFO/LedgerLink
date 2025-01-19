export const Utilities = {
    // Formats a number as currency
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency,
        }).format(amount);
    },

    // Formats a date into long or short formats
    formatDate(date, format = 'long') {
        const options = {
            long: { year: 'numeric', month: 'long', day: 'numeric' },
            short: { year: 'numeric', month: 'short', day: 'numeric' },
        };
        return new Date(date).toLocaleDateString('en-US', options[format]);
    },

    // Creates a debounce function to delay execution of a function until a wait period elapses
    debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    },

    // Creates a throttle function to ensure a function is executed at most once in a specified time frame
    throttle(func, limit) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => (inThrottle = false), limit);
            }
        };
    },

    // Copies text to the clipboard
    copyToClipboard(text) {
        navigator.clipboard.writeText(text)
            .then(() => console.log('Copied to clipboard!'))
            .catch(() => console.error('Failed to copy to clipboard.'));
    },

    // Generates a unique identifier (UUID v4-like)
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
            const r = (Math.random() * 16) | 0;
            const v = c === 'x' ? r : (r & 0x3) | 0x8;
            return v.toString(16);
        });
    },
};
