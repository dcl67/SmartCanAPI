import json
import os.path
import random
import secrets
import string
import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from .models import CanInfo, Bin
from .forms import ConfigurationForm, CanConfigurationForm


@login_required
def configlist(request):
    can_id = request.user.username
    if not can_id:
        return render(request, 'landing.html',
                      {'error_message' : 'Please enter your UUID.'}
                     )
    bins = Bin.objects.filter(s_id__can_id=uuid.UUID(can_id).hex)
    can = CanInfo.objects.get(can_id=uuid.UUID(can_id).hex)
    print(bins)
    print(can)
    return render(request, 'list.html', {'bins': bins, 'can': can})


@login_required
def configure_can(request, pk):
    # Skeleton getters for now, we can build these out once we define
    # the SmartCan's models for identifying each unit
    instance = get_object_or_404(CanInfo, pk=pk)
    form = CanConfigurationForm(request.POST or None, instance=instance)
    if form.is_valid():
        can_id = form.cleaned_data['request.user.username']
        owner = form.cleaned_data['owner']
        form.save()
        return HttpResponseRedirect(reverse('Config:configlist'))
    return render(request, 'edit.html', {'form':form})


@login_required
def configure_bins(request):
    form = ConfigurationForm(request.POST)
    this_can = CanInfo.objects.get(can_id=request.user.username)
    if request.method == 'POST':
        if form.is_valid():
            bin_num = form.cleaned_data['bin_num']
            category = form.cleaned_data['category']
            new_bin = Bin.objects.create(s_id=this_can, bin_num=bin_num, category=category,)
            return HttpResponseRedirect(reverse('Config:config_detail', args=(new_bin.id,)))
    else:
        form = ConfigurationForm()
    return render(request, 'configure.html', {'form':form})


@login_required
def edit_bin(request, pk):
    bin_config = get_object_or_404(Bin, pk=pk)
    form = ConfigurationForm(request.POST, instance=bin_config)
    if form.is_valid():
        s_id = form.cleaned_data['request.user.username']
        bin_num = form.cleaned_data['bin_num']
        category = form.cleaned_data['category']
        form.save()
        return HttpResponseRedirect(reverse('Config:config_detail', kwargs={'pk':pk}))
    return render(request, 'configure.html', {'form':form})


class config_detail(DetailView):
    model = Bin
    template_name = 'info.html'


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
        can_uuid = uuid.UUID(str(can_id)).hex
        num_bins = int(request.POST.get('num_bins', 3))

        # TODO: Add admin owner as someone with access over the can 
        owner = request.user

        # Check can doesn't already exist
        if CanInfo.objects.filter(can_id=can_uuid).exists():
            return JsonResponse({'error': f'Can {can_uuid} is already registered'})

        # Generate random pw, 12-16 chars, using letters, digits, and symbols
        pw_chars = string.ascii_letters + string.digits + string.punctuation
        pw_len = random.randint(12, 16)
        pw_str = ''.join(secrets.choice(pw_chars) for _ in range(pw_len))

        # Create account for bin
        can_user = User.objects.create_user(username=can_uuid, password=pw_str)

        # Create bin object owned by the new account
        new_can = CanInfo.objects.create(can_id=can_uuid, owner=can_user)

        # Populate bins
        categories = Bin.DEFAULT_CATEGORIES
        for i in range(num_bins):
            if i < len(categories):
                Bin.objects.create(s_id=new_can, bin_num=i, category=categories[i])
            else:
                Bin.objects.create(s_id=new_can, bin_num=i, category=None)

        return JsonResponse({'password': pw_str})
    else:
        # TODO: Direct to a manual entry form
        return HttpResponse("Manual Entry Form Goes Here")
