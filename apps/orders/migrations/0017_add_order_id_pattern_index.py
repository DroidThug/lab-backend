from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_alter_laborder_order_id'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
            CREATE INDEX IF NOT EXISTS orders_laborder_order_id_pattern_idx 
            ON orders_laborder (order_id text_pattern_ops);
            ''',
            reverse_sql='''
            DROP INDEX IF EXISTS orders_laborder_order_id_pattern_idx;
            '''
        )
    ]