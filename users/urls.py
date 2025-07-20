from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path
from . import views 

urlpatterns = [
    path('', views.UserSearchView.as_view(), name='user_search'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('me/', views.UserProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]