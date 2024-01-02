#

import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from core.shared_def import upd_visit

@login_required(login_url='/kpp/login/')
def man(request, l1=0):

    upd_visit(request.user)

    if int(l1) > 9:
        l1 = 0
    html = str(l1)+'.html'

    if (not request.user.has_perm("kpp.can_adm")) and int(l1) > 8:
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 1})

    return render(request, html)
