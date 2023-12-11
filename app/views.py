import pandas_ta as ta
from plotly.offline import plot

import pandas as pd
import yfinance as yf
from django import template
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader

from app import utils
from .models import ListedStock, Indicator, NewsItem, RiskAnalysis
from dateutil.relativedelta import relativedelta
from .constant import crypto_currency
from app.open_ai import llm_news, chatgpt_call
import datetime
from datetime import datetime
import logging
import threading
import time

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

def index(request):
    # to clear sessions
    request.session.pop("authenticated")
    request.session.pop("visit_count_search")
    if not 'authenticated' in request.session:
        print("Unauthorised user")
        request.session["authenticated"] = False
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    stock_id = request.GET.get('stock_id', None)
    stock_obj = ListedStock.objects.filter(id=stock_id).first()
    period = '3mo'
    if not stock_obj:
        symbol = "^NSEI"
        stock_obj = ListedStock.objects.filter(symbol=symbol).first()
    ticker = stock_obj.ticker
    stock = yf.Ticker(ticker)
    if start_date and end_date:
        data = stock.history(start=start_date, end=end_date)
    else:
        data = stock.history(period=period)
    prices = data['Close'].tolist()
    dates = data.index.strftime('%Y-%m-%d').tolist()
    context = {'prices': prices, "dates": dates, "stock_name": stock_obj.name,
               "stock_symbol": stock_obj.symbol, 'stock_id': stock_obj.id}
    return render(request, "index.html", context)


def gainers_losers_status(request):
    top_gainers = Indicator.objects.filter(
        indicator_type="TOPGAINER").order_by('-id')[:3]
    top_losers = Indicator.objects.filter(
        indicator_type="TOPLOSER").order_by('-id')[:3]
    top_crypto = Indicator.objects.filter(
        indicator_type="TOPCRYPTO").order_by('-id')[:3]
    context = {
        "gainers": list(top_gainers.values()),
        "losers": list(top_losers.values()),
        "crypto": list(top_crypto.values())
    }
    return JsonResponse(context, safe=False)


def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('error-404.html')
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template('error-500.html')
        return HttpResponse(html_template.render(context, request))


def add_stocks_into_db(request):
    if request.method == 'GET':
        print("enter")
        # ListedStock.objects.all().delete() # to delete all
        df = pd.read_csv("./stocks.csv")
        for index, row in df.iterrows():
            stock = ListedStock(name=row['NAME'], symbol=row['SYMBOL'],
                                slug=row['SLUG'].lower(), ticker=row['TICKER'], exchange=row['SERIES'])
            # stock = ListedStock(name=row['NAME OF COMPANY'], symbol=row['SYMBOL'],symbol1=row['SYMBOL1'],
            #                     slug=row['NAME OF COMPANY'].lower(), ticker=row['SYMBOL'], exchange='NSI')
            
            stock.save()
        return HttpResponse('Successfull added')


def search_items(request):
    authenticated = request.session.get("authenticated", False)
    visit_count = request.session.get("visit_count_search", 0)

    # Check if the user is authenticated or visit count is less than 2
    if authenticated or visit_count < 2:
        print("authenticated",authenticated)
        print("visit_count",visit_count)
        # Increment the visit count if the user is not authenticated
        if not authenticated:
            ("not authenticate user search")
            request.session["visit_count_search"] = visit_count + 1
        keyword = request.GET.get('q')
        if keyword:
            items = ListedStock.objects.filter(name__icontains=keyword)[:12]
            data = [{'name': item.name, 'symbol': item.symbol,
                    'stock_id': item.id} for item in items]
        else:
            data = []
        return JsonResponse(data, safe=False)
    else:
        # return render(request, 'popup_template.html', {'popup_message': 'Please log in to perform the search.'})
        return JsonResponse({'message': 'Please log in to perform the search.'})


def historical_data(request):
    # symbol = request.GET.get('symbol')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    interval = request.GET.get('interval')
    stock_id = request.GET.get('stock_id', None)
    stock_obj = ListedStock.objects.filter(id=stock_id).first()
    interval_period = {"1m": "1d", "5m": "1d", "15m": "5d", "30m": "5d",
                       "1h": "5d", "1d": "1mo", "1wk": "3mo", "1mo": "2y", "3mo": "5y"}
    period = '3mo'
    if not stock_obj:
        symbol = "^NSEI"
        stock_obj = ListedStock.objects.filter(symbol=symbol).first()
    ticker = stock_obj.ticker
    stock = yf.Ticker(ticker)
    if start_date and end_date and not interval:
        data = stock.history(start=start_date, end=end_date)
    elif start_date and end_date and interval:
        data = stock.history(start=start_date, end=end_date, interval=interval)
    elif not start_date and not end_date and interval:
        period = interval_period.get(interval)
        data = stock.history(period=period, interval=interval)
    else:
        data = stock.history(period=period)

    prices = data['Close'].tolist()
    dates = data.index.strftime('%Y-%m-%d').tolist()
    context = {'prices': prices, "dates": dates,
               "stock_name": stock_obj.name, 'stock_id': stock_obj.id}

    return JsonResponse(context, safe=False)


