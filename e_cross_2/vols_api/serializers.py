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


class PolylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = links
        fields = ['id', 'lineidid', 'linecncn', 'cabtype', 'cabcolor', 'path', 'param']


class CreatePolylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = links
        fields = ['id', 'lineidid', 'linecncn', 'cabtype', 'cabcolor', 'path', 'param']

    def create(self, validated_data):
        poly = links(
            lineidid=validated_data['lineidid'],
            linecncn=validated_data['linecncn'],
            cabtype=validated_data['cabtype'],
            cabcolor=validated_data['cabcolor'],
            path=validated_data['path'],
            param=validated_data['param'],
        )
        # poly.save()
        return poly


