"""Utility functions for use with categorization and disposal

Functions:
    votes_to_percentages -- Returns a descending list of categories with
        confidence percentages
"""
from typing import List, Tuple

from django.conf import settings
from django.db.models import QuerySet

from .models import DisposableVote


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
