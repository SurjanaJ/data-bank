from django.contrib import admin

from .models import Publication,Index,Climate_Data, Climate_Place_Meta, Crime, Crime_Meta, Currency_Meta,  Education, Education_Degree_Meta, Education_Level_Meta, Energy, Energy_Meta, ForestData, Occupation, Occupation_Meta,PopulationData,Land_Code_Meta,Land, Services, Services_Meta,Transport_Meta,Transport,Tourism,Tourism_Meta,Hotel,Water,Water_Meta,Public_Unitillity,Mine_Meta,Mining,Road_Meta,Road,Housing_Meta,Housing,Health_disease_Meta,Health_disease,Political_Data,Disaster_Data_Meta,Disaster_Data

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

class Services_Admin(admin.ModelAdmin):
    list_display = ['id','Country','Direction','Code', 'Value']
admin.site.register(Services, Services_Admin)
admin.site.register(Services_Meta)


class Crime_Admin(admin.ModelAdmin):
    list_display = ['id', 'Country', 'Year', 'Code','Gender','Age','District','created_date','modified_date']
admin.site.register(Crime, Crime_Admin)
admin.site.register(Crime_Meta)

class Education_Admin(admin.ModelAdmin):
    list_display = ['id', 'Level_Code', 'Degree_Code', 'Male','Female','created_date','modified_date']
admin.site.register(Education,Education_Admin)
admin.site.register(Education_Level_Meta)
admin.site.register(Education_Degree_Meta)

class Occupation_Meta_Admin(admin.ModelAdmin):
    list_display = ['id', 'SOC_Code', 'SOC_Group', 'SOC_Title']
class Occupation_Admin(admin.ModelAdmin):
    list_display = ['id', 'Country','Year','Code','Number']

admin.site.register(Occupation_Meta, Occupation_Meta_Admin)
admin.site.register(Occupation, Occupation_Admin)
admin.site.register(Climate_Place_Meta)
admin.site.register(Climate_Data)

class Energy_Meta_Admin(admin.ModelAdmin):
    list_display = ['id', 'Code', 'Energy_Type', 'created_date','modified_date']
class Energy_Admin(admin.ModelAdmin):
    list_display = ['id', 'Country','Year','Power_Code','created_date','modified_date']

admin.site.register(Energy_Meta, Energy_Meta_Admin)
admin.site.register(Energy, Energy_Admin)

class Index_Admin(admin.ModelAdmin):
    list_display = ['id','Country','Year','Index_Name','Score','Rank','No_Of_Countries','created_date','modified_date']
admin.site.register(Index, Index_Admin)


class Publication_Admin(admin.ModelAdmin):
    list_display = ['id','Country','Year','Book_Name','Writer_Name','created_date','modified_date']
admin.site.register(Publication, Publication_Admin)


admin.site.register(Currency_Meta)

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

admin.site.register(Road_Meta)

admin.site.register(Road)


admin.site.register(Housing_Meta)

admin.site.register(Housing)

admin.site.register(Health_disease_Meta)

admin.site.register(Health_disease)

admin.site.register(Political_Data)

admin.site.register(Disaster_Data_Meta)

admin.site.register(Disaster_Data)




