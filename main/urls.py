from django.conf.urls import include, url
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from rest_framework_swagger.views import get_swagger_view


API_TITLE = 'Loyalty Exchange API'
API_DESCRIPTION = 'A Web API for Loyalty Exchange.'
schema_view = get_schema_view(title=API_TITLE)

urlpatterns = [
    url(r'^', include('services.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^schema/$', schema_view),
    # url(r'^docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION))
    url(r'^swagger/$', get_swagger_view(title='API Docs'), name='api_docs'),

# auth
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^account/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/profile/$', RedirectView.as_view(url='/', permanent=True), name='profile-redirect'),
]
