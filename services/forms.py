# Didn't use

from django.contrib.auth.forms import AuthenticationForm

class RemoteLoginAwareLoginForm(AuthenticationForm):
    def clean(self):
        cleaned_data = super(RemoteLoginAwareLoginForm, self).clean()
        print("***********RemoteLoginAwareLoginForm")
        print(self.errors)
        if self.errors:  # <==== self.errors is {}, even when login will fail
            # Perform additional checks
            return cleaned_data
