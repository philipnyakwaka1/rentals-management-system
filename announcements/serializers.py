from .models import Notice, Comment
from rest_framework import serializers
from django.contrib.auth.models import User
from buildings.models import Building


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['pk', 'owner', 'building', 'notice', 'created_at', 'updated_at']
        extra_kwargs = {'created_at': {'read_only': True}, 'updated_at': {'read_only': True}}

    def update(self, instance, validated_data):
        if 'owner' in validated_data.keys():
            raise serializers.ValidationError('cannot change user')
        if 'building' in validated_data.keys():
            raise serializers.ValidationError('cannot change building')
        for key, val in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, val)
        instance.save()
        return instance

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['pk', 'tenant', 'building', 'comment', 'created_at', 'updated_at']
        extra_kwargs = {'created_at': {'read_only': True}, 'updated_at': {'read_only': True}}
    
    def update(self, instance, validated_data):
        if 'tenant' in validated_data.keys():
            raise serializers.ValidationError('cannot change user')
        if 'building' in validated_data.keys():
            raise serializers.ValidationError('cannot change building')
        for key, val in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, val)
        instance.save()
        return instance
