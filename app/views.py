import pandas_ta as ta
from plotly.offline import plot

import pandas as pd
import yfinance as yf
from django import template
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader

from .utils import get_current_status, get_crypto_status, get_day_gainers, get_day_losers,get_top_crypto
from .models import ListedStock
from .constant import indian_index, global_indicators,crypto_currency
import datetime




# @login_required(login_url="/login/")
def index(request):
    symbol = request.GET.get('symbol')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    period = '3mo'
    if not symbol:
        symbol = "TATAMOTORS"
    stock_obj = ListedStock.objects.filter(symbol=symbol).first()
    new_symbol = symbol + ".NS"
    stock = yf.Ticker(new_symbol)
    if start_date and end_date:
        data = stock.history(start=start_date, end=end_date)
    else:
        data = stock.history(period=period)
    prices = data['Close'].tolist()
    dates = data.index.strftime('%Y-%m-%d').tolist()

    # Calculate Supertrend and MACD indicators
    data = stock.history(period="5d", interval='5m')
    data.ta.supertrend(length=20, multiplier=2, append=True)
    today = datetime.date.today()
    if today.weekday() >= 5:
        days_to_subtract = today.weekday() - 4
        today -= datetime.timedelta(days=days_to_subtract)
    today = today.strftime('%Y-%m-%d')
    start_time = pd.Timestamp(today + ' 09:15:00+05:30')
    data = data.loc[start_time:]

    # Create buy/sell signals based on MACD and Supertrend
    data.drop(['SUPERTl_20_2.0','SUPERTs_20_2.0'],axis=1,inplace=True)
    data = data.loc[data['SUPERT_20_2.0'] != 0].copy()
    data.dropna(inplace=True)

    # Create x and y data for plot
    x_data = data.index
    y_data = data['Close']

    # Create trace for candlestick chart
    candlestick_trace = {
        'x': x_data,
        'open': data['Open'],
        'high': data['High'],
        'low': data['Low'],
        'close': y_data,
        'type': 'candlestick',
        'name': symbol,
        'showlegend': False
    }


    # Create trace for Supertrend
    supertrend_trace = {
        'x': x_data,
        'y': data['SUPERT_20_2.0'],
        'type': 'scatter',
        'mode': 'lines',
        'line': {
            'width': 2,
            'color': 'green'
        },
        'name': 'Trend'
    }

    # Add buy/sell signals
    buy_signals_trace = {
        'x': [],
        'y': [],
        'mode': 'markers',
        'marker': {
            'symbol': 'triangle-up',
            'size': 15,
            'color': 'green'
        },
        'name': 'Sell',
        'showlegend': True
    }

    # Add buy/sell signals
    sell_signals_trace = {
        'x': [],
        'y': [],
        'mode': 'markers',
        'marker': {
            'symbol': 'triangle-down',
            'size': 15,
            'color': 'red'
        },
        'name': 'Buy',
        'showlegend': True
    }

    for i in range(1, len(data)):
        if data['SUPERT_20_2.0'][i] > y_data[i] and data['SUPERT_20_2.0'][i-1] <= y_data[i-1]:
            # Buy signal
            buy_signals_trace['x'].append(x_data[i])
            buy_signals_trace['y'].append(y_data[i])
            buy_signals_trace['marker']['symbol'] = 'triangle-up'
            buy_signals_trace['marker']['color'] = 'green'
        elif data['SUPERT_20_2.0'][i] < y_data[i] and data['SUPERT_20_2.0'][i-1] >= y_data[i-1]:
            # Sell signal
            sell_signals_trace['x'].append(x_data[i])
            sell_signals_trace['y'].append(y_data[i])
            sell_signals_trace['marker']['symbol'] = 'triangle-down'
            sell_signals_trace['marker']['color'] = 'red'


    # Create layout for plot
    layout = {
        'title': {
        'text': stock_obj.name,
        'x': 0.5,
        'xanchor': 'center'
        },
        'xaxis': {
        'rangeslider': {
        'visible': False
                }
            }
        }

    # Create figure and plot data
    graph_data = [candlestick_trace, supertrend_trace, sell_signals_trace, buy_signals_trace]
    
    chart = plot({'data': graph_data, 'layout': layout}, output_type='div')
    context = {'prices': prices, "dates":dates, "stock_name": stock_obj.name, "stock_symbol": symbol,
                'chart': chart, 'pred_chart': chart}
    # print(context)
    return render(request, "index.html", context)

