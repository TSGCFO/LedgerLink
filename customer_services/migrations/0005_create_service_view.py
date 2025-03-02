from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('customer_services', '0004_add_cascade_delete'),
    ]

    operations = [
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
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS customer_services_customerserviceview;"
        ),
        migrations.RunSQL(
            sql="CREATE UNIQUE INDEX ON customer_services_customerserviceview (id);",
            reverse_sql="DROP INDEX IF EXISTS customer_services_customerserviceview_id_idx;"
        ),
    ] 