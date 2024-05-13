#  cross__forms

from django import forms
# from django.forms.widgets import SelectDateWidget

from .models import Kvartal#, Street, Building
from core.models import Templ_locker, Templ_cross, Templ_box_cable, Templ_box, Templ_subunit
from core.models import engineer, COffice, firm, manage_comp, Energy_type
from core.e_config import conf

####################################################################################################

class edit_bu_Form(forms.Form):
    kvar = forms.ChoiceField(label='квартал', widget=forms.Select, choices=[], required=False)

    info_comp = forms.ChoiceField(widget=forms.Select(attrs={'size': 1}), choices=[])
    info_cont = forms.CharField(max_length=2000, required=False, widget=forms.TextInput(attrs={'size': 151}))
    cnt_place = forms.CharField(max_length=500, required=False, widget=forms.TextInput(attrs={'size': 80}))
    cnt_price = forms.CharField(max_length=500, required=False, widget=forms.TextInput(attrs={'size': 60}))
    deadline_use = forms.BooleanField(required=False)
    deadline_d = forms.ChoiceField(widget=forms.Select, choices=[])
    deadline_m = forms.ChoiceField(widget=forms.Select, choices=[])
    electricity = forms.CharField(max_length=500, required=False, widget=forms.TextInput(attrs={'size': 151}))
    info_signs = forms.BooleanField(required=False)
    senior_home = forms.CharField(max_length=500, required=False, widget=forms.TextInput(attrs={'size': 151}))
    tech_conditions = forms.CharField(max_length=500, required=False, widget=forms.TextInput(attrs={'size': 151}))
    access = forms.CharField(max_length=2000, required=False, widget=forms.TextInput(attrs={'size': 151}))
    prim = forms.CharField(max_length=1000, required=False, widget=forms.TextInput(attrs={'size': 151}))

    def __init__(self, *args, **kwargs):
        super(edit_bu_Form, self).__init__(*args, **kwargs)
        self.fields['kvar'].choices = Kvartal.objects.values_list('id', 'name').order_by('name')
        self.fields['info_comp'].choices = manage_comp.objects.values_list('id', 'name').order_by('name')
        d_list = [(i, i) for i in range(1, 32)]
        self.fields['deadline_d'].choices = d_list
        self.fields['deadline_m'].choices = [(key, value) for key, value in conf.MONTHS.items()]

class new_locker_Form(forms.Form):
    lo_name = forms.CharField(label='Имя (УД-1, УА-5-2, ...)', max_length=30)
    lo_name_type = forms.ChoiceField(label='Тип', widget=forms.Select, choices=[])
    co = forms.ChoiceField(label='офис', required=False, widget=forms.Select, choices=[])

    def __init__(self, *args, **kwargs):
        super(new_locker_Form, self).__init__(*args, **kwargs)
        self.fields['lo_name_type'].choices = Templ_locker.objects.values_list('id', 'name').order_by('name')
        co_list2 = COffice.objects.values_list('name', flat=True).order_by('name')
        self.fields['co'].choices = [(i, i) for i in co_list2]

