#

import datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
#from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.template.loader import render_to_string
from weasyprint import HTML#, CSS

from .models import Appp
from cross.models import Street, Building
from cross.models import Box, Box_ports, Device_ports
from core.models import History

from .forms import add_app_Form, edit_app_Form, n_order_Form
from .forms import app_reject_Form, app_delay_Form, app_complete_Form, app_find_Form

from core.shared_def import upd_visit, to_his#, from_bgb_gog_rq
from core.e_config import conf
#from .views_ext import nsd_unset_send
from core.views import trans_his

####################################################################################################
####################################################################################################

@login_required(login_url='/core/login/')
def app(request, status=0):

    if not request.user.has_perm("core.can_app_view"):
        return render(request, 'denied.html', {'mess': 'нет прав просмотра заявок', 'back': 2})

    start_date_3 = datetime.date.today() - datetime.timedelta(3)
    start_date_10 = datetime.date.today() - datetime.timedelta(10)
    start_date_60 = datetime.datetime.today() - datetime.timedelta(60)

    if int(status) > 5:
        status = 0
    #if int(status) == 2 or int(status) == 3:
    if int(status) in (2, 3):
        app_l = Appp.objects.filter(app_status=status, date_1__gt=start_date_60).order_by('-date_1')
    else:
        app_l = Appp.objects.filter(app_status=status).order_by('-date_1')

    pag = Paginator(app_l, 33)
    page = request.GET.get('page')
    try:
        app_list = pag.page(page)
    except PageNotAnInteger:
        app_list = pag.page(1)
    except EmptyPage:
        app_list = pag.page(pag.num_pages)

    form_f = app_find_Form()
    return render(request, 'app_'+str(status)+'.html', {'app_list': app_list,
                                                        'form_f': form_f,
                                                        'app_t': True,
                                                        'exp_date_3': start_date_3,
                                                        'exp_date_10': start_date_10,
                                                        'count': app_l.count(),
                                                        'count0': Appp.objects.filter(app_status=0).count(),
                                                        'count4': Appp.objects.filter(app_status=4).count(),
                                                        })


@login_required(login_url='/core/login/')
def app_sort(request, status=0):

    if not request.user.has_perm("core.can_app_view"):
        return render(request, 'denied.html', {'mess': 'нет прав просмотра заявок', 'back': 3})

    start_date_3 = datetime.date.today() - datetime.timedelta(3)
    start_date_10 = datetime.date.today() - datetime.timedelta(10)
    start_date_60 = datetime.datetime.today() - datetime.timedelta(60)

    if int(status) > 5:
        status = 0
    #if int(status) == 2 or int(status) == 3:
    if int(status) in (2, 3):
        app_l = Appp.objects.filter(app_status=status, date_1__gt=start_date_60).order_by('street', 'build', 'kv')
    else:
        app_l = Appp.objects.filter(app_status=status).order_by('street', 'build', 'kv')

    form_f = app_find_Form()
    return render(request, 'app_'+str(status)+'.html', {'app_list': app_l,
                                                        'form_f': form_f,
                                                        'find': True,
                                                        'exp_date_3': start_date_3,
                                                        'exp_date_10': start_date_10,
                                                        'count': app_l.count(),
                                                        'count0': Appp.objects.filter(app_status=0).count(),
                                                        'count4': Appp.objects.filter(app_status=4).count(),
                                                        })

####################################################################################################

@login_required(login_url='/core/login/')
def app_find(request, status):

    upd_visit(request.user, 'a_find')

    if not request.user.has_perm("core.can_app_view"):
        return render(request, 'denied.html', {'mess': 'нет прав просмотра заявок', 'back': 3})

    if request.method == 'POST':
        form_f = app_find_Form(request.POST)
        dog = form_f.data['dog'].strip()
        if len(dog) > 1:
            dog_list = Box_ports.objects.filter(dogovor=dog)
            dog_list_his = Box_ports.objects.filter(his_dogovor=dog)
            app_f = Appp.objects.filter(Q(dogovor=dog) | Q(n_order=dog)).values().order_by('-date_1')
            for ob in app_f:
                ob['color_app'] = conf.COLOR_APP[ob['app_status']]

            return render(request, 'app_find.html', {'app_find': app_f,
                                                     'dog_list': dog_list,
                                                     'dog_list_his': dog_list_his,
                                                     'color': conf.COLOR_CROSS,
                                                     'form_f': form_f,
                                                     'find': True,
                                                     })

    return HttpResponseRedirect('/app/status='+str(status))


