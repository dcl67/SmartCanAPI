from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views import *

app_name = "Config"
urlpatterns = [
    path('', views.home, name='config_home'),
    path('configlist/', views.configlist, name='configlist'),
    path('configlist/<int:pk>', views.configure_can, name='configure_can'), 
    path('<int:smartcan_id>/configure/submit', views.submit_configuration, name='submit_configure'), # submit view for configure not yet defined
    path('configlist/user', views.UpdateUser, name='edit_user'),
    path('configlist/bin', views.configure_bins, name='configure_bin'),
    path('configlist/bin/<int:pk>', views.config_detail.as_view(), name='config_detail'),
    path('configlist/bin/edit/<int:pk>', views.edit_bin, name='edit_bin'),
    path('<int:smartcan_id>/statistics/', views.statistics, name='statistics'), #statistics view not yet defined

    path('register/', views.registerhtml, name='registerhtml'), #configure not yet defined
    path('register/submit/<uuid:can_id>', views.register, name='register'),

    path('redirect', views.redirect, name='redirect'), #configure not yet defined, probably won't need this
]