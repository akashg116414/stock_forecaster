# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from datetime import date
from jugaad_data.nse import bhavcopy_save
import pandas as pd
from .models import ListedStock
import datetime

# @login_required(login_url="/login/")
def index(request):
    return render(request, "index.html")

# @login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'error-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'error-500.html' )
        return HttpResponse(html_template.render(context, request))


def add_stocks_into_db(request):
    if request.method == 'GET':
        print("enter")
        # ListedStock.objects.all().delete() # to delete all
        df = pd.read_csv("./EQUITY_L.csv")
        for index, row in df.iterrows():
            stock = ListedStock(name=row['NAME OF COMPANY'],symbol=row['SYMBOL'],slug = "Equity",category= row[" SERIES"])
            stock.save()
        return HttpResponse('Successfull added')
