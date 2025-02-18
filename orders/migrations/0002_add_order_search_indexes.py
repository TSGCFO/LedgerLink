from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
            CREATE INDEX IF NOT EXISTS idx_order_customer_id 
            ON orders_order(customer_id);
            
            CREATE INDEX IF NOT EXISTS idx_order_reference_number 
            ON orders_order(reference_number);
            
            CREATE INDEX IF NOT EXISTS idx_order_transaction_id 
            ON orders_order(transaction_id);
            
            CREATE INDEX IF NOT EXISTS idx_order_ship_to_name 
            ON orders_order(ship_to_name);
            ''',
            reverse_sql='''
            DROP INDEX IF EXISTS idx_order_customer_id;
            DROP INDEX IF EXISTS idx_order_reference_number;
            DROP INDEX IF EXISTS idx_order_transaction_id;
            DROP INDEX IF EXISTS idx_order_ship_to_name;
            '''
        ),
    ]