from django import forms
from django.forms import ModelForm

from .models import *

class ConfigurationForm(forms.ModelForm):
    class Meta:
        model=Configuration
        fields='__all__'