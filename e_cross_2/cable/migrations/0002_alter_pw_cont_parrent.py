# Generated by Django 4.0.2 on 2023-06-11 22:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cross', '0003_alter_box_parrent_alter_building_parrent_and_more'),
        ('cable', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pw_cont',
            name='parrent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cross.kvartal'),
        ),
    ]
