module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/frontend/pact/consumers/**/*.test.js'],
  transform: {
    '^.+\\.jsx?$': 'babel-jest'
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(@pact-foundation)/)'
  ],
  moduleFileExtensions: ['js', 'json', 'jsx', 'node'],
  reporters: ['default'],
  testTimeout: 30000,
  bail: true,
  verbose: true
};