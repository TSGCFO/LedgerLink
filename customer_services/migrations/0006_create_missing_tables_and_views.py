# Generated manually to fix missing tables and views

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer_services', '0005_create_service_view'),
    ]

    operations = [
        # Create the missing many-to-many table for CustomerService and Product
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS customer_services_customerservice_skus (
                id SERIAL PRIMARY KEY,
                customerservice_id BIGINT NOT NULL REFERENCES customer_services_customerservice(id) ON DELETE CASCADE,
                product_id BIGINT NOT NULL REFERENCES products_product(id) ON DELETE CASCADE,
                UNIQUE (customerservice_id, product_id)
            );
            
            CREATE INDEX customer_services_customerservice_skus_customerservice_id_idx 
            ON customer_services_customerservice_skus(customerservice_id);
            
            CREATE INDEX customer_services_customerservice_skus_product_id_idx 
            ON customer_services_customerservice_skus(product_id);
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS customer_services_customerservice_skus_product_id_idx;
            DROP INDEX IF EXISTS customer_services_customerservice_skus_customerservice_id_idx;
            DROP TABLE IF EXISTS customer_services_customerservice_skus;
            """
        ),
        
        # Create the materialized view for customer services
        migrations.RunSQL(
            sql="""
            CREATE MATERIALIZED VIEW customer_services_customerserviceview AS
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
            
            CREATE UNIQUE INDEX customer_services_customerserviceview_id_idx 
            ON customer_services_customerserviceview(id);
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS customer_services_customerserviceview_id_idx;
            DROP MATERIALIZED VIEW IF EXISTS customer_services_customerserviceview;
            """
        ),
        
        # Create the regular view for backward compatibility
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE VIEW customer_service_view AS
            SELECT 
                cs.id,
                CONCAT(c.company_name, ' - ', s.service_name) as customer_service
            FROM customer_services_customerservice cs
            JOIN services_service s ON cs.service_id = s.id
            JOIN customers_customer c ON cs.customer_id = c.id;
            """,
            reverse_sql="DROP VIEW IF EXISTS customer_service_view;"
        ),
    ]