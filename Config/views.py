from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

def configure(request, smartcanid):
    # Skeleton getters for now, we can build these out once we define 
    # the SmartCan's models for identifying each unit
    instance=get_object_or_404(Configuration, pk=smartcanid)
    form=ConfigurationForm(request.POST or None, instance=instance)
    #if form.is_valid():
        

def submit_configuration(request, smartcanid):
    return HttpResponseRedirect(str(smartcanid)+'/configure/')

def statistics(request, smartcanid):
    instance=get_object_or_404(Configuration, pk=smartcanid)

def register(request, smartcanid):
    instance=get_object_or_404(Configuration, pk=smartcanid)

def redirect(request, smartcanid):
    return HttpResponseRedirect(str(smartcanid)+'/register/')