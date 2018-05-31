"""Views for handling voting and categorization"""

from __future__ import unicode_literals
import collections
from contextlib import suppress
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import EmptyResultSet
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect
from django.views.decorators.http import require_POST

from Config.models import CanInfo, Bin
from .models import Category, Disposable, DisposableVote
from .utils import send_rotate_to_can, votes_to_percentages


@login_required
@require_POST
def dispose(request):
    """View that receives POST requests for disposals from home's form"""
    try:
        user_text = request.POST.get('disposable_item')
        if user_text is None:
            return render(request, 'VoteHandler/home.html',
                          {'error_message' : 'Please enter text.'}
                         )
        disposable = Disposable.objects.get(name=user_text.lower())
    except Disposable.DoesNotExist:
        # Create the object, so we have something to assosciate the votes with
        Disposable.objects.create(name=user_text)
        return redirect('VoteHandler:categorize', disposable_name=user_text)

    # If we don't have any votes, ask the user to categorize
    try:
        top_category = disposable.get_top_category()
    except EmptyResultSet:
        return redirect('VoteHandler:categorize', disposable_name=user_text)

    # Get the top category and redirect to categorization if the system is not confident
    top_category_id = top_category.id
    votes = disposable.get_top_votes()
    percentage_tuples = votes_to_percentages(votes)
    if percentage_tuples[0][1] / 100 < settings.MIN_CONFIDENCE:
        return redirect('VoteHandler:categorize', disposable_name=user_text)

    send_rotate_to_can(user=request.user, bin_num=top_category_id)

    args = (disposable.id, top_category_id)
    url = f"{reverse('VoteHandler:result', args=args)}?{urlencode(percentage_tuples)}"
    return HttpResponseRedirect(url)


@login_required
def categorize(request, disposable_name):
    """View that guides user to selecting the correct category"""
    err_msg, votes = None, None
    try:
        disposeable = Disposable.objects.get(name=disposable_name.lower())
    except Disposable.DoesNotExist:
        err_msg = "The item '{0}' does not exist in the database".format(disposable_name)
    else:
        with suppress(EmptyResultSet):
            votes = {v.category.name: v.count for v in disposeable.get_top_votes()}

    return render(request, 'VoteHandler/categorize.html',
                  {
                      'disposable_name': disposable_name,
                      'error_message': err_msg,
                      'votes': votes
                  }
                 )


@login_required
def home(request):
    """Simple landing page for text entry"""
    bin_num_to_cats = None
    with suppress(CanInfo.DoesNotExist):
        can_instance = CanInfo.objects.get(owner=request.user)
        bins = Bin.objects.filter(s_id__can_id=can_instance.can_id)

        # Ordered dict of bin_num to list of categories
        default_pairs = sorted([(can_bin.bin_num, []) for can_bin in bins], reverse=True)
        bin_num_to_cats = collections.OrderedDict(default_pairs)
        for can_bin in bins:
            bin_num_to_cats[can_bin.bin_num].append(can_bin.category)

    return render(request, 'VoteHandler/home.html', {'bin_num_to_cats': bin_num_to_cats})


@login_required
def result(request, disposable_id, category_id):
    """View that handles displaying the results of a dispose to the user"""
    votes = request.GET
    return render(
        request,
        'VoteHandler/result.html',
        {
            'disposable_name': Disposable.objects.get(id=disposable_id).name,
            'category_name': Category.objects.get(id=category_id).name,
            'votes': sorted(votes.items(), key=lambda x: x[1], reverse=True)
        }
    )

@login_required
@require_POST
def carousel_vote(request):
    """
    A POST view for voting via images
    """
    # Get disposable and category
    data = request.POST
    disposable = Disposable.objects.get(name=data['disp_item'])
    category = Category.objects.get(name=data['vote'])

    # Create with zero votes if it didn't exist
    d_votes, _ = DisposableVote.objects.get_or_create(
        disposable=disposable,
        category=category,
        defaults={'count': 0}
    )

    d_votes.add_votes(settings.CATEGORIZE_VOTE_WEIGHT)
    send_rotate_to_can(user=request.user, bin_num=category.id)

    return redirect('VoteHandler:home')


@login_required
@require_POST
def manual_rotate(request):
    """Rotate to a specified bin from a homepage bin button"""
    bin_instance = Bin.objects.filter(
        s_id__can_id=request.user.username,
        bin_num=request.POST.get('bin')
    )
    if bin_instance.exists():
        send_rotate_to_can(user=request.user, bin_num=bin_instance[0].category.id)

    return redirect('VoteHandler:home')
