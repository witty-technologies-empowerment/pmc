# Generated by Django 2.2.6 on 2019-10-07 06:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0013_requestdetail_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestdetail',
            name='added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
