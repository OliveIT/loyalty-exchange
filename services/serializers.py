from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from services.models import Service, Membership, CurrencyRate
from rest_auth.serializers import UserDetailsSerializer

class UserSerializer(UserDetailsSerializer):

    company_name = serializers.CharField(source="userprofile.company_name")
    phone = serializers.CharField(source="userprofile.phone")

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ('company_name','phone')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('userprofile', {})
        company_name = profile_data.get('company_name')
        phone = profile_data.get('phone')

        instance = super(UserSerializer, self).update(instance, validated_data)

        # get and update user profile
        profile = instance.userprofile
        if profile_data:
            if company_name:
                profile.company_name = company_name
            if phone:
                profile.phone = phone
            profile.save()
        return instance

    def destroy(self, request, pk=None, **kwargs):
        request.user.is_active = False
        request.user.save()
        return Response(status=204)


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    # owner = serializers.ReadOnlyField(source='owner.username')
    # highlight = serializers.HyperlinkedIdentityField(
    #     view_name='service-highlight', format='html')

    class Meta:
        model = Service
        fields = ('url', 'id', 'title', 'description', #'highlight', 'owner'
                  'is_opened', 'service_type', 'country', 'subscribers')

    """
    @transaction.atomic
    def update(self, instance, validated_data):
        '''
        Cutomize the update function for the serializer to update the
        related_field values.
        '''

        if 'memberships' in validated_data:
            instance = self._update_membership(instance, validated_data)

            # remove memberships key from validated_data to use update method of
            # base serializer class to update model fields
            validated_data.pop('memberships', None)

        return super(ServiceSerializer, self).update(instance, validated_data)


    def _update_membership(self, instance, validated_data):
        '''
        Update membership data for a service.
        '''
        memberships = self.initial_data.get('memberships')
        ## typo??
        if isinstance(memberships, list) and len(memberships) >= 1:
            # make a set of incoming membership
            incoming_customer_ids = set()

            try:
                for member in memberships:
                    incoming_customer_ids.add(member['id'])
            except:
                raise serializers.ValidationError(
                    'id is required field in memberships objects.'
                )

            Membership.objects.filter(
                service_id=instance.id
            ).delete()

            # add merchant member mappings
            Membership.objects.bulk_create(
                [
                    Membership(
                        service_id=instance.id,
                        customer_id=customer
                    )
                    for customer in incoming_customer_ids
                ]
            )
            return instance
        else:
            raise serializers.ValidationError(
                    'memberships is not a list of objects'
                )
    """

# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     services = serializers.HyperlinkedRelatedField(
#         many=True, view_name='service-detail', read_only=True)

#     class Meta:
#         model = User
#         fields = ('url', 'id', 'username', 'services')

# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ('url', 'id',  'username', 'email', 'first_name', 'last_name')

class CurrencyRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyRate
        fields = ('id',  'currency', 'rate' )

class MembershipSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='member.id')
    name = serializers.ReadOnlyField(source='member.name')

    class Meta:
        model = Membership
        fields = ('id', 'name', 'role')