class edit_lo_Form(new_locker_Form):#(forms.Form):
    status = forms.ChoiceField(label='статус', widget=forms.RadioSelect, choices=conf.STATUS_LIST_LO)
    # date_ent = forms.DateField(label='дата приемки', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    rasp = forms.CharField(label='расположение', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 54}))
    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 54}))
    detached = forms.BooleanField(required=False)
    coord = forms.CharField(label='координаты', max_length=32, required=False, widget=forms.TextInput(attrs={'size': 54}))
    racks = forms.CharField(label='стойки, ёмкость', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 54}))
    cab_door = forms.ChoiceField(label='ключи от УД', required=False, widget=forms.Select, choices=[])
    cab_key1 = forms.IntegerField(label='', required=False, min_value=1, max_value=3, widget=forms.NumberInput(attrs={'class': 'int_field'}))
    cab_key2 = forms.IntegerField(label='', required=False, min_value=1, max_value=96, widget=forms.NumberInput(attrs={'class': 'int_field'}))
    object_owner = forms.CharField(label='владелец', max_length=60, required=False, widget=forms.TextInput(attrs={'size': 20}))
    object_owner_list = forms.ChoiceField(label='владелец', required=False, widget=forms.Select, choices=[])

    def __init__(self, *args, **kwargs):
        super(edit_lo_Form, self).__init__(*args, **kwargs)
        self.fields['racks'].disabled = True                                                        ###########
        key_type = [(i, i) for i in conf.KEY_DOOR_TYPE]
        self.fields['cab_door'].choices = key_type
        own_list = list(firm.objects.filter(lo=True).values_list('name', flat=True).order_by('name'))
        self.fields['object_owner_list'].choices = [('', '')] + [(i, i) for i in own_list]
        self.fields['coord'].disabled = True

class energy_Form(forms.Form):
    en_model = forms.ChoiceField(label='тип/модель', required=False, widget=forms.Select, choices=[])
    en_sn = forms.CharField(label='номер счетчика', max_length=20, required=False, widget=forms.TextInput(attrs={'size': 26}))
    en_meter1 = forms.CharField(label='предыдущие показания', max_length=14, required=False, widget=forms.TextInput(attrs={'size': 26}))
    en_meter2 = forms.CharField(label='текущие показания', max_length=14, required=False, widget=forms.TextInput(attrs={'size': 26}))

    def __init__(self, *args, **kwargs):
        super(energy_Form, self).__init__(*args, **kwargs)
        self.fields['en_model'].choices = Energy_type.objects.values_list('id', 'name').order_by('id')


class new_cr_Form(forms.Form):
    cr_name = forms.CharField(label='Имя кросса (M-1, M-2, kc-1,...)', max_length=30)
    cr_name_type = forms.ChoiceField(label='Тип кросса', widget=forms.Select, choices=[])

    def __init__(self, *args, **kwargs):
        super(new_cr_Form, self).__init__(*args, **kwargs)
        self.fields['cr_name_type'].choices = Templ_cross.objects.values_list('id', 'name').order_by('name')

class edit_cr_Form(new_cr_Form):
    ch_type = forms.BooleanField(required=False)
    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 66}))
    rack_num = forms.ChoiceField(label='стойка', widget=forms.Select, choices=[], required=False)
    rack_pos = forms.IntegerField(label='позиция', min_value=0, max_value=64, required=False)
    object_owner = forms.CharField(label='владелец', max_length=60, required=False, widget=forms.TextInput(attrs={'size': 20}))
    object_owner_list = forms.ChoiceField(label='владелец', required=False, widget=forms.Select, choices=[])

    def __init__(self, *args, **kwargs):
        super(edit_cr_Form, self).__init__(*args, **kwargs)
        own_list = list(firm.objects.filter(lo=True).values_list('name', flat=True).order_by('name'))
        self.fields['object_owner_list'].choices = [('', '')] + [(i, i) for i in own_list]

#####

class new_dev_Form(forms.Form):
    dev_name = forms.CharField(label='Имя устройства (Abc-1-1-1,...)', max_length=20, widget=forms.TextInput(attrs={'size': 30}))
    vlantz = forms.CharField(label='vlan ТЗ', max_length=30, required=False, widget=forms.TextInput(attrs={'size': 30}))

