# Generated by Django 4.1.12 on 2023-12-24 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cross', '0006_remove_building_double_remove_building_double_list'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='device',
            name='con_type',
        ),
        migrations.RemoveField(
            model_name='device',
            name='name_type',
        ),
    ]