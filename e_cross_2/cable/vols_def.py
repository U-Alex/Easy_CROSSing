# cable__vols_def

#from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from cable.models import Coupling_ports, links

####################################################################################################


def vols_coup_move(coup_id, pos):

    links_L = links.objects.filter(lineidid__startswith=str(coup_id)+',')
    links_R = links.objects.filter(lineidid__endswith=','+str(coup_id))

    for ob in links_L:
        path = ob.path.split("||", 1)
        if pos[0] == path[0]:
            ob.path = pos[1]+'||'+path[1]
            ob.save()

    for ob in links_R:
        path = ob.path.rsplit("||", 1)
        if pos[0] == path[1]:
            ob.path = path[0]+'||'+pos[1]
            ob.save()

    return


def vols_cab_up(coup_id, cab_num_1):

    cab_num_2 = cab_num_1 - 1
    links_1_L = links.objects.filter(lineidid__startswith=str(coup_id)+',', linecncn__startswith=str(cab_num_1)+',')
    links_1_R = links.objects.filter(lineidid__endswith=','+str(coup_id), linecncn__endswith=','+str(cab_num_1))
    links_2_L = links.objects.filter(lineidid__startswith=str(coup_id)+',', linecncn__startswith=str(cab_num_2)+',')
    links_2_R = links.objects.filter(lineidid__endswith=','+str(coup_id), linecncn__endswith=','+str(cab_num_2))

    link_1, link_2 = 0, 0
    with transaction.atomic():
        if links_1_L.count() == 1:
            link_1 = links_1_L.first()
            cncn = link_1.linecncn.split(',')[1]
            link_1.linecncn = str(cab_num_2)+','+cncn
        elif links_1_R.count() == 1:
            link_1 = links_1_R.first()
            cncn = link_1.linecncn.split(',')[0]
            link_1.linecncn = cncn+','+str(cab_num_2)
        if links_2_L.count() == 1:
            link_2 = links_2_L.first()
            cncn = link_2.linecncn.split(',')[1]
            link_2.linecncn = str(cab_num_1)+','+cncn
        elif links_2_R.count() == 1:
            link_2 = links_2_R.first()
            cncn = link_2.linecncn.split(',')[0]
            link_2.linecncn = cncn+','+str(cab_num_1)
        if link_1:
            link_1.save()
        if link_2:
            link_2.save()

    return


def vols_cab_remove(coup_id, cab_num):

    links_L = links.objects.filter(lineidid__startswith=str(coup_id)+',', linecncn__startswith=str(cab_num)+',')
    links_R = links.objects.filter(lineidid__endswith=','+str(coup_id), linecncn__endswith=','+str(cab_num))

    if links_L.count() > 0:
        links_L.delete()
    if links_R.count() > 0:
        links_R.delete()

    return