class edit_dev_Form(forms.Form):
    dev_name = forms.CharField(label='имя устройства', max_length=20)
    ip = forms.GenericIPAddressField(label='IP-адрес', protocol='IPv4', required=False)
    mac = forms.CharField(label='MAC-адрес', max_length=17, required=False)
    ip_mask = forms.IntegerField(label='маска (CIDR)', min_value=0, max_value=32)
    ip_gateway = forms.GenericIPAddressField(label='шлюз', protocol='IPv4', required=False)
    vlan = forms.IntegerField(label='vlan управления', min_value=0, max_value=4096)
    sn = forms.CharField(label='серийный номер', max_length=20, required=False)
    vers_po = forms.CharField(label='версия ПО', max_length=48, required=False)

    man_conf = forms.CharField(label='подготовил', max_length=30, required=False, widget=forms.TextInput(attrs={'size': 20}))
    man_conf_list = forms.ChoiceField(required=False, widget=forms.Select, choices=[])
    man_install = forms.CharField(label='монтаж', max_length=30, required=False, widget=forms.TextInput(attrs={'size': 20}))
    man_install_list = forms.ChoiceField(required=False, widget=forms.Select, choices=[])

    # date_ent = forms.DateField(label='дата ввода', required=False, widget=SelectDateWidget(months=conf.MONTHS, years=conf.YEARS))
    date_ent = forms.DateField(label='дата ввода', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    # date_repl = forms.DateField(label='дата замены', required=False, widget=SelectDateWidget(months=conf.MONTHS, years=conf.YEARS))
    date_repl = forms.DateField(label='дата замены', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 51}))
    rack_num = forms.ChoiceField(label='стойка', widget=forms.Select, choices=[], required=False)
    rack_pos = forms.IntegerField(label='позиция', min_value=0, max_value=64, required=False)
    object_owner = forms.CharField(label='владелец', max_length=60, required=False, widget=forms.TextInput(attrs={'size': 20}))
    object_owner_list = forms.ChoiceField(label='владелец', required=False, widget=forms.Select, choices=[])

    def __init__(self, *args, **kwargs):
        super(edit_dev_Form, self).__init__(*args, **kwargs)
        eng_list2 = engineer.objects.filter(lo=True).values_list('fio', flat=True).order_by('fio')
        eng_list = [(i, i) for i in eng_list2]
        self.fields['man_conf_list'].choices = eng_list
        self.fields['man_install_list'].choices = eng_list
        own_list = firm.objects.filter(lo=True).values_list('name', flat=True).order_by('name')
        self.fields['object_owner_list'].choices = [('', '')] + [(i, i) for i in own_list]

#####

class new_box_Form(forms.Form):
    box_name_type = forms.ChoiceField(label='тип коробки', widget=forms.RadioSelect, choices=[])
    box_name = forms.CharField(label='КРТ', max_length=8, widget=forms.TextInput(attrs={'size': 3}))
    box_num = forms.CharField(label='№ в подъезде', max_length=8, widget=forms.TextInput(attrs={'size': 3}))
    cable_name_type = forms.ChoiceField(label='тип первого кабеля в крт', widget=forms.RadioSelect, choices=[])

    def __init__(self, *args, **kwargs):
        super(new_box_Form, self).__init__(*args, **kwargs)
        self.fields['box_name_type'].choices = Templ_box.objects.values_list('id', 'name').order_by('name')
        self.fields['cable_name_type'].choices = Templ_box_cable.objects.values_list('id', 'name').order_by('ports')

class edit_box_Form(new_box_Form):
    box_stairway = forms.CharField(label='подъезд', max_length=8, required=False, widget=forms.TextInput(attrs={'size': 3}))
    floor = forms.CharField(label='этаж', max_length=6, required=False, widget=forms.TextInput(attrs={'size': 3}))
    add_cable = forms.BooleanField(required=False)
    del_cable = forms.BooleanField(required=False)
    serv_area = forms.CharField(label='зона действия', max_length=280, required=False, widget=forms.TextInput(attrs={'size': 90}))
    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 90}))
    rack_num = forms.ChoiceField(label='стойка', widget=forms.Select, choices=[], required=False)
    rack_pos = forms.IntegerField(label='позиция', min_value=0, max_value=64, required=False)

    def __init__(self, *args, **kwargs):
        super(edit_box_Form, self).__init__(*args, **kwargs)
        self.fields['cable_name_type'].required = False
        self.fields['cable_name_type'].label = 'тип добавляемого кабеля'

