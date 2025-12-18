# statist__views_storage

import datetime

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt

from cross.models import Building
# from cross.models import Locker, Device, Box, Subunit
# from cross.models import Cross_ports, Device_ports, Box_ports
# from cross.models import Templ_device
# from cable.models import PW_cont, Coupling, Coupling_ports
# from core.models import last_visit, Energy_type, Subunit_type, History, Templ_subunit
from .forms import upl_Form

from core.e_config import conf

####################################################################################################


@login_required(login_url='/core/login/')
def bu_input_card(request, bu_id):

    try:
        bu = Building.objects.get(pk=bu_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    f_list = []
    f_exist = False

    url = f"input_card/{bu.id}/"
    try:
        f_list = default_storage.listdir(url)[1]
        f_list.sort()
    except FileNotFoundError:
        pass

    if request.method == 'POST':
        if not request.user.has_perm("core.can_adm"):
            return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 0})

        form = upl_Form(request.POST, request.FILES)
        if form.is_valid():
            upl_file = request.FILES['file']
            url_f = f'{url}{upl_file.name}'
            if default_storage.exists(url_f):
                f_exist = True
            else:
                path = default_storage.save(url_f, upl_file)

                return HttpResponseRedirect(f'/statist/bu_input_card={bu_id}/')

    form = upl_Form()

    return render(request, 'bu_input_card.html', {'bu': bu,
                                           'url': url,
                                           'form': form,
                                           'f_list': f_list,
                                           'f_exist': f_exist
                                           })


@login_required(login_url='/core/login/')
def bu_input_card_del(request, bu_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1})

    try:
        bu = Building.objects.get(pk=bu_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    url = f'input_card/{bu.id}/'

    if request.method == 'POST':
        d_file = request.POST['d_file']
        if default_storage.exists(url+d_file):
            default_storage.delete(url+d_file)
        return HttpResponseRedirect(f'/statist/bu_input_card={bu.id}/')

    d_file = request.GET['d_file']

    return render(request, 'bu_input_card_del.html', {'bu': bu, 'd_file': d_file})

####################################################################################################


@login_required(login_url='/core/login/')
def bu_doc(request, bu_id):

    try:
        bu = Building.objects.get(pk=bu_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    f_list = []
    f_exist = False

    url = f"doc/{bu.id}/"
    try:
        f_list = default_storage.listdir(url)[1]
        f_list.sort()
    except FileNotFoundError:
        pass

    if request.method == 'POST':
        if not request.user.has_perm("core.can_adm"):
            return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 0})

        form = upl_Form(request.POST, request.FILES)
        if form.is_valid():
            upl_file = request.FILES['file']
            url_f = f'{url}{upl_file.name}'
            if default_storage.exists(url_f):
                f_exist = True
            else:
                path = default_storage.save(url_f, upl_file)
                return HttpResponseRedirect(f'/statist/bu_doc={bu_id}/')

    form = upl_Form()

    return render(request, 'bu_doc.html', {'bu': bu,
                                           'url': url,
                                           'form': form,
                                           'f_list': f_list,
                                           'f_exist': f_exist
                                           })


@login_required(login_url='/core/login/')
def bu_doc_del(request, bu_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1})

    try:
        bu = Building.objects.get(pk=bu_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    url = f'doc/{bu.id}/'

    if request.method == 'POST':
        d_file = request.POST['d_file']
        if default_storage.exists(url+d_file):
            default_storage.delete(url+d_file)
        return HttpResponseRedirect(f'/statist/bu_doc={bu.id}/')

    d_file = request.GET['d_file']

    return render(request, 'bu_doc_del.html', {'bu': bu, 'd_file': d_file})

####################################################################################################
