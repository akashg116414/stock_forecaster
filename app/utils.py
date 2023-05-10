import requests
import pandas as pd

base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"

def build_url(ticker, start_date = None, end_date = None, interval = "1d"):
    
    if end_date is None:  
        end_seconds = int(pd.Timestamp("now").timestamp())
        
    else:
        end_seconds = int(pd.Timestamp(end_date).timestamp())
        
    if start_date is None:
        start_seconds = 7223400    
        
    else:
        start_seconds = int(pd.Timestamp(start_date).timestamp())
    
    site = base_url + ticker
    
    params = {"period1": start_seconds, "period2": end_seconds,
              "interval": interval.lower(), "events": "div,splits"}
    return site, params
    
    
def get_live_price(ticker):

    start_date= None
    end_date = pd.Timestamp.today() + pd.DateOffset(10)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    site, params = build_url(ticker, start_date, end_date)
    
    resp = requests.get(site, params = params, headers = headers)
    
    
    if not resp.ok:
        raise AssertionError(resp.json())
        
    # get JSON response
    data = resp.json()
    
    # get open / high / low / close data
    frame = pd.DataFrame(data["chart"]["result"][0]["indicators"]["quote"][0])
    
    return frame.close.iloc[-1]
    

def get_current_status(ticker , headers = {'User-agent': 'Mozilla/5.0'}): 
    site = "https://finance.yahoo.com/quote/" + ticker + "?p=" + ticker
    
    tables = pd.read_html(requests.get(site, headers=headers).text)
    tables = tables[0]
    tables.index  = tables[0] 
    try:
        current_price = get_live_price(ticker)
    except: 
        current_price = tables[1]['Previous Close']
    price_change = (current_price - tables[1]['Previous Close'])
    price_change_percentage = (price_change/tables[1]['Previous Close'])*100
    status = {"current_price" : current_price, "price_change" : price_change, "price_change_percentage": price_change_percentage}
    return status