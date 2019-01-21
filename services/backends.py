from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework import authentication
from rest_framework import exceptions

UserModel = get_user_model()

class CustomAuthBackend(ModelBackend):
    # def authenticate(self, request, phone=None, email=None, password=None, **kwargs):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print("CustomAuthBackend: authenticate")
        print(username)
        print(password)
        print(kwargs)
        user = None
        try:
            # if phone:
            #     user = UserModel.objects.get(phone=phone)
            # if not user and email:
            #     user = UserModel.objects.get(email=email)
            user = UserModel.objects.get(phone=username)
        except UserModel.DoesNotExist:
            pass

        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # UserModel().set_password(password)
            UserModel().set_password(password)

            # raise exceptions.AuthenticationFailed('No such user')

        if not user:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        # return is_active or is_active is None
        if is_active == False :
            return None

        email_address = user.emailaddress_set.get(email=user.email)
        if not email_address.verified:
            # raise exceptions.AuthenticationFailed('Email Not Verified')
            # raise exceptions.ValidationError("###### Email Not Verified")
            return None

        return True