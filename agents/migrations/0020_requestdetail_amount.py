# Generated by Django 2.2.6 on 2019-10-07 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0019_remove_requestdetail_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestdetail',
            name='amount',
            field=models.CharField(default=1000, max_length=20),
            preserve_default=False,
        ),
    ]
