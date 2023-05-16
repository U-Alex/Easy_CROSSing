#

from django import forms
from django.forms import ModelForm
from .models import manage_comp
from cross.models import Street
from .models import Templ_locker, Templ_cross, Templ_device, Templ_box, Templ_box_cable, Templ_subunit
from cable.models import Templ_cable, Templ_coupling

####################################################################################################

class n_kvar_Form(forms.Form):
    n_kvar = forms.CharField(label='квартал', max_length=28, widget=forms.TextInput(attrs={'size': 28}))

class n_str_Form(forms.Form):
    n_str = forms.CharField(label='улица', max_length=28, widget=forms.TextInput(attrs={'size': 28}))

class n_bu_Form(forms.Form):
    street = forms.ChoiceField(label='улица', widget=forms.Select, choices=[])
    house_num = forms.CharField(label='№', max_length=6, required=False, widget=forms.TextInput(attrs={'size': 5}))

    def __init__(self, *args, **kwargs):
        super(n_bu_Form, self).__init__(*args, **kwargs)
        self.fields['street'].choices = Street.objects.values_list('id', 'name').order_by('name')

class sprav_upr_Form(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size': 141}))
    info = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 141}))
    class Meta:
        model = manage_comp
        fields = ['name', 'info']

class switch_agr_Form(forms.Form):
    lo_id = forms.IntegerField(label='locker_id', min_value=1)
    agr = forms.ChoiceField(label='УА / УД', widget=forms.RadioSelect, choices=[[1, 'УА'], [0, 'УД']])

class templ_lo_Form(ModelForm):
    #units = forms.IntegerField(label='кол-во мест', min_value=1, max_value=64)
    class Meta:
        model = Templ_locker
        fields = ['name']

class templ_cr_Form(ModelForm):
    name = forms.CharField(label='Имя шаблона', max_length=30)
    ports = forms.IntegerField(label='количество портов', min_value=1, max_value=256)
    #port_t_x = forms.ChoiceField(disabled=1, label='тип порта', widget=forms.Select, choices=[(1, 'x'), (2, 't'), (3, 'tx')], required=False)
    v_col = forms.IntegerField(label='количество портов по вертикали', min_value=1, max_value=256)
    v_row = forms.IntegerField(label='количество портов по горизонтали', min_value=1, max_value=256)
    #v_row = forms.IntegerField(widget=forms.NumberInput(attrs={'readonly':'True'}), min_value=1, max_value=256)
    v_forw_l_r = forms.BooleanField(label='направление нумерации (справа налево (V)/сверху вниз ( ))', required=False)
    ext_p = forms.BooleanField(label='расширяемый кросс (кассета)', required=False)
    units = forms.IntegerField(label='занимаемый объём', min_value=1, max_value=5)
    class Meta:
        model = Templ_cross
        fields = ['name', 'ports', 'v_col', 'v_row', 'v_forw_l_r', 'ext_p', 'units']

class templ_dev_Form(ModelForm):
    #parrent = forms.ChoiceField(label='тип оборудования', choices=[])
    name = forms.CharField(label='Имя шаблона', max_length=30)
    ports = forms.IntegerField(label='количество портов', min_value=1, max_value=128)
    port_alias_list = forms.CharField(label='port_alias_list', max_length=2000, widget=forms.TextInput(attrs={'size': 150}))
    port_t_x_list = forms.CharField(label='port_t_x_list', max_length=2000, widget=forms.TextInput(attrs={'size': 150}))
    port_speed_list = forms.CharField(label='port_speed_list', max_length=2000, widget=forms.TextInput(attrs={'size': 150}))
    units = forms.IntegerField(label='занимаемый объём', min_value=1, max_value=5)
    class Meta:
        model = Templ_device
        fields = ['parrent', 'name', 'ports', 'port_alias_list', 'port_t_x_list', 'port_speed_list', 'units']

class templ_box_Form(ModelForm):
    name = forms.CharField(label='Имя шаблона', max_length=30)
    units = forms.IntegerField(label='объём', min_value=1, max_value=5)
    class Meta:
        model = Templ_box
        fields = ['name', 'units']

class templ_box_cable_Form(ModelForm):
    name = forms.CharField(label='Имя шаблона', max_length=30)
    ports = forms.IntegerField(label='кол-во портов', min_value=1, max_value=50)
    alias_list = forms.CharField(label='алиасы пар', max_length=2000, widget=forms.TextInput(attrs={'size': 151}))
    num_plints = forms.IntegerField(label='кол-во плинтов', min_value=1, max_value=4)
    color_cable = forms.CharField(label='цвет отображения', max_length=30)
    #units = forms.IntegerField(label='объём', min_value=1, max_value=5)
    class Meta:
        model = Templ_box_cable
        fields = ['name', 'ports', 'alias_list', 'num_plints', 'color_cable']#, 'units']

class templ_cab_Form(ModelForm):
    name = forms.CharField(label='Имя шаблона', max_length=36)
    capacity = forms.IntegerField(label='ёмкость', min_value=1, max_value=256)
    modules = forms.IntegerField(label='кол-во модулей', min_value=1, max_value=16)
    mod_capa_list = forms.CharField(label='mod_capa_list', max_length=1000, widget=forms.TextInput(attrs={'size': 150}))
    mod_color_list = forms.CharField(label='mod_color_list', max_length=1000, widget=forms.TextInput(attrs={'size': 150}))
    fiber_colors_list = forms.CharField(label='fiber_colors_list', max_length=2000, widget=forms.TextInput(attrs={'size': 150}))
    class Meta:
        model = Templ_cable
        fields = ['name', 'capacity', 'modules', 'mod_capa_list', 'mod_color_list', 'fiber_colors_list']

class templ_coup_Form(ModelForm):
    class Meta:
        model = Templ_coupling
        fields = ['name']

class templ_su_Form(ModelForm):
    #parrent = forms.ChoiceField(label='тип оборудования', choices=[])
    name = forms.CharField(label='Имя шаблона', max_length=30)

    class Meta:
        model = Templ_subunit
        fields = ['parrent', 'name']

class upl_Form(forms.Form):
    #title = forms.CharField(max_length=50)
    file = forms.FileField()
