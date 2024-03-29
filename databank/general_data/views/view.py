from datetime import datetime
from django.db import DataError
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import resolve, reverse
from django.db.models import Q
import pandas as pd
from trade_data import views
from ..models import Hotel, Land, Mine_Meta, PopulationData, Public_Unitillity,Road_Meta,Housing_Meta,Health_disease_Meta,Disaster_Data_Meta,Budgetary_Data, Production, Production_Meta,Publication,Index,Climate_Data, Crime, Crime_Meta, Disaster_Data, Exchange, Health_disease,Road,Mining,Housing,Political_Data, Education, Education_Degree_Meta, Education_Level_Meta, Energy, Energy_Meta, ForestData, Country_meta, Land_Code_Meta, Occupation, Occupation_Meta, Services, Services_Meta, Tourism, Tourism_Meta, Transport, Transport_Meta, Water, Water_Meta,Activity_Meta,ActivityData
from ..forms import UpdateActivity, UpdateForest, UpdateHotel, UpdateLand, UpdatePopulation, UpdateTourism, UpdateTransport, UpdateUtility, UpdateWater,UploadActivityMetaForm ,UpdateBudget, UpdateProduction, UpdatePublication,UpdateClimate, UpdateCrime, UpdateDisaster,UpdateExchange, UpdateHealthDisease,UpdateHousing, UpdateIndex,UpdateMining,UpdatePolitical,UpdateRoad, UpdateEducation, UpdateEnergy, UpdateOccupation, UpdateServices, UploadCrimeMetaForm,  UploadEducationDegreeMetaForm, UploadEducationLevelMetaForm, UploadEnergyMetaForm, UploadForestDataForm,UploadForestData, UploadLandMetaForm, UploadOccupationMetaForm, UploadProductionMetaForm, UploadServicesMetaForm, UploadTourismMetaForm, UploadTransportMetaForm, UploadWaterMetaForm,UploadMiningMetaForm,UploadHousingMetaForm,UploadHealthDiseaseMetaForm,UploadRoadMetaForm,UploadDisasterMetaForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse
from .energy_view import strip_spaces

from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users

def is_valid_queryparam(param):
    return param !='' and param is not None
    
