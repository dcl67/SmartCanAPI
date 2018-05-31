from django import forms
from django.forms import ModelForm, RadioSelect

from .models import *
from VoteHandler.models import Category

class ConfigurationForm(forms.ModelForm):
    class Meta:
        model = Bin
        fields = ['bin_num', 'category',]

class CanConfigurationForm(forms.ModelForm):
    class Meta:
        model = CanInfo
        fields = '__all__'