class new_su_Form(forms.Form):
    su_name = forms.CharField(label='Имя устройства', max_length=20, widget=forms.TextInput(attrs={'size': 50}))
    
class edit_subunit_Form(forms.Form):
    name = forms.CharField(label='имя устройства', max_length=20)
    name_type = forms.ChoiceField(label='тип устройства', widget=forms.Select, choices=[])
    poe = forms.ChoiceField(label='Эл.питание', widget=forms.Select, choices=[])
    ip = forms.GenericIPAddressField(label='IP-адрес', protocol='IPv4', required=False)
    mac = forms.CharField(label='MAC-адрес', max_length=17, required=False)
    sn = forms.CharField(label='серийный номер', max_length=20, required=False)
    inv = forms.CharField(label='инвентарный номер', max_length=40, required=False)
    stairway = forms.CharField(label='подъезд', max_length=8, required=False, widget=forms.TextInput(attrs={'size': 3}))
    floor = forms.CharField(label='этаж', max_length=6, required=False, widget=forms.TextInput(attrs={'size': 3}))
    man_install = forms.CharField(label='монтаж', max_length=30, required=False, widget=forms.TextInput(attrs={'size': 20}))
    man_install_list = forms.ChoiceField(required=False, widget=forms.Select, choices=[])
    date_ent = forms.DateField(label='дата ввода', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_repl = forms.DateField(label='дата замены', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    prim = forms.CharField(label='примечание', max_length=180, required=False, widget=forms.TextInput(attrs={'size': 71}))
    object_owner = forms.CharField(label='владелец', max_length=60, required=False, widget=forms.TextInput(attrs={'size': 20}))
    object_owner_list = forms.ChoiceField(label='владелец', required=False, widget=forms.Select, choices=[])
    
    def __init__(self, *args, **kwargs):
        super(edit_subunit_Form, self).__init__(*args, **kwargs)
        self.fields['name_type'].choices = Templ_subunit.objects.values_list('id', 'name').order_by('parrent_id', 'name')#conf.SUBUNIT_TYPE
        self.fields['poe'].choices = conf.POE_TYPE
        eng_list2 = engineer.objects.filter(lo=True).values_list('fio', flat=True).order_by('fio')
        self.fields['man_install_list'].choices = [(i, i) for i in eng_list2]
        own_list = firm.objects.filter(lo=True).values_list('name', flat=True).order_by('name')
        self.fields['object_owner_list'].choices = [('', '')] + [(i, i) for i in own_list]

####################################################################################################

class sel_up_status_Form(forms.Form):
    status = forms.ChoiceField(label='статус кроссировки', widget=forms.RadioSelect, choices=conf.STATUS_LIST)

class cr_ab_Form(forms.Form):
    dog = forms.CharField(label='договор', max_length=12, required=False, widget=forms.TextInput(attrs={'size': 12}))
    kvar = forms.CharField(label='кв', max_length=6, required=False, widget=forms.TextInput(attrs={'size': 5}))
    fio = forms.CharField(label='ФИО', max_length=90, required=False, widget=forms.TextInput(attrs={'size': 66}))
    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 62}))
    status = forms.ChoiceField(label='статус кроссировки', widget=forms.RadioSelect, choices=conf.STATUS_LIST)

class del_ab_Form(forms.Form):
    pri = forms.ChoiceField(label='причина снятия', widget=forms.RadioSelect, choices=conf.PRI_LIST_F)

class edit_racks_Form(forms.Form):
    racks = forms.CharField(label='стойки, ёмкость', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 101}))

####################################################################################################

