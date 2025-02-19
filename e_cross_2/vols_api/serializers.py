#

from rest_framework import serializers

from cable.models import PW_cont, Coupling, Coupling_ports, links
from cross.models import Locker, Cross, Cross_ports

#############################################################################


class CoupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupling
        fields = ['id', 'parrent', 'parr_type', 'name', 'name_type', 'object_owner',
                  'installed', 'date_ent', 'rasp', 'prim',  'coord_x', 'coord_y']
        read_only_fields = fields


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
        read_only_fields = fields


class CrossSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cross
        fields = ['id', 'parrent', 'name', 'name_type', 'con_type', 'v_col', 'v_row', 'v_forw_l_r',
                  'prim', 'rack_num', 'rack_pos', 'object_owner']
        read_only_fields = fields


class CrossPortsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cross_ports
        fields = ['id', 'parrent', 'num', 'port_t_x', 'p_valid', 'prim', 'opt_len',
                  'up_cross_id', 'up_status', 'int_c_dest', 'int_c_id', 'int_c_status', 'cab_p_id']
        read_only_fields = fields

#############################################################################


class PwcontSerializer(serializers.ModelSerializer):
    class Meta:
        model = PW_cont
        fields = ['id', 'parrent', 'name', 'obj_type', 'object_owner',
                  'rasp', 'prim',  'coord_x', 'coord_y']
        read_only_fields = fields


class PwcontSerializerUpdate(PwcontSerializer):
    class Meta:
        model = PW_cont
        fields = ['id', 'coord_x', 'coord_y']


class PolylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = links
        fields = ['id', 'lineidid', 'linecncn', 'cabtype', 'cabcolor', 'path', 'param']
        read_only_fields = fields


class PolylineSerializerUpdate(PolylineSerializer):
    class Meta:
        model = links
        fields = ['id', 'path', 'param']


