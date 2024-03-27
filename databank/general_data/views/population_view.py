from datetime import datetime
from django.db import DataError
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import PopulationData, Country_meta
from ..forms import UploadPopulationDataForm,UploadPopulationData
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse
from .energy_view import strip_spaces
from trade_data import views



from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users

def is_valid_queryparam(param):
    return param !='' and param is not None

@login_required(login_url = 'login')
def display_population_table(request):
    data = PopulationData.objects.all()
    country_categories = Country_meta.objects.all()
    gender_option = [choice[1] for choice in PopulationData.Gender_Options]
    age_group_options=[choice[1] for choice in PopulationData.Age_Group_Options]

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    gender=request.GET.get('gender')
    age_group=request.GET.get('age_group')
    min_population = request.GET.get('minimum_population')
    max_population = request.GET.get('maximum_population')


    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(gender) and gender != '--':
        data = data.filter(Gender=gender)

    if is_valid_queryparam(age_group) and age_group != '--':
        data = data.filter(Age_Group=age_group)
    
    if is_valid_queryparam(min_population):
        data = data.filter(Population_gte=min_population)

    if is_valid_queryparam(max_population):
        data = data.filter(Population__lt=max_population)

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'page':page,
        'query_len': len(page),
        'country_categories':country_categories,
        'gender_options':gender_option,
        'age_group_options':age_group_options
    }
    return render(request, 'general_data/population_templates/population_table.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
@require_POST
def delete_selected_population(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('population_table')
    try:
        PopulationData.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('population_table')

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def delete_population_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(PopulationData, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('population_table')
    except Exception as e:
        messages.error(request, f'Error deleting item: {e}')


# @login_required(login_url = 'login')
# @allowed_users(allowed_roles=['admin'])
# def update_population_record(request,pk):
#     population_record = PopulationData.objects.get(id=pk)
#     form = UploadPopulationData(instance=population_record)

#     if request.method == 'POST':
#         form = UploadPopulationData(request.POST, instance=population_record)
#         if form.is_valid():
#             form.save()
#             return redirect('population_table')
        
#     context={'form':form,}
#     return render(request,'general_data/population_templates/update_population_record.html',context)


@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_population_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0
    
    if request.method == 'POST':
        form = UploadPopulationDataForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['population_data_file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)
            # age_group_options = [option[0] for option in PopulationData.Age_Group_Options]
            # gender_options = [option[0] for option in PopulationData.Gender_Options]
            
             # Check if required columns exist
            required_columns = ['Year', 'Country', 'Gender','Age Group','Population']  # Add your required column names here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing columns: {', '.join(missing_columns)}")
                return render(request,'general_data/invalid_upload.html', {'missing_columns': missing_columns, 'tables': tables, 'meta_tables': views.meta_tables,} )
            
            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    data = {
                        'Year' : row['Year'],
                        'Country' : row['Country'],
                        'Gender' : row['Gender'],
                        'Age Group' : row['Age Group'],
                        'Population' : row['Population']
                    }
                    
                    # get existing data
                    try:
                        population_instance = PopulationData.objects.get(id=id)
                        population_data = data

                        try:
                            Country = Country_meta.objects.get(Country_Name = row['Country'] )

                            population_instance.Year = row['Year']
                            population_instance.Country = Country_meta.objects.get(Country_Name=Country)
                            population_instance.Gender = row['Gender']
                            population_instance.Age_Group = row['Age Group']
                            population_instance.Population = row['Population']
                            population_instance.save()

                            updated_count +=1
                        except Exception as e:
                            population_data = data
                            errors.append({'row_index': index, 'data': population_data, 'reason': str(e)})
                            continue
                    
                    
                    # no existing data
                    except:
                        population_data = data
                        errors.append({
                                        'row_index': index,
                                        'data': population_data,
                                        'reason': f'Error inserting row {index}: {e}'
                                    })
                        continue
                    
            else:
                for index,row in df.iterrows():
                    data = {
                        'Year' : row['Year'],
                        'Country' : row['Country'],
                        'Gender' : row['Gender'],
                        'Age Group' : row['Age Group'],
                        'Population' : row['Population']
                    }

                      

                    try:
                        Country = Country_meta.objects.get(Country_Name=row['Country'])
                            
                        population_data ={
                        'Year' : row['Year'],
                        'Country' : Country,
                        'Gender' : row['Gender'],
                        'Age Group' : row['Age Group'],
                        'Population' : row['Population']
                        }

                        existing_record = PopulationData.objects.filter(
                                Q(Year = row['Year'])
                                & Q(Country = Country)
                                & Q(Gender = row['Gender'])
                                & Q(Age_Group = row['Age Group'])
                                & Q(Population = row['Population'])
                            ).first()
                
                        if existing_record:
                            population_data = data
                            duplicate_data.append({
                                        'row_index' :index,
                                        'data': population_data,
                                        'reason': 'Duplicate record found'
                                    })
                        else:
                            try:
                                population_data ={
                                'Year' : row['Year'],
                                'Country' : Country,
                                'Gender' : row['Gender'],
                                'Age_Group' : row['Age Group'],
                                'Population' : row['Population']
                                }
                                populationData = PopulationData(**population_data)
                                populationData.save()
                                added_count += 1
                        
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")


                    except Exception as e:
                        population_data = data
                        errors.append({'row_index': index, 'data': population_data, 'reason': str(e)})
                        continue
                        
            if added_count > 0 :
                messages.success(request,str(added_count)+'records added')
            
            if updated_count > 0 :
                messages.info(request,str(updated_count)+'records updated')
            
            if errors:
                request.session['errors'] = errors
                return render(request, 'trade_data/error_template.html', {'errors': errors, 'tables': tables, 'meta_tables': views.meta_tables, })
            
            if duplicate_data:
                request.session['duplicate_data'] = duplicate_data
                return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data, 'tables': tables, 'meta_tables': views.meta_tables,})
            
            else:
           # form is not valid
                return redirect('population_table') 
                
    else:
        form = UploadPopulationDataForm()

    return render(request,'general_data/population_templates/upload_population_form.html',{'form':form})

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def update_selected_population(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('population_table')

    else:
        queryset = PopulationData.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','Gender','Age_Group','Population')))
        df.rename(columns={'country': 'Country','Age_Group':'Age Group' }, inplace=True)
        df = df[['id','Year','Country','Gender','Age Group','Population']]
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
                


