from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '_all_'


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'email',
            'usertype',
            'phone',
            'address'
        ]

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email'),
            usertype=validated_data['usertype'],
            phone=validated_data.get('phone'),
            address=validated_data.get('address')
        )

        return user