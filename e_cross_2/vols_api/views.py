#

from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
from rest_framework import status

from cable.models import PW_cont, Coupling, links, Coupling_ports
from cross.models import Locker
from .serializers import CoupSerializer, LockerSerializer, PwcontSerializer, LinksSerializer
from .decorators import check_perm


#################################################################

# @csrf_exempt
@check_perm
def coup(request, c_id=0, crud_perm=(False,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET':
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
def locker(request, l_id=0, crud_perm=(False,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET':
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
def pwcont(request, p_id=0, crud_perm=(False,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET':
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


@check_perm
def polyline(request, p_id=0, crud_perm=(False,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET':
        _links = links.objects.all()
        if p_id:
            try:
                link = _links.get(pk=p_id)
                serializer = LinksSerializer(link)
                return JsonResponse(serializer.data, safe=False)
            except ObjectDoesNotExist:
                return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)

        serializer = LinksSerializer(_links, many=True)
        return JsonResponse(serializer.data, safe=False)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


@check_perm
def coup_links(request, c_id, crud_perm=(False,) * 4):
    _C, _R, _U, _D = crud_perm
    if request.method == 'GET':
        coup_p = Coupling_ports.objects.filter(parrent_id=c_id, fiber_num=1)\
            .values_list('up_id', flat=True)
        coup_p_up = Coupling_ports.objects.filter(pk__in=coup_p)\
            .values_list('parrent_id', flat=True)
        coups = Coupling.objects.filter(pk__in=coup_p_up)

        serializer = CoupSerializer(coups, many=True)
        return JsonResponse(serializer.data, safe=False)

    return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)


