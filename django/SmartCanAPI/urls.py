"""SmartCanAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('VoteHandler.urls')),
    path('config/', include('Config.urls')),

    #User views
    #Not defining a sign-up view
    #Will call this a paid service, thus we will manually create Django accounts for users and provide them logins
    #accounts/password_reset can deal with resetting passwords
    path('accounts/', include('django.contrib.auth.urls')),
]

admin.site.site_header = ("Smart Can Admin")
admin.site.site_title = ("Smart Can Admin")