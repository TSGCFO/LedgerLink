export const AppState = {
    state: {
        theme: localStorage.getItem('theme') || 'auto', // 'light', 'dark', or 'auto'
        prefersDark: window.matchMedia('(prefers-color-scheme: dark)').matches, // System preference
        sidebarOpen: window.innerWidth >= 1024, // Sidebar visibility depends on screen width
        activeModals: [], // Tracks open modals
        loading: false, // Tracks if the application is in a loading state
        filters: {}, // Stores filters for tables or data views
    },
    listeners: [], // Stores functions that need to be called on state changes

    // Updates the state and notifies all listeners
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.notify();
        this.persist();
    },

    // Returns a copy of the current state
    getState() {
        return { ...this.state };
    },

    // Subscribes a new listener function to state changes
    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter((l) => l !== listener);
        };
    },

    // Notifies all listeners about a state update
    notify() {
        this.listeners.forEach((listener) => listener(this.state));
    },

    // Persists certain state values in localStorage
    persist() {
        localStorage.setItem('theme', this.state.theme);
    },

    // Sets the theme and updates the DOM
    setTheme(mode) {
        if (!['light', 'dark', 'auto'].includes(mode)) {
            console.error(`Invalid theme mode: ${mode}. Resetting to auto.`);
            mode = 'auto';
        }
        this.setState({ theme: mode });
        document.documentElement.dataset.theme = mode; // Update DOM
    },

    // Cycles through themes (auto -> light -> dark or auto -> dark -> light)
    cycleTheme() {
        const { theme, prefersDark } = this.state;

        if (prefersDark) {
            if (theme === 'auto') {
                this.setTheme('light');
            } else if (theme === 'light') {
                this.setTheme('dark');
            } else {
                this.setTheme('auto');
            }
        } else {
            if (theme === 'auto') {
                this.setTheme('dark');
            } else if (theme === 'dark') {
                this.setTheme('light');
            } else {
                this.setTheme('auto');
            }
        }
    },

    // Initializes the theme on page load
    initTheme() {
        const theme = localStorage.getItem('theme') || 'auto';
        this.setTheme(theme);

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            this.setState({ prefersDark: e.matches });
            if (this.state.theme === 'auto') {
                this.setTheme('auto'); // Update DOM based on new system preference
            }
        });
    },
};

// Add event listeners for theme toggle buttons
document.addEventListener('DOMContentLoaded', () => {
    const themeButtons = document.querySelectorAll('.theme-toggle');
    themeButtons.forEach((btn) => {
        btn.addEventListener('click', () => AppState.cycleTheme());
    });

    // React to state changes (e.g., update the DOM or notify components)
    AppState.subscribe((state) => {
        console.log('Theme updated:', state.theme);
        // Additional logic when the theme changes, if needed
    });

    AppState.initTheme(); // Initialize theme on page load
});
