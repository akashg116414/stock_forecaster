# -*- encoding: utf-8 -*-

from django.contrib import admin

from .models import GlobalIndex, IndianIndex, ListedStock


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