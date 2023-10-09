from django.contrib import admin
from .models import Country_meta, Unit_meta, HS_Code_meta, TradeData
# Register your models here.

admin.site.register(Country_meta)
admin.site.register(Unit_meta)
admin.site.register(HS_Code_meta)
admin.site.register(TradeData)

