#

from rest_framework import serializers

from cable.models import PW_cont, Coupling, Coupling_ports, links
from cross.models import Locker

#############################################################################


class CoupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupling
        fields = ['id', 'parrent', 'parr_type', 'name', 'name_type', 'object_owner',
                  'installed', 'date_ent', 'rasp', 'prim',  'coord_x', 'coord_y']


class CoupSerializerUpdate(CoupSerializer):
    class Meta:
        model = Coupling
        fields = ['id', 'coord_x', 'coord_y', 'parrent', 'parr_type']
        read_only_fields = ['parrent', 'parr_type']


class CoupPortsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupling_ports
        fields = ['id', 'parrent', 'cable_num', 'cable_type', 'fiber_num', 'fiber_color', 'mod_num', 'mod_color',
                  'p_valid', 'changed', 'prim', 'up_id', 'up_info', 'int_c_dest', 'int_c_id', 'int_c_status']
        read_only_fields = fields

#############################################################################


class LockerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locker
        fields = ['id', 'name', 'name_type', 'object_owner', 'co', 'status',
                  'agr', 'detached', 'date_ent', 'rasp', 'prim',  'coord_x', 'coord_y']


class PwcontSerializer(serializers.ModelSerializer):
    class Meta:
        model = PW_cont
        fields = ['id', 'parrent', 'name', 'obj_type', 'object_owner',
                  'rasp', 'prim',  'coord_x', 'coord_y']


class PwcontSerializerUpdate(PwcontSerializer):
    class Meta:
        model = PW_cont
        fields = ['id', 'coord_x', 'coord_y']


class PolylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = links
        fields = ['id', 'lineidid', 'linecncn', 'cabtype', 'cabcolor', 'path', 'param']


class PolylineSerializerUpdate(PolylineSerializer):
    class Meta:
        model = links
        fields = ['id', 'path', 'param']

