#

from rest_framework import serializers

from cable.models import PW_cont, Coupling, links
from cross.models import Locker


# class CoupSerializer(serializers.HyperlinkedModelSerializer):
class CoupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupling
        fields = ['id', 'parrent', 'parr_type', 'name', 'name_type', 'object_owner',
                  'installed', 'date_ent', 'rasp', 'prim',  'coord_x', 'coord_y']


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


class LinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = links
        fields = ['id', 'lineidid', 'linecncn', 'cabtype', 'cabcolor', 'path', 'param']

