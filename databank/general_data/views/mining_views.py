from datetime import datetime
from django.db import DataError
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd

from .energy_view import strip_spaces
from ..models import Mining, Country_meta,Mine_Meta
from ..forms import UploadMiningForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse

from trade_data import views
from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users

def is_valid_queryparam(param):
    return param !='' and param is not None

@login_required(login_url = 'login')
def display_mining_table(request):
    data = Mining.objects.all()

    mine_codes=Mine_Meta.objects.all()
    unit_options = [choice[1] for choice in Mining.Unit_Options ]

    country_categories = Country_meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    mine_code = request.GET.get('mine_code')
    unit = request.GET.get('mine_unit')  
    minimum_current_production = request.GET.get('minimum_current_production')
    maximum_current_production = request.GET.get('maximum_current_production')
    minimum_potential_stock = request.GET.get('minimum_potential_stock')
    maximum_potential_stock = request.GET.get('maximum_potential_stock')
    mining_company_name = request.GET.get('mining_company_name')

  
    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(mine_code) and mine_code != '--':
        data=data.filter(Code_id = mine_code)

    if is_valid_queryparam(unit)  and unit != '--':
        data=data.filter(Unit=unit) 

    if is_valid_queryparam(minimum_current_production):
        data = data.filter(Current_Production__gte=minimum_current_production)

    if is_valid_queryparam(maximum_current_production):
        data = data.filter(Current_Production__lt=maximum_current_production)

    if is_valid_queryparam(minimum_potential_stock):
        data = data.filter(Potential_Stock__gte=minimum_potential_stock)

    if is_valid_queryparam(maximum_potential_stock):
        data = data.filter(Potential_Stock__lt=maximum_potential_stock)

    if is_valid_queryparam(mining_company_name):
        data=data.filter(Q(Mining_Company_Name__icontains=mining_company_name)).distinct()


    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context={
        'tables':tables,
        'data_len':len(data),
        'query_len': len(page),
        'page':page, 
        'country_categories':country_categories,
        'unit_options':unit_options,
        'mine_codes':mine_codes,

    }
    return render(request, 'general_data/mining_templates/mining_table.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_mining_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadMiningForm(request.POST, request.FILES)  
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data, dtype={'Code': str})
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

            unit_options = [option[0] for option in Mining.Unit_Options]
             # Check if required columns exist
            required_columns = ['Year', 'Country', 'Code','Unit','Current Production','Potential Stock','Mining Company Name']  # Add your required column names here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing columns: {', '.join(missing_columns)}")
                return render(request,'general_data/invalid_upload.html', {'missing_columns': missing_columns, 'tables': tables, 'meta_tables': views.meta_tables,} )
            
            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Code': row['Code'],
                        'Mine Type': row['Mine Type'],
                        'Unit': row['Unit'],
                        'Current Production': row['Current Production'],
                        'Potential Stock': row['Potential Stock'],
                        'Mining Company Name': row['Mining Company Name']
                    }

                    #get existing data
                    try:
                        mining_instance = Mining.objects.get(id=id)
                        mining_data= data

                        #check if meta values exist
                        try:
                            Country = Country_meta.objects.get(Country_Name=row['Country'])
                            Code = Mine_Meta.objects.get(Code=row['Code'])

                            mining_instance.Year = row['Year']
                            mining_instance.Country = Country
                            mining_instance.Code = Code
                            mining_instance.Unit = row['Unit']
                            mining_instance.Current_Production = row['Current Production']
                            mining_instance.Potential_Stock = row['Potential Stock']
                            mining_instance.Mining_Company_Name = row['Mining Company Name']

                            mining_instance.save()
                            updated_count +=1

                        #meta does not exist
                        except Exception as e:
                            mining_data= data
                            errors.append({'row_index': index, 'data': mining_data, 'reason': str(e)})
                            continue


                    #instance does not exist
                    except Exception as e:
                        mining_data= data
                        errors.append({
                            'row_index': index,
                            'data': mining_data,
                            'reason': f'Error inserting row {index}:{e}'
                        })
                        continue

            #add new data        
            else:
                for index, row in df.iterrows():
                    data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Code': row['Code'],
                        'Mine Type': row['Mine Type'],
                        'Unit': row['Unit'],
                        'Current Production': row['Current Production'],
                        'Potential Stock': row['Potential Stock'],
                        'Mining Company Name': row['Mining Company Name']
                    }

                    # if mining_data['Unit'] not in unit_options:
                    #     errors.append({'row_index': index,'data': mining_data, 'reason': f'Error inserting row {index}: Invalid unit value'})
                    

                    #check if the meta values exist
                    try:
                        Country = Country_meta.objects.get(Country_Name=row['Country'])
                        Code = Mine_Meta.objects.get(Code=row['Code'])

                        mining_data = {
                        'Year': row['Year'],
                        'Country': Country,
                        'Code': Code,
                        'Mine Type': row['Mine Type'],
                        'Unit': row['Unit'],
                        'Current Production': row['Current Production'],
                        'Potential Stock': row['Potential Stock'],
                        'Mining Company Name': row['Mining Company Name']
                    }
                        
                        existing_record = Mining.objects.filter(
                            Q(Year = row['Year'])
                            & Q(Country = Country)
                            & Q(Code = Code)
                            & Q(Unit = row['Unit'])
                            & Q(Current_Production = row['Current Production'])
                            & Q(Potential_Stock = row['Potential Stock'])
                            & Q(Mining_Company_Name = row['Mining Company Name'])
                        ).first()

                        # show duplicate data
                        if existing_record:
                            mining_data = data
                            duplicate_data.append({
                                'row_index': index,
                                'data': {key: str(value) for key, value in mining_data.items()}
                            })
                            continue
                        else:
                            #add new record
                            try:
                                mining_data = {
                                    'Year': row['Year'],
                                    'Country': Country,
                                    'Code': Code,
                                    'Unit': row['Unit'],
                                    'Current_Production': row['Current Production'],
                                    'Potential_Stock': row['Potential Stock'],
                                    'Mining_Company_Name': row['Mining Company Name']
                                }
                                miningData = Mining(**mining_data)
                                miningData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")

                    #meta does not exist
                    except Exception as e:
                        mining_data = data
                        errors.append({'row_index': index, 'data': mining_data, 'reason': str(e)})
                        continue

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
                return redirect('mining_table')

    else:
        form = UploadMiningForm()

    return render(request, 'general_data/upload_form.html', {'form': form, 'tables': tables})

@login_required(login_url = 'login')
def display_mining_meta(request):
    data = Mine_Meta.objects.all()
    total_data = data.count()

    column_names = Mine_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])              
def update_selected_mining(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('mining_table')

    else:
        queryset = Mining.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        code = F('Code__Code'),
        Mine_Type = F('Code__Mine_Type')
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','code','Mine_Type','Unit','Current_Production','Potential_Stock','Mining_Company_Name')))

        df.rename(columns={'country':'Country','code':'Code','Mine_Type': 'Mine Type','Current_Production':'Current Production','Potential_Stock':'Potential Stock', 'Mining_Company_Name':'Mining Company Name'}, inplace=True)
        
        df = df[['id','Year','Country','Code','Mine Type','Unit','Current Production','Potential Stock','Mining Company Name']]
        
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