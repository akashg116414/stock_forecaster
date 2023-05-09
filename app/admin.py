# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import ListedStock, GlobalIndex, IndianIndex


class ListedStockAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol','category')

class GlobalIndexAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", 'category', "flag")

class IndianIndexAdmin(admin.ModelAdmin):
    list_display = ("name","symbol",'category',"flag")
# Register your models here.


admin.site.register(ListedStock, ListedStockAdmin)
admin.site.register(GlobalIndex, GlobalIndexAdmin)
admin.site.register(IndianIndex, IndianIndexAdmin)