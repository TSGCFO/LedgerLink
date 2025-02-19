from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0001_initial'),
    ]

    sql = '''
    DROP VIEW IF EXISTS orders_sku_view;
    DROP MATERIALIZED VIEW IF EXISTS orders_sku_view;
    
    CREATE MATERIALIZED VIEW orders_sku_view AS
    WITH normalized_skus AS (
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
            CASE 
                WHEN jsonb_typeof(o.sku_quantity) = 'array' THEN
                    sku_data.sku
                WHEN jsonb_typeof(o.sku_quantity) = 'object' THEN
                    sku_data.sku
            END as sku_name,
            CASE 
                WHEN jsonb_typeof(o.sku_quantity) = 'array' THEN
                    CAST(sku_data.quantity AS numeric)
                WHEN jsonb_typeof(o.sku_quantity) = 'object' THEN
                    CAST(sku_data.quantity AS numeric)
            END as sku_count
        FROM 
            orders_order o
        CROSS JOIN LATERAL (
            SELECT sku->>'sku' as sku, sku->>'quantity' as quantity
            FROM jsonb_array_elements(
                CASE WHEN jsonb_typeof(o.sku_quantity) = 'array' 
                THEN o.sku_quantity 
                ELSE '[]'::jsonb 
                END
            ) as sku
            UNION ALL
            SELECT k as sku, v as quantity
            FROM jsonb_each_text(
                CASE WHEN jsonb_typeof(o.sku_quantity) = 'object' 
                THEN o.sku_quantity 
                ELSE '{}'::jsonb 
                END
            ) as t(k, v)
        ) as sku_data
        WHERE o.sku_quantity IS NOT NULL
    )
    SELECT 
        n.*,
        CASE 
            WHEN p.labeling_unit_1 = 'case' AND p.labeling_quantity_1 > 0 
            THEN FLOOR(n.sku_count::numeric / p.labeling_quantity_1::numeric)
            ELSE 0 
        END as cases,
        CASE 
            WHEN p.labeling_unit_1 = 'case' AND p.labeling_quantity_1 > 0 
            THEN n.sku_count % p.labeling_quantity_1
            ELSE n.sku_count 
        END as picks,
        p.labeling_quantity_1 as case_size,
        p.labeling_unit_1 as case_unit
    FROM 
        normalized_skus n
        LEFT JOIN products_product p ON 
            p.sku = n.sku_name 
            AND p.customer_id = n.customer_id;

    -- Create unique index (required for concurrent refresh)
    CREATE UNIQUE INDEX idx_sku_view_unique ON orders_sku_view(transaction_id, sku_name);
    
    -- Create indexes for better query performance
    CREATE INDEX idx_sku_view_customer ON orders_sku_view(customer_id);
    CREATE INDEX idx_sku_view_sku ON orders_sku_view(sku_name);
    CREATE INDEX idx_sku_view_cases ON orders_sku_view(cases);
    
    -- Create indexes for the base tables if they don't exist
    CREATE INDEX IF NOT EXISTS idx_products_sku_customer ON products_product(sku, customer_id);
    CREATE INDEX IF NOT EXISTS idx_orders_sku_quantity ON orders_order USING GIN (sku_quantity);

    -- Create function to refresh materialized view
    CREATE OR REPLACE FUNCTION refresh_orders_sku_view()
    RETURNS trigger AS $$
    DECLARE
        last_refresh timestamp;
    BEGIN
        SELECT last_refresh INTO last_refresh FROM pg_stat_user_tables 
        WHERE relname = 'orders_sku_view';
        
        IF last_refresh IS NULL OR 
           (CURRENT_TIMESTAMP - last_refresh) > interval '5 minutes' THEN
            RAISE NOTICE 'Refreshing orders_sku_view materialized view';
            REFRESH MATERIALIZED VIEW CONCURRENTLY orders_sku_view;
        END IF;
        
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;

    -- Create trigger for orders table
    DROP TRIGGER IF EXISTS refresh_orders_sku_view_on_order ON orders_order;
    CREATE TRIGGER refresh_orders_sku_view_on_order
    AFTER INSERT OR UPDATE OR DELETE ON orders_order
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_orders_sku_view();

    -- Create trigger for products table
    DROP TRIGGER IF EXISTS refresh_orders_sku_view_on_product ON products_product;
    CREATE TRIGGER refresh_orders_sku_view_on_product
    AFTER INSERT OR UPDATE OR DELETE ON products_product
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_orders_sku_view();

    -- Do initial refresh
    REFRESH MATERIALIZED VIEW orders_sku_view;
    '''

    reverse_sql = '''
    DROP TRIGGER IF EXISTS refresh_orders_sku_view_on_order ON orders_order;
    DROP TRIGGER IF EXISTS refresh_orders_sku_view_on_product ON products_product;
    DROP FUNCTION IF EXISTS refresh_orders_sku_view();
    DROP MATERIALIZED VIEW IF EXISTS orders_sku_view;
    DROP INDEX IF EXISTS idx_products_sku_customer;
    DROP INDEX IF EXISTS idx_orders_sku_quantity;
    '''

    operations = [
        migrations.RunSQL(sql, reverse_sql)
    ] 