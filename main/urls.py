from django.conf.urls import include, url
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from rest_framework_swagger.views import get_swagger_view
# from services.forms import RemoteLoginAwareLoginForm

from django.contrib.auth import views
from django.contrib.auth import views as auth_views
from services.views_custom import CustomObtainAuthToken

API_TITLE = 'Loyalty Exchange API'
API_DESCRIPTION = 'A Web API for Loyalty Exchange.'
schema_view = get_schema_view(title=API_TITLE)

####
# login = views.LoginView.as_view(template_name='/home/captainhook/Documents/Projects/wajesmart/real/loyalty-exchange/env/lib/python3.6/site-packages/rest_framework/templates/rest_framework/login.html', authentication_form=RemoteLoginAwareLoginForm)
# login_kwargs = {}
# logout = views.LogoutView.as_view()
####

urlpatterns = [
    url(r'^', include('django.contrib.auth.urls')), #hotfix
    url(r'^', include('services.urls')),

    # url(r'^rest-urls/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^rest-urls/login/$', login, name='auth-login'),

    # url(r'^rest-urls/login/$', auth_views.login, {'template_name': 'rest_framework/login.html', 'authentication_form':RemoteLoginAwareLoginForm}, name='login'),
    # url(r'^rest-urls/logout/$', logout, name='auth-logout'),

    # url(r'^schema/$', schema_view),
    # url(r'^docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION))
    url(r'^swagger/$', get_swagger_view(title='API Docs'), name='api_docs'),

# auth
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/registration/', include('rest_auth.registration.urls')),
    url(r'^auth/new-login/', CustomObtainAuthToken.as_view()),

    # url(r'^account/', include('allauth.urls')),
    # url(r'^accounts/profile/$', RedirectView.as_view(url='/', permanent=True), name='profile-redirect'),

    url(r'^admin/', admin.site.urls),
]
