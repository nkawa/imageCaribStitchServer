# Generated by Django 4.0.4 on 2022-07-01 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imclient', '0002_filedir'),
    ]

    operations = [
        migrations.AddField(
            model_name='imfile',
            name='fhuman',
            field=models.CharField(default='0', max_length=20),
        ),
    ]