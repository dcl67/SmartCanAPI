"""Utility functions for use with categorization and disposal

Functions:
    votes_to_percentages -- Returns a descending list of categories with
        confidence percentages
"""
from typing import List, Tuple

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import QuerySet

from Config.models import CanInfo
from .models import DisposableVote

def send_rotate_to_can(user: User, bin_num: int) -> bool:
    """Send the rotate command to the bin assosciated with the user

    Arguments:
        user {User} -- The user account the can is logged in as
        bin_num {int} -- The bin number to rotate to

    Returns:
        bool -- True if the command was sent, False otherwise.
    """
    if user is None:
        return False

    try:
        can_info = CanInfo.objects.get(owner=user)
    except CanInfo.DoesNotExist:
        return False

    request_channel = can_info.channel_name
    if request_channel is None:
        return False

    # Send msg to channel synchronously
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
        request_channel,
        {
            "type": "ws.rotate",
            "category": bin_num
        }
    )

    return True


def votes_to_percentages(votes: QuerySet) -> List[Tuple[str, float]]:
    """Returns a descending list of categories with confidence percentages

    Arguments:
        votes {QuerySet} -- DisposableVotes to analyze

    Returns:
        List[Tuple[str, float]] -- list of categories with confidence percentages
            in ('category', percentage) format
    """
    if not isinstance(votes, QuerySet) or votes.model is not DisposableVote:
        raise TypeError('votes must be a QuerySet of DisposableVotes')

    if not votes.exists():
        raise ValueError('votes cannot be empty')

    total = 0
    for vote in votes:
        total += vote.count
    # If there are less than MIN_NORMALIZE_COUNT votes, treat it as less certain
    if total < settings.MIN_NORMALIZE_COUNT:
        total = settings.MIN_NORMALIZE_COUNT
    normalized_dict = {v.category.name: 100*v.count/total for v in votes}
    return sorted(normalized_dict.items(), key=lambda x: x[1], reverse=True)
