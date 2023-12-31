from django.contrib import admin

from .models import ForestData,PopulationData,Land_Code_Meta,Land,Transport_Meta,Transport,Tourism,Tourism_Meta,Hotel,Water,Water_Meta,Public_Unitillity,Mine_Meta,Mining,Energy_Meta,Energy,Road_Meta,Road,Housing_Meta,Housing,Health_disease_Meta,Health_disease,Budgetary_Data,Political_Data,Disaster_Data_Meta,Disaster_Data

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


class Transport_Admin(admin.ModelAdmin):
    list_display=['id','Year','Country','Transport_Classification_Code','Unit','Quantity']
    
    

class Water_Admin(admin.ModelAdmin):
    list_display=['id','Year','Country','Water_Type_Code','Unit','Volume','Name_Of_The_River']







admin.site.register(Transport_Meta)

admin.site.register(Transport,Transport_Admin)

admin.site.register(Tourism_Meta)

admin.site.register(Tourism)

admin.site.register(Hotel)

admin.site.register(Water_Meta)

admin.site.register(Water,Water_Admin)

admin.site.register(Public_Unitillity)

admin.site.register(Mine_Meta)

admin.site.register(Mining)

admin.site.register(Energy_Meta)

admin.site.register(Energy)

admin.site.register(Road_Meta)

admin.site.register(Road)

admin.site.register(Housing_Meta)

admin.site.register(Housing)

admin.site.register(Health_disease_Meta)

admin.site.register(Health_disease)

admin.site.register(Budgetary_Data)

admin.site.register(Political_Data)

admin.site.register(Disaster_Data_Meta)

admin.site.register(Disaster_Data)