@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_forest_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0 

    if request.method == 'POST':
        form = UploadForestDataForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['forest_data_file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

            # Check if required columns exist
            required_columns = ['Year', 'Country', 'Name Of The Plant','Scientific Name','Local Name','Stock Unit','Stock Available','Area Unit','Area Covered']  # Add your required column names here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing columns: {', '.join(missing_columns)}")
                return render(request,'general_data/invalid_upload.html', {'missing_columns': missing_columns, 'tables': tables, 'meta_tables': views.meta_tables,} )
            
            
            #Update existing data
            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Name Of The Plant': row['Name Of The Plant'],
                        'Scientific Name': row['Scientific Name'],
                        'Local Name': row['Local Name'],
                        'Stock Unit': row['Stock Unit'],
                        'Stock Available': row['Stock Available'],
                        'Area Unit': row['Area Unit'],
                        'Area Covered': row['Area Covered']
                    }

                    try:
                        forest_instance = ForestData.objects.get(id=id)
                        forest_data = data

                        try:
                            Country = Country_meta.objects.filter(Country_Name=row['Country']).first()
                            
                            forest_instance.Year = row['Year']
                            forest_instance.Country = Country
                            forest_instance.Name_Of_The_Plant = row['Name Of The Plant']
                            forest_instance.Scientific_Name = row['Scientific Name']
                            forest_instance.Local_Name = row['Local Name']
                            forest_instance.Stock_Unit = row['Stock Unit']
                            forest_instance.Stock_Available = row['Stock Available']
                            forest_instance.Area_Unit = row['Area Unit']
                            forest_instance.Area_Covered = row['Area Covered']

                            forest_instance.save()
                            updated_count += 1

                        except Exception as e:
                            forest_data = data
                            errors.append({
                                            'row_index': index,
                                            'data': forest_data,
                                            'reason': f'Error inserting row {index}: {e}'
                                        })
                            continue

                    except Exception as e:
                        forest_data = data
                        errors.append({
                                    'row_index': index,
                                    'data': forest_data,
                                    'reason': f'Error inserting row {index}: {e}'
                                })
                        continue

            else:

                for index, row in df.iterrows():
                    data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Name Of The Plant': row['Name Of The Plant'],
                        'Scientific Name': row['Scientific Name'],
                        'Local Name': row['Local Name'],
                        'Stock Unit': row['Stock Unit'],
                        'Stock Available': row['Stock Available'],
                        'Area Unit': row['Area Unit'],
                        'Area Covered': row['Area Covered']
                    }


                    try:
                        Country = Country_meta.objects.get(Country_Name=row['Country'])

                        forest_data = {
                        'Year': row['Year'],
                        'Country': Country,
                        'Name Of The Plant': row['Name Of The Plant'],
                        'Scientific Name': row['Scientific Name'],
                        'Local Name': row['Local Name'],
                        'Stock Unit': row['Stock Unit'],
                        'Stock Available': row['Stock Available'],
                        'Area Unit': row['Area Unit'],
                        'Area Covered': row['Area Covered']}

                        existing_record = ForestData.objects.filter(
                            Q(Year=row['Year']) 
                            & Q(Country=Country) 
                            & Q(Name_Of_The_Plant = forest_data['Name Of The Plant']) 
                            & Q(Stock_Unit = forest_data['Stock Unit']) 
                            & Q(Area_Unit = forest_data['Area Unit']) 
                            & Q(Scientific_Name = forest_data['Scientific Name']) 
                            & Q(Local_Name = forest_data['Local Name']) 
                            & Q(Stock_Available = forest_data['Stock Available']) 
                            & Q(Area_Covered = forest_data['Area Covered'])).first()  

                        # show duplicate data
                        if existing_record:
                            forest_data = data

                            duplicate_data.append({
                                'row_index': index,
                                'data': {key: str(value) for key, value in forest_data.items()}
                            })
                            continue
                        else:
                            #add new record
                            try:
                                forest_data = {
                                'Year': row['Year'],
                                'Country': Country,
                                'Name_Of_The_Plant': row['Name Of The Plant'],
                                'Scientific_Name': row['Scientific Name'],
                                'Local_Name': row['Local Name'],
                                'Stock_Unit': row['Stock Unit'],
                                'Stock_Available': row['Stock Available'],
                                'Area_Unit': row['Area Unit'],
                                'Area_Covered': row['Area Covered']}
                                forestData = ForestData(**forest_data)
                                forestData.save()
                                added_count += 1
                            
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")
                          
                    
                    except Exception as e:
                        forest_data = data
                        errors.append({
                                    'row_index': index,
                                    'data': forest_data,
                                    'reason': f'Error inserting row {index}: {e}'
                                })
                        continue


            if added_count > 0:
                messages.success(request, f'{added_count} records added')

            if updated_count > 0:
                messages.success(request, f'{updated_count} records updated')

            if errors:
                request.session['errors'] = errors
                return render(request, 'trade_data/error_template.html', {'errors': errors, 'tables': tables, 'meta_tables': views.meta_tables, })
            
            if duplicate_data:
                request.session['duplicate_data'] = duplicate_data
                return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data, 'tables': tables, 'meta_tables': views.meta_tables,})

            else:
           # form is not valid
                return redirect('forest_table')

    else:
        form = UploadForestDataForm()

    return render(request, 'general_data/upload_form.html', {'form': form, 'tables':tables})

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def update_forest_record(request,pk):
    forest_record = ForestData.objects.get(id=pk)
    form = UploadForestData(instance=forest_record)

    if request.method == 'POST':
        form = UploadForestData(request.POST, instance=forest_record)
        if form.is_valid():
            form.save()
            return redirect('forest_table')
        
    context={'form':form,}
    return render(request,'general_data/update_forest_record.html',context)