####################################################################################################

@csrf_exempt
def from_bgb(request):

    try:
        dog = Box_ports.objects.get(pk=request.GET['dog_id']).dogovor
        result = from_bgb_gog_rq(dog)
        c_par = result[0]
        c_tv = result[1]
    except:
        c_par = False
        c_tv = False

    return render(request, 'from_bgb.html', {'c_par': c_par, 'c_tv': c_tv})


####################################################################################################

@login_required(login_url='/core/login/')
def add_app(request):

    upd_visit(request.user, 'a_add')

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 2,
                                               'next_url': '/app/add_app/'
                                               })

    if request.method == 'POST':
        form = add_app_Form(request.POST)
        if form.is_valid():
            type_proc = int(form.cleaned_data['type_proc'])
            #проверка на задвоение
            #if Appp.objects.filter(type_proc=form.cleaned_data['type_proc'], dogovor=form.cleaned_data['dog']).filter(app_status__in=[0,1,4]).count() != 0:
            #    return HttpResponseRedirect('/app/status=0/')
            if Appp.objects.filter(n_order=form.cleaned_data['n_order']).filter(app_status__in=[0, 1, 4]).count() != 0:
                return render(request, 'error.html', {'mess': 'заявка с таким номером ордера уже есть',
                                                      'back': 0,
                                                      'next_url': '/app/status%3D0/'
                                                      })

            str_name = Street.objects.get(pk=form.cleaned_data['street']).name

            n_app = Appp.objects.create(type_proc=type_proc,
                                        dogovor='0' if type_proc == 0 else form.cleaned_data['dog'],
                                        n_order=form.cleaned_data['n_order'],
                                        street=str_name,
                                        build=form.cleaned_data['house_num'].upper(),
                                        kv=form.cleaned_data['kv'],
                                        fio=form.cleaned_data['fio'],
                                        prim=form.cleaned_data['prim'],
                                        )

            return HttpResponseRedirect('/app/status=0/')

    else:
        form = add_app_Form()

    return render(request, 'add_app.html', {'form': form})


####################################################################################################

@login_required(login_url='/core/login/')
def edit(request, app_id):

    upd_visit(request.user, 'a_edit')

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 2,
                                               'next_url': '/app/edit='+app_id+'/'
                                               })

    app = Appp.objects.get(pk=app_id)

    if request.method == 'POST':
        form = edit_app_Form(request.POST)
        if form.is_valid() and app.app_status == 0:
            change = False
            if Street.objects.get(pk=form.cleaned_data['street']).name != '----':
                change = True
                app.street = Street.objects.get(pk=form.cleaned_data['street']).name
            if form.cleaned_data['house_num'] != app.build:
                change = True
                app.build = form.cleaned_data['house_num']
            if form.cleaned_data['kv'] != app.kv:
                change = True
                app.kv = form.cleaned_data['kv']
            if form.cleaned_data['fio'] != app.fio:
                change = True
                app.fio = form.cleaned_data['fio']
            if form.cleaned_data['prim'] != app.prim:
                change = True
                app.prim = form.cleaned_data['prim']
            if form.cleaned_data['comment'] != app.comment:
                change = True
                app.comment = form.cleaned_data['comment']

            if change:
                app.save()

            return HttpResponseRedirect('/app/status=0/')

        if form.is_valid() and app.app_status == 1:
            app.comment = form.cleaned_data['comment']
            app.save()

            return HttpResponseRedirect('/app/status=1/')

    else:
        form = edit_app_Form(initial={'dog': app.dogovor,
                                      'house_num': app.build,
                                      'kv': app.kv,
                                      'fio': app.fio,
                                      'prim': app.prim,
                                      'comment': app.comment
                                      })

    return render(request, 'app_edit.html', {'app_edit': app, 'form': form})


####################################################################################################

