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

admin.site.register(Kvartal)
admin.site.register(Street)
admin.site.register(Building)
admin.site.register(Locker)
admin.site.register(Cross)
admin.site.register(Device)
admin.site.register(Box)
admin.site.register(Cross_ports)
admin.site.register(Device_ports)
admin.site.register(Device_ports_v)
admin.site.register(Box_ports)
admin.site.register(Subunit)
