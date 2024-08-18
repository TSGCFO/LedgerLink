I have begun developing an application for my business that focuses on creating billing and invoicing systems for our customers. I am using PostgreSQL for 
the database schema and have set up several tables to handle our fulfillment business. Currently, we are managing billing using Excel workbooks for each 
order. However, with the high volume of orders we handle on a daily basis (around 400 to 500), it has become challenging to manage different rates for 
different customers. Each customer has a unique rate card based on their requirements, and we deal with numerous SKUs.

The database schema is in place using PostgreSQL, but it is not fully complete. I am now beginning to write code to calculate billing costs for our 
customers. While I have managed to do this for one customer, the challenge lies in organizing the code, which currently exists in multiple files and 
scattered chunks.

For the back-end of my project, I am using Python(Django) and PostgreSQL. I have not started working on the front-end yet. My schema consists of several tables:

1. **Customers table**, where I store customer information along with their unique IDs.
2. **Products table**, which contains my client's SKUs, their descriptions, and details about master cases and units.
3. **Services table**, which includes various services.
4. **Customer services table**, where I assign services from the services table to specific customers and set the pricing.
5. **Orders table**, where I manually feed the orders from my customers' shopping carts while I am still in the testing phase.

## Progress So Far
I have been able to achieve certain milestones in the project:
- **Database and Models Setup** completed in 1 week
- **Views and Forms Implementation** completed in 2 weeks




here is my project directory so far
    
```markdown
LedgerLink/
├── LedgerLink/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── billing/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│       └── billing/
│           ├── charge_detail.html
│           ├── invoice_detail.html
│           ├── invoice_form.html
│           ├── invoice_list.html
│           ├── uninvoiced_charge_list.html
├── customers/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│       └── customers/
│           ├── customer_confirm_delete.html
│           ├── customer_detail.html
│           ├── customer_form.html
│           ├── customer_list.html
├── customer_services/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│       └── customer_services/
│           ├── customer_service_confirm_delete.html
│           ├── customer_service_detail.html
│           ├── customer_service_form.html
│           ├── customer_service_list.html
├── inserts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│       └── inserts/
│           ├── insert_confirm_delete.html
│           ├── insert_detail.html
│           ├── insert_form.html
│           ├── insert_list.html
├── manage.py
├── materials/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│       └── materials/
│           ├── boxprice_confirm_delete.html
│           ├── boxprice_detail.html
│           ├── boxprice_form.html
│           ├── boxprice_list.html
│           ├── material_confirm_delete.html
│           ├── material_detail.html
│           ├── material_form.html
│           ├── material_list.html
├── orders/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│       └── orders/
│           ├── order_confirm_delete.html
│           ├── order_detail.html
│           ├── order_form.html
│           ├── order_list.html
├── products/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│       └── products/
│           ├── product_detail.html
│           ├── product_form.html
│           ├── product_list.html
│           ├── product_upload.html
├── rules/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│       └── rules/
│           ├── create_rule.html
│           ├── create_rule_group.html
│           ├── rule_group_detail.html
│           ├── rule_group_list.html
├── services/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│       └── services/
│           ├── service_confirm_delete.html
│           ├── service_detail.html
│           ├── service_form.html
│           ├── service_list.html
├── shipping/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│       └── shipping/
│           ├── cadshipping_confirm_delete.html
│           ├── cadshipping_detail.html
│           ├── cadshipping_form.html
│           ├── cadshipping_list.html
│           ├── usshipping_confirm_delete.html
│           ├── usshipping_detail.html
│           ├── usshipping_form.html
│           ├── usshipping_list.html
```











# SPEC-001: Billing and Invoicing System

