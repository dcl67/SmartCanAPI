from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from .models import CanInfo, Bin

def configlanding(request):
    return HttpResponse('foo')

def configure(request, smartcan_id):
    # Skeleton getters for now, we can build these out once we define 
    # the SmartCan's models for identifying each unit
    instance=get_object_or_404(CanInfo, pk=smartcan_id)
    form=ConfigurationForm(request.POST or None, instance=instance)
    if request.method=='POST':
        if form.is_valid():
            category=form.cleaned_data['category']
            return HttpResponseRedirect(reverse('config_detail', kwargs={'pk':pk}))
    else:
        form=ConfigurationForm()
    return render(request,'templates/configure.html', {'form':form})
    #if form.is_valid():
        
def config_detail(request, pk):
    

def submit_configuration(request, smartcanid):
    return HttpResponseRedirect(str(smartcanid)+'/configure/')

def statistics(request, smartcanid):
    instance=get_object_or_404(CanInfo, pk=smartcanid)

def register(request, smartcanid):
    instance=get_object_or_404(CanInfo, pk=smartcanid)

def redirect(request, smartcanid):
    return HttpResponseRedirect(str(smartcanid)+'/register/')

def initialize(request):
    # Considering moving all of this under register
    #TODO: make front end logic to pass the number of bins entered into this view
    num_bins = 'foo' # later, get this number from the form
    uuid = 'bar'
    i=0
    while i<num_bins:
        Bins.objects.create(sId= uuid, bin_num=i, categor=None)
        i=i+1