from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import resolve, reverse
from django.db.models import Q
import pandas as pd

from trade_data import views
from ..models import Publication,Index,Climate_Data, Crime, Crime_Meta, Disaster_Data, Health_disease,Road,Mining,Housing,Political_Data, Education, Education_Degree_Meta, Education_Level_Meta, Energy, Energy_Meta, Exchange, ForestData, Country_meta, Land_Code_Meta, Occupation, Occupation_Meta, Services, Services_Meta, Tourism_Meta, Transport_Meta, Water_Meta
from ..forms import UpdatePublication,UpdateClimate, UpdateCrime, UpdateDisaster, UpdateHealthDisease,UpdateHousing, UpdateIndex,UpdateMining,UpdatePolitical,UpdateRoad, UpdateEducation, UpdateEnergy, UpdateExchange, UpdateOccupation, UpdateServices, UploadCrimeMetaForm,  UploadEducationDegreeMetaForm, UploadEducationLevelMetaForm, UploadEnergyMetaForm, UploadForestDataForm,UploadForestData, UploadLandMetaForm, UploadOccupationMetaForm, UploadServicesMetaForm, UploadTourismMetaForm, UploadTransportMetaForm, UploadWaterMetaForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST


def is_valid_queryparam(param):
    return param !='' and param is not None
    

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

            Stock_unit_options = [option[0] for option in ForestData.Stock_Unit_Options]
            Area_unit_options = [option[0] for option in ForestData.Area_Unit_Options]
            if 'id' in df.columns or 'ID' in df.columns:
                cols = df.columns.tolist()
                for index, row in df.iterrows():
                    id_value = row.get('id')
                    try:
                        forest_instance = ForestData.objects.get(id=id_value)
                    except Exception as e:
                        data = {col: row[col] for col in cols}
                        data['Year'] = data['Year'].isoformat()
                        errors.append({
                                    'row_index': index,
                                    'data': data,
                                    'reason': f'Error inserting row {index}: {e}'
                                })
                        break

                    forest_data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Name_of_the_plant': row['Name_Of_The_Plant'],
                        'Scientific_Name': row['Scientific_Name'],
                        'Local_Name': row['Local_Name'],
                        'Stock_Unit': row['Stock_Unit'],
                        'Stock_Available': row['Stock_Available'],
                        'Area_Unit': row['Area_Unit'],
                        'Area_Covered': row['Area_Covered']
                    }

                    if forest_data['Stock_Unit'] not in Stock_unit_options:
                        errors.append({'row_index': index, 'reason': f'Error inserting row {index}: Invalid Stock unit value'})
                    elif forest_data['Area_Unit'] not in Area_unit_options:
                        errors.append({'row_index': index, 'reason': f'Error inserting row {index}: Invalid Area unit value'})
                    else:    
                        Year = pd.to_datetime(row['Year']).date()
                        # Retrieve Country_meta instance or None if not found
                        country_instance = Country_meta.objects.filter(Country_Name=row['Country']).first()
                        if country_instance is None:
                            raise ValueError(f"Country '{row['Country']}' not found")
                        
                        forest_instance.Year = Year
                        forest_instance.Country = country_instance
                        forest_instance.Name_Of_The_Plant = row['Name_Of_The_Plant']
                        forest_instance.Scientific_Name = row['Scientific_Name']
                        forest_instance.Local_Name = row['Local_Name']
                        forest_instance.Stock_Unit = row['Stock_Unit']
                        forest_instance.Stock_Available = row['Stock_Available']
                        forest_instance.Area_Unit = row['Area_Unit']
                        forest_instance.Area_Covered = row['Area_Covered']
                        forest_instance.save()
                        updated_count += 1

            else:

                Stock_unit_options = [option[0] for option in ForestData.Stock_Unit_Options]
                Area_unit_options = [option[0] for option in ForestData.Area_Unit_Options]
                for index, row in df.iterrows():
                    forest_data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Name_of_the_plant': row['Name_Of_The_Plant'],
                        'Scientific_Name' : row['Scientific_Name'],
                        'Local_Name' : row['Local_Name'],
                        'Stock_Unit' : row['Stock_Unit'],
                        'Stock_Available' : row['Stock_Available'],
                        'Area_Unit' : row['Area_Unit'],
                        'Area_Covered' : row['Area_Covered']
                    }

                    if forest_data['Stock_Unit'] not in Stock_unit_options:
                        errors.append({
                            'row_index': index,
                            'data': forest_data,
                            'reason': f'Error inserting row {index}: Invalid Stock unit value'
                        })

                    elif forest_data['Area_Unit'] not in Area_unit_options:
                        errors.append({
                            'row_index': index,
                            'data': forest_data,
                            'reason': f'Error inserting row {index}: Invalid Area unit value'
                        })

                    else:

                        try:
                            calender_date = datetime.strptime(str(row['Year'].date().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                        except:
                            calender_date = datetime.strptime(f'{str(row["Year"].date().strftime("%Y-%m-%d"))}-01-01', '%Y-%m-%d').date()

                        Country = None

                        try:
                            Year = calender_date.strftime('%Y-%m-%d')
                            Country = Country_meta.objects.get(Country_Name=row['Country'])

                            forest_data = {
                                    'Year': Year,
                                    'Country': Country,
                                    'Name_Of_The_Plant': row['Name_Of_The_Plant'],
                                    'Scientific_Name' : row['Scientific_Name'],
                                    'Local_Name' : row['Local_Name'],
                                    'Stock_Unit' : row['Stock_Unit'],
                                    'Stock_Available' : row['Stock_Available'],
                                    'Area_Unit' : row['Area_Unit'],
                                    'Area_Covered' : row['Area_Covered']
                            }
                        except Exception as e:
                                errors.append({
                                    'row_index': index,
                                    'data': forest_data,
                                    'reason': f'Error inserting row {index}: {e}'
                                })
                                continue

                        existing_record = ForestData.objects.filter(
                            Q(Year=Year) & Q(Country=Country) & Q(Name_Of_The_Plant = forest_data['Name_Of_The_Plant']) & Q(Stock_Unit = forest_data['Stock_Unit']) & Q(Area_Unit = forest_data['Area_Unit'])).first()        

                        if existing_record:
                            duplicate_data.append({
                                'row_index':index,
                                'data': forest_data,
                                'reason': 'Duplicate data found'
                            })


                        else:
                            try:
                                Forestdata = ForestData(**forest_data)
                                Forestdata.save()
                                added_count +=1

                            except Exception as e:
                                errors.append({
                                    'row_index': index,
                                    'data': forest_data,
                                    'reason': f"Error inserting row {index}: {e}"
                                })

            if added_count > 0:
                messages.success(request, f'{added_count} records added')

            if updated_count > 0:
                messages.success(request, f'{updated_count} records updated')

            if errors:
                request.session['errors'] = errors
                return render(request, 'general_data/error_template.html', {'errors': errors})

            if duplicate_data:
                return render(request, 'general_data/duplicate_template.html', {'duplicate_data': duplicate_data})

    else:
        form = UploadForestDataForm()

    return render(request, 'general_data/upload_form.html', {'form': form, 'tables':tables})

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

    paginator = Paginator(data, 10)
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

def delete_forest_record(request, item_id):
    try:
        item_to_delete = get_object_or_404(ForestData, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('forest_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")

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

def update_record(request,pk):
    resolved =  resolve(request.path_info)
    view_name = resolved.url_name
    model_mapping = {
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
        'update_index_record':Index,
        'update_publication_record':Publication,
    }

    form_mapping = {
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
        Index: UpdateIndex,
        Publication: UpdatePublication,
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
        Index: 'index_table',
        Publication: 'publication_table',
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

    context = {'form': form, 'meta_tables': views.meta_tables}
    return render(request, 'general_data/update_record.html', context)
   
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
        'delete_climate_record': Climate_Data,
        'delete_exchange_record': Exchange,
        'delete_energy_record':Energy,
        'delete_index_record': Index,
        'delete_publication_record': Publication,
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
        Index : 'index_table',
        Publication: 'publication_table',
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
