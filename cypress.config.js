const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5176', // Using port from CORS settings in Django
    setupNodeEvents(on, config) {
      // implement node event listeners here
      on('task', {
        log(message) {
          console.log(message);
          return null;
        },
      });
    },
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 800,
    chromeWebSecurity: false,
    defaultCommandTimeout: 10000,
    video: true,
    screenshotOnRunFailure: true,
    env: {
      apiUrl: 'http://localhost:8000/api'
    }
  },
});