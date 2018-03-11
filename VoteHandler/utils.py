from django.conf import settings

from .models import DisposableVote

def votes_to_percentages(QuerySet_votes):
    """
    Takes a QuerySet of DisposableVote and returns a list of categories 
    with confidence percentages in of the form ('category', percentage) in 
    descending order
    """
    total = 0
    for vote in QuerySet_votes:
        total += vote.count
    # If there are less than MIN_NORMALIZE_COUNT votes, treat it as less certain
    if total < settings.MIN_NORMALIZE_COUNT: 
        total = settings.MIN_NORMALIZE_COUNT
    d = {v.category.name: v.count/total for v in QuerySet_votes} 
    return sorted(d.items(), key=lambda x: x[1]/total, reverse=True)