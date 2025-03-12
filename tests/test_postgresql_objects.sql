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

-- Create orders_sku_view materialized view required by test methods
CREATE MATERIALIZED VIEW IF NOT EXISTS orders_sku_view AS
SELECT 
    o.transaction_id,
    (o.sku_quantity->>'name')::text AS sku_name,
    (o.sku_quantity->>'cases')::integer AS cases,
    (o.sku_quantity->>'picks')::integer AS picks,
    (o.sku_quantity->>'case_size')::integer AS case_size,
    (o.sku_quantity->>'case_unit')::text AS case_unit
FROM 
    orders_order o
WHERE 
    o.sku_quantity IS NOT NULL
WITH NO DATA;

-- Create indexes on the materialized view
CREATE UNIQUE INDEX IF NOT EXISTS orders_sku_view_transaction_id_idx ON orders_sku_view (transaction_id);
CREATE INDEX IF NOT EXISTS orders_sku_view_sku_name_idx ON orders_sku_view (sku_name);

-- Conditional refresh of the materialized view
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM orders_order) > 0 THEN
        EXECUTE 'REFRESH MATERIALIZED VIEW orders_sku_view';
    END IF;
END $$;

-- Create any missing tables required for testing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'billing_billingreportdetail'
    ) THEN
        CREATE TABLE billing_billingreportdetail (
            id SERIAL PRIMARY KEY,
            service_breakdown JSONB NOT NULL,
            total_amount DECIMAL(10, 2) NOT NULL,
            order_id INT NOT NULL,
            report_id INT NOT NULL,
            CONSTRAINT fk_order FOREIGN KEY(order_id) REFERENCES orders_order(transaction_id) ON DELETE CASCADE,
            CONSTRAINT fk_report FOREIGN KEY(report_id) REFERENCES billing_billingreport(id) ON DELETE CASCADE
        );
        
        -- Create indexes
        CREATE INDEX idx_billingreportdetail_report_order ON billing_billingreportdetail(report_id, order_id);
        CREATE INDEX idx_billingreportdetail_total_amount ON billing_billingreportdetail(total_amount);
    END IF;
END $$;

-- Add any missing columns to existing tables
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'billing_billingreport' AND column_name = 'generated_at'
    ) THEN
        ALTER TABLE billing_billingreport ADD COLUMN generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;
END $$;