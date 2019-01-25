from django.conf import settings

from django.core import serializers
from django.db.models import Sum
from django.db.models.functions import Coalesce
from services.models import Service, UserProfile, Membership, RedeemTransaction, TransferTransaction
from services.serializers import ServiceSerializer, ProfileSerializer, MembershipSerializer, RedeemTransactionSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import os, sys, inspect
import random
import string

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage

from decimal import Decimal

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from services.helpers.web3helper import web3helper

# from web3.providers.eth_tester import EthereumTesterProvider


# w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/b5d9a6731e714ddda0c3ca38f410b3cf"))
# with open(str( settings.BASE_DIR + '/truffle/build/contracts/LEToken.json'), 'r') as abi_definition:
#     abi = json.load(abi_definition)['abi']
# contract_address = "0xA44C1aE4A46193d8373355849D3fFebf68A8143F"
# contract = w3.eth.contract(address=contract_address, abi=abi)
# concise_contract = ConciseContract(contract)
# nonce = w3.eth.getTransactionCount('0x5ce9454909639D2D17A3F753ce7d93fa0b9aB12E')
# admin_private = "0xaaaaaaaaaaaaaaaaaaaaa"

# def mint_token(address, amount):
#     # tx_hash = self.contract.functions.mint(address, amount).transact({'from': self.w3.eth.accounts[0], 'gas': 1000000, })
#     tx_hash = concise_contract.mint(address, amount, transact={'from': self.w3.eth.accounts[1], 'gas': 100000})
#     self.w3.eth.waitForTransactionReceipt(tx_hash)
#     pass

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
        if not profile.user.is_superuser:
            res.append(update_a_customer(pk = profile.pk, eth=eth))

    # content = JSONRenderer().render(res)
    return res

def call_service_get_api(service):
    # res = requests.get('http://199.192.26.112/API/listmerchantcustomer/',data={ "merchID": 10 })
    # print("service.api_url " + service.api_url)
    status_message = "ok"
    retval = {}
    try:
        # https://stackoverflow.com/questions/9733638/post-json-using-python-requests
        res = requests.get(service.api_url)
        if res.ok:
            # success
            retval = res.json()
            retval = retval['data']
            return (retval, status_message, )
        # error code
        status_message = "something's wrong at service side"
    except (requests.ConnectionError, requests.Timeout, requests.exceptions.HTTPError) as e:
        status_message = str(e)
    except ValueError as e:
        status_message = str(e)
    except KeyError as e:
        status_message = str(e)
    return (retval, status_message, )


def call_service_deduct_api(membership, deduct_amount):
    status_message = "ok"
    try:
        # https://stackoverflow.com/questions/9733638/post-json-using-python-requests
        # https://www.google.com/url?q=http://199.192.26.112/API/listmerchantcustomer/?merchID%3D10%26amount%3D0%26serviceID%3DFacebook%26customerIdentifier%3D%2B120000001&sa=D&source=hangouts&ust=1548481890248000&usg=AFQjCNGnu-b-JPsHSGvqNgK2raGQRCyuRQ
        res = requests.get(url=membership.service.api_url, params = {
            "amount" : deduct_amount,
            "serviceID" : membership.service.title,
            "customerIdentifier": str(membership.profile.user.phone)
        })
        if res.ok:
            # success
            retval = res.json()  # check if json
            retval = retval['data']  # check if there's data field
            return True
        # error code
        status_message = "Something's wrong at service side"
    except (requests.ConnectionError, requests.Timeout, requests.exceptions.HTTPError) as e:
        status_message = str(e)
    except ValueError as e:
        status_message = str(e)
    except KeyError as e:
        status_message = str(e)
    print("!!!! Deduction API failed:\n" + status_message)
    return False


