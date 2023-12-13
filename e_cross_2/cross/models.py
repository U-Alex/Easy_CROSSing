# cross__models

import datetime

from django.db import models
from core.models import Device_type, Subunit_type, Templ_device

class Kvartal(models.Model):
    #id = models.BigAutoField(primary_key=True)    ############## после update to 3.2
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.id)+' | '+self.name

class Street(models.Model):
    parrent = models.IntegerField(default=0)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name#'id-'+str(self.id)+' | '+self.name

class Building(models.Model):
    parrent = models.ForeignKey(Street, on_delete=models.PROTECT)
    name = models.CharField(max_length=30, blank=True)
    house_num = models.CharField(max_length=10)
    kvar = models.IntegerField(default=1)
    #double = models.BooleanField(default=False) ###
    double_id = models.IntegerField(default=0)
    #double_list = models.CharField(max_length=30, blank=True)   ###

    info_comp = models.IntegerField(default=1)                          # УК/ТСЖ/ЖСК   kpp.manage_comp
    info_cont = models.CharField(max_length=2048, blank=True)           # Контактная информация уполномоченного представителя собственников
    cnt_place = models.CharField(max_length=512, blank=True)            # Договор на размещение оборудования
    cnt_price = models.CharField(max_length=512, blank=True)            # Цена договора на размещение оборудования
    deadline = models.DateField(null=True, blank=True)                  # Сроки оплаты и оплата по договору (за размещение)
    electricity = models.CharField(max_length=512, blank=True)          # Акты сверки показаний и возмещение эл/эн
    info_signs = models.BooleanField(default=False)                     # Информационные таблички
    senior_home = models.CharField(max_length=512, blank=True)          # Льгота старшему дома
    tech_conditions = models.CharField(max_length=512, blank=True)      # Наличие тех.условий и актов разграничения
    access = models.CharField(max_length=2048, blank=True)              # Доступ
    prim = models.CharField(max_length=1024, blank=True)                # Примечание

    def __str__(self):
        return str(self.id)+' | '+self.name+' '+self.house_num

class Locker(models.Model):
    parrent = models.ForeignKey(Building, on_delete=models.PROTECT)
    name = models.CharField(max_length=30)
    name_type = models.CharField(max_length=30)
    con_type = models.IntegerField()
    agr = models.BooleanField(default=False)
#    obj_type = models.ForeignKey(Templ_locker, on_delete=models.PROTECT, default=1) ### на новой базе - default=0 (или без))
    detached = models.BooleanField(default=False)
    co = models.CharField(max_length=10)
    status = models.IntegerField(default=0)
    date_ent = models.DateField(null=True, blank=True)
    rasp = models.CharField(max_length=200, blank=True)
    prim = models.CharField(max_length=200, blank=True)
    coord_x = models.FloatField(default=0)
    coord_y = models.FloatField(default=0)

    racks = models.CharField(max_length=200, blank=True)                # name,max_units,...
    cab_door = models.CharField(max_length=20, blank=True)              # ключ от уд
    cab_key = models.CharField(max_length=6, blank=True)                # шкаф с ключами
    object_owner = models.CharField(max_length=60, blank=True)          # владелец

    en_model = models.IntegerField(default=1)
    en_sn = models.CharField(max_length=20, blank=True)
    en_date_reg = models.DateField(null=True, blank=True)
    en_date_check = models.DateField(null=True, blank=True)
    en_meter = models.CharField(max_length=30, default=',')

    def __str__(self):
        #return str(self.id)+' | '+self.name+' || '+str(self.parrent)
        return f"{str(self.id)} | {self.name} ⏩ {str(self.parrent)}"

class Cross(models.Model):
    parrent = models.ForeignKey(Locker, on_delete=models.PROTECT)
    name = models.CharField(max_length=30)
    name_type = models.CharField(max_length=30)
    con_type = models.IntegerField()
    v_col = models.IntegerField(default=1)
    v_row = models.IntegerField(default=1)
    v_forw_l_r = models.BooleanField(default=True)                      #счет портов - справа налево/сверху вниз
    prim = models.CharField(max_length=180, blank=True)
    rack_num = models.PositiveSmallIntegerField(default=0)
    rack_pos = models.PositiveSmallIntegerField(default=0)
    object_owner = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return str(self.id)+' | '+self.name+' | type-'+str(self.name_type)

class Device(models.Model):
    parrent = models.ForeignKey(Locker, on_delete=models.PROTECT)
    name = models.CharField(max_length=30)
    name_type = models.CharField(max_length=30, blank=True)
    con_type = models.IntegerField()
    obj_type = models.ForeignKey(Templ_device, on_delete=models.PROTECT, default=1) ### на новой базе - default=0 (или без))
    ip_addr = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True) ###для опроса конфигураций
    mac_addr = models.CharField(max_length=30, blank=True)
    sn = models.CharField(max_length=20, blank=True)
    vers_po = models.CharField(max_length=48, blank=True)
    man_conf = models.CharField(max_length=30, blank=True)
    man_install = models.CharField(max_length=30, blank=True)
    date_ent = models.DateField(null=True, blank=True)
    date_repl = models.DateField(null=True, blank=True)
    prim = models.CharField(max_length=180, blank=True)
    rack_num = models.PositiveSmallIntegerField(default=0)
    rack_pos = models.PositiveSmallIntegerField(default=0)
    date_upd = models.DateTimeField(null=True, blank=True)
    object_owner = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f"{str(self.id)} | {self.name} || {self.obj_type.name} ⏩ {str(self.parrent.name)}"

