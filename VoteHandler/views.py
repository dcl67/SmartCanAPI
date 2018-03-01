# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib.parse

from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from .models import Category, Disposable, DisposableVote

# TODO: Write some tests!

def dispose(request):
    """View that receives POST requests for disposals from home's form"""
    try:
        user_text = request.POST.get('disposable_item', '')
        if not user_text:
            return render(request, 'VoteHandler/home.html',
             {'error_message' : "Please enter text."})
        disposeable = Disposable.objects.get(name=user_text.lower())
    except Disposable.DoesNotExist:
        return redirect('VoteHandler:categorize', disposable_name=user_text)
    else:
        # TODO: Add logic to redirect to category if the total # of votes is low
        top_category_id = disposeable.get_top_category().id
        votes_tuples = disposeable.get_top_votes()
        # Checking num votes
        # if len(votes_tuples) < 10:
        #     return redirect('VoteHandler:categorize', disposable_name=user_text)
        # TODO: See if this can be cleaned up. Possibly save context in session 
        # cookie read it in template?
        return HttpResponseRedirect("{0}?{1}".format(
         reverse('VoteHandler:result', args=(disposeable.id, top_category_id)), 
         urllib.parse.urlencode(votes_tuples)))

def categorize(request, disposable_name):
    """View that guides user to selecting the correct category"""
    return render(request, 'VoteHandler/categorize.html', 
        {'disposable_name' : disposable_name})

def home(request):
    """Simple landing page for text entry"""
    return render(request, 'VoteHandler/home.html')

def result(request, disposable_name, category_name):
    """View that handles displaying the results of a dispose to the user"""
    votes = request.GET
    return render(request, 'VoteHandler/result.html', 
    {'disposable_name' : Disposable.objects.get(id=disposable_name).name,
     'category_name' : Category.objects.get(id=category_name).name,
     'votes' : votes})

# def from_speech(request):
#     pass
