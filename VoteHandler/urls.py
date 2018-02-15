from django.urls import path

from . import views

app_name = "VoteHandler"
urlpatterns = [
    #This is for passing in a string into the URL for processing in views.py
    path('', views.home, name='home'),
    path('dispose/', views.dispose, name='dispose'),
    path('result/<int:disposable_name>/<int:category_name>/', views.result, name='result'),
    #path('fromSpeech/', view.from_speech, name='from_speech'),

]