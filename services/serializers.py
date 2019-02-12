# from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from services.models import Service, Membership, CurrencyRate, MyUser, UserProfile, RedeemTransaction, TransferTransaction
from rest_auth.serializers import UserDetailsSerializer

class UserSerializer(serializers.ModelSerializer):

    class Meta():
        model = MyUser
        fields = ('id', 'email', 'phone', 'first_name', 'last_name')
        # fields = UserDetailsSerializer.Meta.fields + ('phone', ) #, 'company_name', 'birth')
        read_only_fields = ('email', 'phone',)


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ('id', 'title', 'description', #'highlight', 'owner'
                  'service_type', 'country','is_opened', 'api_url' )#, 'subscribers')


class CurrencyRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyRate
        fields = ('id',  'currency', 'rate' )


class MembershipSerializer(serializers.ModelSerializer):
    # service = ServiceSerializer()   # to include details of service
    service_title = serializers.ReadOnlyField(source='service.title')
    class Meta:
        model = Membership
        # fields = '__all__'
        fields = ('id', 'identifier', 'points', 'rate', 'profile', 'service', 'service_title' ) 
        read_only_fields = ('points', 'rate',)


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    email = serializers.ReadOnlyField(source='user.email')
    phone = serializers.CharField(source='user.phone', read_only=True)
    extra_points = serializers.DecimalField(max_digits=16, decimal_places=6)
    services = ServiceSerializer(many=True, read_only=True)
    memberships = MembershipSerializer(source='membership', many=True, read_only=True)
    class Meta:
        model = UserProfile
        fields = ('user_id', 'email', 'phone', 'eth_public_key', 'extra_points','memberships', 'services')
        read_only_fields = ('eth_public_key', 'phone', )
        depth = 1


class RedeemTransactionSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.phone')
    # service = serializers.CharField(source='service.title')
    service = serializers.SerializerMethodField('get_servicetitle') # method field!!!

    amount = serializers.DecimalField(max_digits=16, decimal_places=6, read_only=True)
    created_at = serializers.DateTimeField()

    class Meta:
        model = RedeemTransaction
        fields = ('id', 'user', 'service', 'amount', 'created_at')
    
    def get_servicetitle(self, obj):
        if obj.service == None:
            return None
        return obj.service.title


class TransferTransactionSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.phone')
    receiver = serializers.CharField(source='receiver.phone')
    amount = serializers.DecimalField(max_digits=16, decimal_places=6, read_only=True)
    confirmed = serializers.BooleanField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()

    class Meta:
        model = TransferTransaction
        fields = ('id', 'sender', 'receiver', 'amount', 'confirmed', 'status', 'created_at')
