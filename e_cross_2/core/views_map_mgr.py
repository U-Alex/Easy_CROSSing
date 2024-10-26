#
import datetime
import os
import shutil
import subprocess
import imghdr
import time

from PIL import Image

#from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.shortcuts import render

import deepzoom
from .models import map_slot

from .forms import upl_Form
from core.e_config import conf
from views_ext import ProcessLock as lock

####################################################################################################

@login_required(login_url='/core/login/')
def m_manager(request, m_num):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    f_list = []
    f_exist = False
    f_png = True
    try:
        f_list1 = default_storage.listdir(f'map_1/{m_num}/')[1]
        f_list2 = default_storage.listdir(f'map_2/{m_num}/')[1]
    except:
        return render(request, 'error.html', {'mess': 'невозможно получить список файлов', 'back': 2})

    cut1, cut2 = [], []
    for ob in f_list1:
        cut1.append(ob.rsplit(".", 1)[0])
    for ob in f_list2:
        cut2.append(ob.rsplit(".", 1)[0])
    cut12 = list(set(cut1 + cut2))
    cut12.sort()
    link = subprocess.Popen(['/usr/bin/ls', '-ld', f'{conf.HOME_PATH}{conf.MAP_PATH}{m_num}/map.dzi'],
                            stdout=subprocess.PIPE,
                            shell=False)
    link_out = link.stdout.read().decode("utf-8")
    sym_link = link_out[link_out.rfind('/'):][1:].rsplit(".", 1)[0]

    for ob in cut12:
        f_list.append([f_list1[cut1.index(ob)] if (ob in cut1) else False,
                       f_list2[cut2.index(ob)] if (ob in cut2) else False,
                       True if (sym_link == ob) else False
                       ])
    if request.method == 'POST':
        form = upl_Form(request.POST, request.FILES)
        if form.is_valid():
            upl_file = request.FILES['file']
            url_f = f'map_1/{m_num}/{upl_file.name}'
            if imghdr.what(upl_file) != 'png':
                f_png = False
            elif default_storage.exists(url_f):
                f_exist = True
            else:
                default_storage.save(url_f, upl_file)
                Image.MAX_IMAGE_PIXELS = None
                prev = Image.open(upl_file)
                prev.thumbnail((512, 512))
                prev.save(f'{conf.HOME_PATH}{conf.MAP1_PATH}{m_num}/prev/{upl_file.name}')
                prev.close()
                return HttpResponseRedirect(f'/core/m_manager{m_num}/')

    form = upl_Form()
    pass_on = lock.is_cut()
    map_list = map_slot.objects.all().order_by('num').values_list()

    return render(request, 'serv_map_mgr.html', {'form': form,
                                                 'f_list': f_list,
                                                 'f_exist': f_exist,
                                                 'f_png': f_png,
                                                 'cut': pass_on[0],
                                                 'debug': (pass_on[1], pass_on[2]),
                                                 'm_num': int(m_num),
                                                 'map_list': map_list,
                                                 })


@login_required(login_url='/core/login/')
def m_manager_cut(request, m_num):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1})
    if lock.is_cut()[0]:
        return render(request, 'error.html', {'mess': 'выполняется фоновый процесс', 'back': 1})

    f_name = request.GET.get('f_name', False)
    if not f_name:
        return render(request, 'error.html', {'mess': 'файл не найден', 'back': 1})

    if default_storage.exists(f'map_2/{m_num}/{f_name.rsplit(".", 1)[0]}.dzi'):
        default_storage.delete(f'map_2/{m_num}/{f_name.rsplit(".", 1)[0]}.dzi')
    if default_storage.exists(f'map_2/{m_num}/{f_name.rsplit(".", 1)[0]}_files'):
        shutil.rmtree(f'{conf.HOME_PATH}{m_num.MAP2_PATH}{m_num}/{f_name.rsplit(".", 1)[0]}_files')

    source = f'{conf.HOME_PATH}{conf.MAP1_PATH}{m_num}/{f_name}'
    destination = f'{conf.HOME_PATH}{conf.MAP2_PATH}{m_num}/{f_name.rsplit(".", 1)[0]}.dzi'

    creator = deepzoom.ImageCreator(
        tile_size=256,
        tile_overlap=0,
        tile_format="png",
        image_quality=1,
        resize_filter="bicubic",
    )
    lock.set_map_cut(True, request.user.get_full_name())
    creator.create(source, destination)
    # time.sleep(10)
    lock.set_map_cut(False)

    return HttpResponseRedirect(f'/core/m_manager{m_num}/')


@login_required(login_url='/core/login/')
def m_manager_map_on(request, m_num):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1})
    if lock.is_cut()[0]:
        return render(request, 'error.html', {'mess': 'выполняется фоновый процесс', 'back': 1})

    f_name = request.GET.get('f_name', False)
    if not f_name:
        return render(request, 'error.html', {'mess': 'файл не найден', 'back': 1})

    try:
        os.unlink(f'{conf.HOME_PATH}{conf.MAP_PATH}{m_num}/map.dzi')
        os.unlink(f'{conf.HOME_PATH}{conf.MAP_PATH}{m_num}/map_files')
    except:
        pass
    os.symlink(f'{conf.HOME_PATH}{conf.MAP2_PATH}{m_num}/{f_name}',
               f'{conf.HOME_PATH}{conf.MAP_PATH}{m_num}/map.dzi')
    os.symlink(f'{conf.HOME_PATH}{conf.MAP2_PATH}{m_num}/{f_name.rsplit(".", 1)[0]}_files',
               f'{conf.HOME_PATH}{conf.MAP_PATH}{m_num}/map_files')

    return HttpResponseRedirect(f'/core/m_manager{m_num}/')


@login_required(login_url='/core/login/')
def m_manager_del(request, m_num, ftype=1):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1})
    if lock.is_cut()[0]:
        return render(request, 'error.html', {'mess': 'выполняется фоновый процесс', 'back': 1})

    d_file = request.GET.get('d_file', False)
    if not d_file:
        return render(request, 'error.html', {'mess': 'файл не найден', 'back': 1})

    if default_storage.exists(f'map_{ftype}/{m_num}/{d_file}'):
        default_storage.delete(f'map_{ftype}/{m_num}/{d_file}')
    if default_storage.exists(f'map_{ftype}/{m_num}/{d_file.rsplit(".", 1)[0]}_files'):
        shutil.rmtree(f'{conf.HOME_PATH}{conf.MAP2_PATH}{m_num}/{d_file.rsplit(".", 1)[0]}_files')
    if default_storage.exists(f'map_{ftype}/{m_num}/prev/{d_file}'):
        default_storage.delete(f'map_{ftype}/{m_num}/prev/{d_file}')

    return HttpResponseRedirect('/core/m_manager' + m_num)

# def cut_working():
#     return [True, 'Debug...']
#     proc = subprocess.Popen(['ps -x | grep magick-slicer'], stdout=subprocess.PIPE, shell=True)
#     res = proc.stdout.read().decode("utf-8").split('\n')
#     on = True
#     for ob in res:
#         if 'MagickSlicer-master/magick-slicer.sh' in ob:
#             on = False
#             break
#     return [on, res]

