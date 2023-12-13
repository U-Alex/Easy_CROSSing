# core__views_objects
#
# import datetime

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from cross.models import Kvartal, Street, Building, Locker
from cable.models import PW_cont, Coupling
#
from .forms import add_kv_Form, add_st_Form, add_bu_Form
from .forms import del_kv_Form, del_st_Form, del_bu_Form
#
# from core.shared_def import to_his
# from core.e_config import conf


####################################################################################################

@login_required(login_url='/core/login/')
def o_manager(request):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 1})

    mess = False
    add_form_kv, add_form_st, add_form_bu = False, False, False
    del_form_kv, del_form_st, del_form_bu = False, False, False

    if 'form1' in request.POST:
        form = add_kv_Form(request.POST)
        if form.is_valid():
            n_kvar = form.cleaned_data['kv']
            if Kvartal.objects.filter(name=n_kvar).exists():
                mess = f'квартал: {n_kvar} - уже есть'
            else:
                Kvartal.objects.create(name=n_kvar)
                mess = f'квартал: {n_kvar} - добавлено'

    if 'form2' in request.POST:
        form = add_st_Form(request.POST)
        if form.is_valid():
            n_str = form.cleaned_data['st']
            if Street.objects.filter(name=n_str).exists():
                mess = f'улица: {n_str} уже есть'
            else:
                Street.objects.create(parrent=0, name=n_str)
                mess = f'улица: {n_str} добавлено'

    if 'form3' in request.POST:
        form = add_bu_Form(request.POST)
        if form.is_valid():
            sel_str = form.cleaned_data['street']
            str_name = Street.objects.get(pk=sel_str).name
            h_num = form.cleaned_data['h_num']
            double_id = 0
            if form.cleaned_data['double'] and form.cleaned_data['double_id']:
                double_id = int(form.cleaned_data['double_id'])
            if Building.objects.filter(parrent_id=sel_str, house_num=h_num).exists():
                mess = f'здание: {str_name} {h_num} уже есть'
            else:
                Building.objects.create(parrent_id=sel_str, name=str_name, house_num=h_num, double_id=double_id)
                mess = f'здание: {str_name} {h_num} добавлено'

    if 'form4' in request.POST:
        form = del_kv_Form(request.POST)
        if form.is_valid():
            n_kvar = form.cleaned_data['kv']
            del_kv = Kvartal.objects.get(pk=n_kvar)
            if (Building.objects.filter(kvar=n_kvar).exists()) \
            or (PW_cont.objects.filter(parrent_id=n_kvar).exists()):
                mess = f'квартал: {del_kv.name} удалить нельзя, в нем есть объекты'
            else:
                del_kv.delete()
                mess = f'квартал: {del_kv.name} удалён'

    if 'form5' in request.POST:
        form = del_st_Form(request.POST)
        if form.is_valid():
            n_str = form.cleaned_data['st']
            del_st = Street.objects.get(pk=n_str)
            if Building.objects.filter(parrent=n_str).exists():
                mess = f'улицу: {del_st.name} удалить нельзя, в ней есть объекты'
            else:
                del_st.delete()
                mess = f'улица: {del_st.name} удалёна'

    if 'form6' in request.POST:
        form = del_bu_Form(request.POST)
        if form.is_valid():
            n_bu = form.cleaned_data['bu']
            del_bu = Building.objects.get(pk=n_bu)
            if (Locker.objects.filter(parrent=n_bu).exists()) \
            or (Coupling.objects.filter(parrent=n_bu, parr_type=1).exists()):
                mess = f'здание: {del_bu.name} {del_bu.house_num} удалить нельзя, в нем есть объекты'
            else:
                del_bu.delete()
                mess = f'здание: {del_bu.name} {del_bu.house_num} удалено'


    if not add_form_kv: add_form_kv = add_kv_Form()
    if not add_form_st: add_form_st = add_st_Form()
    if not add_form_bu: add_form_bu = add_bu_Form()
    if not del_form_kv: del_form_kv = del_kv_Form()
    if not del_form_st: del_form_st = del_st_Form()
    if not del_form_bu: del_form_bu = del_bu_Form()

    bu_list = Building.objects.exclude(double_id=0)

    return render(request, 'serv_obj_mgr.html', {'forms_add': [add_form_kv, add_form_st, add_form_bu],
                                                 'forms_del': [del_form_kv, del_form_st, del_form_bu],
                                                 'mess': mess,
                                                 'bu_list': bu_list,
                                                 })











