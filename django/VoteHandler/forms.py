"""Forms for VoteHandler

Contains:
    CategorizationForm - form for categorizing a disposable
"""
from django.forms import ModelChoiceField, ModelForm, RadioSelect

from .models import Category, DisposableVote


class CategorizationForm(ModelForm):
    """A form for categorizing a disposable"""

    def __init__(self, *args, **kwargs):
        super(CategorizationForm, self).__init__(*args, **kwargs)
        self.fields['disposable'].required = False
        self.fields['count'].required = False

    category = ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label=None,
        widget=RadioSelect
    )

    # override since we don't care if it's unique
    def validate_unique(self):
        pass

    class Meta:
        model = DisposableVote
        fields = '__all__'
