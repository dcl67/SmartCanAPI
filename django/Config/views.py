from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.detail import DetailView
import json
import os.path


from .models import CanInfo, Bin
from .forms import ConfigurationForm

def home(request):
    return render(request, 'landing.html')

def configlist(request):
    can_id = request.POST.get('can_id')
    if not can_id:
        return render(request, 'landing.html',
            {'error_message' : 'Please enter your UUID.'}
        )
    bins = Bin.objects.filter(sId__can_id=can_id)
    can = CanInfo.objects.get(can_id=can_id)

    return render(request, 'list.html', {'bins': bins, 'can': can })

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
            new_bin = Bin.objects.create(sId=sId,bin_num=bin_num,category=category,)
            return HttpResponseRedirect(reverse('Config:config_detail', args=(new_bin.id,)))
    else:
        form=ConfigurationForm()
    return render(request,'configure.html', {'form':form})


def edit_bin(request, pk):
    bin_config = get_object_or_404(Bin, pk=pk)
    form = ConfigurationForm(request.POST, instance=bin_config)
    if form.is_valid():
        sID=form.cleaned_data
        bin_num=form.cleaned_data['bin_num']
        category=form.cleaned_data['category']
        form.save()
        return HttpResponseRedirect(reverse('Config:config_detail', kwargs={'pk':pk}))
    return render(request,'configure.html',{'form':form})

#def config_detail(request,pk):
class config_detail(DetailView):
    model = Bin
    template_name='info.html'

def submit_configuration(request, smartcanid):
    return HttpResponseRedirect(str(smartcanid)+'/configure/')

def statistics(request, smartcanid):
    instance=get_object_or_404(CanInfo, pk=smartcanid)

def registerhtml(request):
    """
    Hosting for the front end of registration
    """
    return render(request, 'register.html')

def register(request, can_id):
    """
    Back-end to handle registration of a Smart Can
    """
    # Gonna change this to allow a file to open this, POST the data and save it.
    #instance=get_object_or_404(CanInfo, pk=smartcanid)
    #id_num=request.POST.get('id_number') #might switch this, have it sent over via web-socket from the smart can
    #id_num=UUID.uuid4()
    #bin_num=request.POST.get('number_bins')
    number_bins=int(bin_num)
    #channel_num=request.POST.get('channel_num')
    registered_can=CanInfo.objects.create(can_id=can_id, channel_name=channel_num, config=' ')
    i=0
    while i < number_bins:
        print("num bins are: "+str(number_bins))
        print("i is: "+str(i))
        Bin.objects.create(sId=registered_can,bin_num=i,category=None)
        i+=1
    return HttpResponseRedirect(reverse('Config:configlist'))

def redirect(request, smartcanid):
    return HttpResponseRedirect(str(smartcanid)+'/register/')

def json_reader(request):
    my_path = os.path.abspath(os.path.dirname(__file__))
    json_data = os.path.join(my_path,'../config.json')
    datas = open(json_data).read()
    data = json.dumps(datas)
    print(data)
    return HttpResponse(data)