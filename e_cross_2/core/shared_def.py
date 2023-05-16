#

import datetime
import re
import json
import requests
#import psycopg2 as db_tv

from django.core.exceptions import ObjectDoesNotExist

from core.models import last_visit, History
from core.models import Templ_cross
from cross.models import Building, Locker
from cross.models import Cross_ports, Device_ports
from cable.models import PW_cont, Coupling_ports, Templ_cable
#from eq_rent.models import equipment

from core.e_config import conf

####################################################################################################


def chain_trace(p_id, p_type, transit=False):
    #   ch_list[n][0]:
    #   1-Coupling_ports
    #   2-Cross_ports
    #   4-Device_ports
    #   8-loopback
    ch_list = []
    p_all = Coupling_ports.objects.all()
    c_all = Templ_cable.objects.all()

    if p_type == '1':
        start_cr = Cross_ports.objects.get(pk=p_id)
        ch_list.append([2,
                        start_cr,
                        False,
                        False,
                        Templ_cross.objects.get(pk=start_cr.parrent.con_type)
                        ])
        start_id = start_cr.cab_p_id
    elif p_type == '0':
        start_id = p_id
    else:
        return False
    if start_id == 0:
        return False

    fin = False
    par1 = p_all.get(pk=start_id)
    ch_list.append([1,
                    par1,
                    find_coup_parrent(par1.parrent),
                    False,
                    c_all.get(pk=par1.cable_type)
                    ])
    start_id = par1.up_id
    first_id = par1.id
    total_len = 0

    while not fin:
        par2 = p_all.get(pk=start_id)
        #check cable_len
        fib1 = p_all.get(parrent=par2.parrent_id, cable_num=par2.cable_num, fiber_num=1)
        c_info = fib1.up_info.split('∿')
        #if len(c_info) < 3:
        if not re.match(r'^[0-9]+$', c_info[2]):
            c_info = ['',0,0,0,None]
        #elif c_info[0] != r'^[0-9]+$': #!= r'^\d+$': #== '':
        #elif not re.match(r'^[0-9]+$', c_info[0]):
        #    c_info[0] = 0
        total_len += int(c_info[2])
        #
        ch_list.append([1,
                        par2,
                        find_coup_parrent(par2.parrent),
                        [int(c_info[2]), total_len],
                        c_all.get(pk=par2.cable_type)
                        ])
        if par2.int_c_status == 0:              #не сварено
            fin = True
            continue
        elif par2.int_c_dest == 0:              #варка
            par3 = p_all.get(pk=par2.int_c_id)
            if first_id == par3.id:
                fin = True
                ch_list.append([8,
                                'loopback detected'
                                ])
                continue
            ch_list.append([1,
                            par3,
                            find_coup_parrent(par3.parrent),
                            False,
                            c_all.get(pk=par3.cable_type)
                            ])
            start_id = par3.up_id
            continue
        elif par2.int_c_dest == 1:              #кросс
            par4 = Cross_ports.objects.get(pk=par2.int_c_id)
            ch_list.append([2,
                            par4,
                            False,
                            False,
                            Templ_cross.objects.get(pk=par4.parrent.con_type)
                            ])
            #if transit and par4.up_status != 0:
            #    print('upper cross_port found')
            if par4.int_c_status == 0:
                fin = True
                continue
            elif par4.int_c_dest == 1:
                par5 = Cross_ports.objects.get(pk=par4.int_c_id)
                total_len += conf.CROSS_LEN
                ch_list.append([2,
                                par5,
                                False,
                                [conf.CROSS_LEN, total_len],
                                Templ_cross.objects.get(pk=par5.parrent.con_type)
                                ])
                if par5.cab_p_id != 0:
                    par1 = p_all.get(pk=par5.cab_p_id)
                    if first_id == par1.id:
                        fin = True
                        ch_list.append([8,
                                        'loopback detected'
                                        ])
                        continue
                    ch_list.append([1,
                                    par1,
                                    find_coup_parrent(par1.parrent),
                                    False,
                                    c_all.get(pk=par1.cable_type)
                                    ])
                    start_id = par1.up_id
                    continue
                fin = True
                continue
            elif par4.int_c_dest == 2:
                par5 = Device_ports.objects.get(pk=par4.int_c_id)
                ch_list.append([4,
                                par5,
                                False
                                ])
                fin = True
                continue
    #ch_list.append([9, 'end'])
    if ch_list[0][0] == 1:
        li0 = [[0]]
        li0.extend(ch_list)
        ch_list = li0
        #ch_list.reverse(); ch_list.append([0]); ch_list.reverse()
#experimental
    if transit:
        res = ch_list.pop()
        if res[0] == 4:
            res = ch_list.pop()
        elif res[0] == 8:
            return False
        return res
#
    if len(ch_list) %2 > 0:
        ch_list.append([0])

    ch_list2 = []
    i = 0
    while i != len(ch_list):
        ch_list2.append([ch_list[i], ch_list[i+1]])
        i += 2

    return ch_list2


####################################################################################################

def find_coup_parrent(coup):   #определяем родителя

    if coup.parr_type == 0:
        try:
            return Locker.objects.get(pk=coup.parrent)
        except ObjectDoesNotExist:
            return False
    elif coup.parr_type == 1:
        return Building.objects.get(pk=coup.parrent)
    else:
        return PW_cont.objects.get(pk=coup.parrent)


####################################################################################################

def upd_visit(user, prim=''):

    if last_visit.objects.filter(pk=user.id).exists():
        #prim = last_visit.objects.get(pk=user.id).prim + '▲' + prim
        prim += '▲' + last_visit.objects.get(pk=user.id).prim

    upd = last_visit.objects.update_or_create(pk=user.id, defaults={'login': user.username,
                                                                    'fullname': user.first_name +' '+ user.last_name,
                                                                    'date_l_v': datetime.datetime.now(),
                                                                    #'prim': prim[-100:]
                                                                    'prim': prim[:100]
                                                                    })
    return


def to_his(data):

    his = History.objects.create(user=data[0],
                                 obj_type=data[1],
                                 obj_id=data[2],
                                 operation1=data[3],
                                 operation2=data[4],
                                 text=data[5]
                                 )
    return