class edit_cr_p_Form(forms.Form):
    status1 = forms.ChoiceField(label='статус (внешняя связь)', required=False, widget=forms.RadioSelect, choices=conf.STATUS_LIST)
    status2 = forms.ChoiceField(label='статус (внутренняя связь)', required=False, widget=forms.RadioSelect, choices=conf.STATUS_LIST)
    valid = forms.BooleanField(required=False)
    prim = forms.CharField(label='примечание', max_length=50, required=False, widget=forms.TextInput(attrs={'size': 51}))
    opt_len = forms.IntegerField(label='оптическая длина', min_value=0, max_value=9999)

class edit_dev_p_Form(forms.Form):
    status = forms.ChoiceField(label='статус (внешняя связь)', required=False, widget=forms.RadioSelect, choices=conf.STATUS_LIST)
    valid = forms.BooleanField(required=False)
    #alias = forms.CharField(label='алиас', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 51}))
    alias = forms.CharField(label='алиас', max_length=50, widget=forms.TextInput(attrs={'size': 51}))
    desc = forms.CharField(label='description', max_length=50, required=False, widget=forms.TextInput(attrs={'size': 51}))
    prim = forms.CharField(label='примечание', max_length=50, required=False, widget=forms.TextInput(attrs={'size': 51}))
    uplink = forms.BooleanField(required=False)

class new_dev_p_v_Form(forms.Form):
    parrent_p = forms.IntegerField(label='родительский порт', min_value=0, max_value=128, required=False)
    p_alias = forms.CharField(label='алиас', max_length=30, widget=forms.TextInput(attrs={'size': 51}))
    prim = forms.CharField(label='примечание', max_length=50, required=False, widget=forms.TextInput(attrs={'size': 51}))
    vlan_untag = forms.CharField(label='vlan_untag', max_length=32, required=False, widget=forms.TextInput(attrs={'size': 51}))
    ip = forms.CharField(label='ip-addr', max_length=32, required=False, widget=forms.TextInput(attrs={'size': 51}))

class edit_dev_p_v_Form(new_dev_p_v_Form):
    desc = forms.CharField(label='description', max_length=50, required=False, widget=forms.TextInput(attrs={'size': 51}))
    vlan_tag_list = forms.CharField(label='vlan_tag_list', max_length=2048, required=False, widget=forms.TextInput(attrs={'size': 51}))
    shut = forms.BooleanField(required=False)
    mvr = forms.ChoiceField(label='mvr type', widget=forms.Select, choices=[('', '---'), ('s', 'source'), ('r', 'receiver')], required=False)
    vlantz = forms.CharField(label='vlan ТЗ', max_length=30, widget=forms.TextInput(attrs={'size': 51}), required=False)

class edit_box_p_Form(forms.Form):
    status1 = forms.ChoiceField(label='статус (кабельная связь)', required=False, widget=forms.RadioSelect, choices=conf.STATUS_LIST)
    status2 = forms.ChoiceField(label='статус (абонентская связь)', required=False, widget=forms.RadioSelect, choices=conf.STATUS_LIST)
    valid = forms.BooleanField(required=False)
    changed = forms.BooleanField(required=False)

    dog  = forms.CharField(label='договор', max_length=12, required=False, widget=forms.TextInput(attrs={'size': 14}))
    kv   = forms.CharField(label='кв', max_length=6, required=False, widget=forms.TextInput(attrs={'size': 5}))
    fio  = forms.CharField(label='ФИО', max_length=90, required=False, widget=forms.TextInput(attrs={'size': 66}))
    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 66}))
    h_dog  = forms.CharField(label='договор', max_length=12, required=False, widget=forms.TextInput(attrs={'size': 14}))
    h_kv   = forms.CharField(label='кв', max_length=6, required=False, widget=forms.TextInput(attrs={'size': 5}))
    h_fio  = forms.CharField(label='ФИО', max_length=90, required=False, widget=forms.TextInput(attrs={'size': 66}))
    h_prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 66}))
