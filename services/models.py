from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager

from phonenumber_field.modelfields import PhoneNumberField

class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    first_name = models.CharField(max_length=20, blank=True, default='')
    last_name = models.CharField(max_length=20, blank=True, default='')
    date_joined = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Is the user allowed to have access to the admin',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text= 'Is the user account currently active',
    )
    USERNAME_FIELD = 'phone'
    objects = MyUserManager()
 
    def __str__(self):
        return self.email
 
    def get_full_name(self):
        return self.email
 
    def get_short_name(self):
        return self.email


class UserProfile(models.Model):
    """
    This model contains mainly user's wallet related data
    """

    # one to one relationship with MyUser model
    user = models.OneToOneField(MyUser, primary_key=True, related_name='profile', on_delete=models.CASCADE)

    extra_data = models.DecimalField(default=0, max_digits=16, decimal_places=6)

    # additional fields for user
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email;

@receiver(pre_delete, sender=MyUser)
def delete_profile_for_user(sender, instance=None, **kwargs):
    if instance:
        user_profile = UserProfile.objects.get(user=instance)
        user_profile.delete()

@receiver(post_save, sender=MyUser)
def create_profile_for_user(sender, instance=None, created=False, **kwargs):
    if created:
        #generate eth wallet
        profile, newly = UserProfile.objects.get_or_create(user=instance)
