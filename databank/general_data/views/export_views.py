from ..models import ForestData,Land,Hotel,Transport,Tourism,Water,PopulationData,Mining,Political_Data,Road,Housing,Health_disease,Disaster_Data,Public_Unitillity
from io import BytesIO
from ..views import view,population_view,tourism_view,transport_view,hotel_view,water_view,political_views,road_views,mining_views,health_diseases_views,housing_views,disaster_views
import xlsxwriter
from django.db.models import Q
from django.db.models import F
import pandas as pd
from django.shortcuts import HttpResponse


def filter(request):
    data =ForestData.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    name_of_the_plant = request.GET.get('name_of_the_plant')
    stock_available = request.GET.get('stock_available')
    area_unit = request.GET.get('area_unit')

    if view.is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if view.is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if view.is_valid_queryparam(name_of_the_plant):
        data=data.filter(Q(Name_Of_The_Plant__icontains=name_of_the_plant)).distinct()

    if view.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if view.is_valid_queryparam(area_unit)  and area_unit != '--':
        data=data.filter(Area_Unit=area_unit)

    if view.is_valid_queryparam(stock_available):
        data=data.filter(Stock_Available__gte=stock_available)

    return data

def export_forest_table_to_excel(request):
    data=filter(request)

    data=data.annotate(
        country_name=F('Country__Country_Name'),
    )

    df=pd.DataFrame(data.values('Year','country_name','Name_Of_The_Plant','Scientific_Name','Local_Name','Stock_Unit','Stock_Available','Area_Unit','Area_Covered'))


    df.rename(columns={'country_name': 'Country'},inplace=True)

    df = df[['Year','Country','Name_Of_The_Plant','Scientific_Name','Local_Name','Stock_Unit','Stock_Available','Area_Unit','Area_Covered']]
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    writer.close()
    output.seek(0)

    response = HttpResponse(
        output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=forest_table.xlsx'
    return response


# export land 

def filter_land(request):
    data =Land.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    land_code = request.GET.get('land_code')
    unit = request.GET.get('land_unit')
    min_value = request.GET.get('minimum_population')
    max_value = request.GET.get('maximum_population')

 
 
    if view.is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if view.is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if view.is_valid_queryparam(land_code) and land_code != '--':
        data=data.filter(Land_Code = land_code)
     

    if view.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)
        

    if view.is_valid_queryparam(unit)  and unit != '--':
        data=data.filter(Unit=unit)

    if view.is_valid_queryparam(min_value):
        data = data.filter(Area__gte=min_value)

    if view.is_valid_queryparam(max_value):
        data = data.filter(Area__lt=max_value)

    return data




def export_land_table_to_excel(request):
    data=filter_land(request)

    data = data.annotate(
        country_name=F('Country__Country_Name'),
        land_code=F('Land_Code__Code'),
        land_type=F('Land_Code__Land_Type')

    )
    df = pd.DataFrame(data.values('Year','country_name','land_code','land_type','Unit','Area'))


    df.rename(columns={'country_name':'Country','land_code':'Land_Code','land_type':'Land_Type'},inplace=True)


    df= df[['Year','Country','Land_Code','Land_Type','Unit','Area']]

    output=BytesIO()
    writer = pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='Sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Land.xlsx'
    return response



#filter hotel required


def filter_hotel(request):
    data=Hotel.objects.all()

    
    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    name_of_the_hotel=request.GET.get('name_of_the_hotel')
    name_of_the_city=request.GET.get('name_of_the_city')



    country_category = request.GET.get('country_category')

    if hotel_view.is_valid_queryparam (date_min):
        data=data.filter(Year__gte=date_min)

    if hotel_view.is_valid_queryparam(date_max):
        data=data.filter(Year__lte=date_max)

    if hotel_view.is_valid_queryparam(name_of_the_hotel):
        data=data.filter(Q(Name_Of_The_Hotel__icontains=name_of_the_hotel)).distinct()

    if hotel_view.is_valid_queryparam(name_of_the_city):
        data=data.filter(Q(City__icontains=name_of_the_city)).distinct()
 
    if hotel_view.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    return data

