from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
# from rest_auth.registration.serializers import RegisterSerializer
from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import (email_address_exists, get_username_max_length)

UserModel = get_user_model()

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_phone(self, phone, password):
        user = None

        if phone and password:
            user = authenticate(username=phone, password=password)
        else:
            msg = _('Must include "phone" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_phone_email(self, phone, email, password):
        user = None

        if email and password:
            user = authenticate(email=email, password=password)
        elif phone and password:
            user = authenticate(username=phone, password=password)
        else:
            msg = _('Must include either "phone" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        phone = attrs.get('phone')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through phone
            elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_phone(phone, password)

            # Authentication through either phone or email
            else:
                user = self._validate_phone_email(phone, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    phone = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if phone:
                user = self._validate_phone_email(phone, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs

"""
class CustomRegisterSerializer(RegisterSerializer):
    # first_name = serializers.CharField(required = True, write_only=True)
    # last_name = serializers.CharField(required = True, write_only=True)
    # birth = serializers.CharField(required = True, write_only=True)

    # company_name = serializers.CharField(required = True, write_only=True)
    # phone = serializers.CharField(required = True, write_only=True)

    # class Meta(RegisterSerializer.Meta):
    #     fields = RegisterSerializer.Meta.fields + ('company_name','phone')

    # def custom_signup(self, request, user):
    #     profile = user.profile
    #     profile.company_name = "asdf"
    #     profile.phone = '2435-4325'
    #     profile.save()

    def get_cleaned_data(self):
        super(CustomRegisterSerializer, self).get_cleaned_data()
        return {
            # 'username': self.validated_data.get('username', ''),
            'email': self.validated_data.get('email', ''),
            'phone': self.validated_data.get('phone', ''),
            'password1': self.validated_data.get('password1', ''),
            # 'first_name': self.validated_data.get('first_name', ''),
            # 'last_name': self.validated_data.get('last_name', ''),
            # 'company_name': self.validated_data.get('company_name', ''),
            # 'birth': self.validated_data.get('birth', ''),
        }

    def custom_signup(self, request, user):
        cleaned = self.get_cleaned_data()
        # profile = user.profile
        # profile.company_name = cleaned['company_name']
        # profile.phone = cleaned['phone']
        # profile.birth = cleaned['birth']
        # profile.save()
        pass
"""

class CustomRegisterSerializer(serializers.Serializer):
    # phone = serializers.CharField(
    #     max_length=get_username_max_length(),
    #     min_length=allauth_settings.USERNAME_MIN_LENGTH,
    #     required=allauth_settings.USERNAME_REQUIRED
    # )

    phone = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    # email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email
    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        
        # see if existing phone
        users = get_user_model().objects
        ret = users.filter(**{'phone' + '__iexact': data['phone']}).exists()
        if ret:
            raise serializers.ValidationError(
                    _("A user is already registered with this phone number."))
        return data

    def custom_signup(self, request, user):
        # cleaned = self.get_cleaned_data()
        # user.phone = cleaned['phone']
        # user.save()
        pass

    def get_cleaned_data(self):
        return {
            'phone': self.validated_data.get('phone', ''),
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
