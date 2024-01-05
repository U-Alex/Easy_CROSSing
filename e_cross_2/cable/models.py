# cable__models

from django.db import models

from cross.models import Kvartal

class PW_cont(models.Model):
    parrent = models.ForeignKey(Kvartal, on_delete=models.PROTECT)
    name = models.CharField(max_length=30)
    obj_type = models.IntegerField(default=0)                               #1-опора, 2-колодец
    object_owner = models.CharField(max_length=60, blank=True)
    rasp = models.CharField(max_length=200, blank=True)
    prim = models.CharField(max_length=200, blank=True)
    coord_x = models.FloatField(default=0)
    coord_y = models.FloatField(default=0)

    def __str__(self):
        return f"{self.id} | {self.name} ⏩ {self.parrent}"

class Coupling(models.Model):
    parrent = models.IntegerField(default=0)
    parr_type = models.IntegerField(default=0)                              #0-Locker, 1-Building, 2-PW_cont
    name = models.CharField(max_length=40)
    name_type = models.CharField(max_length=30)
    object_owner = models.CharField(max_length=60, blank=True)
    installed = models.BooleanField(default=True)
    date_ent = models.DateField(null=True, blank=True)
    rasp = models.CharField(max_length=200, blank=True)
    prim = models.CharField(max_length=200, blank=True)
    coord_x = models.FloatField(default=0)
    coord_y = models.FloatField(default=0)

    def __str__(self):
        return f"{self.id} | parr_type: {self.parr_type} | {self.name} | {self.name_type}"

class Coupling_ports(models.Model):
    parrent = models.ForeignKey(Coupling, on_delete=models.CASCADE)
    cable_num = models.IntegerField(default=0)                              #№ кабеля в муфте
    cable_type = models.IntegerField(default=0)                             #тип кабеля
    fiber_num = models.IntegerField(default=0)                              #№ волокна в кабеле
    fiber_color = models.CharField(max_length=16, blank=True)               #цвет волокна в кабеле
    mod_num = models.IntegerField(default=0)                                #№ модуля в кабеле
    mod_color = models.CharField(max_length=16, blank=True)                 #цвет модуля в кабеле
    p_valid = models.BooleanField(default=True)
    changed = models.BooleanField(default=False)                            #запланированы изменения
    prim = models.CharField(max_length=200, blank=True)

    up_id = models.IntegerField(default=0)
    up_info = models.CharField(max_length=256, blank=True)                  #владелец волокна/кабеля,физич длина,запас,дата прокладки
    int_c_dest = models.IntegerField(default=0)                             #0-в муфту, 1-в кросс
    int_c_id = models.IntegerField(default=0)
    int_c_status = models.IntegerField(default=0)                           #0-разрыв, 1-транзит, 2-варка

    def __str__(self):
        return f"{self.id} | cab: {self.cable_num} | fib: {self.fiber_num} ⏩ {self.parrent}"

####################################################################################################

class Templ_cable(models.Model):
    name = models.CharField(max_length=36)
    capacity = models.IntegerField(default=0)                               #ёмкость
    modules = models.IntegerField(default=0)
    mod_capa_list = models.CharField(max_length=1024, blank=True)           #соответствие модуль-волокно
    mod_color_list = models.CharField(max_length=1024, blank=True)          #список цветов
    fiber_colors_list = models.CharField(max_length=2048, blank=True)       #список цветов

    def __str__(self):
        return f"{self.id} | {self.name} | capa: {self.capacity} | mod: {self.modules}"

class Templ_coupling(models.Model):
    name = models.CharField(max_length=36)

    def __str__(self):
        return f"{self.id} | {self.name}"

####################################################################################################

#таблицы для внешней программы VOLS

class links(models.Model):
    lineidid = models.CharField(max_length=15)
    linecncn = models.CharField(max_length=15)
    cabtype = models.CharField(max_length=64)
    cabcolor = models.CharField(max_length=7)
    path = models.CharField(max_length=4096)
    param = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.id} | {self.lineidid} | {self.linecncn} | {self.cabtype} | {self.cabcolor} | {self.path} | {self.param}"

class labels(models.Model):
    text = models.CharField(max_length=4096)
    pos = models.CharField(max_length=15)
    color1 = models.CharField(max_length=7)
    color2 = models.CharField(max_length=7)
    param = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.id} | {self.text} | {self.pos} | {self.color1} | {self.color2} | {self.param}"
