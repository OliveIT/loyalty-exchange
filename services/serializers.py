from django.contrib.auth.models import User
from rest_framework import serializers

from services.models import Service, Membership


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    # owner = serializers.ReadOnlyField(source='owner.username')
    # highlight = serializers.HyperlinkedIdentityField(
    #     view_name='service-highlight', format='html')

    class Meta:
        model = Service
        fields = ('url', 'id', 'title', 'description', #'highlight', 'owner'
                  'is_opened', 'service_type', 'country')

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

        return super(TeamSerializer, self).update(instance, validated_data)


    def _update_membership(self, instance, validated_data):
        '''
        Update membership data for a team.
        '''
        memberships = self.initial_data.get('memberships')
        if isinstance(membership, list) and len(memberships) >= 1:
            # make a set of incoming membership
            incoming_player_ids = set()

            try:
                for member in memberships:
                    incoming_player_ids.add(member['id'])
            except:
                raise serializers.ValidationError(
                    'id is required field in memberships objects.'
                )

            Membership.objects.filter(
                team_id=instance.id
            ).delete()

            # add merchant member mappings
            Membership.objects.bulk_create(
                [
                    Membership(
                        team_id=instance.id,
                        player_id=player
                    )
                    for player in incoming_player_ids
                ]
            )
            return instance
        else:
            raise serializers.ValidationError(
                    'memberships is not a list of objects'
                )

class UserSerializer(serializers.HyperlinkedModelSerializer):
    services = serializers.HyperlinkedRelatedField(
        many=True, view_name='service-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'services')