def export_hotel_table_to_excel(request):
    data=filter_hotel(request)

    data=data.annotate(
        country_name=F('Country__Country_Name'),
    )

    df = pd.DataFrame(data.values('Year','country_name','Name_Of_The_Hotel','Capacity_Room','Occupancy_In_Year','City'))

    df.rename(columns={'country_name':'Country'},inplace=True)

    df = df[['Year','Country','Name_Of_The_Hotel','Capacity_Room','Occupancy_In_Year','City']]

    output=BytesIO()
    writer = pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='Sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Hotel_Data.xlsx'
    return response


#filter population required
def filter_population(request):
    data = PopulationData.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    gender=request.GET.get('gender')
    age_group=request.GET.get('age_group')
    min_population = request.GET.get('minimum_population')
    max_population = request.GET.get('maximum_population')


    if population_view.is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if population_view.is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if population_view.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if population_view.is_valid_queryparam(gender) and gender != '--':
        data = data.filter(Gender=gender)

    if population_view.is_valid_queryparam(age_group) and age_group != '--':
        data = data.filter(Age_Group=age_group)
    
    if population_view.is_valid_queryparam(min_population):
        data = data.filter(Population__gte=min_population)

    if population_view.is_valid_queryparam(max_population):
        data = data.filter(Population__lt=max_population)

    return data

def export_population_table_to_excel(request):
    data = filter_population(request)

    data = data.annotate(
        country_name=F('Country__Country_Name'),
    )

    df = pd.DataFrame(data.values('Year','country_name','Gender','Age_Group','Population'))
    df.rename(columns={'country_name':'Country'},inplace=True)

    df = df[['Year','Country','Gender','Age_Group','Population']]

    output=BytesIO()
    writer = pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='Sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Population_Data.xlsx'
    return response


# filter tourism

def filter_tourism(request):
    data = Tourism.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    arrival_mode = request.GET.get('arrival_mode')
    country_category = request.GET.get('country_category')
    nationality_category = request.GET.get('nationality_category')
    min_tourist = request.GET.get('minimum_tourist')
    max_tourist = request.GET.get('maximum_tourist')


    if tourism_view.is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if  tourism_view.is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if  tourism_view.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if  tourism_view.is_valid_queryparam(nationality_category) and nationality_category != '--':
        data = data.filter(Nationality_Of_Tourism_id=nationality_category)

    if  tourism_view.is_valid_queryparam(arrival_mode) and arrival_mode != '--':
        data = data.filter(Arrival_code_id=arrival_mode)

    if  tourism_view.is_valid_queryparam(min_tourist):
        data = data.filter(Number_Of_Tourist__gte=min_tourist)

    if  tourism_view.is_valid_queryparam(max_tourist):
        data = data.filter(Number_Of_Tourist__lt=max_tourist)

    return data



def export_tourism_table_to_excel(request):
    data = filter_tourism(request)
    data = data.annotate(
        country_name=F('Country__Country_Name'),
        arrival_mode=F('Arrival_code__Code'),
        nationality_of_tourism=F('Nationality_Of_Tourism__Country_Name')
    )

    df = pd.DataFrame(data.values('Year','country_name','Number_Of_Tourist','nationality_of_tourism','arrival_mode','Number'))


    df.rename(columns={'country_name':'Country','nationality_of_tourism':'Nationality_Of_Tourism','arrival_mode':'Arrival_Mode'},inplace=True)  

    df = df[['Year','Country','Number_Of_Tourist','Nationality_Of_Tourism','Arrival_Mode','Number']]  
    
    output=BytesIO()
    writer = pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='Sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Tourism_Data.xlsx'
    return response