@login_required(login_url='/core/login/')
def app_install(request, app_id, box_p_id=0):

    upd_visit(request.user, 'a_inst')

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 2,
                                               'next_url': '/app/install='+app_id+'/'
                                               })
    #title = False
    bron = False    #есть бронь на кроссе
    box_list = []
    #old_kv_list = [] ######################
    app = Appp.objects.get(pk=app_id)
    cur_status = app.app_status
    if cur_status in [0, 1, 4]:
        title = 'ор: '+app.n_order
        dog_list = Box_ports.objects.filter(dogovor=app.n_order)
    else:
        title = 'дог: '+app.dogovor
        dog_list = Box_ports.objects.filter(dogovor=app.dogovor)

    accept = False if (cur_status == 3) else True   #разрешить бронирование, если не отказано
    try:
        bu = Building.objects.get(name=app.street, house_num=app.build)
        box_list = Box.objects.filter(parrent__parrent_id=bu.id).order_by('parrent_id', 'name', 'num')
        #old_kv_list = Box_ports.objects.filter(parrent__parrent__parrent_id=bu.id).filter(his_ab_kv=app.kv) ######################
    except ObjectDoesNotExist:
        bu = 0

    if len(dog_list) != 1:
        accept = False
    for ob in dog_list:
        if ob.int_c_status in [1, 3]:
            accept = False
        if ob.int_c_status == 2:
            bron = True

    if request.method == 'POST' and accept:
        app.app_status = 1
        app.box_port = box_p_id
        app.man_oper = request.user.get_full_name()
        app.date_2 = datetime.datetime.now()
        app.resource = res_for_bil(box_p_id)+' || ор: '+app.n_order
        app.save()

        return HttpResponseRedirect('/app/install='+str(app.id))
#
    dog_list_his = Box_ports.objects.filter(his_dogovor=app.dogovor)        #.sort_by#############
    box = []
    kv_exists = []                                          #номера квартиры из заявки найдены на других ресурсах
    if len(box_list) != 0:
        for box_ob in box_list:
            p_count = 0
            box_ob_p = Box_ports.objects.filter(parrent_id=box_ob.id).order_by('num')
            box_p_v = []
            col = 0
            while col < box_ob_p.count():
                col += 1
                p_count += 1
                curr_p = box_ob_p.get(num=p_count)
                plint = curr_p.p_alias[:1]
                if not plint.isdigit():
                    plint = '0'
                pair = curr_p.p_alias[3:-1]
                app_kv = app.kv.split('_')[0]               #отрезал другие линии
                his_kv = curr_p.his_ab_kv.split('_')[0]     #отрезал другие линии
                box_p_v.append([curr_p.id,
                                pair,
                                curr_p.int_c_status,
                                curr_p.p_valid,
                                conf.COLOR_CROSS[curr_p.int_c_status],
                                conf.COLOR_PLINT[int(plint)],
                                True if (app_kv == his_kv and app.kv != '') else False,
                                True if (curr_p.up_status in (1, 3)) else False,
                                str(curr_p.dogovor),
                                ' кв:'+str(curr_p.ab_kv) if curr_p.ab_kv != '' else '',
                                str(curr_p.his_dogovor),
                                ' кв:'+str(curr_p.his_ab_kv) if curr_p.his_ab_kv != '' else '',
                                curr_p.date_del #if curr_p.his_dogovor != '' or curr_p.his_ab_kv != '' else ''
                                ])
                if app_kv == curr_p.ab_kv.split('_')[0]:
                    kv_exists.append(curr_p)
            s_area = False                  #проверка зоны действия
            s_a1 = box_ob.serv_area.split(',')
            for ob1 in s_a1:
                if app.kv == ob1 and app.kv != '':
                    s_area = True
                    break
                else:
                    app_kv = app.kv.split('_')[0]               #отрезал другие линии
                    if app_kv.isdigit():
                        ob2 = ob1.split('-')
                        if len(ob2) == 2:
                            if ob2[0].isdigit() and ob2[1].isdigit():
                                if int(app_kv) >= int(ob2[0]) and int(app_kv) <= int(ob2[1]):
                                    s_area = True
                                    break
            
            box.append({'parrent_id': box_ob.parrent_id,
                        'id': box_ob.id,
                        'name': box_ob.name,
                        'num': box_ob.num,
                        'name_type': box_ob.name_type,
                        'box_p': box_p_v,
                        's_area': s_area,
                        'lo_name': box_ob.parrent.name,
                        })

    return render(request, 'app_install.html', {'app': app,
                                                'dog_list': dog_list,
                                                'dog_list_his': dog_list_his,
                                                'color': conf.COLOR_CROSS,
                                                'bu': bu,
                                                'box': box,
                                                #'old_kv_list': old_kv_list, #deprecated
                                                'form1': app_reject_Form(),
                                                'form2': app_delay_Form(),
                                                'form3': app_complete_Form(),
                                                'accept': accept,
                                                'bron': bron,
                                                'form_f': app_find_Form(),
                                                'title': title,
                                                'kv_exists': kv_exists,
                                                })


