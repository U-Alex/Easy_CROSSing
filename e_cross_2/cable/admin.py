from django.contrib import admin

from .models import PW_cont
from .models import Coupling
from .models import Coupling_ports
from .models import Templ_cable
from .models import Templ_coupling

from .models import links
from .models import labels

admin.site.register(PW_cont)
admin.site.register(Coupling)
admin.site.register(Coupling_ports)
admin.site.register(Templ_cable)
admin.site.register(Templ_coupling)

admin.site.register(links)
admin.site.register(labels)
