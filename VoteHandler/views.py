# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib.parse

from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect

from .models import Category, Disposable, DisposableVote

# TODO: Write some tests!

def dispose(request):
    try:
        user_text = request.POST.get('disposable_item', '')
        if not user_text:
            return render(request, 'VoteHandler/home.html', {'error_message' : "Please enter text."})
        disposeable = Disposable.objects.get(name=user_text.lower())
    except Disposable.DoesNotExist:
        return HttpResponseRedirect(reverse('VoteHandler:categorize', args=(user_text,)))
    else:
        top_category_id = disposeable.get_top_category().id
        votes_tuples = disposeable.get_top_votes()
        return HttpResponseRedirect("{0}?{1}".format(reverse('VoteHandler:result', args=(disposeable.id, top_category_id)), 
            urllib.parse.urlencode(votes_tuples)))

def categorize(request, disposable_name):
    return render(request, 'VoteHandler/categorize.html', 
        {'disposable_name' : disposable_name})

def home(request):
    return render(request, 'VoteHandler/home.html')

def result(request, disposable_name, category_name):
    votes = request.GET
    return render(request, 'VoteHandler/result.html', 
    {'disposable_name' : Disposable.objects.get(id=disposable_name).name,
     'category_name' : Category.objects.get(id=category_name).name,
     'votes' : votes})

# def from_speech(request):
#     pass