####################################################################################################

def res_for_bil(p_id):

    box_p = Box_ports.objects.get(pk=p_id)
    dev_p = Device_ports.objects.get(pk=box_p.up_device_id)

    lite = ''
    if len(box_p.parrent.parrent.rasp) > 0 or len(box_p.parrent.parrent.prim) > 0 or len(box_p.parrent.parrent.cab_door) > 0:
        lite += 'шк: '
        lite += box_p.parrent.parrent.rasp+', ' if len(box_p.parrent.parrent.rasp) > 0 else ''
        lite += box_p.parrent.parrent.prim+', ' if len(box_p.parrent.parrent.prim) > 0 else ''
        if len(box_p.parrent.parrent.cab_door) > 0:
            if conf.KEY_DOOR_TYPE.index(box_p.parrent.parrent.cab_door) == 1:
                lite += 'ключ: '+box_p.parrent.parrent.cab_key+', '
            else:
                lite += 'ключ: '+box_p.parrent.parrent.cab_door+', '
        lite += ' || '
    lite += 'ком: '+dev_p.parrent.name
    lite += ' ('+str(dev_p.parrent.ip_addr)+')' if (dev_p.parrent.ip_addr is not None) else ''
    lite += ' порт: '+str(dev_p.num)+' || '
    if box_p.parrent.name != '0':
        lite += 'крт: '+box_p.parrent.name+'-'+box_p.parrent.num+'-'+box_p.p_alias+', '
        lite += 'эт: '+box_p.parrent.floor+', под: '+box_p.parrent.name
        lite += ' ('+box_p.parrent.prim+')' if len(box_p.parrent.prim) > 0 else ''
    else:
        lite += 'крт: напрямую, '

    prim = box_p.ab_prim
    if len(prim) > 3:
        if prim.find('.~') != -1:
            prim1 = prim[:prim.find('{')]
            prim2 = prim[prim.find('{'):prim.find('}')]
            prim3 = prim[prim.find('.~'):]
            lite += ' || прим: '+prim1
            #if prim.find('.~') != -1:
            lite += ' снять с '+prim2[1:]
            lite += prim3[2:]
        else:
            lite += ' || прим: '+prim

    return lite


####################################################################################################

@login_required(login_url='/core/login/')
def app_reject(request, app_id):

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/app/status%3D0/'
                                               })

    bron = False
    app = Appp.objects.get(pk=app_id)
    dog_list = Box_ports.objects.filter(dogovor=app.dogovor)
    for ob in dog_list:
        if ob.int_c_status == 2:
            bron = True

    if not bron and request.method == 'POST':
        form = app_reject_Form(request.POST)
        if form.data['reject'] != '0':
            app.app_status = 3
            app.box_port = 0
            app.man_oper = request.user.username
            app.date_2 = datetime.datetime.now()
            app.comment = form.data['comment']
            app.resource = ''
            app.pause_type = conf.APP_REJECT_LIST[int(form.data['reject'])]
            app.save()
            return HttpResponseRedirect('/app/status=0')

        else:
            form = app_reject_Form(initial={'comment': form.data['comment']})
    else:
        form = app_reject_Form()

    return render(request, 'comment.html', {'app': app, 'form': form})


@login_required(login_url='/core/login/')
def app_delay(request, app_id):

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/app/status%3D0/'
                                               })

    bron = False
    app = Appp.objects.get(pk=app_id)
    dog_list = Box_ports.objects.filter(dogovor=app.dogovor)
    for ob in dog_list:
        if ob.int_c_status == 2:
            bron = True

    if not bron and request.method == 'POST':
        form = app_delay_Form(request.POST)
        if form.data['delay'] != '0':
            app.app_status = 4
            app.box_port = 0
            app.man_oper = request.user.username
            app.date_2 = datetime.datetime.now()
            app.comment = form.data['comment']
            app.resource = ''
            app.pause_type = conf.APP_DELAY_LIST[int(form.data['delay'])]
            app.save()
            #to_bill
            return HttpResponseRedirect('/app/status=0')

        else:
            form = app_delay_Form(initial={'comment': form.data['comment']})
    else:
        form = app_delay_Form()

    return render(request, 'comment.html', {'app': app, 'form': form})


