# billing/tests/factories.py
# 
# This file now imports from the shared factories in the main conftest.py
# Only override factory methods if you need app-specific customization

# Import the shared factories from the main conftest.py
from conftest import (
    CustomerFactory, 
    OrderFactory, 
    UserFactory, 
    BillingReportFactory, 
    BillingReportDetailFactory,
    ServiceFactory,
    CustomerServiceFactory
)