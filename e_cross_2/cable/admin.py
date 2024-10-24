from django.contrib import admin

from .models import PW_cont
from .models import Coupling
from .models import Coupling_ports
from .models import Templ_cable
from .models import Templ_coupling

from .models import links
from .models import labels

# admin.site.register(PW_cont)
# admin.site.register(Coupling)
# admin.site.register(Coupling_ports)
admin.site.register(Templ_cable)
admin.site.register(Templ_coupling)

admin.site.register(links)
admin.site.register(labels)


@admin.register(PW_cont)
class PW_contAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parrent']
    search_fields = ('pk__exact', )
    search_help_text = 'фильтр по id'
    ordering = ['id']


@admin.register(Coupling)
class CouplingAdmin(admin.ModelAdmin):
    list_display = ['id', 'parr_type', 'name', 'name_type']
    search_fields = ('pk__exact', )
    search_help_text = 'фильтр по id'
    ordering = ['id']


@admin.register(Coupling_ports)
class CouplingPortsAdmin(admin.ModelAdmin):
    list_display = ['id', 'cable_num', 'fiber_num', 'parrent']
    search_fields = ('parrent__pk__exact', )
    search_help_text = 'фильтр по parrent_id'
    ordering = ['id']