class GetPoints(APIView):
    """
    Send request to Service Provider's api url and get point value.
    """

    # def get(self, request, format=None):
    #     services = Service.objects.all()
    #     serializer = ServiceSerializer(services, many=True)
    #     return Response(serializer.data)

    def get(self, request, format=None):
        # for services
        #     data fetch from service
        #     for service.members
        #         
        # web3helper = Web3Helper()
        # web3helper.mint_token("")
        
        services = Service.objects.all()
        for service in services: # all services

            response, status_message = call_service_get_api(service)
            if status_message != 'ok':
                print(service.title + "'s API is not working.")
                print(status_message)
                continue

            # members of current service
            memberships = Membership.objects.filter(service=service.pk)

            for membership in memberships:
                # check if this guy is included in the response
                # isFound = False
                for res in response:
                    if res['customerIdentifier'] == membership.profile.user.phone:
                    # if res['customerIdentifier'] == membership.identifier:
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

    if real_points == 0:    # don't waste electricity
        return amount # ignore

    if real_points >= amount:
        # deduct   amount / membership.rate from service
        if not call_service_deduct_api(membership, amount / membership.rate):
            return amount # ignore

        deducted_amount = real_points - amount
        membership.points = deducted_amount / membership.rate
        membership.save()

        return 0
    # deduct  membership.points from service
    if not call_service_deduct_api(membership, membership.points):
        return amount  # ignore
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

def create_new_transfer_tx(sender, receiver, amount, current_site="example.com"):
    # https://medium.com/@frfahim/django-registration-with-confirmation-email-bb5da011e4ef
    # otp_code = account_activation_token.make_token(sender)
    otp_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))

    tx = TransferTransaction(
        id=None,
        sender=sender,
        receiver=receiver,
        amount=amount,
        otp_code=otp_code
    )
    tx.save()

    mail_subject = 'Confirm the transfer of your Loyalty Points.'
    message = render_to_string('confirm_transfer_email.html', {
        'sender': sender,
        'receiver': receiver,
        'domain': current_site.domain,
        'amount': amount,
        # 'uid':urlsafe_base64_encode(force_bytes(sender.pk)),
        'token':otp_code,
    })
    email = EmailMessage(
        mail_subject, message, to=[sender.email]
    )
    email.send()
    pass


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
                    current_site = get_current_site(request)
                    create_new_transfer_tx(sender = sender.user, receiver=receiver.user, amount=amount, current_site=current_site)
                    return Response({'message': "Confirmation Email Sent!"}, status=status.HTTP_200_OK)
                else:
                    error_msg['details'] = "Not enough points!"
            else:
                error_msg['details'] = "Sender or Receiver not found!"
        else:
            error_msg['details'] = "sender, receiver's ID, amount > 1 fields are required!"

        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

class ConfirmTransferPoints(APIView):
    """
    Send request to Service Provider's api url and get point value.
    """

    # def get(self, request, format=None):
    #     services = Service.objects.all()
    #     serializer = ServiceSerializer(services, many=True)
    #     return Response(serializer.data)

    def post(self, request, format=None):
        otp = request.data.get('otp', None)

        error_msg = {
            "details": "Unexpected Error Occured!"
        }

        while True:
            if not otp:
                error_msg['details'] = "Confirmation Code is missing!"
                break

            transfer_tx = TransferTransaction.objects.get(otp_code=otp)

            if not transfer_tx:
                error_msg['details'] = "Invalid Confirmation Code!"
                break
            
            if transfer_tx.confirmed:
                error_msg['details'] = "Transfer Transaction is already confirmed!"
                break

            transfer_tx.confirmed = True
            transfer_tx.status = "Confirmed"
            transfer_tx.save()
            
            sender = UserProfile.objects.get(user=transfer_tx.sender)
            receiver = UserProfile.objects.get(user=transfer_tx.receiver)
            # user first() method to get model object from array
            amount = transfer_tx.amount

            sender_status = update_a_customer(pk=transfer_tx.sender)

            if sender_status['total'] < amount:
                error_msg['details'] = "Not enough points!"
                break

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

            sender_status = update_a_customer(pk=transfer_tx.sender)
            return Response(sender_status, status=status.HTTP_200_OK)
        # end-while
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
