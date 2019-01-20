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
