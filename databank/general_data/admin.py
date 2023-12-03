from django.contrib import admin

from .models import ForestData,PopulationData,Land_Code_Meta,Land,Transport_Meta,Transport

admin.site.register(PopulationData)
admin.site.register(Land_Code_Meta)

class ForestData_Admin(admin.ModelAdmin ):
    list_display = ('id', 'Name_Of_The_Plant','Country', 'Area_Unit', 'Area_Covered',  'Stock_Unit', 'Stock_Available')

admin.site.register(ForestData, ForestData_Admin)

admin.site.register(Land)

admin.site.register(Transport_Meta)

admin.site.register(Transport)


