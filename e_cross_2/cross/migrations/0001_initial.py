# Generated by Django 5.0.2 on 2024-10-25 12:02

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Box',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=8)),
                ('num', models.CharField(max_length=8)),
                ('name_type', models.CharField(max_length=20)),
                ('con_type', models.IntegerField(default=0)),
                ('stairway', models.CharField(blank=True, max_length=8)),
                ('floor', models.CharField(blank=True, max_length=6)),
                ('serv_area', models.CharField(blank=True, max_length=300)),
                ('num_plints', models.IntegerField(blank=True, default=0)),
                ('prim', models.CharField(blank=True, max_length=180)),
                ('rack_num', models.PositiveSmallIntegerField(default=0)),
                ('rack_pos', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30)),
                ('house_num', models.CharField(max_length=10)),
                ('kvar', models.IntegerField(default=1)),
                ('double_id', models.IntegerField(default=0)),
                ('info_comp', models.IntegerField(default=1)),
                ('info_cont', models.CharField(blank=True, max_length=2048)),
                ('cnt_place', models.CharField(blank=True, max_length=512)),
                ('cnt_price', models.CharField(blank=True, max_length=512)),
                ('deadline', models.DateField(blank=True, null=True)),
                ('electricity', models.CharField(blank=True, max_length=512)),
                ('info_signs', models.BooleanField(default=False)),
                ('senior_home', models.CharField(blank=True, max_length=512)),
                ('tech_conditions', models.CharField(blank=True, max_length=512)),
                ('access', models.CharField(blank=True, max_length=2048)),
                ('prim', models.CharField(blank=True, max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Cross',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('name_type', models.CharField(max_length=30)),
                ('con_type', models.IntegerField()),
                ('v_col', models.IntegerField(default=1)),
                ('v_row', models.IntegerField(default=1)),
                ('v_forw_l_r', models.BooleanField(default=True)),
                ('prim', models.CharField(blank=True, max_length=180)),
                ('rack_num', models.PositiveSmallIntegerField(default=0)),
                ('rack_pos', models.PositiveSmallIntegerField(default=0)),
                ('object_owner', models.CharField(blank=True, max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Kvartal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Street',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parrent', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Box_ports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cable_id', models.IntegerField(default=0)),
                ('num', models.IntegerField()),
                ('port_t_x', models.IntegerField(default=0)),
                ('p_valid', models.BooleanField(default=True)),
                ('p_alias', models.CharField(max_length=30)),
                ('changed', models.BooleanField(default=False)),
                ('up_device_id', models.IntegerField(default=0)),
                ('up_status', models.IntegerField(default=0)),
                ('int_c_status', models.IntegerField(default=0)),
                ('dogovor', models.CharField(blank=True, max_length=12)),
                ('ab_kv', models.CharField(blank=True, max_length=6)),
                ('ab_fio', models.CharField(blank=True, max_length=320)),
                ('ab_prim', models.CharField(blank=True, max_length=2048)),
                ('his_dogovor', models.CharField(blank=True, max_length=12)),
                ('his_ab_kv', models.CharField(blank=True, max_length=6)),
                ('his_ab_fio', models.CharField(blank=True, max_length=320)),
                ('his_ab_prim', models.CharField(blank=True, max_length=2048)),
                ('date_cr', models.DateTimeField(default=datetime.datetime.now)),
                ('date_del', models.DateTimeField(default=datetime.datetime.now)),
                ('parrent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cross.box')),
            ],
        ),
        migrations.CreateModel(
            name='Cross_ports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField()),
                ('port_t_x', models.IntegerField(default=0)),
                ('p_valid', models.BooleanField(default=True)),
                ('prim', models.CharField(blank=True, max_length=60)),
                ('opt_len', models.IntegerField(default=0)),
                ('up_cross_id', models.IntegerField(default=0)),
                ('up_status', models.IntegerField(default=0)),
                ('int_c_dest', models.IntegerField(default=0)),
                ('int_c_id', models.IntegerField(default=0)),
                ('int_c_status', models.IntegerField(default=0)),
                ('cab_p_id', models.IntegerField(default=0)),
                ('parrent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cross.cross')),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('ip_addr', models.GenericIPAddressField(blank=True, null=True, protocol='IPv4')),
                ('mac_addr', models.CharField(blank=True, max_length=30)),
                ('ip_mask', models.IntegerField(default=0)),
                ('ip_gateway', models.GenericIPAddressField(blank=True, null=True, protocol='IPv4')),
                ('vlan', models.IntegerField(default=0)),
                ('sn', models.CharField(blank=True, max_length=20)),
                ('vers_po', models.CharField(blank=True, max_length=48)),
                ('man_conf', models.CharField(blank=True, max_length=30)),
                ('man_install', models.CharField(blank=True, max_length=30)),
                ('date_ent', models.DateField(blank=True, null=True)),
                ('date_repl', models.DateField(blank=True, null=True)),
                ('prim', models.CharField(blank=True, max_length=180)),
                ('rack_num', models.PositiveSmallIntegerField(default=0)),
                ('rack_pos', models.PositiveSmallIntegerField(default=0)),
                ('date_upd', models.DateTimeField(blank=True, null=True)),
                ('object_owner', models.CharField(blank=True, max_length=60)),
                ('obj_type', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='core.templ_device')),
            ],
        ),
        migrations.CreateModel(
            name='Device_ports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField()),
                ('port_t_x', models.IntegerField(default=0)),
                ('port_speed', models.IntegerField(default=0)),
                ('p_valid', models.BooleanField(default=True)),
                ('p_alias', models.CharField(blank=True, max_length=30)),
                ('prim', models.CharField(blank=True, max_length=200)),
                ('uplink', models.BooleanField(default=False)),
                ('vlantz', models.CharField(blank=True, max_length=30)),
                ('int_c_dest', models.IntegerField(default=0)),
                ('int_c_id', models.IntegerField(default=0)),
                ('int_c_status', models.IntegerField(default=0)),
                ('int_c_t_x', models.IntegerField(default=0)),
                ('int_c_speed', models.IntegerField(default=0)),
                ('vlan_tag_list', models.CharField(blank=True, max_length=2048)),
                ('mvr', models.CharField(blank=True, max_length=1)),
                ('vlan_untag', models.CharField(blank=True, max_length=128)),
                ('ip', models.CharField(blank=True, max_length=128)),
                ('shut', models.BooleanField(default=False)),
                ('desc', models.CharField(blank=True, max_length=64)),
                ('p_chan', models.IntegerField(default=0)),
                ('trunk', models.BooleanField(default=False)),
                ('parrent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cross.device')),
            ],
        ),
        migrations.CreateModel(
            name='Device_ports_v',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parrent_p', models.IntegerField(default=0)),
                ('p_alias', models.CharField(blank=True, max_length=30)),
                ('prim', models.CharField(blank=True, max_length=200)),
                ('vlan_untag', models.CharField(blank=True, max_length=128)),
                ('ip', models.CharField(blank=True, max_length=128)),
                ('shut', models.BooleanField(default=False)),
                ('desc', models.CharField(blank=True, max_length=30)),
                ('parrent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cross.device')),
            ],
        ),
        migrations.CreateModel(
            name='Locker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('name_type', models.CharField(max_length=30)),
                ('con_type', models.IntegerField()),
                ('agr', models.BooleanField(default=False)),
                ('detached', models.BooleanField(default=False)),
                ('co', models.CharField(max_length=10)),
                ('status', models.IntegerField(default=0)),
                ('date_ent', models.DateField(blank=True, null=True)),
                ('rasp', models.CharField(blank=True, max_length=200)),
                ('prim', models.CharField(blank=True, max_length=200)),
                ('coord_x', models.FloatField(default=0)),
                ('coord_y', models.FloatField(default=0)),
                ('racks', models.CharField(blank=True, max_length=200)),
                ('cab_door', models.CharField(blank=True, max_length=20)),
                ('cab_key', models.CharField(blank=True, max_length=6)),
                ('object_owner', models.CharField(blank=True, max_length=60)),
                ('en_model', models.IntegerField(default=1)),
                ('en_sn', models.CharField(blank=True, max_length=20)),
                ('en_date_reg', models.DateField(blank=True, null=True)),
                ('en_date_check', models.DateField(blank=True, null=True)),
                ('en_meter', models.CharField(default=',', max_length=30)),
                ('parrent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cross.building')),
            ],
        ),
        migrations.AddField(
            model_name='device',
            name='parrent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cross.locker'),
        ),
        migrations.AddField(
            model_name='cross',
            name='parrent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cross.locker'),
        ),
        migrations.AddField(
            model_name='box',
            name='parrent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cross.locker'),
        ),
        migrations.AddField(
            model_name='building',
            name='parrent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cross.street'),
        ),
        migrations.CreateModel(
            name='Subunit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('con_type', models.IntegerField(default=0)),
                ('poe', models.IntegerField(default=0)),
                ('ip_addr', models.GenericIPAddressField(blank=True, null=True, protocol='IPv4')),
                ('mac_addr', models.CharField(blank=True, max_length=30)),
                ('sn', models.CharField(blank=True, max_length=20)),
                ('inv', models.CharField(blank=True, max_length=40)),
                ('man_install', models.CharField(blank=True, max_length=30)),
                ('date_ent', models.DateField(blank=True, null=True)),
                ('date_repl', models.DateField(blank=True, null=True)),
                ('stairway', models.CharField(blank=True, max_length=8)),
                ('floor', models.CharField(blank=True, max_length=6)),
                ('prim', models.CharField(blank=True, max_length=180)),
                ('object_owner', models.CharField(blank=True, max_length=60)),
                ('box_p_id', models.IntegerField(default=0)),
                ('parrent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cross.locker')),
            ],
        ),
    ]
