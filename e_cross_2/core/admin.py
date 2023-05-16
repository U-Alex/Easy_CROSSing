from django.contrib import admin

# Register your models here.

from .models import History
from .models import engineer
from .models import COffice
from .models import Device_type
from .models import last_visit
from .models import firm
from .models import manage_comp
from .models import Energy_type
from .models import Subunit_type
from .models import map_slot

from .models import Templ_locker
from .models import Templ_cross
from .models import Templ_device
from .models import Templ_box
from .models import Templ_box_cable
from .models import Templ_subunit

admin.site.register(History)
admin.site.register(engineer)
admin.site.register(COffice)
admin.site.register(Device_type)
admin.site.register(last_visit)
admin.site.register(firm)
admin.site.register(manage_comp)
admin.site.register(Energy_type)
admin.site.register(Subunit_type)
admin.site.register(map_slot)

admin.site.register(Templ_locker)
admin.site.register(Templ_cross)
admin.site.register(Templ_device)
admin.site.register(Templ_box)
admin.site.register(Templ_box_cable)
admin.site.register(Templ_subunit)
