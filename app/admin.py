# -*- encoding: utf-8 -*-

from django.contrib import admin

from .models import ListedStock, Indicator, NewsItem, RiskAnalysis

@admin.register(ListedStock)
class ListedStockAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol','category', 'ticker', 'exchange')

@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'price', 'change', 'percentage_change', 'indicator_type', 'created_at', 'updated_at')

@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('headline', 'url', 'description', 'source', 'timestamp', 'listed_stock', 'sentiment_score')

@admin.register(RiskAnalysis)
class RiskAnalysisAdmin(admin.ModelAdmin):
    list_display = ('risk_category', 'time', 'stock_list')
