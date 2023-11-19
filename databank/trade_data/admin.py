from django.contrib import admin

from .models import Country_meta, HS_Code_meta, Unit_meta, TradeData

# Register your models here.

class CountryMeta_Admin(admin.ModelAdmin):
    list_display = ('id', 'Country_Name', 'Country_Code_2', 'Country_Code_3')

class UnitMeta_Admin(admin.ModelAdmin):
    list_display = ('id', 'Unit_Code', 'Unit_Name')

class HSCodeMeta_Admin(admin.ModelAdmin):
    list_display = ('id', 'HS_Code', 'Product_Information')

class TradeData_Admin(admin.ModelAdmin):
    list_display = ('id', 'Trade_Type', 'Calender', 'Country', 'HS_Code')

admin.site.register(Country_meta, CountryMeta_Admin)
admin.site.register(Unit_meta, UnitMeta_Admin)
admin.site.register(HS_Code_meta, HSCodeMeta_Admin)
admin.site.register(TradeData, TradeData_Admin)