## Table of Contents
1. [Background](#background)
2. [Requirements](#requirements)
   1. [Must Have](#must-have)
   2. [Should Have](#should-have)
   3. [Could Have](#could-have)

## Background
The business handles a high volume of orders daily, each requiring billing and invoicing with unique rate cards for different customers. Currently, this process is managed manually using Excel, which is inefficient and prone to errors. The aim is to develop an automated billing and invoicing system using PostgreSQL for the database and Django for the backend.

## Requirements
The billing and invoicing system should meet the following requirements:

### Must Have

* Ability to store customer information, including unique IDs.
* Capability to store product information, including SKUs, descriptions, and details about master cases and units.
* Functionality to store and manage various services offered.
* Ability to assign services to specific customers and set pricing.
* Functionality to manually feed and manage orders during the testing phase.
* Automated calculation of billing costs for customers based on their unique rate cards.
* Scalable backend using Django and PostgreSQL.
* Maintainable codebase with clear organization and documentation.
* Analytics and reporting capabilities for billing and order management.
* Integration with other business systems (e.g., CRM, ERP) for seamless data flow.

### Should Have

* User-friendly front-end interface for managing customers, products, services, and orders.
* Capability to handle a high volume of orders (400-500 daily) efficiently.
* Ability to generate and send invoices automatically.
* Robust error handling and validation to prevent data inconsistencies.

### Could Have

* Advanced AI-based analytics (for future versions).
* Mobile application interface (for future versions).



```-- auto-generated definition
create table billing_customer
(
    customer_id         integer generated by default as identity
        primary key,
    company_name        varchar(100)             not null,
    legal_business_name varchar(100)             not null,
    email               varchar(254)
        unique
        constraint billing_customer_email_ce101ff3_uniq
            unique,
    phone               varchar(20),
    address             varchar(200),
    city                varchar(50),
    state               varchar(50),
    zip                 varchar(20),
    country             varchar(50),
    business_type       varchar(50),
    created_at          timestamp with time zone not null,
    updated_at          timestamp with time zone not null
);

alter table billing_customer
    owner to postgres;

create index billing_customer_email_ce101ff3_like
    on billing_customer (email varchar_pattern_ops);

create index billing_customer_email_idx
    on billing_customer (email);
```

```-- auto-generated definition
create table billing_insert
(
    insert_id       integer generated by default as identity
        primary key,
    sku             varchar(100)                                       not null,
    insert_name     varchar(100)                                       not null,
    insert_quantity integer                                            not null
        constraint insert_qty_check
            check (insert_quantity >= 0),
    created_at      timestamp with time zone default CURRENT_TIMESTAMP not null,
    updated_at      timestamp with time zone default CURRENT_TIMESTAMP not null,
    customer_id     integer                                            not null
        constraint billing_insert_customer_id_657ae49d_fk_billing_c
            references billing_customer
            deferrable initially deferred
);

alter table billing_insert
    owner to postgres;

create index billing_insert_customer_id_657ae49d
    on billing_insert (customer_id);

create index ins_sku_cust_idx
    on billing_insert (sku, customer_id);

create index ins_cust_id_idx
    on billing_insert (customer_id);
```


```-- auto-generated definition
create table billing_material
(
    material_id integer generated by default as identity
        primary key,
    name        varchar(100)   not null
        unique,
    description text,
    unit_price  numeric(10, 2) not null
);

alter table billing_material
    owner to postgres;

create index billing_material_name_59d8212e_like
    on billing_material (name varchar_pattern_ops);
```

```-- auto-generated definition
create table billing_service
(
    service_id   integer generated by default as identity
        primary key,
    service_name varchar(100)             not null
        unique,
    description  text,
    created_at   timestamp with time zone not null,
    updated_at   timestamp with time zone not null
);

alter table billing_service
    owner to postgres;

create index billing_service_service_name_71f96ed4_like
    on billing_service (service_name varchar_pattern_ops);

create index billing_svc_name_idx
    on billing_service (service_name);

-- auto-generated definition
create table billing_product
(
    id                  bigint generated by default as identity
        primary key,
    sku                 varchar(100)             not null,
    labeling_unit_1     varchar(50),
    labeling_quantity_1 integer
        constraint billing_product_labeling_quantity_1_check
            check (labeling_quantity_1 >= 0),
    labeling_unit_2     varchar(50),
    labeling_quantity_2 integer
        constraint billing_product_labeling_quantity_2_check
            check (labeling_quantity_2 >= 0),
    labeling_unit_3     varchar(50),
    labeling_quantity_3 integer
        constraint billing_product_labeling_quantity_3_check
            check (labeling_quantity_3 >= 0),
    labeling_unit_4     varchar(50),
    labeling_quantity_4 integer
        constraint billing_product_labeling_quantity_4_check
            check (labeling_quantity_4 >= 0),
    labeling_unit_5     varchar(50),
    labeling_quantity_5 integer
        constraint billing_product_labeling_quantity_5_check
            check (labeling_quantity_5 >= 0),
    created_at          timestamp with time zone not null,
    updated_at          timestamp with time zone not null,
    customer_id         integer                  not null
        constraint billing_product_customer_id_0393b97a_fk_billing_c
            references billing_customer
            deferrable initially deferred,
    constraint billing_product_sku_customer_id_uniq
        unique (sku, customer_id)
);

alter table billing_product
    owner to postgres;

create index billing_product_customer_id_0393b97a
    on billing_product (customer_id);

create index product_cust_id_idx
    on billing_product (customer_id);

-- auto-generated definition
create table billing_order
(
    transaction_id   integer      not null
        primary key,
    customer_id      integer      not null,
    customer         varchar(100) not null,
    close_date       timestamp with time zone,
    reference_number varchar(100) not null,
    ship_to_name     varchar(100),
    ship_to_company  varchar(100),
    ship_to_address  varchar(200),
    ship_to_address2 varchar(200),
    ship_to_city     varchar(100),
    ship_to_state    varchar(50),
    ship_to_zip      varchar(20),
    ship_to_country  varchar(50),
    weight_lb        numeric,
    line_items       integer,
    sku_quantity     jsonb,
    total_item_qty   integer,
    volume_cuft      numeric,
    packages         integer,
    notes            text,
    carrier          varchar(50)
);

comment on column billing_order.carrier is 'company used to ship packages';

alter table billing_order
    owner to postgres;

create index billing_order_customer_id_idx
    on billing_order (customer_id);

-- auto-generated definition
create table "CAD_shipping"
(
    transaction_id           integer not null
        constraint shipping_details_pkey
            primary key
        constraint cad_shipping_billing_order_transaction_id_fk
            references billing_order,
    customer_id              integer not null
        constraint cad_shipping_billing_customer_customer_id_fk
            references billing_customer,
    customer                 varchar(255),
    service_code_description varchar(255),
    "ship to name"           varchar(255),
    ship_to_address_1        varchar(255),
    ship_to_address_2        varchar(255),
    shiptoaddress3           varchar(255),
    ship_to_city             varchar(255),
    ship_to_state            varchar(255),
    ship_to_country          varchar(255),
    ship_to_postal_code      varchar(20),
    tracking_number          varchar(50),
    pre_tax_shipping_charge  numeric(10, 2),
    tax1type                 varchar(50),
    tax1amount               numeric(10, 2),
    tax2type                 varchar(50),
    tax2amount               numeric(10, 2),
    tax3type                 varchar(50),
    tax3amount               numeric(10, 2),
    fuel_surcharge           numeric(10, 2),
    reference                varchar(255),
    weight                   numeric(10, 2),
    gross_weight             numeric(10, 2),
    box_length               numeric(10, 2),
    box_width                numeric(10, 2),
    box_height               numeric(10, 2),
    box_name                 varchar(255),
    ship_date                timestamp with time zone,
    carrier                  varchar(50),
    raw_ship_date            text
);

alter table "CAD_shipping"
    owner to postgres;

create index customer_id
    on "CAD_shipping" (customer_id);

-- auto-generated definition
create table billing_customerservice
(
    customer_service_id integer generated by default as identity
        primary key,
    unit_price          numeric(10, 2)           not null,
    created_at          timestamp with time zone not null,
    updated_at          timestamp with time zone not null,
    customer_id         integer                  not null
        constraint billing_customerserv_customer_id_dbbd91d3_fk_billing_c
            references billing_customer
            deferrable initially deferred,
    service_id          integer                  not null
        constraint billing_customerserv_service_id_7bf2f410_fk_billing_s
            references billing_service
            deferrable initially deferred,
    constraint customer_service_cust_serv_key
        unique (customer_id, service_id)
);

alter table billing_customerservice
    owner to postgres;

create index cust_serv_cust_id_idx
    on billing_customerservice (customer_id);

create index cust_serv_serv_id_idx
    on billing_customerservice (service_id);

create index billing_customerservice_customer_id_dbbd91d3
    on billing_customerservice (customer_id);

create index billing_customerservice_service_id_7bf2f410
    on billing_customerservice (service_id);

-- auto-generated definition
create table "US_shipping"
(
    transaction_id        integer not null
        constraint us_shipping_pkey
            primary key,
    customer_id           integer
        constraint us_shipping_billing_customer_customer_id_fk
            references billing_customer
            on update cascade on delete cascade,
    customer              varchar(255),
    ship_date             date,
    ship_to_name          varchar(255),
    ship_to_address_1     varchar(255),
    ship_to_address_2     varchar(255),
    ship_to_city          varchar(255),
    ship_to_state         varchar(255),
    ship_to_zip           varchar(20),
    ship_to_country_code  varchar(10),
    tracking_number       varchar(50),
    service_name          varchar(255),
    weight_lbs            numeric(10, 2),
    length_in             numeric(10, 2),
    width_in              numeric(10, 2),
    height_in             numeric(10, 2),
    base_chg              numeric(10, 2),
    carrier_peak_charge   numeric(10, 2),
    wizmo_peak_charge     numeric(10, 2),
    accessorial_charges   numeric(10, 2),
    rate                  numeric(10, 2),
    hst                   numeric(10, 2),
    gst                   numeric(10, 2),
    current_status        varchar(255),
    delivery_status       varchar(255),
    first_attempt_date    date,
    delivery_date         date,
    days_to_first_deliver integer
);

alter table "US_shipping"
    owner to postgres;

create index "US_shipping by customer_id"
    on "US_shipping" (customer_id, customer);

```

```-- auto-generated definition
create table billing_boxprice
(
    id         bigint generated by default as identity
        primary key,
    "Box_type" varchar(50)    not null,
    price      numeric(10, 2) not null
        constraint price_gte_0
            check (price >= (0)::numeric),
    length     numeric(5, 2)
        constraint length_gt_0_bbp
            check (length > (0)::numeric),
    width      numeric(5, 2)
        constraint width_gt_0_bbp
            check (width > (0)::numeric),
    height     numeric(5, 2)
        constraint height_gt_0_bbp
            check (height > (0)::numeric)
);

alter table billing_boxprice
    owner to postgres;

create index billing_boxprice_length_62d69d_idx
    on billing_boxprice (length, width, height);
```


Write this code in natural language

# billing/services.py

from .models import BillingRule
from decimal import Decimal

MATCHA_TEA_SKUS = ['ABO-311', 'ABO-312', 'ABO-321-03', 'ABO-322', 'ABO-323', 'ABO-324', 'ABO-325', 'ABO-331', 'ABO-341', 'ABO-351']
COSTCO_SKUS = ['ABO-171', 'ABO-072']
EXCLUDED_FLATBOX_SKUS = COSTCO_SKUS + ['ABO-111', 'ABO-112', 'ABO-117', 'ABO-121', 'ABO-127', 'ABO-131', 'ABO-137']

# Function to calculate billing based on customer's billing rules
def calculate_billing(order):
    total_cost = Decimal('0.0')
    
    # Get all billing rules for the customer
    billing_rules = BillingRule.objects.filter(customer=order.customer)
    for rule in billing_rules:
        # Apply different rules based on the rule type
        if rule.rule_type == 'service':
            total_cost += apply_service_rule(order, rule.rule_details, rule.filters)
        elif rule.rule_type == 'shipping':
            total_cost += apply_shipping_rule(order, rule.rule_details, rule.filters)
        elif rule.rule_type == 'material':
            total_cost += apply_material_rule(order, rule.rule_details, rule.filters)
    
    return total_cost

# Function to apply service rule to the order
def apply_service_rule(order, rule_details, filters):
    # If the order does not meet the filters, return 0 cost
    if not apply_filters(order, filters):
        return Decimal('0.0')

    service_cost = Decimal('0.0')
    # Get the rate from the rule details, default to 2.50 if not specified
    rate = Decimal(rule_details.get('rate', '2.50'))
    for item in order.items.all():
        # If the item is not a MATCHA_TEA_SKU, add the cost to the total
        if item.sku not in MATCHA_TEA_SKUS:
            service_cost += item.quantity * rate
    return service_cost

# Function to apply shipping rule to the order
def apply_shipping_rule(order, rule_details, filters):
    # If the order does not meet the filters, return 0 cost
    if not apply_filters(order, filters):
        return Decimal('0.0')

    # Get the flat rate from the rule details, default to 10.0 if not specified
    return Decimal(rule_details.get('flat_rate', '10.0'))

# Function to apply material rule to the order
def apply_material_rule(order, rule_details, filters):
    # If the order does not meet the filters, return 0 cost
    if not apply_filters(order, filters):
        return Decimal('0.0')

    materials_cost = Decimal('0.0')
    # Get the rate from the rule details, default to 1.0 if not specified
    rate = Decimal(rule_details.get('rate', '1.0'))
    for item in order.items.all():
        # Add the cost of materials to the total based on the quantity and rate
        materials_cost += item.quantity * rate
    return materials_cost

# Function to apply filters to the order
def apply_filters(order, filters):
    for filter in filters:
        column = filter['column']
        condition = filter['condition']
        value = filter['value']
        # Check if the order meets the specified filter conditions
        if column == 'notes':
            if condition == 'contains' and value not in order.notes:
                return False
            if condition == 'does_not_contain' and value in order.notes:
                return False
            if condition == 'starts_with' and not order.notes.startswith(value):
                return False
        # Add other column filters as needed
    return True



alter table public.billing_servicerule
    add primary key (id);

