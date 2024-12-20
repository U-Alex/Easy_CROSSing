#  find__forms

from django import forms

from cross.models import Kvartal, Street
from core.models import COffice

####################################################################################################


class find_Form_map(forms.Form):
    street = forms.ChoiceField(label='улица', widget=forms.Select, choices=[])
    h_num = forms.ChoiceField(label='№', widget=forms.Select, required=False, choices=[])
    agr_list = forms.ChoiceField(label='УА', widget=forms.Select, required=False, choices=[])

    def __init__(self, *args, **kwargs):
        super(find_Form_map, self).__init__(*args, **kwargs)
        self.fields['street'].choices = Street.objects.values_list('id', 'name').order_by('name')
        co_list2 = list(COffice.objects.values_list('name', flat=True).order_by('name'))
        self.fields['agr_list'].choices = [(i, i) for i in co_list2]


class find_Form_kv(forms.Form):
    kvar = forms.ChoiceField(label='квартал', widget=forms.Select(attrs={'class': 'head_kv_form'}), choices=[])

    def __init__(self, *args, **kwargs):
        super(find_Form_kv, self).__init__(*args, **kwargs)
        self.fields['kvar'].choices = Kvartal.objects.values_list('id', 'name').order_by('name')

####################################################################################################


class find_Form_bu(forms.Form):
    street = forms.ChoiceField(label='улица', widget=forms.Select, choices=[])
    house_num = forms.CharField(label='№', max_length=8, required=False, widget=forms.TextInput(attrs={'size': 5}))

    def __init__(self, *args, **kwargs):
        super(find_Form_bu, self).__init__(*args, **kwargs)
        self.fields['street'].choices = Street.objects.values_list('id', 'name').order_by('name')


class find_Form_agr(forms.Form):
    co = forms.ChoiceField(label='агрегация', widget=forms.Select, choices=[])

    def __init__(self, *args, **kwargs):
        super(find_Form_agr, self).__init__(*args, **kwargs)
        co_list2 = list(COffice.objects.exclude(pk=1).values_list('name', flat=True).order_by('name'))
        self.fields['co'].choices = [['all', 'все']] + [(i, i) for i in co_list2]


class find_Form_dev(forms.Form):
    dev_ip = forms.CharField(label='ip', max_length=20, required=False, widget=forms.TextInput(attrs={'size': 14}))
    dev_mac = forms.CharField(label='mac', max_length=20, required=False, widget=forms.TextInput(attrs={'size': 14}))
    dev_sn = forms.CharField(label='sn/inv', max_length=20, required=False, widget=forms.TextInput(attrs={'size': 14}))
    dev_vlan = forms.CharField(label='vlan', max_length=20, required=False, widget=forms.TextInput(attrs={'size': 14}))

####################################################################################################

