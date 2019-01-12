from django.core import serializers
from services.models import Service, UserProfile, Membership
from services.serializers import ServiceSerializer, ProfileSerializer, MembershipSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json

class GetPoints(APIView):
    """
    Send request to Service Provider's api url and get point value.
    """

    # def get(self, request, format=None):
    #     services = Service.objects.all()
    #     serializer = ServiceSerializer(services, many=True)
    #     return Response(serializer.data)

    def post(self, request, format=None):
        user_id = request.data.get('user', None)
        service_id = request.data.get('service', None)
        identifier = request.data.get('identifier', None)
        password = request.data.get('password', None)
        flag_save_id = request.data.get('save_id', False)

        error_msg = {
            "details": "Unexpected Error Occured!"
        }

        if user_id and service_id and identifier and password:
            # Membership.objects.get(pk=1)
            service = Service.objects.get(pk=service_id)
            profile = UserProfile.objects.get(pk=user_id)
            # user first() method to get model object from array
            membership = Membership.objects.filter(profile=user_id, service=service_id).first()
            if service and profile and membership:
                try:
                    # https://stackoverflow.com/questions/9733638/post-json-using-python-requests
                    res = requests.post('http://localhost:37037/api/service/points/get', data=request.data)
                    if res.status_code == 200 or res.status_code == 201:
                        # success
                        retval = res.json()
                        membership.points = retval['points']
                        if flag_save_id:
                            membership.identifier = identifier
                        membership.save()
                        retval = serializers.serialize('json', [ membership, ])
                        return Response(retval, status=status.HTTP_201_CREATED)
                    # error code
                    error_msg['details'] = res.json()
                except (requests.ConnectionError, requests.Timeout, requests.exceptions.HTTPError) as e:
                    # exception
                    error_msg['details'] = str(e)
            else:
                error_msg['details'] = "User or Service not found or user isn't a member of the service!"
        else:
            error_msg['details'] = "user, service, identifer, password fields are required!"
        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

        # serializer = MembershipSerializer(data=request.data)
        # if serializer.is_valid():
        #     return Response(request.data, status=status.HTTP_201_CREATED)
            # serializer.save()



class RedeemPoints(APIView):
    """
    Send request to Service Provider's api url and get point value.
    """

    # def get(self, request, format=None):
    #     services = Service.objects.all()
    #     serializer = ServiceSerializer(services, many=True)
    #     return Response(serializer.data)

    def post(self, request, format=None):
        user_id = request.data.get('user', None)
        service_id = request.data.get('service', None)
        identifier = request.data.get('identifier', None)
        password = request.data.get('password', None)
        flag_save_id = request.data.get('save_id', False)
        amount = request.data.get('amount', 0)

        error_msg = {
            "details": "Unexpected Error Occured!"
        }

        if user_id and service_id and identifier and password and amount >= 1:
            # Membership.objects.get(pk=1)
            service = Service.objects.get(pk=service_id)
            profile = UserProfile.objects.get(pk=user_id)
            # user first() method to get model object from array
            membership = Membership.objects.filter(profile=user_id, service=service_id).first()
            if service and profile and membership:
                try:
                    # https://stackoverflow.com/questions/9733638/post-json-using-python-requests
                    res = requests.post('http://localhost:37037/api/service/points/redeem', data=request.data)
                    if res.status_code == 200 or res.status_code == 201:
                        # success
                        retval = res.json()
                        membership.points = retval['points']
                        if flag_save_id:
                            membership.identifier = identifier
                        membership.save()
                        retval = serializers.serialize('json', [ membership, ])
                        return Response(retval, status=status.HTTP_201_CREATED)
                    # error code
                    error_msg['details'] = res.json()
                except (requests.ConnectionError, requests.Timeout, requests.exceptions.HTTPError) as e:
                    # exception
                    # TRICK str()
                    error_msg['details'] = str(e)
            else:
                error_msg['details'] = "User or Service not found or user isn't a member of the service!"
        else:
            error_msg['details'] = "user, service, identifer, password, positive amount fields are required!"
        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
