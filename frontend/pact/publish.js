const pact = require('@pact-foundation/pact-node');
const path = require('path');
const fs = require('fs');

// Get and validate env vars
const pactBrokerUrl = process.env.PACT_BROKER_URL || 'http://localhost:9292';
const pactBrokerUsername = process.env.PACT_BROKER_USERNAME;
const pactBrokerPassword = process.env.PACT_BROKER_PASSWORD;
const pactBrokerToken = process.env.PACT_BROKER_TOKEN;

// Validate we have authentication details if needed
if (pactBrokerUrl !== 'http://localhost:9292' && 
    !pactBrokerToken && 
    (!pactBrokerUsername || !pactBrokerPassword)) {
  console.error('Error: Pact Broker authentication details missing!');
  console.error('Set either PACT_BROKER_TOKEN or both PACT_BROKER_USERNAME and PACT_BROKER_PASSWORD');
  process.exit(1);
}

// Get the version - using git hash or env var
const getConsumerVersion = () => {
  let version = process.env.PACT_CONSUMER_VERSION;
  if (!version) {
    try {
      // Try to use git commit hash if available
      const { execSync } = require('child_process');
      version = execSync('git rev-parse --short HEAD').toString().trim();
    } catch (error) {
      // Fallback to timestamp if git is not available
      version = `dev-${new Date().toISOString().replace(/:/g, '-')}`;
    }
  }
  return version;
};

// Get the contract file paths
const getPactFiles = () => {
  const pactDir = path.resolve(__dirname, '../../pacts');
  
  if (!fs.existsSync(pactDir)) {
    console.error(`Error: No pact files found in ${pactDir}`);
    console.error('Run consumer tests first to generate pact files');
    process.exit(1);
  }
  
  const files = fs.readdirSync(pactDir)
    .filter(file => file.endsWith('.json'))
    .map(file => path.join(pactDir, file));
  
  if (files.length === 0) {
    console.error('Error: No pact JSON files found');
    process.exit(1);
  }
  
  return files;
};

// Configure the publisher
const publisherOptions = {
  pactFilesOrDirs: getPactFiles(),
  pactBroker: pactBrokerUrl,
  consumerVersion: getConsumerVersion(),
  tags: [process.env.NODE_ENV || 'development'],
};

// Add authentication if provided
if (pactBrokerToken) {
  publisherOptions.pactBrokerToken = pactBrokerToken;
} else if (pactBrokerUsername && pactBrokerPassword) {
  publisherOptions.pactBrokerUsername = pactBrokerUsername;
  publisherOptions.pactBrokerPassword = pactBrokerPassword;
}

console.log(`Publishing pacts to broker at ${pactBrokerUrl}`);
console.log(`Consumer version: ${publisherOptions.consumerVersion}`);

// Publish the pacts
pact.publishPacts(publisherOptions)
  .then(() => {
    console.log('Pacts successfully published!');
  })
  .catch(error => {
    console.error('Error publishing pacts: ', error);
    process.exit(1);
  });