# Generated by Django 4.2.19 on 2025-02-22 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0017_add_order_id_pattern_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='laborder',
            name='order_id',
            field=models.CharField(db_index=True, editable=False, max_length=20, unique=True),
        ),
    ]
