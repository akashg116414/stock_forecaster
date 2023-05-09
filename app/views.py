
from datetime import date

import pandas as pd
import yfinance as yf
from django import template
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader

from .models import ListedStock


# @login_required(login_url="/login/")
def index(request):
    symbol = request.GET.get('symbol')
    start_date = request.GET.get('startDt')
    end_date = request.GET.get('endDt')
    period = '3mo'
    if not symbol:
        symbol = "INFY"
    stock_obj = ListedStock.objects.filter(symbol=symbol).first()
    symbol = symbol + ".NS"
    stock = yf.Ticker(symbol)
    if start_date and end_date:
        data = stock.history(start=start_date, end=end_date)
    else:
        data = stock.history(period='5y',interval='3mo')
    print(data)
    prices = data['Close'].tolist()
    dates = data.index.strftime('%Y-%m-%d').tolist()
    context = {'prices': prices,"dates":dates,"stock_name": stock_obj.name, "stock_symbol": symbol}
    print(context)
    return render(request, "index.html", context)

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
    
    
def search_items(request):
    keyword = request.GET.get('q')
    if keyword:
        items = ListedStock.objects.filter(name__icontains=keyword)[:10]
        data = [{'name': item.name,'symbol':item.symbol} for item in items]
    else:
        data = []
    return JsonResponse(data, safe=False)


# def get_historical_price(request):
