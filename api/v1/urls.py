from django.urls import path, include
from accounts.urls import auth_patterns, user_patterns

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('users/', include(user_patterns)),
]