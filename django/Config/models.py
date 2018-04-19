"""Config's models

    Models:
        CanInfo -- represents a SmartCan instance and related info
        Bin -- bin ownership and category
"""

from django.db import models
from django.contrib.auth.models import User

from VoteHandler.models import Category

class CanInfo(models.Model):
    """A model that represents a SmartCan instance and related info

    Attributes:
        can_id {uuid} -- The uuid of the can. Should match the can username
        owner {User} -- The can's user account that is only for this can
        channel_name {str} -- Channel used to find correct websocket via channels
        config {str} -- A TextField that can store additional information
    """

    can_id = models.UUIDField(verbose_name='Smartcan ID', unique=True)
    # TODO: Rename owner to indicate that this is a can account not an owner
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=None)
    channel_name = models.CharField(max_length=255, null=True, default=None)
    config = models.TextField(max_length=4096)

    def __str__(self):
        return str(self.can_id)

    def __unicode__(self):
        return self.user.get_full_name()

class Bin(models.Model):
    """Model for bin ownership and category

    Attributes:
        s_id {CanInfo} -- The can that the bin is part of
        bin_num {str} -- The bin number with a can
        category {Category} -- A category that the bin can accept

    Note:
        There can be multiple categories per s_id and bin_num combo, allowing
        one bin to accept multiple categories of items

    Restrictions:
        's_id' and 'category' have unique_together
    """

    s_id = models.ForeignKey(CanInfo, on_delete=models.CASCADE, db_column='s_id')
    # TODO: bin_num should be an integer, not a string
    bin_num = models.CharField(max_length=15)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.bin_num) + " in " + str(self.s_id)

    class Meta:
        unique_together = (("s_id", "category"),)

# TODO: Re-add the owners table
#class Owners(models.Model):
#    owner = models.OneToOneField(User, on_delete=models.CASCADE)
#    sId = models.ForeignKey(CanInfo, on_delete=models.CASCADE)
#
#    class Meta:
#        unique_together = (("owner","sId"),)
