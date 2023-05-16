#

from django import forms

#from kpp.models import Subunit_type
#from kpp.shared_conf import conf

####################################################################################################

class upl_Form(forms.Form):
    #title = forms.CharField(max_length=50)
    file = forms.FileField()

#class ext_date_1_Form(forms.Form):
#    #date_1 = forms.DateField(label='дата', required=False, widget=SelectDateWidget(months=conf.MONTHS, years=conf.YEARS))
#    date_m = forms.ChoiceField(label='месяц', widget=forms.Select, choices=m_list)
#    date_y = forms.ChoiceField(label='год', widget=forms.Select, choices=y_list)

class stat4_Form(forms.Form):
    dog_filter = forms.ChoiceField(label='фильтр по договору', required=False, widget=forms.Select, choices=[])

    def __init__(self, *args, **kwargs):
        super(stat4_Form, self).__init__(*args, **kwargs)
        self.fields['dog_filter'].choices = [('all', 'все'), ('0', '0xxxxx'), ('1', '1xxxxx'), ('2', '2xxxxx'), ('3', '3xxxxx'), ('8', '8xxxxx'), ('9', '9xxxxx')]
"""
class stat_su_Form(forms.Form):
    su_filter = forms.ChoiceField(label='фильтр по типу устройства', required=False, widget=forms.Select, choices=[])

    def __init__(self, *args, **kwargs):
        super(stat_su_Form, self).__init__(*args, **kwargs)
        self.fields['su_filter'].choices = Subunit_type.objects.values_list('id', 'name').order_by('id')#conf.SUBUNIT_TYPE


class tb_Form(forms.Form):
    #tbtheme = forms.ChoiceField(required=False, widget=forms.Select, choices=[])
    tbtext = forms.CharField(widget=forms.Textarea(attrs={'cols': 161, 'rows': 41}))

    #def __init__(self, *args, **kwargs):
    #    super(tb_Form, self).__init__(*args, **kwargs)
    #    self.fields['tbtheme'].choices = [('0', 'пожелания'), ('1', 'претензии')]
"""
