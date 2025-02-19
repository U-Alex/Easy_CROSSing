#

from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from json import loads as js_load
from rest_framework import status

from cable.models import PW_cont, Coupling, links, Coupling_ports, Templ_cable
from cross.models import Kvartal, Building, Locker, Cross, Cross_ports
from .serializers import CoupSerializer, LockerSerializer, CrossSerializer, PwcontSerializer, PolylineSerializer
from .serializers import PwcontSerializerUpdate, CoupSerializerUpdate, PolylineSerializerUpdate
from .serializers import CoupPortsSerializer, CrossPortsSerializer
from .decorators import check_perm

from core.shared_def import chain_trace

#################################################################


@csrf_exempt
@check_perm
def coup(request, o_id=0, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R:
        couplings = Coupling.objects.all()
        # if o_id:
        #     try:
        #         coupling = couplings.get(pk=o_id)
        #         serializer = CoupSerializer(coupling)
        #         return JsonResponse(serializer.data, safe=False)
        #     except ObjectDoesNotExist:
        #         return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

        serializer = CoupSerializer(couplings, many=True)
        return JsonResponse(serializer.data, safe=False)

    if request.method == 'POST' and _U:
        json_data = js_load(request.body.decode('utf-8'))
        for ob in json_data:
            ser = CoupSerializerUpdate(ob).data
            Coupling.objects.filter(pk=ser['id']).update(coord_x=ser['coord_x'], coord_y=ser['coord_y'])
            if ser['parr_type'] == 0:
                Locker.objects.filter(pk=ser['parrent']).update(coord_x=ser['coord_x'], coord_y=ser['coord_y'])

        return JsonResponse({"coup_updated_count": len(json_data)}, status=status.HTTP_200_OK)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@check_perm
def locker(request, o_id=0, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R:
        lockers = Locker.objects.all()
        # if o_id:
        #     try:
        #         lo = lockers.get(pk=o_id)
        #         serializer = LockerSerializer(lo)
        #         return JsonResponse(serializer.data, safe=False)
        #     except ObjectDoesNotExist:
        #         return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

        serializer = LockerSerializer(lockers, many=True)
        return JsonResponse(serializer.data, safe=False)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@check_perm
def pwcont(request, o_id=0, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R:
        pwpw = PW_cont.objects.all()
        # if o_id:
        #     try:
        #         pw = pwpw.get(pk=o_id)
        #         serializer = PwcontSerializer(pw)
        #         return JsonResponse(serializer.data, safe=False)
        #     except ObjectDoesNotExist:
        #         return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

        serializer = PwcontSerializer(pwpw, many=True)
        return JsonResponse(serializer.data, safe=False)

    if request.method == 'POST' and _U:
        json_data = js_load(request.body.decode('utf-8'))
        for ob in json_data:
            ser = PwcontSerializerUpdate(ob).data
            PW_cont.objects.filter(pk=ser['id']).update(coord_x=ser['coord_x'], coord_y=ser['coord_y'])

        return JsonResponse({"pw_updated_count": len(json_data)}, status=status.HTTP_200_OK)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@check_perm
def polyline(request, o_id=0, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R:
        _links = links.objects.all()
        # if o_id:
        #     try:
        #         link = _links.get(pk=o_id)
        #         serializer = PolylineSerializer(link)
        #         return JsonResponse(serializer.data, safe=False)
        #     except ObjectDoesNotExist:
        #         return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

        serializer = PolylineSerializer(_links, many=True)
        return JsonResponse(serializer.data, safe=False)

    if request.method == 'PUT' and _C:
        new_poly = js_load(request.body.decode('utf-8'))
        serializer = PolylineSerializer(new_poly)
        poly = links.objects.create(**serializer.data)
        ret_data = serializer.data
        ret_data['id'] = poly.id
        return JsonResponse((ret_data, ), safe=False, status=status.HTTP_201_CREATED)

    if request.method == 'POST' and _U:
        json_data = js_load(request.body.decode('utf-8'))
        for ob in json_data:
            ser = PolylineSerializerUpdate(ob).data
            links.objects.filter(pk=ser['id']).update(path=ser['path'], param=ser['param'])
        return JsonResponse({"links_updated_count": len(json_data)}, status=status.HTTP_200_OK)

    if request.method == 'DELETE' and _D and o_id:
        links.objects.filter(pk=o_id).delete()
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)  # 204 - Broken pipe from ...

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@check_perm
def coup_links(request, o_id, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R and o_id:
        t_cable = Templ_cable.objects.all()
        coup_p = Coupling_ports.objects.filter(parrent_id=o_id, fiber_num=1)\
            .values('cable_num', 'up_id', 'cable_type').order_by('cable_num')
        for ob in coup_p:
            ob['cable_name'], ob['cable_capa'] = t_cable.filter(pk=ob['cable_type'])\
                .values_list('name', 'capacity').first()
            ob['ext_coup_id'], ob['ext_coup_name'], ob['ext_cable_num'], ob['ext_coup_x'], ob['ext_coup_y'] =\
                Coupling_ports.objects.filter(pk=ob['up_id'])\
                .only('parrent')\
                .values_list('parrent__id', 'parrent__name', 'cable_num', 'parrent__coord_x', 'parrent__coord_y')\
                .first()
        return JsonResponse(list(coup_p), safe=False)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@check_perm
def coup_paint(request, o_id, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    result = {}
    if request.method == 'GET' and _R and o_id:
        t_cable = Templ_cable.objects.all()
        cur_coup = Coupling.objects.get(pk=o_id)
        result['cur_coup'] = CoupSerializer(cur_coup).data
        result['coup_parr'] = find_coup_parrent(cur_coup.parr_type, cur_coup.parrent)
        coup_p = Coupling_ports.objects.filter(parrent_id=o_id).order_by('id')
        result['coup_ports'] = CoupPortsSerializer(coup_p, many=True).data
        _tmp = []
        for c_p_l in coup_p.filter(fiber_num=1):
            c_p_ext = Coupling_ports.objects.get(pk=c_p_l.up_id)
            c_p_cab = t_cable.get(pk=c_p_l.cable_type)
            _tmp.append({**CoupSerializer(c_p_ext.parrent).data,
                         'cable_num': c_p_l.cable_num,
                         'ext_cable_num': c_p_ext.cable_num,
                         'cab_name': c_p_cab.name,
                         'cab_capa': c_p_cab.capacity
                         })
        result['cab_links'] = _tmp
        cross_p = {}
        if cur_coup.parr_type == 0:
            cross_p = Cross_ports.objects.select_related('parrent')\
                .filter(parrent__parrent_id=cur_coup.parrent).exclude(cab_p_id=0) \
                .only('id', 'num', 'parrent__name')\
                .values_list('id', 'num', 'parrent__name')
        result['cross_p'] = list(cross_p)

        return JsonResponse(result, safe=False, status=status.HTTP_200_OK)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@check_perm
def coup_paint_ext(request, o_id, cab_l, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm

    if request.method == 'GET' and _R and o_id:
        cab_list = cab_l.split('-')
        coup_p = Coupling_ports.objects.filter(parrent_id=o_id, cable_num__in=cab_list)
        # for ob in coup_p: print(ob)
        result = {int(key): list() for (key) in cab_list}
        for c_p in coup_p:
            res = CoupPortsSerializer(c_p).data
            hop = chain_trace(c_p.id, '0', True)
            # print(c_p.cable_num, c_p.fiber_num, hop)
            if hop:
                if hop[0] == 2:
                    res.update({'end_type': 'cross'})
                    hop_cross = CrossSerializer(Cross.objects.get(pk=hop[1].parrent_id)).data
                    hop_parent = find_coup_parrent(0, hop_cross['parrent'], True)
                    hop_cross.update({'hop_parent_lo': hop_parent[0], 'hop_parent_full': hop_parent[1]})
                    res.update({'hop_cross': hop_cross})
                    res.update({'hop_port': CrossPortsSerializer(hop[1]).data})
                if hop[0] == 1:
                    res.update({'end_type': 'coup'})
                    hop_coup = CoupSerializer(Coupling.objects.get(pk=hop[1].parrent_id)).data
                    hop_parent = find_coup_parrent(hop_coup['parr_type'], hop_coup['parrent'], True)
                    hop_coup.update({'hop_parent_lo': hop_parent[0], 'hop_parent_full': hop_parent[1]})
                    res.update({'hop_coup': hop_coup})
                    res.update({'items_hop': CoupPortsSerializer(hop[1]).data})
            else:
                res.update({'end_type': 'loopback detected'})

            result[c_p.cable_num].append(res)
        # for k, v in result.items():
        #     for ob in v:
        #         print(k, ob)
        return JsonResponse(result, safe=False, status=status.HTTP_200_OK)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


def find_coup_parrent(parr_type, parrent_id, ext_hop=False):
    res, res0 = "", ""
    if parr_type == 0:
        parr = Locker.objects.select_related('parrent', 'parrent__parrent')\
            .filter(pk=parrent_id) \
            .only('name', 'parrent__name', 'parrent__house_num', 'parrent__kvar') \
            .values('name', 'parrent__name', 'parrent__house_num', 'parrent__kvar')\
            .first()
        kvar = Kvartal.objects.get(pk=parr['parrent__kvar']).name
        res = f"уд.: {parr['name']}, ул.: {parr['parrent__name']} {parr['parrent__house_num']}, квартал.: {kvar}"
        res0 = f"уд.: {parr['name']}"
    if parr_type == 1:
        parr = Building.objects\
            .filter(pk=parrent_id) \
            .only('name', 'house_num', 'kvar') \
            .values('name', 'house_num', 'kvar')\
            .first()
        kvar = Kvartal.objects.get(pk=parr['kvar']).name
        res = f"ул.: {parr['name']} {parr['house_num']}, квартал.: {kvar}"
    if parr_type == 2:
        parr = PW_cont.objects.select_related('parrent')\
            .filter(pk=parrent_id) \
            .only('name', 'parrent__name', 'obj_type') \
            .values('name', 'parrent__name', 'obj_type')\
            .first()
        res = f"{'опора' if parr['obj_type'] == 1 else 'колодец'}.: {parr['name']}, квартал.: {parr['parrent__name']}"

    if ext_hop:
        return res0, res
    return res


