from django.urls import path

from . import views
from .views import *

app_name = "Config"
urlpatterns = [
    path('', views.home, name='config_home'),
    path('configlist/', views.configlist, name='configlist'),
    path('<int:smartcan_id>/configure', views.configure, name='configure'), #configure view not yet defined
    path('<int:smartcan_id>/configure/submit', views.submit_configuration, name='submit_configure'), # submit view for configure not yet defined
    path('configure/bin', views.configure_bins, name='configure_bin'),
    path('configure/bin/<int:pk>', views.config_detail.as_view(), name='config_detail'),
    path('configure/bin/edit/<int:pk>', views.edit_bin_config, name='edit_bin'),
    path('<int:smartcan_id>/statistics/', views.statistics, name='statistics'), #statistics view not yet defined

    path('register/', views.registerhtml, name='registerhtml'), #configure not yet defined
    path('register/submit/', views.register, name='register'),

    path('redirect', views.redirect, name='redirect'), #configure not yet defined, probably won't need this

]