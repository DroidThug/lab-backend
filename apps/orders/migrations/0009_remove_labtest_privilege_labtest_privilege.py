# Generated by Django 4.2.19 on 2025-02-21 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_alter_privilege_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='labtest',
            name='privilege',
        ),
        migrations.AddField(
            model_name='labtest',
            name='privilege',
            field=models.PositiveIntegerField(choices=[(1, 'Intern'), (2, 'Postgraduate'), (3, 'Staff')], default=1),
        ),
    ]
