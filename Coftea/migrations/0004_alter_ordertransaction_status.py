# Generated by Django 5.1.2 on 2024-10-31 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Coftea', '0003_product_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordertransaction',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20),
        ),
    ]