# Generated by Django 5.1.4 on 2024-12-23 19:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='building',
            name='building_outline',
        ),
    ]