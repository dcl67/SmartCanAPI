from django.db import models
from django.contrib.auth.models import User

from VoteHandler.models import Category, Disposable

class CanInfo(models.Model):
    can_id = models.UUIDField(verbose_name='Smartcan ID', unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=None)
    channel_name = models.CharField(max_length=255, null=True, default=None)
    config = models.TextField(max_length=4096)

    @staticmethod
    def new_can_id():
        """Returns a random uuid that is not alredy being used as an ID"""
        id = uuid.uuid4();
        # Odds are astronomically low of this actually colliding. Do we need this check?
        while CanInfo.objects.filter(can_id=uuid).exists():
            id = uuid.uuid4()
        return id

    def __str__(self):
        return str(self.can_id)
    
    def __unicode__(self):
        return self.user.get_full_name()

class Bin(models.Model):
    sId = models.ForeignKey(CanInfo, on_delete=models.CASCADE)
    bin_num = models.CharField(max_length=15)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    #accepted_item1 = models.ForeignKey(Disposable, null=False, blank=False)
    # For proof of concept, but will probably remove these
    
    def __str__(self):
        return str(self.bin_num) + " in " + str(self.sId)
    
    class Meta:
        unique_together = (("sId", "category"),)

#class Owners(models.Model):
#    owner = models.OneToOneField(User, on_delete=models.CASCADE)
#    sId = models.ForeignKey(CanInfo, on_delete=models.CASCADE)
#
#    class Meta:
#        unique_together = (("owner","sId"),)