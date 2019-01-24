from django.conf import settings

from django.core import serializers
from django.db.models import Sum
from django.db.models.functions import Coalesce
from services.models import Service, UserProfile, Membership, RedeemTransaction
from services.serializers import ServiceSerializer, ProfileSerializer, MembershipSerializer, RedeemTransactionSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import os, sys, inspect

from decimal import Decimal

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

# from web3.providers.eth_tester import EthereumTesterProvider


w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/b5d9a6731e714ddda0c3ca38f410b3cf"))
with open(str( settings.BASE_DIR + '/truffle/build/contracts/LEToken.json'), 'r') as abi_definition:
    abi = json.load(abi_definition)['abi']
contract_address = "0xA44C1aE4A46193d8373355849D3fFebf68A8143F"
contract = w3.eth.contract(address=contract_address, abi=abi)
concise_contract = ConciseContract(contract)
nonce = w3.eth.getTransactionCount('0x5ce9454909639D2D17A3F753ce7d93fa0b9aB12E')
admin_private = "0xaaaaaaaaaaaaaaaaaaaaa"

def mint_token(address, amount):
    # tx_hash = self.contract.functions.mint(address, amount).transact({'from': self.w3.eth.accounts[0], 'gas': 1000000, })
    tx_hash = concise_contract.mint(address, amount, transact={'from': self.w3.eth.accounts[1], 'gas': 100000})
    self.w3.eth.waitForTransactionReceipt(tx_hash)
    pass

def update_a_customer(pk, eth=False):
    # FIXME when we use hyperlinkedserializer
    # factory = APIRequestFactory()
    # request = factory.get('/')

    # serializer_context = {
    #     'request': Request(request),
    # }
    # serializer = ProfileSerializer(instance = UserProfile.objects.get(pk=pk), context=serializer_context)
    serializer = ProfileSerializer(UserProfile.objects.get(pk=pk))

    # FIXME swallow copy?
    profile_data = dict(serializer.data)
    total = Decimal(profile_data['extra_points'])
    for membership in profile_data['memberships']:
        membership['real_points'] = Decimal(membership['points']) * Decimal(membership['rate'])
        total += Decimal(membership['real_points'])
    profile_data['total'] = total
    # TODO remove useless properties
    del profile_data['services']

    # TODO update via web3
    if eth == True:

        pass

    return profile_data


def update_everyone(eth=False):
    res = []
    for profile in UserProfile.objects.all():
        res.append(update_a_customer(pk = profile.pk, eth=eth))

    # content = JSONRenderer().render(res)
    return res

def fetchAPI(service):
    # res = requests.get(service.api_url, data=None)
    print("service.api_url " + service.api_url)

    json_data = open(settings.BASE_DIR + '/services/fixtures/memberships.json')   
    deserialised = json.load(json_data) # deserialises it
    # data2 = json.dumps(json_data) # json formatted string
    ret = {"result": "ok", "data": []}
    for membership in deserialised:
        if membership['fields']['service_id'] == service.pk:
            ret['data'].append(membership['fields'])

    json_data.close()
    return ret

    # response = {
            #     "result": "ok",
            #     "data": [{  "points": 123.43,
            #         "rate": 2.5,
            #         "customerIdentifier":"dry2",
            #         "serviceID":"Midastouchdrycleaners"},
            #     {   "points": 100.43,
            #         "rate": 2.5,
            #         "customerIdentifier":"dry4",
            #         "serviceID":"Midastouchdrycleaners" },
            #     {   "points": 43.632,
            #         "rate": 2.5,
            #         "customerIdentifier":"dry5",
            #         "serviceID":"Midastouchdrycleaners" }
            #     ]}

class GetPoints(APIView):
    """
    Send request to Service Provider's api url and get point value.
    """

    # def get(self, request, format=None):
    #     services = Service.objects.all()
    #     serializer = ServiceSerializer(services, many=True)
    #     return Response(serializer.data)

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
        with open(str( os.getcwd() + '/truffle/build/contracts/LEToken.json'), 'r') as abi_definition:
            self.abi = json.load(abi_definition)['abi']
        self.contract_address = "0xA44C1aE4A46193d8373355849D3fFebf68A8143F"
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.abi)
        self.concise = ConciseContract(self.contract)
        pass

    def mint_token(self, address, amount):
        # tx_hash = self.contract.functions.mint(address, amount).transact({'from': self.w3.eth.accounts[0], 'gas': 1000000, })
        tx_hash = self.concise.mint(address, amount, transact={'from': self.w3.eth.accounts[1], 'gas': 100000})
        self.w3.eth.waitForTransactionReceipt(tx_hash)
        pass

    def post(self, request, format=None):
        # for services
        #     data fetch from service
        #     for service.members
        #         
        services = Service.objects.all()
        for service in services: # all services
                       
            response = fetchAPI(service)
            # members of current service
            memberships = Membership.objects.filter(service=service.pk)

            for membership in memberships:
                # check if this guy is included in the response
                # isFound = False
                for res in response['data']:
                    # if res['customerIdentifier'] == membership.identifier:
                    if res['identifier'] == membership.identifier:
                        # isFound = True
                        membership.points = res['points']
                        membership.rate = res['rate']
                        membership.save()
                        # TODO Update Ethereum balance here
                        break
                
                # if isFound == True:
                #     break
                # member = membership.profile
                # print(membership.identifier)
            

            # print(service.pk)
            # print( Membership.objects.filter(service__pk = 3) )

        return Response(update_everyone(), status=status.HTTP_200_OK)

        # serializer = MembershipSerializer(data=request.data)
        # if serializer.is_valid():
        #     return Response(request.data, status=status.HTTP_201_CREATED)
            # serializer.save()


