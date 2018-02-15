# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'VoteHandler/home.html')

def dispose(request):
    pass

def result(request, disposable_name, category_name):
    pass

    # def from_speech(request):
    #     pass
