from django.db import models
from django.contrib.auth.models import User

from VoteHandler.models import Category, Disposable

class CanInfo(models.Model):
    can_id = models.UUIDField(verbose_name='Smartcan ID', unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=None)
    channel_name = models.CharField(max_length=255, null=True, default=None)
    config = models.TextField(max_length=4096)

    def __str__(self):
        return str(self.can_id)

    def __unicode__(self):
        return self.user.get_full_name()

class Bin(models.Model):
    s_id = models.ForeignKey(CanInfo, on_delete=models.CASCADE, db_column='s_id')
    bin_num = models.CharField(max_length=15)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    #accepted_item1 = models.ForeignKey(Disposable, null=False, blank=False)
    # For proof of concept, but will probably remove these

    def __str__(self):
        return str(self.bin_num) + " in " + str(self.s_id)

    class Meta:
        unique_together = (("s_id", "category"),)

#class Owners(models.Model):
#    owner = models.OneToOneField(User, on_delete=models.CASCADE)
#    sId = models.ForeignKey(CanInfo, on_delete=models.CASCADE)
#
#    class Meta:
#        unique_together = (("owner","sId"),)
