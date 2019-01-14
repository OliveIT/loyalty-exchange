from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

STYLES = ['airline', 'mart', 'spa', 'gym', 'taxi']
COUNTRIES = ['US', 'CA', 'DE', 'FR', 'UK']
STYLE_CHOICES = sorted([(item, item) for item in STYLES])
COUNTRY_CHOICES = sorted((item, item) for item in COUNTRIES)

class Service(models.Model):
    title = models.CharField(max_length=100, blank=False, default='')
    description = models.TextField()
    service_type = models.CharField(choices=STYLE_CHOICES, default='airline', max_length=100)
    country = models.CharField(choices=COUNTRY_CHOICES, default='US', max_length=100)
    is_opened = models.BooleanField(default=True)
    # owner = models.ForeignKey(
    #     'auth.User', related_name='services', on_delete=models.CASCADE)
    contact = models.TextField()
    api_url = models.CharField(max_length=300, blank=False, default='')
    created = models.DateTimeField(auto_now_add=True)
    
    # subscribers = models.ManyToManyField(User)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created', )

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
    user = models.OneToOneField(User, primary_key=True, related_name='profile', on_delete=models.CASCADE)
    # custom fields for user
    wallet = models.CharField(max_length=100, null=True)
    company_name = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=100, unique=True, null=True)

    #####
    services = models.ManyToManyField(
        Service,
        through='Membership',
        # through_fields=('profile', 'service'),
        # related_name='members'
    )
    is_active = models.BooleanField(default=True)
    # install_ts = models.DateTimeField(auto_now_add=True)
    # update_ts = models.DateTimeField(auto_now_add=True)
    #####

    def __str__(self):
        return self.user.username + ' at ' + self.company_name ;

@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance=None, created=False, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        print("########### create_profile_for_user")

@receiver(pre_delete, sender=User)
def delete_profile_for_user(sender, instance=None, **kwargs):
    if instance:
        user_profile = UserProfile.objects.get(user=instance)
        user_profile.delete()
        print("########### delete_profile_for_user")

@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance=None, created=False, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        print("########### create_profile_for_user")


class Membership(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='membership')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)#, related_name='membership')

    points = models.IntegerField(default=0)
    identifier = models.CharField(max_length=100, blank=True, default='')
    #date_of_joining = models.DateTimeField()
    install_ts = models.DateTimeField(auto_now_add=True, blank=True)
    update_ts = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.service.title + ' ' + self.profile.username + ' ' + self.points + ' pts'

class CurrencyRate(models.Model):
    currency = models.CharField(default='USD', max_length=100)
    rate = models.CharField(default='1', max_length=100)
    updated_ts = models.DateTimeField(auto_now_add=True, blank=True)
