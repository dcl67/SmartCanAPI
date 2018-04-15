import json
import os.path
import random
import secrets
import string

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from .models import CanInfo, Bin
from .forms import ConfigurationForm, CanConfigurationForm


def home(request):
    return render(request, 'landing.html')


@login_required
def configlist(request):
    can_id = request.POST.get('can_id')
    if not can_id:
        return render(request, 'landing.html',
                      {'error_message' : 'Please enter your UUID.'}
                     )
    bins = Bin.objects.filter(sId__can_id=can_id)
    can = CanInfo.objects.get(can_id=can_id)
    return render(request, 'list.html', {'bins': bins, 'can': can})


@login_required
def configure_can(request, pk):
    # Skeleton getters for now, we can build these out once we define
    # the SmartCan's models for identifying each unit
    instance = get_object_or_404(CanInfo, pk=pk)
    form = CanConfigurationForm(request.POST or None, instance=instance)
    if form.is_valid():
        can_id = form.cleaned_data['can_id']
        owner = form.cleaned_data['owner']
        form.save()
        return HttpResponseRedirect(reverse('Config:configlist'))
    return render(request, 'edit.html', {'form':form})


@login_required
def configure_bins(request):
    form = ConfigurationForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            sId = form.cleaned_data['sId']
            bin_num = form.cleaned_data['bin_num']
            category = form.cleaned_data['category']
            new_bin = Bin.objects.create(sId=sId, bin_num=bin_num, category=category,)
            return HttpResponseRedirect(reverse('Config:config_detail', args=(new_bin.id,)))
    else:
        form = ConfigurationForm()
    return render(request, 'configure.html', {'form':form})


@login_required
def edit_bin(request, pk):
    bin_config = get_object_or_404(Bin, pk=pk)
    form = ConfigurationForm(request.POST, instance=bin_config)
    if form.is_valid():
        s_id = form.cleaned_data
        bin_num = form.cleaned_data['bin_num']
        category = form.cleaned_data['category']
        form.save()
        return HttpResponseRedirect(reverse('Config:config_detail', kwargs={'pk':pk}))
    return render(request, 'configure.html', {'form':form})


class config_detail(DetailView):
    model = Bin
    template_name = 'info.html'


@login_required
def submit_configuration(request, smartcanid):
    return HttpResponseRedirect(str(smartcanid)+'/configure/')


@login_required
def statistics(request, smartcanid):
    """
    Tabled for now
    """
    instance = get_object_or_404(CanInfo, pk=smartcanid)


def registerhtml(request):
    """
    Hosting for the front end of registration
    """
    return render(request, 'register.html')


@login_required
def register(request, can_id):
    """
    POST: 
        Creates a bin object with empty bins that is owned by the 
        logged in account and creates an account for the can.
    
    Arguments:
        can_id {uuid} -- The uuid that doubles as the can ID of the can you
                         want to register
    
    Returns:
        [JSONResponse] -- Contains the password for the newly created can a
                          count
    """

    if request.method == 'POST':
        # Create bin object
        can_uuid = can_id
        num_bins = int(request.POST.get('num_bins'))
        owner = request.user
        CanInfo.objects.create(can_id=can_uuid, owner=owner)

        # Populate bins
        for i in range(num_bins):
            Bin.objects.create(s_id=can_uuid, bin_num=i, category=None)

        # Generate random pw, 12-16 chars, using letters, digits, and symbols
        pw_chars = string.ascii_letters + string.digits + string.punctuation
        pw_len = random.randint(12, 16)
        pw_str = ''.join(secrets.choice(pw_chars) for _ in range(pw_len))

        # Create account for bin
        User.objects.create_user(username=can_uuid, password=pw_str)

        return JsonResponse({'password': pw_str})
    else:
        # TODO: Direct to a manual entry form
        pass


@login_required
def redirect(request, smartcanid):
    return HttpResponseRedirect(str(smartcanid)+'/register/')


def json_reader(request):
    my_path = os.path.abspath(os.path.dirname(__file__))
    json_data = os.path.join(my_path, '../config.json')
    datas = open(json_data).read()
    data = json.dumps(datas)
    print(data)
    return HttpResponse(data)
