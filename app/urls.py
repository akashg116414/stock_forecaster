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
    path('indian-index-status/', views.get_indian_index_status, name='indian-index-status'),
    path('signal-data-graph', views.signal_data_graph, name='signal-data-graph'),
    
    
]
