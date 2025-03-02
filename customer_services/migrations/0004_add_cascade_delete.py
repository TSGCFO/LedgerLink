# Generated manually for CASCADE delete behavior

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer_services', '0003_customerserviceview'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL: Drop existing FK and create new one with CASCADE
            sql="""
            ALTER TABLE customer_services_customerservice 
                DROP CONSTRAINT customer_services_cu_customer_id_4bd36f95_fk_customers,
                ADD CONSTRAINT customer_services_cu_customer_id_4bd36f95_fk_customers 
                    FOREIGN KEY (customer_id) 
                    REFERENCES customers_customer(id) 
                    ON DELETE CASCADE 
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            # Reverse SQL: Restore original FK without CASCADE
            reverse_sql="""
            ALTER TABLE customer_services_customerservice 
                DROP CONSTRAINT customer_services_cu_customer_id_4bd36f95_fk_customers,
                ADD CONSTRAINT customer_services_cu_customer_id_4bd36f95_fk_customers 
                    FOREIGN KEY (customer_id) 
                    REFERENCES customers_customer(id) 
                    DEFERRABLE INITIALLY DEFERRED;
            """
        ),
    ] 