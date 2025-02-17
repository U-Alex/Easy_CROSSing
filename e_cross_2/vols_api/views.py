#

from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from json import loads as js_load
# from json import dump as js_dump
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
from rest_framework import status

from cable.models import PW_cont, Coupling, links, Coupling_ports, Templ_cable
from cross.models import Kvartal, Building, Locker
from .serializers import CoupSerializer, LockerSerializer, PwcontSerializer, PolylineSerializer
from .serializers import PwcontSerializerUpdate, CoupSerializerUpdate, PolylineSerializerUpdate
from .serializers import CoupPortsSerializer
from .decorators import check_perm

#################################################################


@csrf_exempt
@check_perm
def coup(request, o_id=0, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R:
        couplings = Coupling.objects.all()
        if o_id:
            try:
                coupling = couplings.get(pk=o_id)
                serializer = CoupSerializer(coupling)
                return JsonResponse(serializer.data, safe=False)
            except ObjectDoesNotExist:
                return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

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
        if o_id:
            try:
                lo = lockers.get(pk=o_id)
                serializer = LockerSerializer(lo)
                return JsonResponse(serializer.data, safe=False)
            except ObjectDoesNotExist:
                return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

        serializer = LockerSerializer(lockers, many=True)
        return JsonResponse(serializer.data, safe=False)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@check_perm
def pwcont(request, o_id=0, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R:
        pwpw = PW_cont.objects.all()
        if o_id:
            try:
                pw = pwpw.get(pk=o_id)
                serializer = PwcontSerializer(pw)
                return JsonResponse(serializer.data, safe=False)
            except ObjectDoesNotExist:
                return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

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
        if o_id:
            try:
                link = _links.get(pk=o_id)
                serializer = PolylineSerializer(link)
                return JsonResponse(serializer.data, safe=False)
            except ObjectDoesNotExist:
                return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

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
        result['coup_parr'] = find_coup_parrent(cur_coup)
        coup_p = Coupling_ports.objects.filter(parrent_id=o_id).order_by('id')
        result['coup_ports'] = CoupPortsSerializer(coup_p, many=True).data
        _tmp = []
        for c_p_l in coup_p.filter(fiber_num=1):
            c_p_ext = Coupling_ports.objects.get(pk=c_p_l.up_id)
            c_p_cab = t_cable.get(pk=c_p_l.cable_type)
            # _tmp.append({'coup_ext_parr': CoupSerializer(c_p_ext.parrent).data,
            _tmp.append({**CoupSerializer(c_p_ext.parrent).data,
                         # 'coup_ext_parr': CoupSerializer(c_p_ext.parrent).data,
                         'cable_num': c_p_l.cable_num,
                         'ext_cable_num': c_p_ext.cable_num,
                         'cab_name': c_p_cab.name,
                         'cab_capa': c_p_cab.capacity
                         })
        result['cab_links'] = _tmp

        for key, val in result.items():
            if key == 'cab_links':
                for ob2 in val:
                    print(key, ob2)
            else:
                print(key, val)

        return JsonResponse(result, safe=False, status=status.HTTP_200_OK)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


def find_coup_parrent(curr_coup):
    res = ""
    if curr_coup.parr_type == 0:
        parr = Locker.objects.select_related('parrent', 'parrent__parrent')\
            .filter(pk=curr_coup.parrent) \
            .only('name', 'parrent__name', 'parrent__house_num', 'parrent__kvar') \
            .values('name', 'parrent__name', 'parrent__house_num', 'parrent__kvar')\
            .first()
        kvar = Kvartal.objects.get(pk=parr['parrent__kvar']).name
        res = f"уд.: {parr['name']}, ул.: {parr['parrent__name']} {parr['parrent__house_num']}, квартал.: {kvar}"
    if curr_coup.parr_type == 1:
        parr = Building.objects\
            .filter(pk=curr_coup.parrent) \
            .only('name', 'house_num', 'kvar') \
            .values('name', 'house_num', 'kvar')\
            .first()
        kvar = Kvartal.objects.get(pk=parr['kvar']).name
        res = f"ул.: {parr['name']} {parr['house_num']}, квартал.: {kvar}"
    if curr_coup.parr_type == 2:
        parr = PW_cont.objects.select_related('parrent')\
            .filter(pk=curr_coup.parrent) \
            .only('name', 'parrent__name', 'obj_type') \
            .values('name', 'parrent__name', 'obj_type')\
            .first()
        res = f"{'опора' if parr['obj_type'] == 1 else 'колодец'}.: {parr['name']}, квартал.: {parr['parrent__name']}"

    return res


