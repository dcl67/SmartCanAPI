from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views import *

app_name = "Config"
urlpatterns = [
    path('', views.configlist, name='configlist'),
    path('<int:pk>', views.configure_can, name='configure_can'), 
    path('bin/', views.configure_bins, name='configure_bin'),
    path('bin/<int:pk>', views.config_detail.as_view(), name='config_detail'),
    path('bin/edit/<int:pk>', views.edit_bin, name='edit_bin'),
    #path('<int:smartcan_id>/statistics/', views.statistics, name='statistics'),
    path('register/submit/<uuid:can_id>', views.register, name='register'),
]