from rest_framework import serializers
from .models import User, Profile
from password_strength import PasswordPolicy


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions']
        extra_kwargs = {'password': {'write_only': True}, 'last_login': {'read_only': True}, 'date_joined': {'read_only': True}}

    def validate_password(self, value):

        class Length:
            def __init__(self, count):
                self.count = count
            def __str__(self):
                return f'password must be at least {self.count} characters long'

        class Uppercase:
            def __init__(self, count):
                self.count = count
            def __str__(self):
                return f'password must contain at least {self.count} uppercase character'

        class Numbers:
            def __init__(self, count):
                self.count = count
            def __str__(self):
                return f'password must contain at least {self.count} number'

        class Special:
            def __init__(self, count):
                self.count = count
            def __str__(self):
                return f'password must contain at least {self.count} special character'
        
        policy = PasswordPolicy.from_names(
            length=8,
            uppercase=1,
            numbers=1,
            special=1,
        )

        password_feedback = policy.test(value)

        if len(password_feedback) > 0:
            for i in range(len(password_feedback)):
                password_feedback[i] = str(eval(str(password_feedback[i])))
            raise serializers.ValidationError({'error': password_feedback})
        return value

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