def gainers_losers_status(request):
    top_gainers_df = get_day_gainers()
    top_losers_df = get_day_losers()
    top_crypto_df = get_top_crypto()
    columns_to_include = ['Symbol', 'Name', 'Price', 'Change', "PercentageChange"]
    gainers_dict = top_gainers_df.head(5)[columns_to_include].to_dict('records')
    losers_dict = top_losers_df.head(5)[columns_to_include].to_dict('records')
    crypto_dict = top_crypto_df.head(5)[columns_to_include].to_dict('records')
    context = {"gainers": gainers_dict,"losers": losers_dict,"crypto": crypto_dict}
    return JsonResponse(context, safe=False)
    
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

def get_indian_index_status(request):
    context = {name:get_current_status(ticker) for name,ticker in indian_index.items()}
    return JsonResponse(context, safe=False)

def get_global_indicator_status(request):
    context = {name:get_current_status(ticker) for name,ticker in global_indicators.items()}
    return JsonResponse(context, safe=False)

def get_global_crypto_status(request):
    context_crypto = {name:get_crypto_status(ticker) for name,ticker in crypto_currency.items()}
    return JsonResponse(context_crypto, safe=False)

def signal_data_graph(request):
    symbol = request.GET.get('symbol')
    if not symbol:
        symbol = "INFY"
    stock_obj = ListedStock.objects.filter(symbol=symbol).first()
    symbol = symbol + ".NS"
    stock = yf.Ticker(symbol)

    signal_data = stock.history(period="5d", interval='5m')
    signal_data.ta.supertrend(length=20, multiplier=2, append=True)

    
    signal_data.drop(['SUPERTl_20_2.0','SUPERTs_20_2.0'],axis=1,inplace=True)
    
    signal_data = signal_data.loc[signal_data['SUPERT_20_2.0'] != 0].copy()
    signal_data.dropna(inplace=True)

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    start_time = pd.Timestamp(today + ' 09:15:00+05:30')
    signal_data = signal_data.loc[start_time:]

    # Create x and y data for plot
    x_data = signal_data.index
    y_data = signal_data['Close']

    # Create trace for candlestick chart
    candlestick_trace = {
        'x': x_data,
        'open': signal_data['Open'],
        'high': signal_data['High'],
        'low': signal_data['Low'],
        'close': y_data,
        'type': 'candlestick',
        'name': symbol,
        'showlegend': False
    }


    # Create trace for Supertrend
    supertrend_trace = {
        'x': x_data,
        'y': signal_data['SUPERT_20_2.0'],
        'type': 'scatter',
        'mode': 'lines',
        'line': {
            'width': 2,
            'color': 'green'
        },
        'name': 'Trend'
    }

    # Add buy/sell signals
    buy_signals_trace = {
        'x': [],
        'y': [],
        'mode': 'markers',
        'marker': {
            'symbol': 'triangle-up',
            'size': 15,
            'color': 'green'
        },
        'name': 'Sell',
        'showlegend': True
    }

    # Add buy/sell signals
    sell_signals_trace = {
        'x': [],
        'y': [],
        'mode': 'markers',
        'marker': {
            'symbol': 'triangle-down',
            'size': 15,
            'color': 'red'
        },
        'name': 'Buy',
        'showlegend': True
    }

    for i in range(1, len(signal_data)):
        if signal_data['SUPERT_20_2.0'][i] > y_data[i] and signal_data['SUPERT_20_2.0'][i-1] <= y_data[i-1]:
            # Buy signal
            buy_signals_trace['x'].append(x_data[i])
            buy_signals_trace['y'].append(y_data[i])
            buy_signals_trace['marker']['symbol'] = 'triangle-up'
            buy_signals_trace['marker']['color'] = 'green'
        elif signal_data['SUPERT_20_2.0'][i] < y_data[i] and signal_data['SUPERT_20_2.0'][i-1] >= y_data[i-1]:
            # Sell signal
            sell_signals_trace['x'].append(x_data[i])
            sell_signals_trace['y'].append(y_data[i])
            sell_signals_trace['marker']['symbol'] = 'triangle-down'
            sell_signals_trace['marker']['color'] = 'red'


    # Create layout for plot
    layout = {
        'title': {
        'text': stock_obj.name,
        'x': 0.5,
        'xanchor': 'center'
        },
        'xaxis': {
        'rangeslider': {
        'visible': False
        }
        }
        }

    # Create figure and plot data
    graph_data = [candlestick_trace, supertrend_trace, sell_signals_trace, buy_signals_trace]
    
    chart = plot({'data': graph_data, 'layout': layout}, output_type='div')
    context = {'chart': chart}

    return JsonResponse(context, safe=False)