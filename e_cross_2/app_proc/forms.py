#

from django import forms

from cross.models import Street
from core.models import engineer
from core.e_config import conf

####################################################################################################


class add_app_Form(forms.Form):
    type_proc = forms.ChoiceField(label='тип операции', widget=forms.Select, choices=conf.TYPE_PROC_LIST)
    street = forms.ChoiceField(label='список улиц', widget=forms.Select, choices=[])
    house_num = forms.CharField(label='здание', max_length=8, widget=forms.TextInput(attrs={'size': 8}))
    dog   = forms.CharField(label='договор', max_length=8, required=False, widget=forms.TextInput(attrs={'size': 11}))
    n_order = forms.CharField(label='ордер', max_length=12, widget=forms.TextInput(attrs={'size': 11}))
    kv    = forms.CharField(label='кв', max_length=6, required=False, widget=forms.TextInput(attrs={'size': 8}))
    fio   = forms.CharField(label='ФИО', max_length=90, required=False, widget=forms.TextInput(attrs={'size': 66}))
    prim  = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 66}))

    def __init__(self, *args, **kwargs):
        super(add_app_Form, self).__init__(*args, **kwargs)
        self.fields['street'].choices = Street.objects.values_list('id', 'name').order_by('name')
        #self.fields['dog'].disabled = True


class edit_app_Form(forms.Form):
    #type_proc = forms.ChoiceField(label='тип операции', widget=forms.Select, choices=conf.TYPE_PROC_LIST)
    street = forms.ChoiceField(label='улица', widget=forms.Select, choices=[])
    house_num = forms.CharField(label='дом', max_length=8, widget=forms.TextInput(attrs={'size': 8}))
    #dog  = forms.CharField(label='договор', max_length=7, widget=forms.TextInput(attrs={'size': 10}))
    kv   = forms.CharField(label='кв', max_length=6, required=False, widget=forms.TextInput(attrs={'size': 8}))
    fio  = forms.CharField(label='ФИО', max_length=90, required=False, widget=forms.TextInput(attrs={'size': 66}))
    prim = forms.CharField(label='примечание', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 66}))
    comment = forms.CharField(label='комментарий ТУ', max_length=190, required=False, widget=forms.TextInput(attrs={'size': 66}))

    def __init__(self, *args, **kwargs):
        super(edit_app_Form, self).__init__(*args, **kwargs)
        self.fields['street'].choices = Street.objects.values_list('id', 'name').order_by('name')


class app_Form(forms.Form):
    comment = forms.CharField(label='комментарий', max_length=350, required=False, widget=forms.TextInput(attrs={'size': 60}))


class app_reject_Form(app_Form):
    reject = forms.ChoiceField(label='причина отказа', widget=forms.Select, choices=conf.APP_REJECT)


class app_delay_Form(app_Form):
    delay = forms.ChoiceField(label='причина откладывания', widget=forms.Select, choices=conf.APP_DELAY)


class app_complete_Form(app_Form):
    dog = forms.CharField(label='договор', max_length=12, required=False, widget=forms.TextInput(attrs={'size': 10}))
    man_install = forms.ChoiceField(label='инсталлятор', widget=forms.Select, choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super(app_complete_Form, self).__init__(*args, **kwargs)
        eng_list2 = list(engineer.objects.values_list('fio', flat=True).order_by('fio'))
        for ob in eng_list2:
            eng_list2[eng_list2.index(ob)] = [ob, ob]
        self.fields['man_install'].choices = eng_list2


class app_find_Form(forms.Form):
    dog = forms.CharField(label='договор: ', max_length=12, widget=forms.TextInput(attrs={'size': 14}))


class n_order_Form(forms.Form):
    n_order = forms.CharField(label='ордер', max_length=12, widget=forms.TextInput(attrs={'size': 14}))

