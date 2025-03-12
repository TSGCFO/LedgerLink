#!/bin/bash
# Script to copy data from production database to test database

# Set variables for both databases
PROD_HOST="db.dorunzumqoeiozqiyiux.supabase.co"
PROD_DB="postgres"
PROD_USER="postgres"
PROD_PASSWORD="Hassan8488\$"

TEST_HOST="localhost"
TEST_DB="ledgerlink_test"
TEST_USER="postgres"
TEST_PASSWORD="postgres"

# Create a temporary directory for data files
TEMP_DIR="./tmp_data_transfer"
mkdir -p $TEMP_DIR

echo "==== Starting Data Transfer Process ===="

# Define the order of tables to copy (based on dependencies)
TABLES=(
    # Core Django tables
    "django_content_type"
    "auth_permission"
    "auth_group"
    "auth_group_permissions"
    "auth_user"
    "auth_user_groups"
    "auth_user_user_permissions"
    
    # Application tables (ordered by dependencies)
    "customers_customer"
    "products_product"
    "services_service"
    "materials_material"
    "materials_boxprice"
    "orders_order"
    "orders_ordersku"
    "shipping_usshipping"
    "shipping_cadshipping"
    "inserts_insert"
    "rules_rulegroup"
    "rules_rule"
    "rules_advancedrule"
    "customer_services_customerservice"
    "billing_billingreport"
    "billing_billingreportdetail"
)

# Export data from production database and import to test database for each table
for TABLE in "${TABLES[@]}"; do
    echo "Processing table: $TABLE"
    
    # Export table from production database
    echo "  Exporting from production..."
    PGPASSWORD=$PROD_PASSWORD pg_dump -h $PROD_HOST -U $PROD_USER -d $PROD_DB \
        --table=public."$TABLE" --data-only --column-inserts > "$TEMP_DIR/$TABLE.sql"
    
    # Check if export was successful
    if [ $? -ne 0 ]; then
        echo "  ERROR: Failed to export $TABLE from production"
        continue
    fi
    
    # Import table to test database
    echo "  Importing to test database..."
    PGPASSWORD=$TEST_PASSWORD psql -h $TEST_HOST -U $TEST_USER -d $TEST_DB \
        -c "TRUNCATE TABLE \"$TABLE\" CASCADE;" 2>/dev/null || echo "  Truncate failed, continuing..."
    
    PGPASSWORD=$TEST_PASSWORD psql -h $TEST_HOST -U $TEST_USER -d $TEST_DB \
        -f "$TEMP_DIR/$TABLE.sql"
    
    # Check if import was successful
    if [ $? -ne 0 ]; then
        echo "  ERROR: Failed to import $TABLE to test database"
        continue
    fi
    
    echo "  Successfully copied $TABLE"
done

# Handle materialized views
echo "Refreshing materialized views..."
PGPASSWORD=$TEST_PASSWORD psql -h $TEST_HOST -U $TEST_USER -d $TEST_DB \
    -c "REFRESH MATERIALIZED VIEW orders_orderskuview;"

PGPASSWORD=$TEST_PASSWORD psql -h $TEST_HOST -U $TEST_USER -d $TEST_DB \
    -c "REFRESH MATERIALIZED VIEW customer_services_customerserviceview;"

# Clean up temporary files
echo "Cleaning up temporary files..."
rm -rf $TEMP_DIR

echo "==== Data Transfer Complete ===="

# Test database with a simple query
echo "Verifying data transfer with simple counts:"
for TABLE in "${TABLES[@]}"; do
    COUNT=$(PGPASSWORD=$TEST_PASSWORD psql -h $TEST_HOST -U $TEST_USER -d $TEST_DB \
        -t -c "SELECT COUNT(*) FROM \"$TABLE\";" | tr -d ' ')
    echo "  $TABLE: $COUNT records"
done

echo "Done!"