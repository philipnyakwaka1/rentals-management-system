from rest_framework import serializers
from .models import User, Profile
from buildings.models import Building
from django.contrib.gis.geos import Point

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        extra_kwargs = {'password': {'write_only': True}}

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'address']

class BuildingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['comment', 'rent', 'payment_details','building', 'county', 'district']
    
    def validate_building(self, value):
        try:
            coord = value.replace(" ","")
            coordinates = coord.split(',')
            return tuple(map(lambda x : float(x), coordinates))
        except Exception as e:
            raise serializers.ValidationError("Coordinate format cannot be parsed. The coordinate should be two floats values separated by a comma.")
    
    def create(self, validated_data):
        coord = validated_data.get('building')
        validated_data['building'] = Point(float(coord[1]), float(coord[0]))
        return Building.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, val in validated_data.items():
            if hasattr(instance, key):
                if key == 'building':
                    val = Point(val[1], val[0])
                setattr(instance, key, val)
        instance.save()
        return instance