def sort_func(e):
    return e['real_points']
"""
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
"""

def deduct_from_service(user_id, service_id, amount):
    membership = Membership.objects.filter(profile=user_id, service=service_id).first()
    real_points = membership.calc_real_points()

    if real_points >= amount:
        deducted_amount = real_points - amount
        membership.points = deducted_amount / membership.rate
        membership.save()

        # deduct   amount / membership.rate
        return 0
    membership.points = 0
    membership.save()
    return amount - real_points

def deduct_from_extra_points(user_id, amount):
    profile = UserProfile.objects.get(pk=user_id)
    extra_points = profile.extra_points
    if extra_points >= amount:
        deducted_amount = extra_points - amount
        profile.extra_points = deducted_amount
        profile.save()
        return 0
    profile.extra_points = 0
    profile.save()
    return amount - extra_points

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
        amount = request.data.get('amount', 0)

        error_msg = {
            "details": "Unexpected Error Occured!"
        }

        if user_id and service_id and amount >= 1:
            # Membership.objects.get(pk=1)
            service = Service.objects.get(pk=service_id)
            profile = UserProfile.objects.get(pk=user_id)
            # user first() method to get model object from array
            if service and profile:
                
                customer_status = update_a_customer(pk=user_id)
                amount = Decimal(amount)

                if customer_status['total'] >= amount:
                    # 1. point of this service
                    # 2. extra points
                    # 3. deduct from other services with less real points first
                    # 4. store transaction history
                    # membership_for_current_service = Membership.objects.filter(profile=user_id, service=service_id).first()
                    remaining = amount
                    for idx, membership in enumerate(customer_status['memberships']):
                        if(membership['service'] == service_id):
                            remaining = deduct_from_service(user_id, service_id, remaining)
                            # now remove this membership from snapshot
                            del customer_status['memberships'][idx]
                            break

                    if remaining > 0 and profile.extra_points > 0:
                        remaining = deduct_from_extra_points(user_id, remaining)
                    
                    if remaining > 0:
                        customer_status['memberships'].sort(key = sort_func)
                        for membership in customer_status['memberships']:
                            remaining = deduct_from_service(user_id=membership['profile'], service_id=membership['service'], amount=remaining)
                            if remaining <= 0:
                                break
                    # store history
                    tx = RedeemTransaction(id=None, amount=amount, user=profile.user, service=service)
                    tx.save()

                    updated_customer_status = update_a_customer(pk=user_id)

                    return Response({'update': updated_customer_status}, status=status.HTTP_200_OK)
                else:
                    error_msg['details'] = "Not enough points!"
            else:
                error_msg['details'] = "User or Service not found!"
        else:
            error_msg['details'] = "user, service, amount > 1 fields are required!"
        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)


class TransferPoints(APIView):
    """
    Send request to Service Provider's api url and get point value.
    """

    # def get(self, request, format=None):
    #     services = Service.objects.all()
    #     serializer = ServiceSerializer(services, many=True)
    #     return Response(serializer.data)

    def post(self, request, format=None):
        sender_id = request.data.get('sender', None)
        receiver_phone = request.data.get('receiver_id', None)
        amount = request.data.get('amount', 0)

        error_msg = {
            "details": "Unexpected Error Occured!"
        }

        if sender_id and receiver_phone and amount >= 1:
            # Membership.objects.get(pk=1)
            sender = UserProfile.objects.get(pk=sender_id)
            receiver = UserProfile.objects.get(user__phone=receiver_phone)
            # user first() method to get model object from array
            if receiver and sender:
                
                sender_status = update_a_customer(pk=sender_id)
                amount = Decimal(amount)

                if sender_status['total'] >= amount:
                    # 1. extra_points
                    # 2. deduct from services increasing order of real points
                    # 3. increase receiver's extra_points
                    remaining = amount

                    if remaining > 0 and sender.extra_points > 0:
                        remaining = deduct_from_extra_points(sender_id, remaining)
                    
                    if remaining > 0:
                        sender_status['memberships'].sort(key = sort_func)
                        for membership in sender_status['memberships']:
                            remaining = deduct_from_service(user_id=membership['profile'], service_id=membership['service'], amount=remaining)
                            if remaining <= 0:
                                break
                    
                    receiver.extra_points += amount
                    receiver.save()
                    # store history
                    # tx = RedeemTransaction(id=None, amount=amount, user=sender.user, service=service)
                    # tx.save()

                    updated_customer_status = update_a_customer(pk=sender_id)

                    return Response({'update': updated_customer_status}, status=status.HTTP_200_OK)
                else:
                    error_msg['details'] = "Not enough points!"
            else:
                error_msg['details'] = "Sender or Receiver not found!"
        else:
            error_msg['details'] = "sender, receiver's ID, amount > 1 fields are required!"

        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)


class TotalPoints(APIView):
    """
    Get a user's total points of all services.
    """

    def get(self, request, format=None):
        # services = Service.objects.all()
        # serializer = ServiceSerializer(services, many=True)
        # return Response(serializer.data)
        user = self.request.query_params.get('user', None)
        if user is not None:
            memberships = Membership.objects.filter(profile=user)
            answer = {
                "count" : memberships.count(),
                "total": memberships.aggregate(sum=Coalesce(Sum('points'), 0))['sum']
            }
            return Response(answer)
        return Response({"details": "no user specified!"}, status=status.HTTP_400_BAD_REQUEST)
