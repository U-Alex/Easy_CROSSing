from django.contrib import admin

from .models import Kvartal
from .models import Street
from .models import Building
from .models import Locker
from .models import Cross
from .models import Device
from .models import Box
from .models import Cross_ports
from .models import Device_ports
from .models import Device_ports_v
from .models import Box_ports
from .models import Subunit

# admin.site.register(Kvartal)
# admin.site.register(Street)
# admin.site.register(Building)
# admin.site.register(Locker)
# admin.site.register(Cross)
# admin.site.register(Device)
# admin.site.register(Box)
# admin.site.register(Cross_ports)
# admin.site.register(Device_ports)
# admin.site.register(Device_ports_v)
# admin.site.register(Box_ports)
# admin.site.register(Subunit)


@admin.register(Kvartal)
class KvartalAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ('pk__exact', )
    search_help_text = 'фильтр по id'
    ordering = ['name']


@admin.register(Street)
class StreetAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ('pk__exact', )
    search_help_text = 'фильтр по id'
    ordering = ['name']


@admin.register(Building)
class LockerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parrent']
    search_fields = ('pk__exact', )
    search_help_text = 'фильтр по id'
    ordering = ['id']


@admin.register(Locker)
class LockerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parrent']
    search_fields = ('pk__exact', )
    search_help_text = 'фильтр по id'
    ordering = ['id']


@admin.register(Cross)
class CrossAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'name_type', 'parrent']
    search_fields = ('pk__exact', )
    search_help_text = 'фильтр по id'
    ordering = ['id']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'obj_type', 'parrent']
    search_fields = ('pk__exact', )
    search_help_text = 'фильтр по id'
    ordering = ['id']


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'num', 'name_type', 'parrent']
    search_fields = ('pk__exact', )
    search_help_text = 'фильтр по id'
    ordering = ['id']


@admin.register(Subunit)
class SubunitAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'con_type', 'parrent']
    search_fields = ('pk__exact', )
    search_help_text = 'фильтр по id'
    ordering = ['id']


@admin.register(Cross_ports)
class CrossPortsAdmin(admin.ModelAdmin):
    list_display = ['id', 'num', 'parrent']
    search_fields = ('parrent__pk__exact', )
    search_help_text = 'фильтр по parrent_id'
    ordering = ['id']


@admin.register(Device_ports)
class DevicePortsAdmin(admin.ModelAdmin):
    list_display = ['id', 'num', 'p_alias', 'parrent']
    search_fields = ('parrent__pk__exact', )
    search_help_text = 'фильтр по parrent_id'
    ordering = ['id']


@admin.register(Box_ports)
class BoxPortsAdmin(admin.ModelAdmin):
    list_display = ['id', 'p_alias', 'parrent']
    search_fields = ('parrent__pk__exact', )
    search_help_text = 'фильтр по parrent_id'
    ordering = ['id']

