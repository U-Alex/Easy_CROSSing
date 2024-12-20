# cable__forms

from django import forms

from cross.models import Street
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
        self.fields['object_owner_list'].choices = [('', '')] + [(i, i) for i in own_list]
        #self.fields['object_owner_list'].disabled = True


class add_Coup_Form(forms.Form):
    name = forms.CharField(label='имя муфты', max_length=40, widget=forms.TextInput(attrs={'size': 51}))
    name_type = forms.ChoiceField(label='тип муфты', widget=forms.RadioSelect, choices=[])
    object_owner = forms.CharField(label='владелец муфты', max_length=60, required=False, widget=forms.TextInput(attrs={'size': 28}))
    object_owner_list = forms.ChoiceField(label='владелец муфты', required=False, widget=forms.Select, choices=[])
    installed = forms.BooleanField(label='установлена', required=False)
    date_ent = forms.DateField(label='дата установки', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    rasp = forms.CharField(label='расположение', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 51}))
    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 51}))
    coord = forms.CharField(label='координаты', max_length=32, required=False, widget=forms.TextInput(attrs={'size': 51}))

    def __init__(self, *args, **kwargs):
        super(add_Coup_Form, self).__init__(*args, **kwargs)
        coup_list = Templ_coupling.objects.values_list('name', flat=True).order_by('name')
        self.fields['name_type'].choices = [(i, i) for i in coup_list]
        own_list = firm.objects.filter(coup=True).values_list('name', flat=True).order_by('name')
        self.fields['object_owner_list'].choices = [('', '')] + [(i, i) for i in own_list]


class edit_Coup_Form(add_Coup_Form):
    change_bu = forms.BooleanField(label='сменить адрес', required=False)
    street = forms.ChoiceField(label='улица', required=False, widget=forms.Select, choices=[], disabled=True)
    house_num = forms.CharField(label='№', max_length=8, required=False, widget=forms.Select, disabled=True)

    def __init__(self, *args, **kwargs):
        super(edit_Coup_Form, self).__init__(*args, **kwargs)
        self.fields['street'].choices = Street.objects.values_list('id', 'name').order_by('name')

####################################################################################################


class coup_cab_edit_Form(forms.Form):
    phys_len = forms.IntegerField(label='длина кабеля между муфтами (в метрах)', min_value=0, max_value=9999)#, required=False)
    res_len = forms.CharField(label='запас кабеля в муфте (в метрах)', max_length=6, required=False, widget=forms.TextInput(attrs={'size': 11}))
    date_ent = forms.DateField(label='дата ввода в муфту', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    owner = forms.ChoiceField(label='владелец кабеля', required=False, widget=forms.Select, choices=[])
    owner_f = forms.BooleanField(label='применить ко всем волокнам в кабеле', required=False)
    prim = forms.CharField(label='примечание', max_length=100, required=False, widget=forms.TextInput(attrs={'size': 54}))

    def __init__(self, *args, **kwargs):
        super(coup_cab_edit_Form, self).__init__(*args, **kwargs)
        own_list = firm.objects.filter(coup=True).values_list('id', 'name').order_by('id')
        self.fields['owner'].choices = [('0', '---')] + [(i[0], i[1]) for i in own_list]


class coup_link_Form(coup_cab_edit_Form):
    sel_cable = forms.ChoiceField(label='тип кабеля', widget=forms.RadioSelect, choices=[])

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
    int_c_status_multi = forms.BooleanField(label='множественное изменение', required=False)
    # int_c_status_e_p = forms.IntegerField(label='конечное волокно', required=False, widget=forms.NumberInput(attrs={'class': 'int_field'}))
    changed = forms.BooleanField(label='запланированы изменения', required=False)
    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 54}))
    owner = forms.ChoiceField(label='владелец волокна', required=False, widget=forms.Select, choices=[])

    def __init__(self, *args, **kwargs):
        super(coup_p_edit_Form, self).__init__(*args, **kwargs)
        own_list = firm.objects.filter(coup=True).values_list('id', 'name').order_by('id')
        self.fields['owner'].choices = [('', '---')] + [(i[0], i[1]) for i in own_list]

