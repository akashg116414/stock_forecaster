
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
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    period = '3mo'
    if not symbol:
        symbol = "INFY"
    stock_obj = ListedStock.objects.filter(symbol=symbol).first()
    new_symbol = symbol + ".NS"
    stock = yf.Ticker(new_symbol)
    if start_date and end_date:
        data = stock.history(start=start_date, end=end_date)
    else:
        data = stock.history(period=period)
    prices = data['Close'].tolist()
    dates = data.index.strftime('%Y-%m-%d').tolist()
    context = {'prices': prices,"dates":dates,"stock_name": stock_obj.name, "stock_symbol": symbol}
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
        items = ListedStock.objects.filter(name__icontains=keyword)[:12]
        data = [{'name': item.name,'symbol':item.symbol} for item in items]
    else:
        data = []
    return JsonResponse(data, safe=False)

def historical_data(request):
    symbol = request.GET.get('symbol')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    interval = request.GET.get('interval')
    interval_period = {"1m":"1d", "5m":"1d", "15m":"5d", "30m":"5d", "1h":"5d", "1d":"1mo", "1wk":"3mo", "1mo":"2y", "3mo":"5y"}
    period = '3mo'
    if not symbol:
        symbol = "INFY"
    symbol = symbol + ".NS"
    stock = yf.Ticker(symbol)
    if start_date and end_date and not interval:
        data = stock.history(start=start_date, end=end_date)
    elif start_date and end_date and interval:
        data = stock.history(start=start_date, end=end_date,interval=interval)
    elif not start_date and not end_date and interval:
        period = interval_period.get(interval)
        data = stock.history(period=period,interval=interval)
    else:
        data = stock.history(period=period)
    prices = data['Close'].tolist()
    dates = data.index.strftime('%Y-%m-%d').tolist()
    context = {'prices': prices,"dates":dates}

    return JsonResponse(context, safe=False)


# def get_historical_price(request):
