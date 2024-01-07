#

import os
import shutil
import subprocess
import imghdr
from PIL import Image

#from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.shortcuts import render

from .models import map_slot

from .forms import upl_Form
from core.e_config import conf

####################################################################################################

@login_required(login_url='/core/login/')
def m_manager(request, m_num):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 2})

    f_list = []
    f_exist = False
    num = str(m_num) + '/'
    try:
        f_list1 = default_storage.listdir('map_1/'+num)[1]
        f_list2 = default_storage.listdir('map_2/'+num)[1]
    except Exception as error:
        #print(error)
        return render(request, 'error.html', {'mess': 'невозможно получить список файлов', 'back': 2})

    cut1 = []
    cut2 = []
    for ob in f_list1:
        cut1.append(ob.rsplit(".", 1)[0])
    for ob in f_list2:
        cut2.append(ob.rsplit(".", 1)[0])
    cut12 = list(set(cut1 + cut2))
    cut12.sort()
    #link = subprocess.Popen(['ls -ld ./'+conf.MAP_PATH+num+'map.dzi'], stdout=subprocess.PIPE, shell=True)
    link = subprocess.Popen(['/usr/bin/ls', '-ld', conf.HOME_PATH+conf.MAP_PATH+num+'map.dzi'], stdout=subprocess.PIPE, shell=False)
    #link_out = link.communicate()[0].decode("utf-8")
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
            url_f = 'map_1/' + num + str(upl_file.name)
            if default_storage.exists(url_f):
                f_exist = True
            else:
                #path = default_storage.save(url_f, upl_file)
                default_storage.save(url_f, upl_file)
                if imghdr.what(conf.HOME_PATH + conf.MAP1_PATH + num + upl_file.name) != 'png':
                    default_storage.delete(upl_file)
                else:
                    #create preview in map_1/prev
                    Image.MAX_IMAGE_PIXELS = None
                    prev = Image.open(upl_file)#.thumbnail([512, 512])
                    prev.thumbnail([512, 512])
                    #default_storage.save('map_1/prev/' + str(upl_file.name), prev)
                    prev.save(conf.HOME_PATH + conf.MAP1_PATH +num + 'prev/' + upl_file.name)
                    prev.close()

                return HttpResponseRedirect('/core/m_manager'+num)

    form = upl_Form()
    pass_on = cut_working()
    map_list = map_slot.objects.all().order_by('num').values_list()

    return render(request, 'serv_map_mgr.html', {'form': form,
                                                 'f_list': f_list,
                                                 'f_exist': f_exist,
                                                 'ok': pass_on[0],
                                                 'deb': pass_on[1],
                                                 'm_num': int(m_num),
                                                 'map_list': map_list,
                                                 })


@login_required(login_url='/core/login/')
def m_manager_cut(request, m_num):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 1})

    if not cut_working()[0]:
        return render(request, 'error.html', {'mess': 'выполняется фоновый процесс', 'back': 1})
    try:
        f_name = request.GET['f_name']
    except:
        f_name = ''
    
    num = str(m_num) + '/'
    #print('os.getcwd(): '+os.getcwd())
    if default_storage.exists('map_2/' + num + f_name.rsplit(".", 1)[0] + '.dzi'):
        default_storage.delete('map_2/' + num + f_name.rsplit(".", 1)[0] + '.dzi')
    if default_storage.exists('map_2/' + num + f_name.rsplit(".", 1)[0] + '_files'):
        shutil.rmtree(conf.HOME_PATH + conf.MAP2_PATH + num + f_name.rsplit(".", 1)[0] + '_files')

    cmd1 = conf.HOME_PATH + conf.SCRIPT_PATH
    cmd2 = conf.HOME_PATH + conf.MAP1_PATH + num + f_name
    cmd3 = conf.HOME_PATH + conf.MAP2_PATH + num + f_name.rsplit(".", 1)[0]
    #os.system(cmd)
    #proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    proc = subprocess.Popen([cmd1, cmd2, cmd3], stdout=subprocess.PIPE, shell=False)
    #data = proc.communicate()#[0].decode("utf-8") #задержка
    #print(proc.stdout.read())
    #p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT, close_fds=False)
    #time.sleep(1)
    #proc.terminate()

    return HttpResponseRedirect('/core/m_manager' + num)


@login_required(login_url='/core/login/')
def m_manager_map_on(request, m_num):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 1})

    if not cut_working()[0]:
        return render(request, 'error.html', {'mess': 'выполняется фоновый процесс', 'back': 1})
    try:
        f_name = request.GET['f_name']
    except:
        #f_name = ''
        return render(request, 'error.html', {'mess': 'файл не найден', 'back': 1})
    
    num = str(m_num) + '/'
    #if os.path.islink(conf.MAP_PATH + 'map.dzi'):
    #    print('islink')
    try:
    #if default_storage.exists('map/map.dzi'):
        os.unlink(conf.HOME_PATH + conf.MAP_PATH + num + 'map.dzi')
    #if default_storage.exists('map/map_files'):
        os.unlink(conf.HOME_PATH + conf.MAP_PATH + num + 'map_files')
    except:
        pass
    os.symlink(conf.HOME_PATH + conf.MAP2_PATH + num + f_name, conf.HOME_PATH + conf.MAP_PATH + num + 'map.dzi')
    #os.symlink('/home/e_cross/media/map_2/map2.dzi', '/home/e_cross/media/map/map.dzi')
    os.symlink(conf.HOME_PATH + conf.MAP2_PATH + num + f_name.rsplit(".", 1)[0] + '_files', conf.HOME_PATH + conf.MAP_PATH + num + 'map_files')
    #print(HOME_PATH + '/' + conf.MAP2_PATH + f_name)

    return HttpResponseRedirect('/core/m_manager' + num)


@login_required(login_url='/core/login/')
def m_manager_del(request, m_num, ftype=1):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 1})

    if not cut_working()[0]:
        return render(request, 'error.html', {'mess': 'выполняется фоновый процесс', 'back': 1})

    url = 'map_'+str(ftype)+'/'
    num = str(m_num) + '/'
    try:
        d_file = request.GET['d_file']
    except:
        d_file = ''
    if default_storage.exists(url + num + d_file):
        default_storage.delete(url + num + d_file)
    if default_storage.exists(url + num + d_file.rsplit(".", 1)[0] + '_files'):
        shutil.rmtree(conf.HOME_PATH + conf.MAP2_PATH + num + d_file.rsplit(".", 1)[0] + '_files')
    #delete preview in map_1/prev
    if default_storage.exists(url + num + 'prev/' + d_file):
        default_storage.delete(url + num + 'prev/' + d_file)

    return HttpResponseRedirect('/core/m_manager' + num)

def cut_working():

    #proc = subprocess.Popen(['ps -e | grep magick-slicer'], stdout=subprocess.PIPE, shell=True)
    proc = subprocess.Popen(['ps -x | grep magick-slicer'], stdout=subprocess.PIPE, shell=True)
    #res = proc.communicate()[0].decode("utf-8")
    res = proc.stdout.read().decode("utf-8").split('\n')
    on = True
    for ob in res:
        if 'MagickSlicer-master/magick-slicer.sh' in ob:
            on = False
            break
    #print(res)
    return [on, res]
    #return True if (len(res) == 0) else False
    #return True if (res.count('/bin/bash') < 1) else False
