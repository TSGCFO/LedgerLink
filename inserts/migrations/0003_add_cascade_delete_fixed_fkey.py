# Generated manually for CASCADE delete behavior

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inserts', '0002_add_cascade_delete'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL: Drop existing FK and create new one with CASCADE
            sql="""
            ALTER TABLE inserts_insert 
                DROP CONSTRAINT inserts_insert_customer_id_04e319d0_fk_customers_customer_id,
                ADD CONSTRAINT inserts_insert_customer_id_04e319d0_fk_customers_customer_id 
                    FOREIGN KEY (customer_id) 
                    REFERENCES customers_customer(id) 
                    ON DELETE CASCADE 
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            # Reverse SQL: Restore original FK without CASCADE
            reverse_sql="""
            ALTER TABLE inserts_insert 
                DROP CONSTRAINT inserts_insert_customer_id_04e319d0_fk_customers_customer_id,
                ADD CONSTRAINT inserts_insert_customer_id_04e319d0_fk_customers_customer_id 
                    FOREIGN KEY (customer_id) 
                    REFERENCES customers_customer(id) 
                    DEFERRABLE INITIALLY DEFERRED;
            """
        ),
    ]