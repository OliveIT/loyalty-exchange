from django.conf import settings

from django.core import serializers
from django.db.models import Sum
from django.db.models.functions import Coalesce
from services.models import Service, UserProfile, Membership, RedeemTransaction, TransferTransaction, MyUser
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


def recalc_a_customer(pk, eth=False):
    serializer = ProfileSerializer(UserProfile.objects.get(pk=pk))

    # swallow copy?
    profile_data = dict(serializer.data)
    total = Decimal(profile_data['extra_points'])
    for membership in profile_data['memberships']:
        membership['real_points'] = Decimal(membership['points']) * Decimal(membership['rate'])
        total += Decimal(membership['real_points'])
    profile_data['total'] = total

    # remove useless properties
    del profile_data['services']

    # update via web3
    if eth == True:
        token_balance = web3helper.get_balance(profile_data['eth_public_key'])
        new_balance = round(total * 10000 )

        if abs(token_balance - new_balance) >= 1:    #ignore small difference
            print('Address: ' + profile_data['eth_public_key'] + 'Original : ' + str(token_balance) + ', New : ' + str(new_balance) + ', User: ' + str(profile_data['phone']) )
            web3helper.set_token(profile_data['eth_public_key'], new_balance)

        pass

    return profile_data


def recalc_everyone(eth=False):
    res = []
    for profile in UserProfile.objects.all():
        if not profile.user.is_superuser:
            res.append(recalc_a_customer(pk = profile.pk, eth=eth))

    # content = JSONRenderer().render(res)
    return res


def update_everyone(eth=False):
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
            isFound = False
            for res in response:
                if res['customerIdentifier'] == membership.identifier:
                    isFound = True
                    membership.points = res['points']
                    membership.rate = res['rate']
                    membership.save()
                    break
            if not isFound:
                membership.points = 0
                membership.save()


def call_service_get_api(service):
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
    except:
        status_message = "unknown error"
    return (retval, status_message, )


