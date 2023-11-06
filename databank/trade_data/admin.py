from django.contrib import admin

from .models import Country_meta, HS_Code_meta, Unit_meta, TradeData

# Register your models here.

class CountryMeta_Admin(admin.ModelAdmin):
    list_display = ('id', 'Country_Name', 'Country_Code_2', 'Country_Code_3')

admin.site.register(Country_meta, CountryMeta_Admin)
admin.site.register(Unit_meta)
admin.site.register(HS_Code_meta)
admin.site.register(TradeData)
