from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_privilege_remove_labtest_privilege_labtest_privilege'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='labtest',
            name='privilege',
        ),
        migrations.AddField(
            model_name='labtest',
            name='privilege',
            field=models.ManyToManyField(related_name='tests', to='orders.Privilege'),
        ),
    ]