####################################################################################################

@login_required(login_url='/core/login/')
def to_inbox(request, app_id):

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/app/status%3D0/'
                                               })

    bron = False
    app = Appp.objects.get(pk=app_id)
    dog_list = Box_ports.objects.filter(dogovor=app.dogovor)
    for ob in dog_list:
        if ob.int_c_status == 2:
            bron = True
    if not bron:
        app.app_status = 0
        app.box_port = 0
        app.resource = ''
        app.pause_type = ''
        app.save()

        return HttpResponseRedirect('/app/status=0')

    return HttpResponseRedirect('/app/install='+str(app.id))


@login_required(login_url='/core/login/')
def app_complete(request, app_id):

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/app/status%3D0/'
                                               })

    app = Appp.objects.get(pk=app_id)

    accept = False if (app.app_status != 1) else True
    dog_list = Box_ports.objects.filter(dogovor=app.n_order)#dog_list = Box_ports.objects.filter(dogovor=app.dogovor)    ##
    if len(dog_list) != 1:
        accept = False
    for ob in dog_list:
        if ob.int_c_status == 1 or ob.int_c_status == 3:
            accept = False

    if accept and request.method == 'POST':
        form = app_complete_Form(request.POST)
        #if len(form.data['dog']) > 5:
        f_dog = form.data['dog'].strip()
        if (len(f_dog) > 3) and (len(f_dog) < 8) and f_dog.isdigit():
            app.app_status = 2
            app.man_install = form.data['man_install']
            app.date_3 = datetime.datetime.now()
            app.comment = form.data['comment']
            app.dogovor = f_dog

            box_p = Box_ports.objects.get(pk=app.box_port)
            with transaction.atomic():
                if box_p.int_c_status == 2:
                    box_p.int_c_status = 1
                    box_p.dogovor = f_dog
                    #box_p.changed = False
                else:
                    return render(request, 'error.html', {'mess': 'нет брони на кроссе', 'back': 1})
                if box_p.up_status == 2:
                    dev_p = Device_ports.objects.get(pk=box_p.up_device_id)
                    dev_p.int_c_status = 1
                    box_p.up_status = 1
                    dev_p.save()
                    to_his([request.user, 6, dev_p.id, 9, 2, 'app.0; УД: '+dev_p.parrent.parrent.name+'; комм: '+dev_p.parrent.name+'; п: '+str(dev_p.num)])
                box_p.save()
                to_his([request.user, 7, box_p.id, 9, 0, 'app.0; УД: '+box_p.parrent.parrent.name+'; крт: '+box_p.parrent.name+'-'+box_p.parrent.num+'-'+str(box_p.p_alias)+'; dog: '+f_dog])
                app.save()

            return HttpResponseRedirect('/app/status=1')

    else:
        form = app_complete_Form(initial={'dog': (app.dogovor if app.dogovor != '0' else '')})

    return render(request, 'comment.html', {'app': app, 'form': form})


@login_required(login_url='/core/login/')
def app_check(request, app_id, check):

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/app/status%3D0/'
                                               })

    app = Appp.objects.get(pk=app_id)
    cur_status = app.app_status
    if int(check) and cur_status == 2:
        app.app_status = 5
        app.save()
    elif not int(check) and cur_status == 5:
        app.app_status = 2
        app.save()

    return HttpResponseRedirect('/app/status='+str(cur_status))


####################################################################################################

@login_required(login_url='/core/login/')
def app_remove(request, app_id):

    upd_visit(request.user, 'a_rem')

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/app/status%3D0/'
                                               })
    app = Appp.objects.get(pk=app_id)
    dog_list_his = Box_ports.objects.filter(his_dogovor=app.dogovor)
    dog_list = Box_ports.objects.filter(dogovor=app.dogovor)

    act = True if (len(dog_list.filter(int_c_status__in=[1, 3])) == 1) else False    #только 1 активная кроссировка для договора

    kv = False
    bu_b_p = False
    if act:
        cur_b_p = dog_list.first()
        if app.kv != cur_b_p.ab_kv:
            kv = True
        else:
            bu_id = cur_b_p.parrent.parrent.parrent_id
            bu_b_p = Box_ports.objects.filter(parrent__parrent__parrent_id = bu_id).filter(int_c_status = 2, ab_kv = app.kv)
            #print(bu_b_p)
    
    history_nsd = History.objects.filter(user='-NSD-', obj_id=app_id).order_by('-id')#('-date_rec')
    his = trans_his(history_nsd)

    return render(request, 'app_remove.html', {'app': app,
                                               'dog_list': dog_list,
                                               'dog_list_his': dog_list_his,
                                               'color': conf.COLOR_CROSS,
                                               'act': act,
                                               'kv': kv,
                                               'form_f': app_find_Form(),
                                               'his': his,
                                               'bu_b_p': bu_b_p,        #порты - бронь + квартира из заявки
                                               })


