from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import CanInfo, Bin
from .forms import ConfigurationForm

def home(request):
    return render(request, 'landing.html')

def configlist(request):
    can_id = request.POST.get('can_id')
    print(can_id)
    if not can_id:
        return render(request, 'landing.html',
            {'error_message' : 'Please enter text.'}
        )
    can = CanInfo.objects.filter(can_id=can_id.lower())



def configure(request, smartcan_id):
    # Skeleton getters for now, we can build these out once we define 
    # the SmartCan's models for identifying each unit
    instance=get_object_or_404(CanInfo, pk=smartcan_id)
    form=ConfigurationForm(request.POST or None, instance=instance)
    print(form)


def configure_bins(request):
    form = ConfigurationForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            sId=form.cleaned_data['sId']
            bin_num=form.cleaned_data['bin_num']
            category=form.cleaned_data['category']
            Bin.objects.create(sId=sId,bin_num=bin_num,category=category,)
            return HttpResponseRedirect(reverse('config_detail', kwargs={'pk':pk}))
    else:
        form=ConfigurationForm()
    return render(request,'configure.html', {'form':form})


def edit_bin_config(request, pk):
    bin_config = get_object_or_404(Bin, pk=pk)
    form = ConfigurationForm(request.POST, instance=bin_config)
    if form.is_valid():
        sID=form.cleaned_data
        bin_num=form.cleaned_data['bin_num']
        category=form.cleaned_data['category']
        form.save()
        return HttpResponseRedirect(reverse('config_detail', kwargs={'pk':pk}))
    return render(request,'configure.html',{'form':form})

def bin_config_detail(request, pk):
    configuration=get_object_or_404(Bin,pk=pk)
    context = {
        'sId':sId,
        'bin_num':bin_num,
        'category':category,
    }
    return render(request,'templates/info.html',context=context)

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