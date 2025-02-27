-- SQL Script to fix discrepancies between Django models and database schema

-- 1. Create the missing many-to-many table for CustomerService and Product
CREATE TABLE IF NOT EXISTS public.customer_services_customerservice_skus (
    id SERIAL PRIMARY KEY,
    customerservice_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    CONSTRAINT customer_services_customerservice_skus_unique UNIQUE (customerservice_id, product_id),
    CONSTRAINT customer_services_customerservice_skus_customerservice_id_fkey FOREIGN KEY (customerservice_id) REFERENCES public.customer_services_customerservice(id) ON DELETE CASCADE,
    CONSTRAINT customer_services_customerservice_skus_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products_product(id) ON DELETE CASCADE
);

-- 2. Create indexes for the junction table
CREATE INDEX IF NOT EXISTS customer_services_customerservice_skus_customerservice_id_idx 
ON public.customer_services_customerservice_skus(customerservice_id);

CREATE INDEX IF NOT EXISTS customer_services_customerservice_skus_product_id_idx 
ON public.customer_services_customerservice_skus(product_id);

-- 3. Create the materialized view for customer services
CREATE MATERIALIZED VIEW IF NOT EXISTS public.customer_services_customerserviceview AS
SELECT 
    cs.id,
    cs.customer_id,
    cs.service_id,
    cs.created_at,
    cs.updated_at,
    s.service_name,
    s.description as service_description,
    s.charge_type,
    c.company_name,
    c.legal_business_name,
    c.email,
    c.phone,
    c.address,
    c.city,
    c.state,
    c.zip,
    c.country,
    c.business_type,
    c.is_active as customer_is_active
FROM customer_services_customerservice cs
JOIN services_service s ON cs.service_id = s.id
JOIN customers_customer c ON cs.customer_id = c.id;

-- 4. Create unique index on the materialized view
CREATE UNIQUE INDEX IF NOT EXISTS customer_services_customerserviceview_id_idx 
ON public.customer_services_customerserviceview(id);

-- 5. Create the regular view for backward compatibility
CREATE OR REPLACE VIEW public.customer_service_view AS
SELECT 
    cs.id,
    CONCAT(c.company_name, ' - ', s.service_name) as customer_service
FROM customer_services_customerservice cs
JOIN services_service s ON cs.service_id = s.id
JOIN customers_customer c ON cs.customer_id = c.id;

-- Note: If you encounter any errors with the IF NOT EXISTS clauses, you can remove them and run each statement individually
-- after checking if the object already exists.