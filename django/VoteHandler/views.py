# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib.parse

from django.conf import settings
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from .forms import CategorizationForm
from .models import Category, Disposable, DisposableVote
from .utils import votes_to_percentages

# TODO: Write some tests!

def dispose(request):
    """View that receives POST requests for disposals from home's form"""
    try:
        user_text = request.POST.get('disposable_item', '')
        if not user_text:
            return render(request, 'VoteHandler/home.html',
                {'error_message' : 'Please enter text.'}
            )
        disposeable = Disposable.objects.get(name=user_text.lower())
    except Disposable.DoesNotExist:
        # Create the object, so we have something to assosciate the votes with
        new_disposable = Disposable(name=user_text)
        new_disposable.save() # TODO: Error handling?
        return redirect('VoteHandler:categorize', disposable_name=user_text)

    top_category = disposeable.get_top_category()
    if not top_category:
        return redirect('VoteHandler:categorize', disposable_name=user_text)

    top_category_id = disposeable.get_top_category().id
    votes = disposeable.get_top_votes()
    percentage_tuples = votes_to_percentages(votes)
    if percentage_tuples[0][1] < settings.MIN_CONFIDENCE:
        return redirect('VoteHandler:categorize', disposable_name=user_text)

    # TODO: This still feels gross, find a way to handle better
    return HttpResponseRedirect("{0}?{1}".format(
        reverse('VoteHandler:result', args=(disposeable.id, top_category_id)), 
        urllib.parse.urlencode(percentage_tuples)
        ))

def categorize(request, disposable_name):
    """View that guides user to selecting the correct category"""
    err_msg, form, votes = None, None, None
    try:
        disposeable = Disposable.objects.get(name=disposable_name.lower())
    except Disposable.DoesNotExist:
        err_msg = "The item '{0}' does not exist in the database".format(disposable_name)
    else:
        initial = {'disposable': disposeable, 'count': settings.CATEGORIZE_VOTE_WEIGHT}
        form = CategorizationForm(initial=initial)
        votes = {v.category.name: v.count for v in disposeable.get_top_votes()}
    return render(request, 'VoteHandler/categorize.html', 
        {
            'disposable_name': disposable_name,
            'error_message': err_msg,
            'form': form,
            'votes': votes
        }
    )

def home(request):
    """Simple landing page for text entry"""
    return render(request, 'VoteHandler/home.html')

def result(request, disposable_name, category_name):
    """View that handles displaying the results of a dispose to the user"""
    votes = request.GET
    return render(request, 'VoteHandler/result.html', 
        {
            'disposable_name': Disposable.objects.get(id=disposable_name).name,
            'category_name': Category.objects.get(id=category_name).name,
            'votes': sorted(votes.items(), key=lambda x: x[1], reverse=True)
        }
    )

def vote(request):
    # TODO: POST adds the votes to that object
    if request.method == 'POST':
        form = CategorizationForm(request.POST)
        if form.is_valid():
            try:
                # If we have an entry, update it
                dv = DisposableVote.objects.get(disposable=form.cleaned_data['disposable'],
                    category=form.cleaned_data['category']
                )
                dv.add_votes(form.cleaned_data['count'])
            except (DisposableVote.DoesNotExist):
                # save new instance
                form.save()
            return redirect('VoteHandler:home')
        else:
            err_msg = 'Form was rejected with error: {0}'.format(form.errors.as_json())
            return render(request, 'VoteHandler/categorize.html', 
                {
                    'disposable_name' : request.POST.get('disposable_name',''),
                    'error_message': err_msg,
                    'form' : form,
                }
            )


# def from_speech(request):
#     pass