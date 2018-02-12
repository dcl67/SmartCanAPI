from django.urls import path

from VoteHandler.views import *

urlpatterns=[
    #This is for passing in a string into the URL for processing in views.py
    path(r'^recycling/(?P<string>[\w\-]+)/$',recycle_votes,name='recycle_votes'),
    path(r'^compost/(?P<string>[\w\-]+)/$',compost_votes,name='compost_votes'),
    path(r'^recycling/(?P<string>[\w\-]+)/$',landfill_votes,name='landfill_votes'),

]