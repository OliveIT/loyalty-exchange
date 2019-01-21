# from django.contrib.auth.models import User
from rest_framework import generics, permissions, renderers, viewsets
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse

from services.models import Service, CurrencyRate, MyUser, UserProfile, Membership
from services.permissions import IsAdminOrReadOnly
from services.serializers import ServiceSerializer, UserSerializer, CurrencyRateSerializer,ProfileSerializer,MembershipSerializer

import json
import requests

class ServiceViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_queryset(self):
        queryset = Service.objects.all()
        title = self.request.query_params.get('title', None)
        if title is not None:
            queryset = queryset.filter(title__startswith=title)
        return queryset
    
    # @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    # def highlight(self, request, *args, **kwargs):
    #     service = self.get_object()
    #     return Response(service.contact)

    def perform_create(self, serializer):
        # serializer.save(owner=self.request.user)
        serializer.save()

class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ 
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        # IsAdminOrReadOnly,
    )

    def get_queryset(self):
        queryset = Membership.objects.all()
        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(profile=user)
        service = self.request.query_params.get('service', None)
        if service is not None:
            queryset = queryset.filter(service=service)
        return queryset
    
class CurrencyRateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset gives up-to-date currency rates
    """
    # queryset = User.objects.all()
    # serializer_class = UserSerializer

    queryset = CurrencyRate.objects.all()
    serializer_class = CurrencyRateSerializer

    def get_rate(self, currency):
        url = 'http://free.currencyconverterapi.com/api/v5/convert?q=' + currency + '_USD&compact=y' 
        r = requests.get(url)
        items = r.json()
        return items[currency + '_USD']['val']

    def list(self, request):
        supported_currencies = ['NGN', 'EUR', 'GBP', 'CNY', 'AUD']
        rates = {}
        for cur in supported_currencies:
            rates[cur] = self.get_rate(cur)
        return Response(data=rates)
