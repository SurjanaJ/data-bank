from django.contrib import admin
from .models import Country_meta,HS_Code_meta, Unit_meta,TradersName_ExporterImporter_meta,TradeData


admin.site.register(Country_meta)
admin.site.register(HS_Code_meta)
admin.site.register(Unit_meta)

admin.site.register(TradersName_ExporterImporter_meta)
admin.site.register(TradeData)
