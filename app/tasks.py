from .models import Indicator
from .utils import (
    get_current_status, 
    get_crypto_status, 
    get_day_gainers, 
    get_day_losers, 
    get_top_crypto
)
from .constant import indian_index, global_indicators, crypto_currency


columns_to_include = ['Symbol', 'Name', 'Price', 'Change', "PercentageChange"]

def update_top_crypto():
    top_crypto_data = get_top_crypto()
    crypto_dict = top_crypto_data.head(3)[columns_to_include].to_dict('records')
    for row in crypto_dict:
        update_indicator(row, 'TOPCRYPTO')


def update_day_losers():
    day_losers_data = get_day_losers()
    losers_dict = day_losers_data.head(3)[columns_to_include].to_dict('records')
    for row in losers_dict:
        update_indicator(row, 'TOPLOSER')

def update_day_gainers():
    day_gainers_data = get_day_gainers()
    gainers_dict = day_gainers_data.head(3)[columns_to_include].to_dict('records')
    for row in gainers_dict:
        update_indicator(row, 'TOPGAINER')

def update_indian_indicator():
    context = [get_current_status(name, ticker) for name,ticker in indian_index.items()]
    for row in context:
        update_indicator(row, 'INDIAN')

def update_global_indicator():
    context = [get_current_status(name, ticker) for name,ticker in global_indicators.items()]
    context_crypto = [get_crypto_status(name,ticker) for name,ticker in crypto_currency.items()]
    context.extend(context_crypto)
    for row in context:
        update_indicator(row, 'GLOBAL')

def update_indicator(value, indicator_type):
    indicator = Indicator.objects.filter(symbol=value['Symbol']).first()

    if indicator:
        indicator.price = value['Price']
        indicator.change = value['Change']
        indicator.percentage_change = value['PercentageChange']
        indicator.save()
    else:
        if indicator_type in ['TOPGAINER', 'TOPLOSER', 'TOPCRYPTO']:
            check_and_remove(indicator_type)
        Indicator.objects.create(
            name=value['Name'],
            symbol=value['Symbol'],
            price=value['Price'],
            change=value['Change'],
            percentage_change=value['PercentageChange'],
            indicator_type = indicator_type
        )

def check_and_remove(indicator_type):
    count = Indicator.objects.filter(indicator_type=indicator_type).count()
    if count >=3:
        first_object = Indicator.objects.filter(indicator_type=indicator_type).first()
        first_object.delete()
