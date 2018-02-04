from django.urls import path

from VoteHandler.views import *

urlpatterns=[
    #This is for passing in a string into the URL for processing in views.py
    path(r'^recycling/(?P<string>[\w\-]+)/$',recycle_votes,name='recycle_votes'),
    path(r'^compost/(?P<string>[\w\-]+)/$',compost_votes,name='compost_votes'),
    path(r'^recycling/(?P<string>[\w\-]+)/$',landfill_votes,name='landfill_votes'),

    #An alternate version I'm playing with for passing in a 
    #Product Key, where you can retrieve the name of the object
    #in views.py
    path(r'^recycling/(?P<pk>\d+)/$',recycle_votes,name='recycle_votes'),
    path(r'^compost/(?P<pk>\d+)/$',compost_votes,name='compost_votes'),
    path(r'^recycling/(?P<pk>\d+)/$',landfill_votes,name='landfill_votes'),

]