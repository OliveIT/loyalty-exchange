# from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from services.models import Service, Membership, CurrencyRate, MyUser, UserProfile
from rest_auth.serializers import UserDetailsSerializer

class UserSerializer(serializers.ModelSerializer):

    # company_name = serializers.CharField(source="profile.company_name")
    phone = serializers.CharField()
    # birth = serializers.CharField(source="profile.birth")

    class Meta():
        model = MyUser
        fields = ('pk', 'email', 'phone') # 'first_name', 'last_name')
        # fields = UserDetailsSerializer.Meta.fields + ('phone', ) #, 'company_name', 'birth')
        read_only_fields = ('email',)

    """
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        # company_name = profile_data.get('company_name')
        phone = profile_data.get('phone')
        # birth = profile_data.get('birth')
        ## initialize super base class
        instance = super(UserSerializer, self).update(instance, validated_data)

        # get and update user profile
        profile = instance.profile
        if profile_data:
            # if company_name:
            #     profile.company_name = company_name
            if phone:
                profile.phone = phone
            # if birth:
            #     profile.birth = birth
            profile.save()
        return instance

    def destroy(self, request, pk=None, **kwargs):
        request.user.is_active = False
        request.user.save()
        return Response(status=204)
    """



# class UserProfileSerializer(serializers.HyperlinkedModelSerializer)
#     class Meta:
#         model = Service
#         fields = ('url', 'id', 'title', 'description', #'highlight', 'owner'
#                   'is_opened', 'service_type', 'country', 'subscribers')


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    # owner = serializers.ReadOnlyField(source='owner.username')
    # highlight = serializers.HyperlinkedIdentityField(
    #     view_name='service-highlight', format='html')

    class Meta:
        model = Service
        fields = ('url', 'id', 'title', 'description', #'highlight', 'owner'
                  'service_type', 'country','is_opened', 'api_url' )#, 'subscribers')

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

class MembershipSerializer(serializers.HyperlinkedModelSerializer):
    # service = ServiceSerializer()   # to inlude details of service
    class Meta:
        model = Membership
        # fields = '__all__'
        fields = ('url', 'identifier', 'points', 'profile', 'service' )


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    email = serializers.ReadOnlyField(source='user.email')
    services = ServiceSerializer(many=True, read_only=True)
    memberships = MembershipSerializer(source='membership', many=True, read_only=True)
    class Meta:
        model = UserProfile
        fields = ('user_id', 'email', 'memberships', 'services')
        # 'company_name',  'wallet', 'is_active',
        depth = 1

"""
    def update(self, instance, validated_data):
        '''
        Cutomize the update function for the serializer to update the
        related_field values.
        '''
        membership_data = validated_data.get('services')
        profile = instance
        memberships = profile.memberships
        print(memberships)
        if 'memberships' in validated_data:
            instance = self._update_membership(instance, validated_data)

            # remove memberships key from validated_data to use update method of
            # base serializer class to update model fields
            validated_data.pop('memberships', None)

        return super(ProfileSerializer, self).update(instance, validated_data)
"""
    # def _update_membership(self, instance, validated_data):
    #     '''
    #     Update membership data for a service.
    #     '''
    #     memberships = self.initial_data.get('memberships')
    #     ## typo??
    #     if isinstance(memberships, list) and len(memberships) >= 1:
    #         # make a set of incoming membership
    #         incoming_service_ids = set()

    #         try:
    #             for member in memberships:
    #                 incoming_customer_ids.add(member['id'])
    #         except:
    #             raise serializers.ValidationError(
    #                 'id is required field in memberships objects.'
    #             )

    #         Membership.objects.filter(
    #             service_id=instance.id
    #         ).delete()

    #         # add merchant member mappings
    #         Membership.objects.bulk_create(
    #             [
    #                 Membership(
    #                     service_id=instance.id,
    #                     customer_id=customer
    #                 )
    #                 for customer in incoming_customer_ids
    #             ]
    #         )
    #         return instance
    #     else:
    #         raise serializers.ValidationError(
    #                 'memberships is not a list of objects'
    #             )