# water 
def filter_water(request):
    data=Water.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    water_code = request.GET.get('water_code')
    name_of_the_river = request.GET.get('name_of_the_river')
    unit=request.GET.get('unit')
    min_volume = request.GET.get('minimum_volume')  
    max_volume = request.GET.get('maximum_volume')


    if water_view.is_valid_queryparam (date_min):
        data=data.filter(Year__gte=date_min)

    if water_view.is_valid_queryparam(date_max):
        data=data.filter(Year__lte=date_max)

    if water_view.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if water_view.is_valid_queryparam(water_code) and water_code != '--':
        data = data.filter(Water_Type_Code_id=water_code)

    if water_view.is_valid_queryparam(unit) and unit != '--':
        data = data.filter(Unit=unit)


    if water_view.is_valid_queryparam(name_of_the_river):
        data=data.filter(Q(Name_Of_The_River__icontains=name_of_the_river)).distinct()

    if water_view.is_valid_queryparam(min_volume):
        data = data.filter(Volume__gte=min_volume)

    if water_view.is_valid_queryparam(max_volume):
        data = data.filter(Volume__lt=max_volume)

    return data


def export_water_table_to_excel(request):
    data=filter_water(request)

    data=data.annotate(
        country_name=F('Country__Country_Name'),
        water_code = F('Water_Type_Code__Code'),
    )

    df=pd.DataFrame(data.values('Year','country_name','water_code','Description','Unit','Volume','Name_Of_The_River'))

    df.rename(columns={'country_name':'Country','water_code':'Water_Type_Code'},inplace=True)

    df=df[['Year','Country','Water_Type_Code','Description','Unit','Volume','Name_Of_The_River']]

    output=BytesIO()
    writer=pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['content-Disposition'] = 'attachment; filename=Water_Data.xlsx'
    return response

# transport 

def filter_transport(request):
    data = Transport.objects.all()
    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    transport_classification_code = request.GET.get('transport_classification_code')

    quantity_unit=request.GET.get('quantity_unit')
    min_quantity = request.GET.get('minimum_quantity')
    max_quantity = request.GET.get('maximum_quantity')

    if transport_view.is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if transport_view.is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if transport_view.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if transport_view.is_valid_queryparam(transport_classification_code) and transport_classification_code != '--':
        data = data.filter(Transport_Classification_Code_id=transport_classification_code)

    if transport_view.is_valid_queryparam(quantity_unit) and quantity_unit != '--':
        data = data.filter(Unit=quantity_unit)

    if transport_view.is_valid_queryparam(min_quantity):
        data = data.filter(Quantity__gte=min_quantity)

    if transport_view.is_valid_queryparam(max_quantity):
        data = data.filter(Quantity__lt=max_quantity)

    return data

def export_transport_table_to_excel(request):
    data = filter_transport(request)
    
    data = data.annotate(
        country_name=F('Country__Country_Name'),
        transport_classification_code = F('Transport_Classification_Code__Code'),
    )

    df=pd.DataFrame(data.values('Year','country_name','transport_classification_code','Unit','Quantity'))

    df.rename(columns={'country_name':'Country','transport_classification_code':'Transport_Classification_Code'},inplace=True)

    df = df[['Year','Country','Transport_Classification_Code','Unit','Quantity']]

    output=BytesIO()
    writer=pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['content-Disposition'] = 'attachment; filename=transport_data.xlsx'
    return response

def filter_public_unitillity(request):
    data = Public_Unitillity.objects.all()


    return data

def export_public_unitillity_table_to_excel(request):
    data = filter_public_unitillity(request)

    df=None
    output=BytesIO()
    writer=pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['content-Disposition'] = 'attachment; filename=public_unitillity_data.xlsx'
    return response



def filter_road(request):
    data = Road.objects.all()


    return data
def export_road_table_to_excel(request):
    data = filter_road(request)

    df=None
    output=BytesIO()
    writer=pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['content-Disposition'] = 'attachment; filename=road_data.xlsx'
    return response


def filter_political(request):
    data = Political_Data.objects.all()


    return data

def export_political_table_to_excel(request):
    data = filter_political(request)

    df=None
    output=BytesIO()
    writer=pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['content-Disposition'] = 'attachment; filename=political_data.xlsx'
    return response


