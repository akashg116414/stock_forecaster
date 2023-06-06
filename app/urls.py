# -*- encoding: utf-8 -*-


from django.urls import path, re_path

from app import views

urlpatterns = [
    # Matches any html file 
    re_path(r'^.*\.html', views.pages, name='pages'),

    # The home page
    path('', views.index, name='home'),

    path("stocks/update", views.add_stocks_into_db),
    path('search/', views.search_items, name='search'),
    path('historical-data/', views.historical_data, name='historical-data'),
    path('forecast-data/', views.forecast_data, name='forecast-data'),
    path('indian-index-status/', views.get_indian_index_status, name='indian-index-status'),
    path('gainers-losers-status/', views.gainers_losers_status, name='gainers-losers-status'),
    path('global-index-status/', views.get_global_indicator_status, name='global-index-status'),
    path('global-crypto-status/', views.get_global_crypto_status, name='global-crypto-status'),
    path('signal-data-graph', views.signal_data_graph, name='signal-data-graph'),
    
]
