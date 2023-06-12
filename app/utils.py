import pandas as pd
import requests
from requests_html import HTMLSession
from .models import ListedStock

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
    

def get_current_status(name, ticker , headers = {'User-agent': 'Mozilla/5.0'}): 
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
    status = {"Name":name, "Symbol":ticker,"Price":round(current_price, 2),"Change":price_change,"PercentageChange":round(price_change_percentage,2)}
    return status

def get_crypto_status(name, ticker, headers = {'User-agent': 'Mozilla/5.0'}): 
    site = "https://finance.yahoo.com/quote/" + ticker + "?p=" + ticker
    tables = pd.read_html(requests.get(site, headers=headers).text)
    tables = tables[0]
    tables.index  = tables[0]
    previous_close = tables[1]['Previous Close']
    current_price = get_live_price(ticker)
    #price change
    price_change = current_price - float(previous_close)
    price_change_percentage = (price_change/float(previous_close))*100
    response =  {"Name":name, "Symbol":ticker,"Price":round(current_price, 2),"Change":price_change,"PercentageChange":round(price_change_percentage,2)}
    return response

def _raw_get_daily_info(site):
    session = HTMLSession()
    resp = session.get(site)
    tables = pd.read_html(resp.html.raw_html)
    df = tables[0].copy()
    df.columns = tables[0].columns
    del df["52 Week Range"]
    df["Price"] = df["Price (Intraday)"]
    df["PercentageChange"] = df["% Change"].map(lambda x: float(x.strip("%+").replace(",", "")))
    fields_to_change = [x for x in df.columns.tolist() if "Vol" in x \
                        or x == "Market Cap"]
    for field in fields_to_change: 
        if type(df[field][0]) == str:
            df[field] = df[field].map(_convert_to_numeric)
    session.close()
    return df
    
def get_day_most_active(count: int = 5):
    return _raw_get_daily_info(f"https://finance.yahoo.com/most-active?offset=0&count={count}")

def get_day_gainers(count: int = 5):
    return _raw_get_daily_info(f"https://finance.yahoo.com/gainers?offset=0&count={count}")

def get_day_losers(count: int = 5):
    return _raw_get_daily_info(f"https://finance.yahoo.com/losers?offset=0&count={count}")

def get_top_crypto():
    '''Gets the top 100 Cryptocurrencies by Market Cap'''      
    session = HTMLSession()
    resp = session.get("https://finance.yahoo.com/cryptocurrencies?offset=0&count=5")
    tables = pd.read_html(resp.html.raw_html)
    df = tables[0].copy()
    df["Price"] = df["Price (Intraday)"]
    df["PercentageChange"] = df["% Change"].map(lambda x: float(str(x).strip("%").\
                                                               strip("+").\
                                                               replace(",", "")))
    del df["52 Week Range"]
    fields_to_change = [x for x in df.columns.tolist() if "Volume" in x \
                        or x == "Market Cap" or x == "Circulating Supply"]
    for field in fields_to_change:
        if type(df[field][0]) == str:
            df[field] = df[field].map(lambda x: _convert_to_numeric(str(x)))     
    session.close()             
    return df

def _convert_to_numeric(s):
    try:
        if "M" in s:
            s = s.strip("M")
            return force_float(s) * 1_000_000
        if "B" in s:
            s = s.strip("B")
            return force_float(s) * 1_000_000_000
        return force_float(s)
    except:
        return s

def force_float(elt):
    try:
        return float(elt)
    except:
        return elt
    
def get_top_indian_gainer():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    # Get the top gainers
    res_gainers = requests.get(
        "https://www.nseindia.com/api/live-analysis-variations?index=gainers", headers=headers
    )
    gainers = res_gainers.json()["allSec"]["data"]

    # Create a DataFrame of the top gainers
    df_gainers = pd.DataFrame(gainers)
    df_gainers_new = pd.DataFrame()
    df_gainers_new["Symbol"] = df_gainers["symbol"].str.upper()
    df_gainers_new["PercentageChange"] = df_gainers["perChange"].map("{:.2f}".format)
    df_gainers_new["Price"] = df_gainers["ltp"]
    df_gainers_new["Change"] = (df_gainers["ltp"] - df_gainers["open_price"]).map("{:.2f}".format)

    # Fetch stock names from ListedStocks model and add them to DataFrame
    listed_stocks = ListedStock.objects.all()  # Replace with your actual code to fetch the ListedStocks model
    symbol_to_name = {stock.symbol: stock.name for stock in listed_stocks}

    df_gainers_new["Name"] = df_gainers_new["Symbol"].map(symbol_to_name)
    df_gainers_new.dropna(subset=["Name"], inplace=True)

    return df_gainers_new

def get_top_indian_looser():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    # Get the top losers
    res_losers = requests.get(
        "https://www.nseindia.com/api/live-analysis-variations?index=loosers", headers=headers
    )
    losers = res_losers.json()["allSec"]["data"]

    # Create a DataFrame of the top losers
    df_losers = pd.DataFrame(losers)
    df_losers_new = pd.DataFrame()
    df_losers_new["Symbol"] = df_losers["symbol"].str.upper()
    df_losers_new["PercentageChange"] = df_losers["perChange"].map("{:.2f}".format)
    df_losers_new["Price"] = df_losers["ltp"]
    df_losers_new["Change"] = (df_losers["ltp"] - df_losers["open_price"]).map("{:.2f}".format)

    # Fetch stock names from ListedStocks model and add them to DataFrame
    listed_stocks = ListedStock.objects.all()  # Replace with your actual code to fetch the ListedStocks model
    symbol_to_name = {stock.symbol: stock.name for stock in listed_stocks}

    df_losers_new["Name"] = df_losers_new["Symbol"].map(symbol_to_name)
    df_losers_new.dropna(subset=["Name"], inplace=True)

    return df_losers_new