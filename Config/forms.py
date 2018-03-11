from Django import forms
from Django.forms import ModelForm, RadioSelect

from .models import *
from VoteHandler.models import Category

class ConfigurationForm(forms.ModelForm):
    choices = forms.ChoiceField(
        choices = Category.objects.all(),
        widget  = forms.ChoiceField,
    )
    class Meta:
        model = Bin