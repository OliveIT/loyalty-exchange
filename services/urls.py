from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from services import views
from services import views_custom

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'profile', views.UserProfileViewSet)
router.register(r'service', views.ServiceViewSet)
router.register(r'membership', views.MembershipViewSet)
router.register(r'currency_rate', views.CurrencyRateViewSet)
router.register(r'redeem_transactions', views.RedeemTransactionViewSet)
# router.register(r'transfer_transactions', views.TransferTransactionViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^getpoints', views_custom.GetPoints.as_view()),
    url(r'^synctokens', views_custom.SyncTokens.as_view()),
    url(r'^redeempoints', views_custom.RedeemPoints.as_view()),
    url(r'^totalpoints', views_custom.TotalPoints.as_view()),
    url(r'^transferpoints', views_custom.TransferPoints.as_view()),
    url(r'^confirm_transferpoints', views_custom.ConfirmTransferPoints.as_view(), name='confirm_transfer'),
]

