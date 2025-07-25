from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/address/add/', views.add_address, name='add_address'),
    path('profile/address/<int:pk>/edit/', views.edit_address, name='edit_address'),
    path('profile/address/<int:pk>/delete/', views.delete_address, name='delete_address'),
]
