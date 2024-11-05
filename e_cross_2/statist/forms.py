#

from django import forms

####################################################################################################


class upl_Form(forms.Form):
    # title = forms.CharField(max_length=50)
    file = forms.FileField()


class stat4_Form(forms.Form):
    dog_filter = forms.ChoiceField(label='фильтр по договору', required=False, widget=forms.Select, choices=[])

    def __init__(self, *args, **kwargs):
        super(stat4_Form, self).__init__(*args, **kwargs)
        self.fields['dog_filter'].choices = [('all', 'все'), ('0', '0xxxxx'), ('1', '1xxxxx'), ('2', '2xxxxx'), ('3', '3xxxxx'), ('8', '8xxxxx'), ('9', '9xxxxx')]

