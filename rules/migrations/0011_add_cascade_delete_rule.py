# Generated manually for CASCADE delete behavior

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0010_add_cascade_delete'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL: Drop existing FK and create new one with CASCADE
            sql="""
            ALTER TABLE rules_rule 
                DROP CONSTRAINT rules_rule_rule_group_id_7b473e52_fk_rules_rulegroup_id,
                ADD CONSTRAINT rules_rule_rule_group_id_7b473e52_fk_rules_rulegroup_id 
                    FOREIGN KEY (rule_group_id) 
                    REFERENCES rules_rulegroup(id) 
                    ON DELETE CASCADE 
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            # Reverse SQL: Restore original FK without CASCADE
            reverse_sql="""
            ALTER TABLE rules_rule 
                DROP CONSTRAINT rules_rule_rule_group_id_7b473e52_fk_rules_rulegroup_id,
                ADD CONSTRAINT rules_rule_rule_group_id_7b473e52_fk_rules_rulegroup_id 
                    FOREIGN KEY (rule_group_id) 
                    REFERENCES rules_rulegroup(id) 
                    DEFERRABLE INITIALLY DEFERRED;
            """
        ),
    ] 