def filter_health_diseases(request):
    data = Health_disease.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    unit=request.GET.get('unit')
    disease_code = request.GET.get('health_disease_code')
    minimum_number = request.GET.get('minimum_number')
    maximum_number = request.GET.get('maximum_number')

    if health_diseases_views.is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if health_diseases_views.is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if health_diseases_views.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if health_diseases_views.is_valid_queryparam(unit)  and unit != '--':
        data=data.filter(Unit=unit)

    if health_diseases_views.is_valid_queryparam(minimum_number):
        data=data.filter(Number_Of_Case__gte=minimum_number)

    if health_diseases_views.is_valid_queryparam(maximum_number):
        data=data.filter(Number_Of_Case__lt=maximum_number)

    return data

def export_health_diseases_table_to_excel(request):
    data = filter_health_diseases(request)

    df=None
    output=BytesIO()
    writer=pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['content-Disposition'] = 'attachment; filename=health_diseases_data.xlsx'
    return response


def filter_housing(request):
    data = Housing.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    house_Code = request.GET.get('house_code')
    min_number = request.GET.get('minimum_number')  
    max_number = request.GET.get('maximum_number')
    name_of_the_city = request.GET.get('name_of_the_city')

  

    if housing_views.is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if housing_views.is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if housing_views.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if housing_views.is_valid_queryparam(house_Code) and house_Code != '--':
        data=data.filter(House_Code = house_Code)

    if housing_views.is_valid_queryparam(name_of_the_city):
        data=data.filter(Q(City__icontains=name_of_the_city)).distinct()

    if housing_views.is_valid_queryparam(max_number):
        data = data.filter(Number__lt=max_number)   

    if housing_views.is_valid_queryparam(min_number):
        data = data.filter(Number__gte=min_number)


    return data

def export_housing_table_to_excel(request):
    data = filter_housing(request)

    df=None
    output=BytesIO()
    writer=pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['content-Disposition'] = 'attachment; filename=housing_data.xlsx'
    return response


def filter_mining(request):
    data = Mining.objects.all()


    return data

def export_mining_table_to_excel(request):
    data = filter_mining(request)

    df=None
    output=BytesIO()
    writer=pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['content-Disposition'] = 'attachment; filename=mining_data.xlsx'
    return response


def filter_disaster(request):
    data = Disaster_Data.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    disaster_Code = request.GET.get('disaster_code')
    min_human_loss = request.GET.get('minimum_human_loss')
    max_human_loss = request.GET.get('maximum_human_loss')
    min_animal_loss = request.GET.get('minimum_animal_loss')
    max_animal_loss = request.GET.get('maximum_animal_loss')
    min_property_loss = request.GET.get('minimum_property_loss')
    max_property_loss = request.GET.get('maximum_property_loss')


    if disaster_views.is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if disaster_views.is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if disaster_views.is_valid_queryparam(disaster_Code) and disaster_Code != '--':
        data=data.filter(Disaster_Code = disaster_Code)
     

    if disaster_views.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if disaster_views.is_valid_queryparam(min_human_loss):
        data = data.filter(Human_Loss__gte=min_human_loss)

    if disaster_views.is_valid_queryparam(max_human_loss):
        data = data.filter(Human_Loss__lt=max_human_loss)

    if disaster_views.is_valid_queryparam(min_animal_loss):
        data = data.filter(Animal_Loss__gte=min_animal_loss)

    if disaster_views.is_valid_queryparam(max_animal_loss):
        data = data.filter(Animal_Loss__lt=max_animal_loss)

    if disaster_views.is_valid_queryparam(min_property_loss):
        data = data.filter(Physical_Properties_Loss_In_USD__gte=min_property_loss)

    if disaster_views.is_valid_queryparam(max_property_loss):
        data = data.filter(Physical_Properties_Loss_In_USD__lt=max_property_loss)

    return data

def export_disaster_table_to_excel(request):
    data = filter_disaster(request)

    df=None
    output=BytesIO()
    writer=pd.ExcelWriter(output,engine='xlsxwriter')
    df.to_excel(writer,sheet_name='sheet1',index=False)

    writer.close()
    output.seek(0)

    response=HttpResponse(
        output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['content-Disposition'] = 'attachment; filename=disaster_data.xlsx'
    return response

