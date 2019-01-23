from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter

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
