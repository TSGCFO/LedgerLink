"""
Pact provider verification tests for the customer API.
These tests verify that the backend can fulfill the contract expected by the frontend.
"""

import os
import pytest
import logging
from django.urls import reverse
from django.test import override_settings
from pact import Verifier

from customers.models import Customer
from test_utils.factories import CustomerFactory

logger = logging.getLogger(__name__)

# Configure provider verification settings
PACT_BROKER_URL = os.environ.get('PACT_BROKER_URL', 'http://localhost:9292')
PACT_BROKER_USERNAME = os.environ.get('PACT_BROKER_USERNAME')
PACT_BROKER_PASSWORD = os.environ.get('PACT_BROKER_PASSWORD')
PACT_BROKER_TOKEN = os.environ.get('PACT_BROKER_TOKEN')
PACT_PROVIDER_VERSION = os.environ.get('PACT_PROVIDER_VERSION', '1.0.0')
PACT_PUBLISH_VERIFICATION_RESULTS = os.environ.get('PACT_PUBLISH_RESULTS', 'false').lower() == 'true'
PACT_PROVIDER_NAME = 'LedgerLinkBackend'
PACT_CONSUMER_NAME = 'LedgerLinkFrontend'

# For local pact file verification (without a broker)
PACT_FILE_PATH = os.environ.get('PACT_FILE_PATH', os.path.join(os.getcwd(), 'pacts', f'{PACT_CONSUMER_NAME}-{PACT_PROVIDER_NAME}.json'))


# Provider state setup functions
def setup_there_are_customers(variables, **kwargs):
    """Setup provider state for 'there are customers'."""
    # Create test customers
    CustomerFactory.create_batch(3)
    logger.info("Created customers for provider state 'there are customers'")


def setup_customer_with_id_exists(variables, **kwargs):
    """Setup provider state for 'customer with id {id} exists'."""
    customer_id = variables.get('id', '1')
    # Create a customer with the specified ID or default to 1
    customer = CustomerFactory(id=customer_id)
    logger.info(f"Created customer with id {customer_id} for provider state")
    return customer


def setup_can_create_a_new_customer(variables, **kwargs):
    """Setup provider state for 'can create a new customer'."""
    # No setup needed, just logging
    logger.info("Setup for provider state 'can create a new customer'")


# Map provider states to setup functions
PROVIDER_STATES = {
    'there are customers': setup_there_are_customers,
    'customer with id 1 exists': lambda variables, **kwargs: setup_customer_with_id_exists({'id': '1'}, **kwargs),
    'can create a new customer': setup_can_create_a_new_customer,
}


# State change URL endpoint for provider verification
@pytest.fixture(scope='session')
def django_db_setup():
    """Configure Django test database for provider verification."""
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ledgerlink_test',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }


@pytest.fixture
def api_client():
    """Create a Django test client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def setup_provider_state(api_client):
    """Create a function to set up provider states."""
    def _setup_provider_state(provider_state, variables=None):
        if variables is None:
            variables = {}
        
        logger.info(f"Setting up provider state: {provider_state}")
        
        # Find and run the appropriate setup function
        setup_func = None
        for state_name, func in PROVIDER_STATES.items():
            if state_name == provider_state:
                setup_func = func
                break
        
        if setup_func:
            return setup_func(variables)
        else:
            logger.warning(f"No setup function found for provider state: {provider_state}")
            return None
    
    return _setup_provider_state


@pytest.mark.django_db
def test_customer_provider_contract_from_broker(live_server, setup_provider_state, monkeypatch):
    """Verify the customer API contract from the Pact broker."""
    # Skip if explicitly specified
    if os.environ.get('SKIP_PACT_VERIFICATION', 'false').lower() == 'true':
        pytest.skip("Skipping Pact verification as requested")
    
    # Override provider state URL to use our setup_provider_state function
    def provider_state_setup(provider_state):
        logger.info(f"Setting up provider state: {provider_state}")
        setup_provider_state(provider_state)
        return True
    
    # Configure verifier
    verifier = Verifier(
        provider='LedgerLinkBackend',
        provider_base_url=live_server.url
    )
    
    # Configure authentication for Pact broker if provided
    pact_broker_opts = {
        'broker_url': PACT_BROKER_URL,
        'provider_version': PACT_PROVIDER_VERSION,
        'provider_tags': [os.environ.get('ENVIRONMENT', 'test')],
        'publish_verification_results': PACT_PUBLISH_VERIFICATION_RESULTS,
    }
    
    if PACT_BROKER_TOKEN:
        pact_broker_opts['broker_token'] = PACT_BROKER_TOKEN
    elif PACT_BROKER_USERNAME and PACT_BROKER_PASSWORD:
        pact_broker_opts['broker_username'] = PACT_BROKER_USERNAME
        pact_broker_opts['broker_password'] = PACT_BROKER_PASSWORD
    
    # Try to verify from broker first, fall back to local file
    broker_reachable = True
    try:
        # Verify contracts from the broker
        success, logs = verifier.verify_with_broker(
            **pact_broker_opts,
            provider_states_setup_url=None,  # We use our custom setup instead
            provider_states_setup_fn=provider_state_setup,
            consumer='LedgerLinkFrontend'
        )
    except Exception as e:
        broker_reachable = False
        logger.warning(f"Could not connect to Pact broker: {e}")
    
    # If broker is not reachable, fall back to local file
    if not broker_reachable:
        logger.info(f"Falling back to local Pact file: {PACT_FILE_PATH}")
        if not os.path.exists(PACT_FILE_PATH):
            pytest.skip(f"No local Pact file found at {PACT_FILE_PATH}")
        
        success, logs = verifier.verify_pacts(
            [PACT_FILE_PATH],
            provider_states_setup_url=None,
            provider_states_setup_fn=provider_state_setup
        )
    
    # Output verification logs
    logger.info(f"Pact verification logs: {logs}")
    
    # Assert verification was successful
    assert success, "Pact verification failed"


@pytest.mark.django_db
def test_customer_provider_contract_local_only(live_server, setup_provider_state, monkeypatch):
    """Verify the customer API contract from a local Pact file only."""
    # Skip if explicitly specified
    if os.environ.get('SKIP_PACT_VERIFICATION', 'false').lower() == 'true':
        pytest.skip("Skipping Pact verification as requested")
    
    # Check if local file exists
    if not os.path.exists(PACT_FILE_PATH):
        pytest.skip(f"No local Pact file found at {PACT_FILE_PATH}")
    
    # Override provider state URL to use our setup_provider_state function
    def provider_state_setup(provider_state):
        logger.info(f"Setting up provider state: {provider_state}")
        setup_provider_state(provider_state)
        return True
    
    # Configure verifier
    verifier = Verifier(
        provider='LedgerLinkBackend',
        provider_base_url=live_server.url
    )
    
    # Verify the local Pact file
    success, logs = verifier.verify_pacts(
        [PACT_FILE_PATH],
        provider_states_setup_url=None,
        provider_states_setup_fn=provider_state_setup
    )
    
    # Output verification logs
    logger.info(f"Pact verification logs: {logs}")
    
    # Assert verification was successful
    assert success, "Pact verification failed"