def call_service_deduct_api(membership, deduct_amount):
    status_message = "ok"
    try:
        # https://stackoverflow.com/questions/9733638/post-json-using-python-requests
        # https://www.google.com/url?q=http://199.192.26.112/API/listmerchantcustomer/?merchID%3D10%26amount%3D0%26serviceID%3DFacebook%26customerIdentifier%3D%2B120000001&sa=D&source=hangouts&ust=1548481890248000&usg=AFQjCNGnu-b-JPsHSGvqNgK2raGQRCyuRQ
        res = requests.get(url=membership.service.api_url, params = {
            "amount" : deduct_amount,
            "serviceID" : membership.service.title,
            "customerIdentifier": str(membership.identifier)
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
    except:
        status_message = "unknown error"
    print("!!!! Deduction API failed:\n" + status_message)
    return False


class GetPoints(APIView):
    """
    Send request to Service Provider's api url and get point value.
    """

    def get(self, request, format=None):
        update_everyone()
        return Response(recalc_everyone(eth=False), status=status.HTTP_200_OK)


def sort_func(e):
    return e['real_points']


def deduct_from_service(membership_id, amount):
    membership = Membership.objects.get(pk=membership_id)
    real_points = membership.calc_real_points()

    if real_points == 0:    # don't waste electricity
        return amount # ignore

    if real_points >= amount:
        # deduct amount / membership.rate from service
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
    Deduct points form Service and DB
    """

    def post(self, request, format=None):
        user_id = request.data.get('user', None)
        service_id = request.data.get('service', None)
        amount = request.data.get('amount', 0)
        mandatory = request.data.get('mandatory', None)

        error_msg = {
            "details": "Unexpected Error Occured!"
        }

        while True:
            if not (user_id >= 1 and amount >= 1 and mandatory != None):
                error_msg['details'] = "User, Amount, Mandatory fields are required!"
                break

            if amount < 1:
                error_msg['details'] = "Amount >= 1"
                break
            
            if mandatory != False and mandatory != True:
                error_msg['details'] = "Mandatory field is invalid"
                break
            
            try:
                profile = UserProfile.objects.get(pk=user_id)
            except UserProfile.DoesNotExist:
                profile = None

            if not profile:
                error_msg['details'] = "User not found!"
                break

            # fetch Service API
            update_everyone()

            customer_status = recalc_a_customer(pk=user_id)
            amount = Decimal(amount)

            customer_memberships = customer_status['memberships']
            remaining = amount

            if mandatory == True:
                if not service_id > 1:
                    error_msg['details'] = "Service field is required!"
                    break

                try:
                    service = Service.objects.get(pk=service_id)
                except Service.DoesNotExist:
                    service = None

                if not service:
                    error_msg['details'] = "Service not found!"
                    break
                
                service_found = False
                total_membership_points = 0
                customer_memberships = []
                for idx, membership in enumerate(customer_status['memberships']):
                    if membership['service'] == service_id:
                        service_found = True
                        customer_memberships.append(membership)
                        total_membership_points += membership['real_points']

                if service_found == False:
                    error_msg['details'] = "This customer is not a member of the service!"
                    break

                if total_membership_points < amount:
                    error_msg['details'] = "Not enough points!"
                    break

                # store history
                tx = RedeemTransaction(id=None, amount=amount, user=profile.user, service=service)

            else:

                if customer_status['total'] < amount:
                    error_msg['details'] = "Not enough points!"
                    break
                
                # 1. point of this service
                # 2. extra points
                # 3. deduct from other services with less real points first
                # 4. store transaction history

                if profile.extra_points > 0:
                    remaining = deduct_from_extra_points(user_id, remaining)

                # store history
                tx = RedeemTransaction(id=None, amount=amount, user=profile.user, service=None)

            if remaining > 0:
                customer_memberships.sort(key = sort_func)
                for membership in customer_memberships:
                    remaining = deduct_from_service(membership_id=membership['id'], amount=remaining)
                    if remaining <= 0:
                        break

            tx.save()

            updated_customer_status = recalc_a_customer(pk=user_id)

            return Response({ 'result': 'ok', 'update': updated_customer_status}, status=status.HTTP_200_OK)
            
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
        'token':otp_code,
    })
    email = EmailMessage(
        mail_subject, message, to=["captainhook99999@hotmail.com", "ozigbochidozie@gmail.com", sender.email,]
    )
    email.send()
    pass


class TransferPoints(APIView):
    """
    Send points to other user
    """

    def post(self, request, format=None):
        sender_id = request.data.get('sender', None)
        receiver_phone = request.data.get('receiver_id', None)
        amount = request.data.get('amount', 0)

        error_msg = {
            "details": "Unexpected Error Occured!"
        }

        if sender_id and receiver_phone and amount >= 1:
            # Membership.objects.get(pk=1)
            try:
                sender = UserProfile.objects.get(pk=sender_id)
            except UserProfile.DoesNotExist:
                sender = None

            try:
                receiver = UserProfile.objects.get(user__phone=receiver_phone)
            except UserProfile.DoesNotExist:
                receiver = None

            # user first() method to get model object from array
            if receiver and sender:
                # fetch Service API
                update_everyone()

                sender_status = recalc_a_customer(pk=sender_id)
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
            error_msg['details'] = "Sender, Receiver's ID, Amount >= 1 fields are required!"

        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

class ConfirmTransferPoints(APIView):
    """
    Confirm transfer points transaction
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

            try:
                transfer_tx = TransferTransaction.objects.get(otp_code=otp)
            except TransferTransaction.DoesNotExist:
                transfer_tx = None

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

            # fetch Service API
            update_everyone()

            sender_status = recalc_a_customer(pk=transfer_tx.sender)

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
                    remaining = deduct_from_service(membership_id=membership['id'], amount=remaining)
                    if remaining <= 0:
                        break
            
            receiver.extra_points += amount
            receiver.save()

            sender_status = recalc_a_customer(pk=transfer_tx.sender)
            return Response(sender_status, status=status.HTTP_200_OK)
        # end-while
        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)


class TotalPoints(APIView):
    """
    Get a user's total points of all services.
    """

    def get(self, request, format=None):
        user_id = self.request.query_params.get('user', None)
        if user_id is not None:
            try:
                MyUser.objects.get(pk=user_id)
                return Response(recalc_a_customer(pk=user_id), status=status.HTTP_200_OK)
            except:
                return Response({"details": "User not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response(recalc_everyone(), status=status.HTTP_200_OK)
