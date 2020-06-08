"""yapspot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from yap.views import index, tos, custom_signup, password_change
from yapspot.settings import DJANGO_ENV

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns = [
    path('nunyabidness24680/', admin.site.urls),
    url(r'^accounts/password/change/$', password_change, name='password_change'), # override password change success url
    url(r'^custom_signup$', custom_signup, name='custom_signup'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^yap/', include('yap.urls')),
    url(r'^$', index, name='index'),
    url(r'^tos$', tos, name='tos'),
]
