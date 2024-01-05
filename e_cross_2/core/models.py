#

import datetime

from django.db import models

class PRM(models.Model):
    class Meta:
        permissions = (("can_adm", "_admin_"),
                       ("can_new", "_create_new_"),
                       ("can_del", "_delete_object_"),
                       ("can_edit", "_edit_object_"),
                       ("can_edit_bu", "_edit_build_"),
                       ("can_edit_en", "_edit_energy_"),
                       ("can_ext", "_ext_cross_"),
                       ("can_int", "_int_cross_"),
                       ("can_ab", "_abonent_app_"),
                       ("can_sh_agr", "_show_agr_"),
                       ("can_app_view", "_app_view_"),
                       ("can_app_edit", "_app_edit_"),
                       ("can_cable_edit", "_cable_edit_"),
                       #("can_plan_edit", "_plan_edit_"),
                       #("can_equip_rent_adm", "can_equip_rent_adm_"),
                       #("can_equip_rent_tp", "can_equip_rent_tp_"),
                       #("can_equip_rent_of1", "can_equip_rent_of1_"),
                       #("can_equip_rent_of2", "can_equip_rent_of2_"),
                       #("can_equip_rent_del", "can_equip_rent_del_"),
                       #("can_hard_edit", "can_hard_edit_"),
                       #("can_telnet", "can_telnet_"),
                       )

class History(models.Model):
    user = models.CharField(max_length=30)
    time_rec = models.DateTimeField(default=datetime.datetime.now)
    obj_type = models.IntegerField(default=0)
    obj_id = models.IntegerField(default=0)
    operation1 = models.IntegerField(default=0)
    operation2 = models.IntegerField(default=0)
    text = models.CharField(max_length=2560, blank=True)

    def __str__(self):
        return f"{self.id} | {self.user} | {self.time_rec} | {self.text}"

class engineer(models.Model):
    fio = models.CharField(max_length=20)
    lo = models.BooleanField(default=False)
    rent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} | lo: {int(self.lo)} | rent: {int(self.rent)} | {self.fio}"

class COffice(models.Model):
    name = models.CharField(max_length=8)

    def __str__(self):
        return f"{self.id} | {self.name}"

class Device_type(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.id} | {self.name}"

class last_visit(models.Model):
    login = models.CharField(max_length=30)
    fullname = models.CharField(max_length=128)
    date_l_v = models.DateTimeField(default=datetime.datetime.now)
    prim = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.date_l_v} | {self.login} | {self.fullname} | >>> {self.prim}"

class firm(models.Model):
    name = models.CharField(max_length=20)
    lo = models.BooleanField(default=False)             # lo, cr, dev
    obj = models.BooleanField(default=False)            #
    coup = models.BooleanField(default=False)           #
    rent = models.BooleanField(default=False)           #equipment

    def __str__(self):
        return f"{self.id} | lo: {int(self.lo)} | obj: {int(self.obj)} | coup: {int(self.coup)} | rent: {int(self.rent)} | {self.name}"

class manage_comp(models.Model):
    name = models.CharField(max_length=60)
    info = models.CharField(max_length=2048, blank=True)

    def __str__(self):
        return f"{self.id} | {self.name} | {self.info}"

class Energy_type(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return f"{str(self.id)} | {self.name}"

class Subunit_type(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.id} | {self.name}"

class map_slot(models.Model):
    num = models.IntegerField(unique=True)
    name = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.id} | {self.num} | {self.name}"

######################################

class Templ_locker(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.id} | {self.name}"

class Templ_cross(models.Model):
    name = models.CharField(max_length=30)
    ports = models.IntegerField(default=0)
    port_t_x = models.IntegerField(default=1)           #1-x 2-t 3-tx
    v_col = models.IntegerField(default=1)
    v_row = models.IntegerField(default=1)
    v_forw_l_r = models.BooleanField(default=True)      #счет портов - справа налево/сверху вниз
    ext_p = models.BooleanField(default=False)          #расширяемый кросс (кассета)
    units = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.id} | {self.name} | ports: {self.ports}"

class Templ_device(models.Model):
    parrent = models.ForeignKey(Device_type, on_delete=models.PROTECT, default=1)
    name = models.CharField(max_length=30)
    ports = models.IntegerField(default=0)
    port_alias_list = models.CharField(max_length=2000)
    port_t_x_list = models.CharField(max_length=2000)
    port_speed_list = models.CharField(max_length=2000)
    units = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.id} | {self.name} | ports: {self.ports} ⏩ {self.parrent}"

class Templ_box(models.Model):
    name = models.CharField(max_length=20)
    units = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.id} | {self.name} | units: {self.units}"

class Templ_subunit(models.Model):
    parrent = models.ForeignKey(Subunit_type, on_delete=models.PROTECT, default=1)
    name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.id} | {self.name} ⏩ {self.parrent}"

class Templ_box_cable(models.Model):
    name = models.CharField(max_length=30)
    ports = models.IntegerField(default=0)
    alias_list = models.CharField(max_length=300)
    #port_t_x = models.IntegerField(default=0)
    num_plints = models.IntegerField(default=0)
    color_cable = models.CharField(max_length=16, blank=True)

    def __str__(self):
        return f"{self.id} | {self.name} | ports: {self.ports}"

