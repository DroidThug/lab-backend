from django.db import migrations, models

def fix_order_ids(apps, schema_editor):
    LabOrder = apps.get_model('orders', 'LabOrder')
    for order in LabOrder.objects.all():
        # Extract just the numeric portion after OR and year
        try:
            numeric_part = ''.join(filter(str.isdigit, order.order_id[4:]))
            year_part = order.order_id[2:4]
            order.order_id = f'OR{year_part}{numeric_part}'
            order.save()
        except (IndexError, ValueError):
            continue

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0015_laborder_clinical_history'),
    ]

    operations = [
        migrations.RunPython(fix_order_ids),
        migrations.AlterField(
            model_name='laborder',
            name='order_id',
            field=models.CharField(max_length=50, unique=True, editable=False, db_index=True),
        ),
    ]