# -*- encoding: utf-8 -*-

from django.contrib import admin

from .models import ListedStock, Indicator

@admin.register(ListedStock)
class ListedStockAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol','category')

@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'price', 'change', 'percentage_change', 'indicator_type', 'created_at', 'updated_at')
