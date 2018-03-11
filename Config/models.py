from django.db import models

from VoteHandler.models import Category, Disposable

class CanInfo(models.Model):
    can_id = models.UUIDField(verbose_name='Smartcan ID', unique=True)
    channel_name = models.CharField(max_length=255, null=True)
    config = models.TextField(max_length=4096) # Do we want three model fields for each of the disposal bins?
    # We can also build these out with 
    # Bin1 = forms.ChoiceField(choices=<disposable methods>, widget=forms.RadioSelect())
    # Or checkboxes to say "This box takes these fields!" Thinking aloud.

    @staticmethod
    def new_can_id():
        """Returns a random uuid that is not alredy being used as an ID"""
        id = uuid.uuid4();
        # Odds are astronomically low of this actually colliding. Do we need this check?
        while CanInfo.objects.filter(can_id=uuid).exists():
            id = uuid.uuid4()
        return id

    def __str__(self):
        return self.can_id

class Bin(models.Model):
    sId = models.ForeignKey(CanInfo, on_delete=models.CASCADE)
    bin_num = models.CharField(max_length=15)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=False, null=False)
    #accepted_item1 = models.ForeignKey(Disposable, null=False, blank=False)
    # For proof of concept, but will probably remove these
    class Meta:
        unique_together = (("sId", "category"),)