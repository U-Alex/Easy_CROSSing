#

from functools import wraps
from typing import Callable
from django.http import JsonResponse
from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.authtoken.models import Token


def check_perm(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(request, c_id=0):

        if token := request.environ.get('HTTP_TOKEN'):      # 'environ' or 'META'
            if user := Token.objects.filter(key=token).first().user:
                groups = list(Group.objects.filter(user=user, name__startswith='vols').values_list('name', flat=True))
                crud_perm = ('vols_create' in groups,
                             'vols_read' in groups,
                             'vols_update' in groups,
                             'vols_delete' in groups)
                return func(request, c_id, crud_perm)
            else:
                return JsonResponse({}, status=status.HTTP_403_FORBIDDEN)
        else:
            return JsonResponse({}, status=status.HTTP_401_UNAUTHORIZED)

    return wrapper

