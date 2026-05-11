from django.db import migrations


class Migration(migrations.Migration):
    """Convert audit_log organization_id from bigint to UUID."""

    dependencies = [
        ('core_organizations', '0002_convert_org_id_to_uuid'),
        ('core_audit', '0002_initial'),
    ]

    operations = [
        # Drop foreign key constraint
        migrations.RunSQL(
            sql="""
                ALTER TABLE audit_auditlog 
                DROP CONSTRAINT IF EXISTS audit_auditlog_organization_id_8d9a4b2f_fk_core_orga;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Change organization_id from bigint to uuid
        migrations.RunSQL(
            sql="""
                ALTER TABLE audit_auditlog 
                ALTER COLUMN organization_id TYPE uuid 
                USING '00000000-0000-0000-0000-' || lpad(organization_id::text, 12, '0')::uuid;
            """,
            reverse_sql="""
                ALTER TABLE audit_auditlog 
                ALTER COLUMN organization_id TYPE bigint 
                USING NULL;
            """,
        ),
        # Recreate foreign key constraint
        migrations.RunSQL(
            sql="""
                ALTER TABLE audit_auditlog 
                ADD CONSTRAINT audit_auditlog_organization_id_8d9a4b2f_fk_core_orga 
                FOREIGN KEY (organization_id) REFERENCES core_organizations_organization(id);
            """,
            reverse_sql="ALTER TABLE audit_auditlog DROP CONSTRAINT IF EXISTS audit_auditlog_organization_id_8d9a4b2f_fk_core_orga;",
        ),
    ]
