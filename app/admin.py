# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import ListedStock


class ListedStockAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol','category')
# Register your models here.

admin.site.register(ListedStock,ListedStockAdmin)