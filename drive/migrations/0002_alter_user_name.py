# Generated by Django 5.1.1 on 2024-09-21 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
