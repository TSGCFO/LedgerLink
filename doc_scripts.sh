#! /usr/bin/bash

cat > docs/index.rst << 'EOF'
Welcome to LedgerLink Documentation
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   project/index
   backend/index
   frontend/index
   testing/index
   api/index
   api_reference/index

Project Overview
---------------

LedgerLink is a web application built with Django REST Framework and React with Material UI. It provides a system for managing customers, orders, products, and billing for a fulfillment or logistics business.

Recent Updates
-------------

**Testing Framework Update - March 2025**
We've implemented Docker-based and TestContainers-based testing frameworks for consistent and reliable test environments.

**Critical Bug Fix - March 2025**
We've fixed a critical bug in the rule evaluation system where the "not equals" (`ne`) operator was not being evaluated correctly. This could have affected billing calculations and business logic decisions.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
EOF
