from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import (email_address_exists, get_username_max_length)
from django.contrib.auth.forms import PasswordResetForm

import phonenumbers

UserModel = get_user_model()

class LoginSerializer(serializers.Serializer):
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

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            # Authentication through email
            if allauth_settings.AUTHENTICATION_METHOD == allauth_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)
        else:
            # Authentication without using allauth
            if email:
                try:
                    auser = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

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
            if allauth_settings.EMAIL_VERIFICATION == allauth_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs

class CustomRegisterSerializer(serializers.Serializer):
    # phone = serializers.CharField(
    #     max_length=get_username_max_length(),
    #     min_length=allauth_settings.USERNAME_MIN_LENGTH,
    #     required=allauth_settings.USERNAME_REQUIRED
    # )
    email = serializers.EmailField(required=True)
    # email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=False)
    first_name = serializers.CharField(required = True, write_only=True)
    last_name = serializers.CharField(required = True, write_only=True)

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
        
        # check if valid phone number format
        try:
            correct_format = phonenumbers.parse(data['phone'], None)
        except phonenumbers.NumberParseException as e:
            raise serializers.ValidationError(_(str(e))) # wrong format
        except KeyError:
            pass # doesn't exist

        # see if existing phone
        # users = get_user_model().objects
        # ret = users.filter(**{'phone' + '__iexact': data['phone']}).exists()
        # if ret:
        #     raise serializers.ValidationError(
        #             _("A user is already registered with this phone number."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'phone': self.validated_data.get('phone', ''),
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class MyPasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()

    password_reset_form_class = PasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {}

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
            ###### USE YOUR TEXT FILE ######
            'email_template_name': 'account/email/password_reset_key_message.txt',
            'subject_template_name': 'account/email/password_reset_key_subject.txt',
        }
        print('##########################################')

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)