####################################################################################################

@login_required(login_url='/core/login/')
def app_reject2(request, app_id):

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/app/status%3D0/'
                                               })

    app = Appp.objects.get(pk=app_id)

    if int(request.POST['reject']) and app.type_proc == 1 and app.app_status == 0:
        app.app_status = 3
        #app.box_port = 0
        app.man_oper = request.user.username
        app.date_2 = datetime.datetime.now()
        #app.resource = ''
        #app.pause_type = conf.APP_REJECT_LIST[int(request.POST['reject'])]
        app.pause_type = conf.APP_REJECT_LIST2[int(request.POST['reject'])]
        app.save()

        return HttpResponseRedirect('/app/status=0')

    return HttpResponseRedirect('/app/remove='+str(app.id))


@login_required(login_url='/core/login/')
def app_complete2(request, app_id):

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/app/status%3D0/'
                                               })
    app = Appp.objects.get(pk=app_id)
    dog_list = Box_ports.objects.filter(dogovor=app.dogovor)
    act = True if (len(dog_list.filter(int_c_status__in=[1, 3])) == 1) else False    #только 1 активная кроссировка для договора

    if act and app.type_proc == 1 and app.app_status == 0:

        app.app_status = 2
        app.man_oper = request.user.username
        app.date_2 = datetime.datetime.now()

        box_p = dog_list.first()
        app.box_port = box_p.id

        with transaction.atomic():
            box_p.int_c_status = 0
            box_p.his_dogovor = box_p.dogovor
            box_p.his_ab_kv = app.kv if (app.kv != '') else box_p.ab_kv
            box_p.his_ab_fio = app.fio if (app.fio != '') else box_p.ab_fio
            box_p.his_ab_prim = box_p.ab_prim
            box_p.dogovor = ''
            box_p.ab_kv = ''
            box_p.ab_fio = ''
            box_p.ab_prim = ''
            box_p.date_del = datetime.datetime.now()
            #box_p.changed = True

            box_p.save()
            to_his([request.user, 7, box_p.id, 8, 0, 'app.1; УД: '+box_p.parrent.parrent.name+'; крт: '+box_p.parrent.name+'-'+box_p.parrent.num+'-'+str(box_p.p_alias)])
        
        app.save()
        
        ##nsd_unset_send(app.id, box_p.id)
        #if not nsd_unset_send(app.id):
        #    return render(request, 'error.html', {'mess': 'отправка не удалась', 'back': 1})
        
        #return HttpResponseRedirect('/app/status=0')
        ##return HttpResponseRedirect('/app/gen_pdf_1='+app_id)

    return HttpResponseRedirect('/app/remove='+str(app.id))


####################################################################################################

def gen_pdf_0(request, app_id):

    app = Appp.objects.get(pk=app_id)
    box_p = False
    b_p_prim = False
    dev_p = False
    if app.box_port != 0:
        box_p = Box_ports.objects.get(pk=app.box_port)
        prim = box_p.ab_prim
        if len(prim) > 3:
            #if prim.find('п:{') != -1:
            if prim.find('.~') != -1:
                prim1 = prim[:prim.find('{')]
                prim2 = prim[prim.find('{'):prim.find('}')]
                prim3 = prim[prim.find('.~'):]
                b_p_prim = prim1+' снять с '+prim2[1:]+prim3[2:]
            else:
                b_p_prim = prim

        if box_p.up_status != 0:
            dev_p = Device_ports.objects.get(pk=box_p.up_device_id)

    html_string = render_to_string('pdf_0.html', {'app': app,
                                                  'box_p': box_p,
                                                  'dev_p': dev_p,
                                                  'b_p_prim': b_p_prim,
                                                  })#.encode('utf-8')
    f_name = 'SET_'+app.n_order[5:]+'.pdf'
    #f_name = str(app.id)+'_'+str(app.type_proc)+'.pdf'

    #html = HTML(string=html_string, encoding='utf-8')
    #pdfkit.from_string(html_string, f_name)
    #pdf = open(f_name)
    #result = html.write_pdf()
    result = HTML(string=html_string).write_pdf()

    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename='+f_name
    response['Content-Transfer-Encoding'] = 'binary'

    response.write(result)
    #with tempfile.NamedTemporaryFile(delete=True) as output:
    #    output.write(result)
    #    output.flush()
    #    output = open(output.name, 'r')
    #    response.write(output.read())
    #pdf.close()
    #os.remove(f_name)

    return response

