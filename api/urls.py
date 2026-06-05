from django.contrib import admin
from django.urls import include, path

from api.views import login_user, logout_user, register_user

urlpatterns = [
    path('register/', register_user),
    path('login/', login_user),
    path('logout/', logout_user),
]