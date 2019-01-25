from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager

from phonenumber_field.modelfields import PhoneNumberField
# to generate eth wallet
import random
import string
from decimal import Decimal
from eth_account import Account

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
    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    # phone = models.CharField(validators=[phone_regex], max_length=17, unique=True, null=True) # validators should be a list
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    first_name = models.EmailField(max_length=100, blank=True, default='')
    last_name = models.EmailField(max_length=100, blank=True, default='')
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


STYLES = ['airline', 'mart', 'spa', 'gym', 'taxi']
COUNTRIES = ['US', 'CA', 'DE', 'FR', 'UK']
STYLE_CHOICES = sorted([(item, item) for item in STYLES])
COUNTRY_CHOICES = sorted((item, item) for item in COUNTRIES)

class Service(models.Model):
    title = models.CharField(max_length=100, blank=False, null=True, unique=True)
    description = models.TextField()
    service_type = models.CharField(blank=False, max_length=100, default='')
    country = models.CharField(blank=False, max_length=100, default='')
    is_opened = models.BooleanField(default=True)
    # owner = models.ForeignKey(
    #     'auth.User', related_name='services', on_delete=models.CASCADE)
    contact = models.TextField()
    api_url = models.CharField(max_length=300, blank=False, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

    # class Meta:
    #     ordering = ('created_at', )

    # def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a contact HTML
        representation of the description service.
        """
        # lexer = get_lexer_by_name(self.service_type)
        # is_opened = self.is_opened and 'table' or False
        # options = self.title and {'title': self.title} or {}
        # formatter = HtmlFormatter(
        #     country=self.country, is_opened=is_opened, full=True, **options)
        # self.contact = highlight(self.description, lexer, formatter)

        # super(Service, self).save(*args, **kwargs)


class UserProfile(models.Model):
    ## FIXME on_delete really required?
    user = models.OneToOneField(MyUser, primary_key=True, related_name='profile', on_delete=models.CASCADE)
    # custom fields for user
    company_name = models.CharField(max_length=100, blank=True, default='')
    eth_public_key = models.CharField(max_length=100, blank=True, default='')
    eth_secret_key = models.CharField(max_length=100, blank=True, default='')

    extra_points = models.DecimalField(default=0, max_digits=16, decimal_places=6)

    #####
    services = models.ManyToManyField(
        Service,
        through='Membership',
        # through_fields=('profile', 'service'),
        related_name='members'
    )
    is_active = models.BooleanField(default=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now_add=True)
    #####

    def __str__(self):
        return self.user.email;

@receiver(pre_delete, sender=MyUser)
def delete_profile_for_user(sender, instance=None, **kwargs):
    if instance:
        user_profile = UserProfile.objects.get(user=instance)
        user_profile.delete()
        print("-------- delete_profile_for_user")

@receiver(post_save, sender=MyUser)
def create_profile_for_user(sender, instance=None, created=False, **kwargs):
    if created:
        entropy = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(50))
        account = Account.create(entropy)
        profile, newly = UserProfile.objects.get_or_create(user=instance, eth_public_key = account.address, eth_secret_key = account.privateKey.hex())
        print("########### create_profile_for_user")


class Membership(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='membership')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)#, related_name='membership')

    # points = models.IntegerField(default=0)
    points = models.DecimalField(default=0, max_digits=16, decimal_places=6)
    rate = models.DecimalField(default=0, max_digits=16, decimal_places=6)
    identifier = models.CharField(max_length=100, blank=True, default='')
    #date_of_joining = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.service.title + ' ' + self.profile.email + ' ' + self.points + ' pts'
    class Meta:
        unique_together = (('profile', 'service'),)

    def calc_real_points(self):
        return Decimal(self.points) * Decimal(self.rate)

class CurrencyRate(models.Model):
    currency = models.CharField(default='USD', max_length=100)
    rate = models.CharField(default='1', max_length=100)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True)

class RedeemTransaction(models.Model):
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=16, decimal_places=6)
    tx_hash = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

class TransferTransaction(models.Model):
    sender = models.ForeignKey(MyUser, related_name="sending_user", on_delete=models.CASCADE)
    receiver = models.ForeignKey(MyUser, related_name="receiving_user", on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=16, decimal_places=6)
    confirmed = models.BooleanField (
        'confirmed',
        default=False,
        help_text= 'User should click the link sent to their email',
    )
    otp_code = models.CharField(max_length=100, blank=False)
    status = models.CharField(max_length=100, blank=False, default='Unconfirmed')
    burn_tx_hash = models.CharField(max_length=100, blank=True, default='')
    mint_tx_hash = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
