# cable__forms

from django import forms
from django.forms.widgets import SelectDateWidget

#from cross.models import Kvartal, Street
from core.models import firm#, COffice
from .models import Templ_cable, Templ_coupling
from core.e_config import conf

####################################################################################################

class add_PW_Form(forms.Form):
    name = forms.CharField(label='имя объекта', max_length=30, widget=forms.TextInput(attrs={'size': 51}))
    obj_type = forms.ChoiceField(label='тип объекта', widget=forms.RadioSelect, choices=conf.OBJ_LIST)
    object_owner = forms.CharField(label='владелец объекта', max_length=60, required=False, widget=forms.TextInput(attrs={'size': 28}))
    object_owner_list = forms.ChoiceField(label='владелец объекта', required=False, widget=forms.Select, choices=[])
    rasp = forms.CharField(label='расположение', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 51}))
    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 51}))
    coord = forms.CharField(label='координаты', max_length=32, required=False, widget=forms.TextInput(attrs={'size': 51}))

    def __init__(self, *args, **kwargs):
        super(add_PW_Form, self).__init__(*args, **kwargs)
        own_list = list(firm.objects.filter(obj=True).values_list('name', flat=True).order_by('name'))
        #for ob in own_list:
        #    own_list[own_list.index(ob)] = [ob, ob]
        self.fields['object_owner_list'].choices = [('', '')] + [(i, i) for i in own_list]
        #self.fields['object_owner_list'].disabled = True

class add_Coup_Form(forms.Form):
    name = forms.CharField(label='имя муфты', max_length=40, widget=forms.TextInput(attrs={'size': 51}))
    name_type = forms.ChoiceField(label='тип муфты', widget=forms.RadioSelect, choices=[])
    object_owner = forms.CharField(label='владелец муфты', max_length=60, required=False, widget=forms.TextInput(attrs={'size': 28}))
    object_owner_list = forms.ChoiceField(label='владелец муфты', required=False, widget=forms.Select, choices=[])
    installed = forms.BooleanField(label='установлена', required=False)
    date_ent = forms.DateField(label='дата установки', required=False, widget=SelectDateWidget(months=conf.MONTHS, years=conf.YEARS))
    rasp = forms.CharField(label='расположение', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 51}))
    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 51}))
    coord = forms.CharField(label='координаты', max_length=32, required=False, widget=forms.TextInput(attrs={'size': 51}))

    def __init__(self, *args, **kwargs):
        super(add_Coup_Form, self).__init__(*args, **kwargs)
        coup_list = Templ_coupling.objects.values_list('name', flat=True).order_by('name')
        #for ob in coup_list2:
        #    coup_list2[coup_list2.index(ob)] = [ob, ob]
        #self.fields['name_type'].choices = coup_list2
        self.fields['name_type'].choices = [(i, i) for i in coup_list]
        own_list = firm.objects.filter(coup=True).values_list('name', flat=True).order_by('name')
        #for ob in own_list:
        #    own_list[own_list.index(ob)] = [ob, ob]
        self.fields['object_owner_list'].choices = [('', '')] + [(i, i) for i in own_list]

####################################################################################################

class coup_cab_edit_Form(forms.Form):
    #phys_len = forms.CharField(label='длина кабеля между муфтами (в метрах)', max_length=8, required=False, widget=forms.TextInput(attrs={'size': 11}))
    phys_len = forms.IntegerField(label='длина кабеля между муфтами (в метрах)', min_value=0, max_value=9999)#, required=False)
    res_len = forms.CharField(label='запас кабеля в муфте (в метрах)', max_length=6, required=False, widget=forms.TextInput(attrs={'size': 11}))
    date_ent = forms.DateField(label='дата ввода в муфту', required=False, widget=SelectDateWidget(months=conf.MONTHS, years=conf.YEARS))
    owner = forms.ChoiceField(label='владелец кабеля', required=False, widget=forms.Select, choices=[])
    owner_f = forms.BooleanField(label='применить ко всем волокнам в кабеле', required=False)

    def __init__(self, *args, **kwargs):
        super(coup_cab_edit_Form, self).__init__(*args, **kwargs)
        own_list = firm.objects.filter(coup=True).values_list('id', 'name').order_by('id')
        self.fields['owner'].choices = [('0', '---')] + [(i[0], i[1]) for i in own_list]

class coup_link_Form(coup_cab_edit_Form):
    sel_cable = forms.ChoiceField(label='тип кабеля', widget=forms.RadioSelect, choices=[])
    """
    phys_len = forms.IntegerField(label='длина кабеля между муфтами (в метрах)', min_value=0, max_value=9999)
    res_len = forms.CharField(label='запас кабеля в муфте (в метрах)', max_length=6, required=False, widget=forms.TextInput(attrs={'size': 11}))
    date_ent = forms.DateField(label='дата ввода в муфту', required=False, widget=SelectDateWidget(months=conf.MONTHS, years=conf.YEARS))
    owner = forms.ChoiceField(label='владелец кабеля', required=False, widget=forms.Select, choices=[])
    """
    def __init__(self, *args, **kwargs):
        super(coup_link_Form, self).__init__(*args, **kwargs)
        self.fields['sel_cable'].choices = Templ_cable.objects.values_list('id', 'name').order_by('capacity', 'name')
    """
        own_list = firm.objects.filter(coup=True).values_list('id', 'name').order_by('id')
        own_list2 = [['0', '---']]
        for ob in own_list:
            own_list2.append([ob[0], ob[1]])
        self.fields['owner'].choices = own_list2
    """

class coup_p_edit_Form(forms.Form):
    valid = forms.BooleanField(required=False)
    int_c_status = forms.ChoiceField(label='тип связи', required=False, widget=forms.RadioSelect, choices=conf.INT_C_STATUS_LIST)
    changed = forms.BooleanField(label='запланированы изменения', required=False)
    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 54}))
    owner = forms.ChoiceField(label='владелец волокна', required=False, widget=forms.Select, choices=[])

    def __init__(self, *args, **kwargs):
        super(coup_p_edit_Form, self).__init__(*args, **kwargs)
        own_list = firm.objects.filter(coup=True).values_list('id', 'name').order_by('id')
        #own_list2 = [['', '---']]
        #for ob in own_list:
        #    own_list2.append([ob[0], ob[1]])
        self.fields['owner'].choices = [('', '---')] + [(i[0], i[1]) for i in own_list]

