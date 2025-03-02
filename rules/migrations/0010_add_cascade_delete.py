# Generated manually for CASCADE delete behavior

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0009_merge_0002_add_tier_config_0008_alter_rule_field'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL: Drop existing FK and create new one with CASCADE
            sql="""
            ALTER TABLE rules_rulegroup 
                DROP CONSTRAINT rules_rulegroup_customer_service_id_c46adf52_fk_customer_,
                ADD CONSTRAINT rules_rulegroup_customer_service_id_c46adf52_fk_customer_ 
                    FOREIGN KEY (customer_service_id) 
                    REFERENCES customer_services_customerservice(id) 
                    ON DELETE CASCADE 
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            # Reverse SQL: Restore original FK without CASCADE
            reverse_sql="""
            ALTER TABLE rules_rulegroup 
                DROP CONSTRAINT rules_rulegroup_customer_service_id_c46adf52_fk_customer_,
                ADD CONSTRAINT rules_rulegroup_customer_service_id_c46adf52_fk_customer_ 
                    FOREIGN KEY (customer_service_id) 
                    REFERENCES customer_services_customerservice(id) 
                    DEFERRABLE INITIALLY DEFERRED;
            """
        ),
    ] 