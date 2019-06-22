# from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from services.models import MyUser, UserProfile
from rest_auth.serializers import UserDetailsSerializer

class UserSerializer(serializers.ModelSerializer):

    class Meta():
        model = MyUser
        fields = ('id', 'email', 'phone', 'first_name', 'last_name')
        # fields = UserDetailsSerializer.Meta.fields + ('phone', )
        read_only_fields = ('email', 'phone',)

class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    email = serializers.ReadOnlyField(source='user.email')
    phone = serializers.CharField(source='user.phone', read_only=True)
    extra_data = serializers.DecimalField(max_digits=16, decimal_places=6)
    class Meta:
        model = UserProfile
        fields = ('user_id', 'email', 'phone', 'extra_data')
        read_only_fields = ('phone', )
        depth = 1