def get_indian_index_status(request):
    indian_indicators = list(Indicator.objects.filter(
        indicator_type="INDIAN").values())
    context = {indicator['name']: indicator for indicator in indian_indicators}
    return JsonResponse(context, safe=False)


def get_global_indicator_status(request):
    all_indicators = list(Indicator.objects.filter(
        indicator_type="GLOBAL").values())
    return JsonResponse(all_indicators, safe=False)


def get_global_crypto_status(request):
    context_crypto = {name: utils.get_crypto_status(
        name, ticker) for name, ticker in crypto_currency.items()}
    return JsonResponse(context_crypto, safe=False)


def signal_data_graph(request):

    stock_id = request.GET.get('stock_id', None)
    stock_obj = ListedStock.objects.filter(id=stock_id).first()
    if not stock_obj:
        symbol = "^NSEI"
        stock_obj = ListedStock.objects.filter(symbol=symbol).first()
    ticker = stock_obj.ticker
    stock = yf.Ticker(ticker)

    signal_data = stock.history(period="5d", interval='5m')
    signal_data.ta.supertrend(length=20, multiplier=2, append=True)

    signal_data.drop(['SUPERTl_20_2.0', 'SUPERTs_20_2.0'],
                     axis=1, inplace=True)

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
        'name': stock_obj.name,
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
        'name': 'buy',
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
        'name': 'Sell',
        'showlegend': True
    }

    for i in range(1, len(signal_data)):
        if signal_data['SUPERT_20_2.0'][i] > y_data[i] and signal_data['SUPERT_20_2.0'][i-1] <= y_data[i-1]:
            # Buy signal
            sell_signals_trace['x'].append(x_data[i])
            sell_signals_trace['y'].append(y_data[i])
            sell_signals_trace['marker']['symbol'] = 'triangle-down'
            sell_signals_trace['marker']['color'] = 'red'
        elif signal_data['SUPERT_20_2.0'][i] < y_data[i] and signal_data['SUPERT_20_2.0'][i-1] >= y_data[i-1]:
            # Sell signal
            buy_signals_trace['x'].append(x_data[i])
            buy_signals_trace['y'].append(y_data[i])
            buy_signals_trace['marker']['symbol'] = 'triangle-up'
            buy_signals_trace['marker']['color'] = 'green'

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
    graph_data = [candlestick_trace, supertrend_trace,
                  sell_signals_trace, buy_signals_trace]

    chart = plot({'data': graph_data, 'layout': layout}, output_type='div')
    context = {'chart': chart}

    return JsonResponse(context, safe=False)


def forecast_data(request):
    price = int(request.GET.get('price', 1000))
    duration = int(request.GET.get('duration', 1))
    print(price, duration)
    stock_id = request.GET.get('stock_id', None)
    stock_obj = ListedStock.objects.filter(id=stock_id).first()
    if not stock_obj:
        symbol = "^NSEI"
        stock_obj = ListedStock.objects.filter(symbol=symbol).first()
    ticker = stock_obj.ticker
    # Download the historical stock data from Yahoo Finance
    data = yf.download(ticker, period="5y", interval='1mo')

    # Prepare the data for Prophet
    data['Date'] = data.index
    last_date = data['Date'][-1]
    percentage = (((data['Close'][-1] - data['Close'][0])/data['Close'][0])/60)
    last_price = data['Close'][-1]
    # for i in range(1, duration+1):
    next_date = last_date + relativedelta(months=duration)
    current = len(data)
    data.loc[current+1, 'Date'] = next_date
    data.loc[current+1, 'Close'] = last_price + last_price*percentage*duration
    prices = data['Close'].tolist()
    dates = pd.to_datetime(data['Date']).dt.strftime('%Y-%m').tolist()
    forecast_price = price + price * percentage * duration
    chart_string = "₹ {} will be ₹ {:.2f} in {} Month".format(
        price, forecast_price, duration)
    context = {'prices': prices, "dates": dates,
               "chart_string": chart_string, "stock_name": stock_obj.name}

    return JsonResponse(context, safe=False)


