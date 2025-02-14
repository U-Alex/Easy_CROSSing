#

from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from json import loads as js_load
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
from rest_framework import status

from cable.models import PW_cont, Coupling, links, Coupling_ports, Templ_cable
from cross.models import Locker
from .serializers import CoupSerializer, LockerSerializer, PwcontSerializer
from .serializers import PolylineSerializer, CreatePolylineSerializer
from .decorators import check_perm


#################################################################

# @csrf_exempt
@check_perm
def coup(request, c_id=0, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R:
        couplings = Coupling.objects.all()
        if c_id:
            try:
                coupling = couplings.get(pk=c_id)
                serializer = CoupSerializer(coupling)
                return JsonResponse(serializer.data, safe=False)
            except ObjectDoesNotExist:
                return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

        serializer = CoupSerializer(couplings, many=True)
        return JsonResponse(serializer.data, safe=False)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@check_perm
def locker(request, l_id=0, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R:
        lockers = Locker.objects.all()
        if l_id:
            try:
                lo = lockers.get(pk=l_id)
                serializer = LockerSerializer(lo)
                return JsonResponse(serializer.data, safe=False)
            except ObjectDoesNotExist:
                return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

        serializer = LockerSerializer(lockers, many=True)
        return JsonResponse(serializer.data, safe=False)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@check_perm
def pwcont(request, p_id=0, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R:
        pwpw = PW_cont.objects.all()
        if p_id:
            try:
                pw = pwpw.get(pk=p_id)
                serializer = PwcontSerializer(pw)
                return JsonResponse(serializer.data, safe=False)
            except ObjectDoesNotExist:
                return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

        serializer = PwcontSerializer(pwpw, many=True)
        return JsonResponse(serializer.data, safe=False)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@check_perm
def polyline(request, p_id=0, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R:
        _links = links.objects.all()
        if p_id:
            try:
                link = _links.get(pk=p_id)
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

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@check_perm
def coup_links(request, c_id, crud_perm=(True,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET' and _R:
        t_cable = Templ_cable.objects.all()
        coup_p = Coupling_ports.objects.filter(parrent_id=c_id, fiber_num=1)\
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


