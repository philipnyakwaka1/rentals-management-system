from .models import Notice, Comment
from rest_framework import serializers
from django.contrib.auth.models import User


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['__all__']
    
    def create(self, validated_data):
        owner = validated_data.get('owner')
        try:
            user = User.objects.get(pk=validated_data.data.get('owner'))
        except User.DoesNotExist:
            raise serializers.ValidationError('owner does not exist, provide a valid user id')
        validated_data['owner'] = user
        return Notice.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'owner' in validated_data.keys():
            raise serializers.ValidationError('cannot change user')
        for key, val in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, val)
        instance.save()
        return instance

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        field = ['__all__']
    
    def create(self, validated_data):
        tenant = validated_data.get('tenant')
        try:
            user = User.objects.get(pk=validated_data.data.get('tenant'))
        except User.DoesNotExist:
            raise serializers.ValidationError('tenant does not exist, provide a valid user id')
        validated_data['tenant'] = user
        return Notice.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        if 'tenant' in validated_data.keys():
            raise serializers.ValidationError('cannot change user')
        for key, val in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, val)
        instance.save()
        return instance