###############################

def gen_pdf_1(request, app_id):

    app = Appp.objects.get(pk=app_id)
    box_p = False
    #b_p_prim = False
    dev_p = False
    if app.box_port != 0:
        box_p = Box_ports.objects.get(pk=app.box_port)
        """
        prim = box_p.ab_prim
        if len(prim) > 3:
            if prim.find('п:{') != -1:
                prim1 = prim[:prim.find('{')]
                prim2 = prim[prim.find('{'):prim.find('}')]
                prim3 = prim[prim.find('.  /'):]
                b_p_prim = prim1+' снять с '+prim2[1:]+prim3[2:]
            else:
                b_p_prim = prim
        """
        if box_p.up_status != 0:
            dev_p = Device_ports.objects.get(pk=box_p.up_device_id)

    html_string = render_to_string('pdf_1.html', {'app': app,
                                                  'box_p': box_p,
                                                  'dev_p': dev_p,
                                                  #'b_p_prim': b_p_prim,
                                                  })#.encode('utf-8')

    result = HTML(string=html_string).write_pdf()

    #f_name = str(app.id)+'_'+str(app.type_proc)+'.pdf'
    f_name = 'REM_'+app.n_order[4:]+'.pdf'

    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename='+f_name
    response['Content-Transfer-Encoding'] = 'binary'

    response.write(result)
    #with tempfile.NamedTemporaryFile(delete=True) as output:
    #    output.write(result)
    #    output.flush()
    #    output = open(output.name, 'r')
    #    response.write(output.read())

    return response

###############################

def gen_pdf_2(request, box_p_id):

    if not request.user.has_perm("core.can_app_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 2,
                                               'next_url': '/app/gen_pdf_2='+box_p_id
                                               })

    box_p = Box_ports.objects.get(pk=box_p_id)
    dev_p = False
    if box_p.up_status != 0:
        dev_p = Device_ports.objects.get(pk=box_p.up_device_id)

    if request.method == 'POST':
        form = n_order_Form(request.POST)
        if form.is_valid():
            n_order = form.cleaned_data['n_order']
            html_string = render_to_string('pdf_2.html', {'app': n_order,
                                                          'box_p': box_p,
                                                          'dev_p': dev_p,
                                                          })#.encode('utf-8')
            result = HTML(string=html_string).write_pdf()

            #f_name = 'REM_'+box_p.his_dogovor+'_b.pdf'
            f_name = 'REM_'+n_order[4:]+'.pdf'
            response = HttpResponse(content_type='application/pdf;')
            response['Content-Disposition'] = 'inline; filename='+f_name
            response['Content-Transfer-Encoding'] = 'binary'
            response.write(result)

            return response
    else:
        form = n_order_Form()

    return render(request, 'n_order.html', {'box_p': box_p, 'form': form})


####################################################################################################

@login_required(login_url='/core/login/')
def show_logs_nsd(request, td):

    if not request.user.has_perm("core.can_app_view"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 3})
    
    t_date = datetime.date.today() - datetime.timedelta(int(td))
    history_nsd = History.objects.filter(time_rec__gt=t_date, user='-NSD-').order_by('-id')#('-date_rec')
    his = trans_his(history_nsd)
    for ob in his:
        #try
        if conf.OPERATION_1_16.index(ob[5]) in [1, 2, 3]:
            ob[2] = 'снятие'
        else:
            ob[2] = ''

    pag = Paginator(his, 30)
    page = request.GET.get('page')
    try:
        p_list = pag.page(page)
    except PageNotAnInteger:
        p_list = pag.page(1)
    except EmptyPage:
        p_list = pag.page(pag.num_pages)

    return render(request, 'app_logs_nsd.html', {'his': p_list})


####################################################################################################
