from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    ClubViewSet,
    LoginView,
    LogoutView,
    CurrentUserView,
    check_username,
    check_email,
    test_db,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'clubs', ClubViewSet, basename='club')

urlpatterns = [
    # Auth endpoints
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('current_user', CurrentUserView.as_view(), name='current_user'),

    # Validation
    path('check_username', check_username, name='check_username'),
    path('check_email', check_email, name='check_email'),

    # DB test route
    path('test-db', test_db, name='test_db'),

    # Include router routes
    path('', include(router.urls)),
] 