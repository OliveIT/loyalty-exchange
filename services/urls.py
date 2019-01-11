from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from services import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'services', views.ServiceViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'currency_rates', views.CurrencyRateViewSet)
router.register(r'profile', views.UserProfileViewSet)
router.register(r'membership', views.MembershipViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls))
]

