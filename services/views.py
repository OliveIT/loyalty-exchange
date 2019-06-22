# from django.contrib.auth.models import User
from rest_framework import generics, permissions, renderers, viewsets
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse

from services.models import MyUser, UserProfile
from services.permissions import IsAdminOrReadOnly
from services.serializers import UserSerializer, ProfileSerializer

import json
import requests
from rest_framework import viewsets, mixins

class NoPostRemoveViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    pass

class UserViewSet(NoPostRemoveViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
