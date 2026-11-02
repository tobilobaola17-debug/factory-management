import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_customer_order_orderitem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='rawmaterial',
            old_name='minimum_level',
            new_name='minimum_stock_level',
        ),
        migrations.AlterField(
            model_name='rawmaterial',
            name='current_quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='rawmaterial',
            name='code',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='rawmaterial',
            name='minimum_stock_level',
            field=models.DecimalField(decimal_places=2, default=10, max_digits=10),
        ),
        migrations.AddField(
            model_name='rawmaterial',
            name='supplier',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='materials',
                to='core.supplier',
            ),
        ),
        migrations.AlterField(
            model_name='rawmaterial',
            name='unit',
            field=models.CharField(default='units', max_length=50),
        ),
        migrations.AlterField(
            model_name='stockmovement',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AddField(
            model_name='stockmovement',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='contact_info',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='supplied_materials',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='profile',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]