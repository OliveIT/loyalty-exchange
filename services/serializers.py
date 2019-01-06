from django.contrib.auth.models import User
from rest_framework import serializers

from services.models import Service


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(
        view_name='service-highlight', format='html')

    class Meta:
        model = Service
        fields = ('url', 'id', 'highlight', 'owner', 'title', 'code',
                  'linenos', 'language', 'style')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    services = serializers.HyperlinkedRelatedField(
        many=True, view_name='service-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'services')
