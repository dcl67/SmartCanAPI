from Django import forms
from Django.forms import ModelForm, RadioSelect

from .models import *
from VoteHandler.models import Category

class ConfigurationForm(forms.ModelForm):
    choices = forms.MultipleChoiceField(
        choices = Category.objects.all()
        widget  = forms.CheckboxSelectMultiple,
    )
    class Meta:
        