from django.contrib import admin

from .models import ForestData,PopulationData,Land_Code_Meta,Land,Transport_Meta,Transport,Tourism,Tourism_Meta,Hotel,Water,Water_Meta

class LandCodeMeta_Admin(admin.ModelAdmin ):
    list_display=('id','Code','Land_Type')

admin.site.register(Land_Code_Meta,LandCodeMeta_Admin)

class ForestData_Admin(admin.ModelAdmin ):
    list_display = ('id', 'Name_Of_The_Plant','Country', 'Area_Unit', 'Area_Covered',  'Stock_Unit', 'Stock_Available')

admin.site.register(ForestData, ForestData_Admin)

class Land_Admin(admin.ModelAdmin ):
    list_display=('id','Year','Country','Land_Code','Unit','Area')

admin.site.register(Land,Land_Admin)


class PopulationData_Admin(admin.ModelAdmin):
    list_display = ['id','Year','Country','Gender','Age_Group','Population']

admin.site.register(PopulationData,PopulationData_Admin)










admin.site.register(Transport_Meta)

admin.site.register(Transport)

admin.site.register(Tourism_Meta)

admin.site.register(Tourism)

admin.site.register(Hotel)

admin.site.register(Water_Meta)

admin.site.register(Water)


