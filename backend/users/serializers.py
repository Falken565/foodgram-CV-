from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Follow

from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        user = request.user
        user_is_subscibed = False
        author = obj
        try:
            user_is_subscibed = Follow.objects.filter(
                user=user, author=author
            ).exists()
        except Exception:
            return user_is_subscibed
        return user_is_subscibed


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        user = self.context["request"].user or self.user
        try:
            validate_password(attrs['new_password'], user)
        except ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )
        return super().validate(attrs)


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'invalid_password': 'invalid password'
    }

    def validate_current_password(self, value):
        is_password_valid = self.context['request'].user.check_password(value)
        if is_password_valid:
            return value
        else:
            self.fail('invalid_password')


class SetPasswordSerializer(PasswordSerializer, CurrentPasswordSerializer):
    pass
