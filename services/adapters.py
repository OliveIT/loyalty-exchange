from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from django.http import HttpResponse, HttpResponseRedirect

class CustomUserAccountAdapter(DefaultAccountAdapter):
    
    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from allauth.account.utils import user_username, user_email, user_field

        data = form.cleaned_data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone')
        email = data.get('email')
        user_email(user, email)
        if first_name:
            user_field(user, 'first_name', first_name)
        if last_name:
            user_field(user, 'last_name', last_name)
        if phone:
            user_field(user, 'phone', phone)
        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()

        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()

        # user = super().save_user(request, user, form, False)
        # user_field(user, 'phone', request.data.get('phone', ''))
        # user.save()
        return user

    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        # url = reverse(
        #     "account_confirm_email",
        #     args=[emailconfirmation.key])
        # ret = build_absolute_uri(
        #     request,
        #     url)
        url = 'http://your.frontend.com/confirmation/'+emailconfirmation.key
        return url

    def respond_email_verification_sent(self, request, user):
        return HttpResponseRedirect('http://your.frontend.com/verification_email_sent/')
