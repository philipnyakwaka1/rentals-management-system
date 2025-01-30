from rest_framework import serializers
from .models import User, Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions']
        extra_kwargs = {'password': {'write_only': True}, 'last_login': {'read_only': True}, 'date_joined': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        for key, val in validated_data.items():
            if hasattr(instance, key):
                if key == 'password':
                    instance.set_password(val)
                    continue
                setattr(instance, key, val)
        instance.save()
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'address']

