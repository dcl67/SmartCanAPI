from django.urls import path

from . import views

app_name = "Config"
urlpatterns = [
    path('', views.configlanding, name='configLanding'),
    path('<int:smartcan_id>/configure', views.configure, name='configure'), #configure view not yet defined
    path('<int:smartcan_id>/configure/submit', views.submit_configuration, name='submit_configure'), # submit view for configure not yet defined
    path('<int:smartcan_id>/statistics/', views.statistics, name='statistics'), #statistics view not yet defined
    path('register/<int:smartcan_id>/', views.register, name='register'), #configure not yet defined
    path('redirect', views.redirect, name='redirect'), #configure not yet defined

    path('initialize', views.initialize, name='initialization'), #might be combined with register later
]