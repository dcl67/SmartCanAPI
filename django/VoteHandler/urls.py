from django.urls import path

from . import views

app_name = "VoteHandler"
urlpatterns = [
    #This is for passing in a string into the URL for processing in views.py
    path('', views.home, name='home'),
    path('categorize/<str:disposable_name>', views.categorize, name='categorize'),
    path('dispose/', views.dispose, name='dispose'),
    path('result/<int:disposable_id>/<int:category_id>/', views.result, name='result'),
    path('vote/carousel', views.carousel_vote, name='carousel_vote'),
    path('manual_rotate/', views.manual_rotate, name='manual_rotate'),
]