# core__views

import datetime
import time
import requests

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User#, Group#, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#from django.db.models import Avg
from django.shortcuts import render
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt

from .models import History, last_visit, manage_comp
from cross.models import Kvartal, Street, Building
from cross.models import Locker, Cross, Device, Box, Subunit
from cross.models import Cross_ports, Device_ports, Device_ports_v, Box_ports
from core.models import Templ_box_cable
from cable.models import Coupling, Coupling_ports

from .forms import sprav_upr_Form#, n_kvar_Form, n_str_Form, n_bu_Form
from .forms import switch_agr_Form

from core.shared_def import to_his
from core.e_config import conf


####################################################################################################


def index(request):

    return HttpResponseRedirect('/find')


def login(request):

    args = {}
    args.update(csrf(request))
    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        next_url = request.POST.get('next_url')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect(next_url)
        else:
            args['next_url'] = next_url
            args['login_error'] = "user not found"
            #request.session['username'] = 'test_session2'
            return render(request, 'login.html', args)
    else:
        try:
            next_url = request.GET['next']
        except:
            next_url = '/'
        args['next_url'] = next_url
        #print(request.session.get('username'))
        return render(request, 'login.html', args)


def logout(request):

    auth.logout(request)
    return HttpResponseRedirect('/')


####################################################################################################

@login_required(login_url='/core/login/')
def service(request):

    #if not request.user.has_perm("core.can_adm"):
    #    return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 2})

    #perm = Permission.objects.get(codename='can_adm')
    #user_list = User.objects.filter(groups__name__in=['tu','tp','adm']).order_by('id')

    start_date = datetime.datetime.today()-datetime.timedelta(1/24/60*20)
    user_list1 = last_visit.objects.all().order_by('id')
    user_list2 = []
    for ob in user_list1:
        if User.objects.filter(pk=ob.id).exists():
            if ob.date_l_v > start_date:
                user_list2.append([ob, True])
            else:
                user_list2.append([ob, False])
        else:
            ob.delete()

    return render(request, 'service.html', {'user_list': user_list2})#HttpResponseRedirect('ok')


@login_required(login_url='/core/login/')
def service_clean_his(request):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 2})

    last_visit.objects.all().update(prim='')

    return HttpResponseRedirect('/core/service/')

####################################################################################################

@login_required(login_url='/core/login/')
def sprav(request):

    if not request.user.has_perm("core.can_edit_bu"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 1})

    return render(request, 'sprav.html', {'comp_list': manage_comp.objects.all().order_by('name')})


@login_required(login_url='/core/login/')
def sprav_upr(request, upr_id):

    if not request.user.has_perm("core.can_edit_bu"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 1})
    try:
        upr = manage_comp.objects.get(pk=upr_id) if (upr_id != '0') else 0
    except ObjectDoesNotExist:
        upr = 0
        upr_id = '0'
    if request.method == 'POST':
        if upr_id != '0':
            form = sprav_upr_Form(request.POST, instance=upr)
        else:
            form = sprav_upr_Form(request.POST)
        form.save()

        return HttpResponseRedirect('/core/sprav/')
    else:
        form = sprav_upr_Form(instance=upr) if (upr_id != '0') else sprav_upr_Form()

    return render(request, 'sprav_upr.html', {'form': form, 'upr': upr})


@login_required(login_url='/core/login/')
def sprav_upr_del(request, upr_id):

    if not request.user.has_perm("core.can_edit_bu"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 1})
    try:
        upr = manage_comp.objects.get(pk=upr_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 1})

    del_ok = False if Building.objects.filter(info_comp=int(upr.id)).exists() else True
    if request.method == 'POST' and del_ok:
        upr.delete()
        return HttpResponseRedirect('/core/sprav/')

    return render(request, 'sprav_del.html', {'upr': upr,
                                              'del_ok': del_ok,
                                              'obj_list': Building.objects.filter(info_comp=int(upr.id))#.count(),
                                              })

####################################################################################################

@login_required(login_url='/core/login/')
def switch_agr(request):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 2})
    ok = False
    err = False
    if request.method == 'POST':
        form = switch_agr_Form(request.POST)
        if form.is_valid():
            try:
                lo = Locker.objects.get(pk=form.cleaned_data['lo_id'])
                if form.cleaned_data['agr'] == '1':
                    if Locker.objects.filter(agr=True, co=lo.co).exists():
                        err = 'УА уже существует '+str(Locker.objects.filter(agr=True, co=lo.co))
                if (int(lo.agr) != int(form.cleaned_data['agr'])) and not err:
                    lo.agr = int(form.cleaned_data['agr'])
                    lo.save()
                    ok = True
            except:
                err = 'locker не найден'
    else:
        form = switch_agr_Form()

    return render(request, 'serv_switch_agr.html', {'ok': ok, 'form': form, 'err': err})

####################################################################################################

@login_required(login_url='/core/login/')
def show_all_logs(request, u, td):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 3})

    cur_user = {'login': 'Все пользователи'}
    date_30 = datetime.date.today() - datetime.timedelta(int(td))
    #history_all = History.objects.filter(date_rec=datetime.date.today()).order_by('-id')
    history_all = History.objects.filter(time_rec__gt=date_30).order_by('-id')#('-date_rec')
    if u != '0':
        try:
            cur_user = last_visit.objects.get(pk=int(u))
            history_all = history_all.filter(user=cur_user.login)
        except ObjectDoesNotExist:
            return render(request, 'error.html', {'mess': 'нет данных', 'back': 3})

    #his = trans_his(history_all)
    p_list = trans_his(history_all)
    """
    pag = Paginator(his, 32)
    page = request.GET.get('page')
    try:
        p_list = pag.page(page)
    except PageNotAnInteger:
        p_list = pag.page(1)
    except EmptyPage:
        p_list = pag.page(pag.num_pages)
    """
    return render(request, 'serv_show_logs_all.html', {'his': p_list, 'cur_user': cur_user})


@login_required(login_url='/core/login/')
def show_logs(request, o_type, o_id):

    history = History.objects.filter(obj_type=o_type, obj_id=o_id).order_by('-id')
    his = trans_his(history)

    pag = Paginator(his, 32)
    page = request.GET.get('page')
    try:
        p_list = pag.page(page)
    except PageNotAnInteger:
        p_list = pag.page(1)
    except EmptyPage:
        p_list = pag.page(pag.num_pages)

    obj = eval(conf.MODELS_LIST[int(o_type)]).objects.get(pk=o_id)

    return render(request, 'serv_show_logs.html', {'his': p_list, 'obj': obj, 'o_type': o_type})


def trans_his(history):
    his = []
    for ob in history:
        op2 = ''
        if ob.operation1 == 8:
            op2 = conf.OPERATION_1_8[ob.operation2]
        if ob.operation1 == 9:
            op2 = conf.OPERATION_1_9[ob.operation2]
        if ob.operation1 == 10:
            op2 = '('+Templ_box_cable.objects.get(id=ob.operation2).name+')'
        if ob.operation1 == 16:
            op2 = conf.OPERATION_1_16[ob.operation2]

        his.append([ob.user,
                    ob.time_rec,
                    conf.OBJECT_TYPE[ob.obj_type],
                    ob.obj_id,
                    conf.OPERATION_1[ob.operation1],
                    op2,
                    ob.text,
                    ])
    return his


####################################################################################################
