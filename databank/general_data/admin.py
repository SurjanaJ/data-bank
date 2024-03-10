from django.contrib import admin

from .models import ActivityData,Activity_Meta,Climate_Data, Climate_Place_Meta, Crime, Crime_Meta, Currency_Meta,  Education, Education_Degree_Meta, Education_Level_Meta, Energy, Energy_Meta, ForestData, Occupation, Occupation_Meta,PopulationData,Land_Code_Meta,Land, Services,Water,Water_Meta, Services_Meta,Transport_Meta,Transport,Tourism,Tourism_Meta,Hotel,Water,Water_Meta,Public_Unitillity,Mine_Meta,Mining,Road_Meta,Road,Housing_Meta,Housing,Health_disease_Meta,Health_disease,Budgetary_Data,Political_Data,Disaster_Data_Meta,Disaster_Data,Exchange

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

admin.site.register(Currency_Meta)
admin.site.register(Exchange)



admin.site.register(Transport_Meta)

admin.site.register(Transport,Transport_Admin)

admin.site.register(Tourism_Meta)

admin.site.register(Tourism)

admin.site.register(Hotel)

admin.site.register(Water_Meta)

admin.site.register(Water,Water_Admin)

admin.site.register(Public_Unitillity)

admin.site.register(Mine_Meta)

class Mining_Admin(admin.ModelAdmin ):
    list_display=('id','Year','Country','Name_Of_Mine','Unit','Current_Production',	'Potential_Stock','Mining_Company_Name')

admin.site.register(Mining,Mining_Admin)

admin.site.register(Road_Meta)

admin.site.register(Road)


admin.site.register(Housing_Meta)

class Housing_Admin(admin.ModelAdmin ):
    list_display=('id','Year','Country','House_Code','City','Number')

admin.site.register(Housing,Housing_Admin)

admin.site.register(Health_disease_Meta)

class Health_Disease_Admin(admin.ModelAdmin ):
    list_display=('id','Year','Country','Disease_Code','Unit','Number_Of_Case')

admin.site.register(Health_disease,Health_Disease_Admin)

admin.site.register(Budgetary_Data)



class Political_Admin(admin.ModelAdmin ):
    list_display=('id','Year','Country','Political_Party_Name','Number_Of_Member','Province','District','Municipality','Wards')

admin.site.register(Political_Data,Political_Admin)


admin.site.register(Disaster_Data_Meta)

class Disaster_Admin(admin.ModelAdmin ):
    list_display=('id','Year','Country','Disaster_Code','Human_Loss','Animal_Loss','Physical_Properties_Loss_In_USD')

admin.site.register(Disaster_Data,Disaster_Admin)

admin.site.register(ActivityData)

admin.site.register(Activity_Meta)




