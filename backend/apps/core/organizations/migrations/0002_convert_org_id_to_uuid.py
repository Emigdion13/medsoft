# Generated manually to convert existing organization id from bigint to UUID

from django.db import migrations


class Migration(migrations.Migration):
    """Convert organization id from bigint to UUID."""

    dependencies = [
        ('core_organizations', '0001_initial'),
    ]

    operations = [
        # Drop primary key constraint (will be recreated later)
        migrations.RunSQL(
            sql="ALTER TABLE core_organizations_organization DROP CONSTRAINT IF EXISTS core_organizations_organization_pkey CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Add new UUID column
        migrations.RunSQL(
            sql="ALTER TABLE core_organizations_organization ADD COLUMN id_new uuid DEFAULT gen_random_uuid();",
            reverse_sql="ALTER TABLE core_organizations_organization DROP COLUMN IF EXISTS id_new;",
        ),
        # Update existing row to have deterministic UUID based on bigint value
        migrations.RunSQL(
            sql="""
                UPDATE core_organizations_organization 
                SET id_new = '00000000-0000-0000-0000-' || lpad(id::text, 12, '0')::uuid;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Drop old id column
        migrations.RunSQL(
            sql="ALTER TABLE core_organizations_organization DROP COLUMN id;",
            reverse_sql="ALTER TABLE core_organizations_organization ADD COLUMN id bigint;",
        ),
        # Rename new column to id
        migrations.RunSQL(
            sql="ALTER TABLE core_organizations_organization RENAME COLUMN id_new TO id;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Add primary key constraint back
        migrations.RunSQL(
            sql="ALTER TABLE core_organizations_organization ADD PRIMARY KEY (id);",
            reverse_sql="ALTER TABLE core_organizations_organization DROP CONSTRAINT IF EXISTS core_organizations_organization_pkey;",
        ),
    ]
