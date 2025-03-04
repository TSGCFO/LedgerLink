-- PostgreSQL-specific objects for testing
-- This script creates materialized views and other PostgreSQL-specific objects required for testing

-- OrderSKUView materialized view (from orders app)
CREATE MATERIALIZED VIEW IF NOT EXISTS orders_orderskuview AS
SELECT 
    o.id AS order_id,
    o.order_number,
    o.customer_id,
    o.order_date,
    o.status,
    o.priority,
    p.id AS product_id,
    p.sku,
    p.labeling_unit_1,
    p.labeling_quantity_1,
    p.labeling_unit_2,
    p.labeling_quantity_2
FROM 
    orders_order o
JOIN 
    products_product p ON p.customer_id = o.customer_id
WITH NO DATA;

-- Conditional refresh of materialized view
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM orders_order) > 0 THEN
        EXECUTE 'REFRESH MATERIALIZED VIEW orders_orderskuview';
    END IF;
END $$;

-- CustomerServiceView materialized view (from customer_services app)
CREATE MATERIALIZED VIEW IF NOT EXISTS customer_services_customerserviceview AS
SELECT
    cs.id,
    cs.customer_id,
    c.company_name,
    s.id AS service_id,
    s.name AS service_name,
    s.description AS service_description,
    s.price,
    s.charge_type
FROM
    customer_services_customerservice cs
JOIN
    customers_customer c ON cs.customer_id = c.id
JOIN
    services_service s ON cs.service_id = s.id
WITH NO DATA;

-- Conditional refresh of materialized view
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM customer_services_customerservice) > 0 THEN
        EXECUTE 'REFRESH MATERIALIZED VIEW customer_services_customerserviceview';
    END IF;
END $$;

-- Create indexes for materialized views
CREATE INDEX IF NOT EXISTS idx_orderskuview_order_id ON orders_orderskuview(order_id);
CREATE INDEX IF NOT EXISTS idx_orderskuview_sku ON orders_orderskuview(sku);
CREATE INDEX IF NOT EXISTS idx_customerserviceview_customer_id ON customer_services_customerserviceview(customer_id);
CREATE INDEX IF NOT EXISTS idx_customerserviceview_service_id ON customer_services_customerserviceview(service_id);