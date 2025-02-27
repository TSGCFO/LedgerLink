from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0004_orderskuview'),
    ]

    operations = [
        migrations.RunSQL(
            # Create the materialized view
            sql="""
            CREATE MATERIALIZED VIEW orders_sku_view AS
            WITH order_skus AS (
                SELECT 
                    o.transaction_id,
                    o.customer_id,
                    o.close_date,
                    o.reference_number,
                    o.ship_to_name,
                    o.ship_to_company,
                    o.ship_to_address,
                    o.ship_to_address2,
                    o.ship_to_city,
                    o.ship_to_state,
                    o.ship_to_zip,
                    o.ship_to_country,
                    o.weight_lb,
                    o.line_items,
                    o.total_item_qty,
                    o.volume_cuft,
                    o.packages,
                    o.notes,
                    o.carrier,
                    o.status,
                    o.priority,
                    sku.key as sku_name,
                    sku.value::integer as sku_count,
                    CASE 
                        WHEN p.labeling_quantity_1 IS NOT NULL THEN 
                            FLOOR(sku.value::integer / NULLIF(p.labeling_quantity_1, 0))
                        ELSE 0 
                    END as cases,
                    CASE 
                        WHEN p.labeling_quantity_1 IS NOT NULL THEN 
                            sku.value::integer % NULLIF(p.labeling_quantity_1, 0)
                        ELSE sku.value::integer
                    END as picks,
                    p.labeling_quantity_1 as case_size,
                    p.labeling_unit_1 as case_unit
                FROM orders_order o,
                jsonb_each_text(o.sku_quantity::jsonb) sku
                LEFT JOIN products_product p ON p.sku = sku.key AND p.customer_id = o.customer_id
            )
            SELECT * FROM order_skus;
            """,
            # Drop the materialized view
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS orders_sku_view;"
        ),
        # Create index on transaction_id
        migrations.RunSQL(
            sql="CREATE UNIQUE INDEX ON orders_sku_view (transaction_id, sku_name);",
            reverse_sql="DROP INDEX IF EXISTS orders_sku_view_transaction_id_sku_name_idx;"
        ),
    ] 