# def delete_selected_records(request):
#     if request.method == 'POST':
#         selected_record_ids = request.POST.getlist('selected_records')
#         ForestData.objects.filter(id__in=selected_record_ids).delete()

#     return redirect('forest_table')

@login_required(login_url = 'login')
def display_forest_table(request):
    url=reverse('forest_table')
    data=ForestData.objects.all()
    country_categories=Country_meta.objects.all()
    stock_unit_categories=[choice[1] for choice in ForestData.Stock_Unit_Options]
    area_unit_categories=[choice[1] for choice in ForestData.Area_Unit_Options]


    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    name_of_the_plant=request.GET.get('name_of_the_plant')
    area_unit=request.GET.get('area_unit')  
    stock_available=request.GET.get('stock_available')

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(name_of_the_plant):
        data=data.filter(Q(Name_Of_The_Plant__icontains=name_of_the_plant)).distinct()

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(area_unit)  and area_unit != '--':
        data=data.filter(Area_Unit=area_unit)

    if is_valid_queryparam(stock_available):
        data=data.filter(Stock_Available__gte=stock_available)
        
    
    #get form data for filteration

    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context={
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'country_categories':country_categories,
        'stock_unit_categories':stock_unit_categories,
        'area_unit_categories':area_unit_categories,
        'tables':tables
    }

    return render(request, 'general_data/forest_table.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def delete_forest_record(request, item_id):
    try:
        item_to_delete = get_object_or_404(ForestData, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('forest_table')
    except Exception as e:
        messages.error(request, f'Error deleting item: {e}')

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
@require_POST
def delete_selected_forest(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('forest_table')
    try:
        ForestData.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('forest_table')

def duplicate_data_to_excel(duplicate_data):
    column_names = list(duplicate_data[0]['data'].keys())
    duplicate_df = pd.DataFrame([d['data'] for d in duplicate_data], columns=column_names)

    # Create a response object with Excel content
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=duplicate_data.xlsx'

    duplicate_df.to_excel(response, index=False, sheet_name='duplicate_data')

    return response

# Get the data from session storage
def download_duplicate_excel(request):
    duplicate_data = request.session.get('duplicate_data', [])
    
    if duplicate_data:
        response = duplicate_data_to_excel(duplicate_data)
        request.session.pop('duplicate_data', None)
        return response
    else:
        return HttpResponse('No data to export.')
    
def error_data_to_excel(error_data):
    column_names = list(error_data[0]['data'].keys())
    error_df = pd.DataFrame([d['data'] for d in error_data], columns=column_names)

    # Create a response object with Excel content
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=error_data.xlsx'

    error_df.to_excel(response, index=False, sheet_name='error_data')

    return response

def download_error_excel(request):
    error_data = request.session.get('errors', [])

    if error_data:
        response = error_data_to_excel(error_data)
        request.session.pop('error_data', None)
        return response
    else:
        return HttpResponse('No data to export.')

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])    
def upload_meta_excel(request):
    errors = []
    duplicate_data = []
    added_count = 0
    updated_count = 0

    form_mapping = {
        '/others/upload_land_meta_excel': UploadLandMetaForm,
        '/others/upload_transport_meta_excel': UploadTransportMetaForm,
        '/others/upload_tourism_meta_excel' : UploadTourismMetaForm,
        '/others/upload_water_meta_excel':UploadWaterMetaForm,   
        '/others/upload_services_meta_excel': UploadServicesMetaForm,  
        '/others/upload_crime_meta_excel': UploadCrimeMetaForm,  
        '/others/upload_education_level_meta_excel':UploadEducationLevelMetaForm,
        '/others/upload_education_degree_meta_excel': UploadEducationDegreeMetaForm,   
        '/others/upload_occupation_meta_excel': UploadOccupationMetaForm,
        '/others/upload_energy_meta_excel' : UploadEnergyMetaForm,
        '/others/upload_mining_meta_excel': UploadMiningMetaForm,
        '/others/upload_road_meta_excel':UploadRoadMetaForm,
        '/others/upload_housing_meta_excel':UploadHousingMetaForm,
        '/others/upload_health_disease_meta_excel':UploadHealthDiseaseMetaForm,
        '/others/upload_disaster_data_meta_excel':UploadDisasterMetaForm,
        '/others/upload_activity_meta_excel':UploadActivityMetaForm,
        '/others/upload_water_meta_excel':UploadWaterMetaForm,
        
        '/others/upload_production_meta_excel':UploadProductionMetaForm,
    }

    form_class = form_mapping.get(request.path)

    model_mapping = {
        UploadLandMetaForm: Land_Code_Meta,
        UploadTransportMetaForm : Transport_Meta,
        UploadTourismMetaForm : Tourism_Meta,
        UploadWaterMetaForm: Water_Meta,
        UploadServicesMetaForm : Services_Meta,
        UploadCrimeMetaForm : Crime_Meta,
        UploadEducationLevelMetaForm : Education_Level_Meta,
        UploadEducationDegreeMetaForm : Education_Degree_Meta,
        UploadOccupationMetaForm :Occupation_Meta,
        UploadEnergyMetaForm : Energy_Meta,
        UploadMiningMetaForm:Mine_Meta,
        UploadRoadMetaForm:Road_Meta,
        UploadHousingMetaForm:Housing_Meta,
        UploadHealthDiseaseMetaForm:Health_disease_Meta,
        UploadDisasterMetaForm:Disaster_Data_Meta,
        UploadActivityMetaForm:Activity_Meta,
        UploadWaterMetaForm:Water_Meta,
        UploadProductionMetaForm: Production_Meta,
    }
    model_class = model_mapping.get(form_class)

    view_mapping = {
    Land_Code_Meta: 'land_meta',
    Transport_Meta: 'transport_meta',
    Tourism_Meta: 'tourism_meta',
    Water_Meta: 'water_meta',
    Services_Meta: 'services_meta',
    Crime_Meta: 'crime_meta',
    Education_Level_Meta : 'education_level_meta',
    Education_Degree_Meta : 'education_degree_meta',
    Occupation_Meta : 'occupation_meta',
    Energy_Meta: 'energy_meta',
    Mine_Meta:'mine_meta',
    Road_Meta:'road_meta',
    Housing_Meta:'housing_meta',
    Health_disease_Meta:'health_disease_meta',
    Disaster_Data_Meta:'disaster_data_meta',
    Activity_Meta:'activity_meta',
    Water_Meta:'water_meta',
    Production_Meta : 'production_meta'
}
    model_view = view_mapping.get(model_class)            

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)

        if form.is_valid():
            excel_data = request.FILES['meta_file']

            df = pd.read_excel(excel_data,dtype={'Code': str})
            cols = df.columns.tolist()
            
            for index, row in df.iterrows():
                data = {col: row[col] for col in cols}
                
                conditions = {f"{key}": value for key, value in data.items()}

                existing_record = model_class.objects.filter(Q(**conditions)).first()
                
                if existing_record:
                    if all(getattr(existing_record, key) == value for key, value in data.items()):
                        duplicate_data.append({'row_index': index, 'data': data})
                    
                    else:
                        # Update the row with non-duplicate data
                        for key, value in data.items():
                            setattr(existing_record, key, value)
                        try:
                            existing_record.save()
                            updated_count += 1
                        except IntegrityError as e:
                            errors.append(f"Error updating row {index}: {e}")

                else:
                    try:
                        model_instance = model_class(**data)
                        model_instance.save()
                        added_count += 1

                        existing_record = model_class.objects.filter()
                    except IntegrityError as e:
                        errors.append(f"Error inserting row {index}: {e}")

            if added_count > 0:
                messages.success(request, str(added_count) + ' records added.')
            
            if updated_count > 0:
                messages.info(request, str(updated_count) + ' records updated.')

            if errors:
                # If there are errors, return them as a response
                return render(request, 'trade_data/error_template.html', {'errors': errors,'tables':tables, 'meta_tables':views.meta_tables,})
            
            elif duplicate_data:
                request.session['duplicate_data'] = duplicate_data
                return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data,'tables':tables, 'meta_tables':views.meta_tables,})
            else:
                return redirect(f'{model_view}')

    else:
        form = form_class()
    return render(request, 'general_data/upload_form.html',  {'form': form, 'tables': tables, 'meta_tables':views.meta_tables,})

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def update_record(request,pk):
    resolved =  resolve(request.path_info)
    view_name = resolved.url_name

    model_mapping = {
        'update_forest_record':ForestData,
        'update_services_record': Services,
        'update_crime_record': Crime,
        'update_education_record': Education,
        'update_occupation_record': Occupation,
        'update_disaster_record':Disaster_Data,
        'update_health_disease_record':Health_disease,
        'update_road_record':Road,
        'update_housing_record':Housing,
        'update_political_record':Political_Data,
        'update_mining_record':Mining,
        'update_climate_record': Climate_Data,
        'update_exchange_record':Exchange,
        'update_energy_record':Energy,
        'update_activity_record':ActivityData,
        'update_index_record':Index,
        'update_publication_record':Publication,
        'update_budget_record':Budgetary_Data,
        'update_production_record': Production,
        'update_population_record':PopulationData,
        'update_land_record':Land,
        'update_transport_record':Transport,
        'update_hotel_record':Hotel,
        'update_water_record':Water,
        'update_tourism_record':Tourism,
        'update_public_unitillity_record':Public_Unitillity,
    }

    form_mapping = {
        ForestData: UpdateForest,
        Services : UpdateServices,
        Crime: UpdateCrime,
        Education: UpdateEducation,
        Occupation: UpdateOccupation,
        Disaster_Data:UpdateDisaster,
        Health_disease:UpdateHealthDisease,
        Road:UpdateRoad,
        Housing:UpdateHousing,
        Political_Data:UpdatePolitical,
        Mining:UpdateMining,
        Climate_Data: UpdateClimate,
        Exchange: UpdateExchange,
        Energy: UpdateEnergy,
        ActivityData:UpdateActivity,
        Index: UpdateIndex,
        Publication: UpdatePublication,
        Budgetary_Data:UpdateBudget,
        Production: UpdateProduction,
        PopulationData:UpdatePopulation,
        Land:UpdateLand,
        Transport:UpdateTransport,
        Hotel: UpdateHotel,
        Water:UpdateWater,
        Tourism: UpdateTourism,
        Public_Unitillity: UpdateUtility,
    }
    view_mapping = {
        Services: 'services_table',
        Crime: 'crime_table',
        Education: 'education_table',
        Occupation:'occupation_table',
        Disaster_Data:'disaster_table',
        Health_disease:'health_disease_table',
        Mining:'mining_table',
        Housing:'housing_table',
        Political_Data:'political_table',
        Road:'road_table',
        Climate_Data:'climate_table',
        Exchange: 'exchange_table',
        Energy: 'energy_table',
        ActivityData:'activity_table',
        Index: 'index_table',
        Publication: 'publication_table',
        Budgetary_Data:'budget_table',
        Production: 'production_table',
        ForestData: 'forest_table',
        PopulationData:'population_table',
        Land:'land_table',
        Transport:'transport_table',
        Hotel:'hotel_table',
        Water:'water_table',
        Tourism:'tourism_table',
        Public_Unitillity:'public_unitillity_table',
    }

    model_class = model_mapping.get(view_name)
    model_form = form_mapping.get(model_class)
    model_view = view_mapping.get(model_class)

    record = model_class.objects.get(id=pk)
    form = model_form(instance=record)

    if request.method == 'POST':
        form = model_form(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect(model_view)

    context = {'form': form,'tables':views.tables, 'meta_tables': views.meta_tables}
    return render(request, 'general_data/update_record.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])  
def delete_record(request,pk):
    resolved =  resolve(request.path_info)
    view_name = resolved.url_name
    model_mapping = {
        'delete_services_record': Services,
        'delete_crime_record': Crime,
        'delete_education_record': Education,
        'delete_occupation_record': Occupation,
        'delete_disaster_record':Disaster_Data,
        'delete_health_disease_record':Health_disease,
        'delete_road_record':Road,
        'delete_mining_record':Mining,
        'delete_housing_record':Housing,
        'delete_political_record':Political_Data,
        'delete_activity_record':ActivityData,
        'delete_climate_record': Climate_Data,
        'delete_exchange_record': Exchange,
        'delete_energy_record':Energy,
        'delete_index_record': Index,
        'delete_publication_record': Publication,
        'delete_budget_record': Budgetary_Data,
        'delete_production_record':Production,
    }

    view_mapping = {
        Services: 'services_table',
        Crime: 'crime_table',
        Education: 'education_table',
        Occupation: 'occupation_table',
        Disaster_Data:'disaster_table',
        Health_disease:'health_disease_table',
        Road:'road_table',
        Mining:'mining_table',
        Housing:'housing_table',
        Political_Data:'political_table',
        Climate_Data:'climate_table',
        Exchange: 'exchange_table',
        Energy:'energy_table',
        ActivityData:'activity_table',
        Index : 'index_table',
        Publication: 'publication_table',
        Budgetary_Data:'budget_table',
        Production:'production_table'
    }

    model_class = model_mapping.get(view_name)
    model_view = view_mapping.get(model_class)

    try:
        item_to_delete = get_object_or_404(model_class, id=pk)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect(model_view)
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])    
def delete_selected(request):
    resolved =  resolve(request.path_info)
    view_name = resolved.url_name
    model_mapping = {
        'delete_selected_services': Services,
        'delete_selected_crime': Crime,
        'delete_selected_education': Education,
        'delete_selected_occupation': Occupation,
        'delete_selected_disaster':Disaster_Data,
        'delete_selected_health_disease':Health_disease,
        'delete_selected_mining':Mining,
        'delete_selected_housing':Housing,
        'delete_selected_road':Road,
        'delete_selected_political':Political_Data,
        'delete_selected_climate':Climate_Data,
        'delete_selected_exchange':Exchange,
        'delete_selected_energy':Energy,
        'delete_selected_index': Index,
        'delete_selected_publication':Publication,
        'delete_selected_budget':Budgetary_Data,
        'delete_selected_production':Production
    }

    view_mapping = {
        Services: 'services_table',
        Crime: 'crime_table',
        Education: 'education_table',
        Occupation:'occupation_table',
        Disaster_Data:'disaster_table',
        Health_disease:'health_disease_table',
        Road:'road_table',
        Mining:'mining_table',
        Housing:'housing_table',
        Political_Data:'political_table',
        Climate_Data: 'climate_table',
        Exchange:'exchange_table',
        Energy:'energy_table',
        Index:'index_table',
        Publication:'publication_table',
        Budgetary_Data: 'budget_table',
        Production: 'production_table'
    }
    model_class = model_mapping.get(view_name)
    model_view = view_mapping.get(model_class)
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect(model_view)
    try:
        model_class.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect(model_view)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])   
def update_selected_forest(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('forest_table')

    else:
        queryset = ForestData.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','Name_Of_The_Plant','Scientific_Name','Local_Name','Stock_Unit','Stock_Available','Area_Unit','Area_Covered')))
        df.rename(columns={'country': 'Country','Name_Of_The_Plant':'Name Of The Plant','Scientific_Name':'Scientific Name','Local_Name':'Local Name', 'Stock_Unit':'Stock Unit','Stock_Available':'Stock Available','Area_Unit':'Area Unit','Area_Covered':'Area Covered'}, inplace=True)
        df = df[['id','Year', 'Country','Year','Country','Name Of The Plant','Scientific Name','Local Name','Stock Unit','Stock Available','Area Unit','Area Covered']]
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')  
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.close()  
        output.seek(0)

        response = HttpResponse(
            output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
        return response