class Box(models.Model):
    parrent = models.ForeignKey(Locker, on_delete=models.PROTECT)
    name = models.CharField(max_length=8)
    num = models.CharField(max_length=8)
    name_type = models.CharField(max_length=20)                         
    con_type = models.IntegerField(default=0)
    stairway = models.CharField(max_length=8, blank=True)
    floor = models.CharField(max_length=6, blank=True)
    serv_area = models.CharField(max_length=300, blank=True)
    num_plints = models.IntegerField(default=0, blank=True)
    prim = models.CharField(max_length=180, blank=True)
    rack_num = models.PositiveSmallIntegerField(default=0)
    rack_pos = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(self.id)+' | '+self.name+'-'+self.num+' | '+self.name_type+' || locker-'+str(self.parrent)

class Subunit(models.Model):
    parrent = models.ForeignKey(Locker, on_delete=models.PROTECT)
    name = models.CharField(max_length=20)
    con_type = models.IntegerField(default=0)
    poe = models.IntegerField(default=0)
    ip_addr = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True)
    mac_addr = models.CharField(max_length=30, blank=True)
    sn = models.CharField(max_length=20, blank=True)
    inv = models.CharField(max_length=40, blank=True)
    man_install = models.CharField(max_length=30, blank=True)
    date_ent = models.DateField(null=True, blank=True)
    date_repl = models.DateField(null=True, blank=True)
    stairway = models.CharField(max_length=8, blank=True)
    floor = models.CharField(max_length=6, blank=True)
    prim = models.CharField(max_length=180, blank=True)
    object_owner = models.CharField(max_length=60, blank=True)
    
    box_p_id = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.id)+' | '+self.name+' || locker-'+str(self.parrent)

####################################################################################################

class Cross_ports(models.Model):
    parrent = models.ForeignKey(Cross, on_delete=models.CASCADE)
    num = models.IntegerField()
    port_t_x = models.IntegerField(default=0)
    p_valid = models.BooleanField(default=True)
    prim = models.CharField(max_length=60, blank=True)
    opt_len = models.IntegerField(default=0)
    up_cross_id = models.IntegerField(default=0)
    up_status = models.IntegerField(default=0)
    int_c_dest = models.IntegerField(default=0)
    int_c_id = models.IntegerField(default=0)
    int_c_status = models.IntegerField(default=0)

    cab_p_id = models.IntegerField(default=0)           #для модуля cable

    def __str__(self):
        return str(self.id)+' | p-'+str(self.num)+' || cr-'+str(self.parrent.name)+' || '+str(self.parrent.parrent)

class Device_ports(models.Model):
    parrent = models.ForeignKey(Device, on_delete=models.CASCADE)
    num = models.IntegerField()
    port_t_x = models.IntegerField(default=0)
    port_speed = models.IntegerField(default=0)                             # reserved
    p_valid = models.BooleanField(default=True)
    p_alias = models.CharField(max_length=30, blank=True)
    prim = models.CharField(max_length=200, blank=True)
    uplink = models.BooleanField(default=False)

    int_c_dest = models.IntegerField(default=0)
    int_c_id = models.IntegerField(default=0)
    int_c_status = models.IntegerField(default=0)
    int_c_t_x = models.IntegerField(default=0)
    int_c_speed = models.IntegerField(default=0)

    vlan_tag_list = models.CharField(max_length=2048, blank=True)
    mvr = models.CharField(max_length=1, blank=True)
    vlan_untag = models.CharField(max_length=128, blank=True)
    ip = models.CharField(max_length=128, blank=True)
    shut = models.BooleanField(default=False)
    desc = models.CharField(max_length=30, blank=True)
    p_chan = models.IntegerField(default=0)
    trunk = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)+' | p-'+str(self.num)+' || dev-'+str(self.parrent)+' || '+str(self.parrent.parrent)

class Device_ports_v(models.Model):
    parrent = models.ForeignKey(Device, on_delete=models.CASCADE)
    parrent_p = models.IntegerField(default=0)
    p_alias = models.CharField(max_length=30, blank=True)
    prim = models.CharField(max_length=200, blank=True)

    vlan_untag = models.CharField(max_length=128, blank=True)
    ip = models.CharField(max_length=128, blank=True)
    shut = models.BooleanField(default=False)
    desc = models.CharField(max_length=30, blank=True)

class Box_ports(models.Model):
    parrent = models.ForeignKey(Box, on_delete=models.CASCADE)
    cable_id = models.IntegerField(default=0)
    num = models.IntegerField()
    port_t_x = models.IntegerField(default=0)
    p_valid = models.BooleanField(default=True)
    p_alias = models.CharField(max_length=30)
    changed = models.BooleanField(default=False)            #запланированы изменения

    up_device_id = models.IntegerField(default=0)
    up_status = models.IntegerField(default=0)
    int_c_status = models.IntegerField(default=0)

    dogovor = models.CharField(max_length=12, blank=True)
    ab_kv = models.CharField(max_length=6, blank=True)
    ab_fio = models.CharField(max_length=320, blank=True)
    ab_prim = models.CharField(max_length=2048, blank=True)

    his_dogovor = models.CharField(max_length=12, blank=True)
    his_ab_kv = models.CharField(max_length=6, blank=True)
    his_ab_fio = models.CharField(max_length=320, blank=True)
    his_ab_prim = models.CharField(max_length=2048, blank=True)

    date_cr = models.DateTimeField(default=datetime.datetime.now)
    date_del = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return str(self.id)+' || box-'+str(self.parrent.name)+'-'+str(self.parrent.num)+'-'+self.p_alias+' || '+str(self.parrent.parrent)

####################################################################################################

