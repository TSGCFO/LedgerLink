from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL: Drop existing FK and create new one with CASCADE
            sql="""
            ALTER TABLE products_product 
                DROP CONSTRAINT products_product_customer_id_c69c604c_fk_customers_customer_id,
                ADD CONSTRAINT products_product_customer_id_c69c604c_fk_customers_customer_id 
                    FOREIGN KEY (customer_id) 
                    REFERENCES customers_customer(id) 
                    ON DELETE CASCADE 
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            # Reverse SQL: Restore original FK without CASCADE
            reverse_sql="""
            ALTER TABLE products_product 
                DROP CONSTRAINT products_product_customer_id_c69c604c_fk_customers_customer_id,
                ADD CONSTRAINT products_product_customer_id_c69c604c_fk_customers_customer_id 
                    FOREIGN KEY (customer_id) 
                    REFERENCES customers_customer(id) 
                    DEFERRABLE INITIALLY DEFERRED;
            """
        ),
    ]