def personalized_investment(request):
    try:
        amount = int(request.GET.get('amount', 1000))
        duration = int(request.GET.get('duration', 1))
        risk = request.GET.get('risk', 'Low')
        stock_list = RiskAnalysis.objects.filter(time=int(duration), risk_category=risk).values("stock_list").last().get('stock_list',[])
        context = {}
        count = 1
        for rank in range(len(stock_list)):
            stock_ticker = stock_list.get(str(rank))
            stock_obj = ListedStock.objects.filter(slug=stock_ticker).first()
            if not stock_obj:
                continue
            stock = yf.Ticker(stock_obj.ticker)
            current_price, est_return = get_return_and_price(stock, duration)
            if not current_price and not est_return:
                continue
            quantity = amount // current_price
            if quantity > 0 and est_return>0:
                package_price = quantity * current_price
                stock_info = {'id':stock_obj.id, 'name': stock_obj.name, 'Stock Price': round(current_price,2), 'number of stocks': quantity, 
                            'package value': round(package_price,2),'est_percent':est_return ,'est_return': round(((est_return*package_price)+package_price),2), 'risk': risk}
                context['rank'+str(count)] = stock_info
                count+=1
                if len(context)==6:
                    break
        if context:
            sorted_data = sorted(context.items(), key=lambda item: item[1]['est_percent'], reverse=True)
            ranked_result = {f'rank{i+1}': value for i, (key, value) in enumerate(sorted_data)}
        x = threading.Thread(target=thread_function, args=(ranked_result,))
        x.start()
        return JsonResponse(ranked_result, safe=False)
    except Exception as err:
        return JsonResponse({"message":str(err)}, safe=False)
    

def stock_news(request):
    stock_id = request.GET.get('stock_id', None)
    if not stock_id:
        return JsonResponse({"error_message": "stock_id is required"}, safe=False)
    stock_obj = ListedStock.objects.filter(id=int(stock_id)).first()
    news_list = list(NewsItem.objects.filter(listed_stock=stock_obj).order_by('-timestamp')[:1].values())
    sentiment_sum = 0
    if len(news_list) > 0:
        for news in news_list:
            sentiment_sum += news['sentiment_score']
        sentiment_score = sentiment_sum/len(news_list)
    else:
        sentiment_score = 0
    if sentiment_score > 0.1:
        sentiment_value = 'Positive'
    elif sentiment_score >= -0.1 and sentiment_score <= 0.1:
        sentiment_value = 'Netural'
    else:
        sentiment_value = 'Negative'
    
    context = {
        "news": news_list,
        "sentiment_score":sentiment_score,
        "sentiment_val": sentiment_value
        }
    return JsonResponse(context, safe=False)

def thread_function(context):
    for context_val in context.values():
        logging.info("News Thread starting for %s", context_val['name'])
        stock_obj = ListedStock.objects.filter(id=context_val['id']).first()
        keyword = "-".join(stock_obj.name.split(" "))
        df = utils.get_stock_news(keyword)
        if not df.empty:
            df = utils.get_stock_news_sentiment(df)
            # Save the news items in the database
            for news_item in df.to_dict(orient='records'):
                news_item['listed_stock'] = stock_obj
                timestamp = news_item.pop('timestamp')
                news_obj, _ = NewsItem.objects.get_or_create(**news_item)
                news_obj.timestamp = timestamp
                news_obj.save()
            logging.info("News Thread ends for %s", context_val['name'])

def temp():
    for id_ in range(1,1800):
        logging.info("News Thread starting for %s", str(id_))
        stock_obj = ListedStock.objects.filter(id=id_).first()
        keyword = "-".join(stock_obj.name.split(" "))
        logging.info("keyword %s", str(keyword))
        df = utils.get_stock_news(keyword)
        if not df.empty:
            df = utils.get_stock_news_sentiment(df)
            # Save the news items in the database
            for news_item in df.to_dict(orient='records'):
                news_item['listed_stock'] = stock_obj
                timestamp = news_item.pop('timestamp')
                news_obj, _ = NewsItem.objects.get_or_create(**news_item)
                news_obj.timestamp = timestamp
                news_obj.save()
            logging.info("News Thread ends for %s",  str(id_))

def get_return_and_price(stock, duration):
    current_price = None
    return_price = None
    history = stock.history(period='5y')
    number = duration * 21
    if not history.empty:
        if number > len(history):
            final_price = history['Close'][-number]
        elif len(history) !=0 and number <= len(history):
            final_price = history['Close'][-len(history)]
        current_price = history['Close'][-1]
        return_price =  ((current_price - final_price)/final_price)

    return current_price, return_price

      
def chat_bot(request):
    if request.method == "POST":
        flag = True
        val = request.POST.get('val', "hello")
        for i in ['news', 'sentiments', 'sentiment','News','Sentiments','Sentiment']:
            if i in val:
                flag = False
                break
        if flag:
            result = chatgpt_call(val)
        else:
            db_chain = llm_news()
            result = db_chain.run(val)
        context = {'result': result}
    return JsonResponse(context, safe=False)