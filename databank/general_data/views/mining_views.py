from datetime import datetime
from django.db import DataError
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
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

def is_valid_queryparam(param):
    return param !='' and param is not None

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
        data=data.filter(Name_Of_Mine_id = mine_code)

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
 
def upload_mining_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadMiningForm(request.POST, request.FILES)  
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data)

            unit_options = [option[0] for option in Mining.Unit_Options]

            if 'id' in df.columns:
                cols = df.columns.tolist()
                for index, row in df.iterrows():
                    id_value = row.get('id')
                    try:
                        mining_instance = Mining.objects.get(id=id_value)
                    except Exception as e:
                        data = {col: row[col] for col in cols}
                        errors.append({
                            'row_index': index,
                            'data': data,
                            'reason': f'Error inserting row {index}:{e}'
                        })
                        continue

                    mining_data = {
                        'Year': row['Year'].date().strftime('%Y-%m-%d'),
                        'Country': row['Country'],
                        'Name_Of_Mine': row['Name_Of_Mine'],
                        'Unit': row['Unit'],
                        'Current_Production': row['Current_Production'],
                        'Potential_Stock': row['Potential_Stock'],
                        'Mining_Company_Name': row['Mining_Company_Name']
                    }

                    try:
                        Year = row['Year']
                        calender_year = pd.to_datetime(Year).date()
                    except ValueError as e:
                        mining_data = {
                            'Year': row['Year'].date().strftime('%Y-%m-%d'),
                            'Country': row['Country'],
                            'Name_Of_Mine': row['Name_Of_Mine'],
                            'Unit': row['Unit'],
                            'Current_Production': row['Current_Production'],
                            'Potential_Stock': row['Potential_Stock'],
                            'Mining_Company_Name': row['Mining_Company_Name']
                        }
                        errors.append({'row_index': index, 'data': mining_data, 'reason': str(e)})
                        continue

                    try:
                        if mining_data['Unit'] not in unit_options:
                            mining_data = {
                                'Year': row['Year'].date().strftime('%Y-%m-%d'),
                                'Country': row['Country'],
                                'Name_Of_Mine': row['Name_Of_Mine'],
                                'Unit': row['Unit'],
                                'Current_Production': row['Current_Production'],
                                'Potential_Stock': row['Potential_Stock'],
                                'Mining_Company_Name': row['Mining_Company_Name']
                            }
                            errors.append({'row_index': index,'data': mining_data, 'reason': f'Error inserting row {index}: Invalid unit value'})

                        else:
                            Year = calender_year
                            country_instance = Country_meta.objects.get(Country_Name=row['Country'])
                            mine_type = Mine_Meta.objects.get(Mine_Type=row['Name_Of_Mine'])

                            mining_instance.Year = row['Year']
                            mining_instance.Country = country_instance
                            mining_instance.Name_Of_Mine = mine_type
                            mining_instance.Unit = row['Unit']
                            mining_instance.Current_Production = row['Current_Production']
                            mining_instance.Potential_Stock = row['Potential_Stock']
                            mining_instance.Mining_Company_Name = row['Mining_Company_Name']

                            mining_instance.save()
                            updated_count += 1
                    except Exception as e:
                        mining_data = {
                            'Year': row['Year'].date().strftime('%Y-%m-%d'),
                            'Country': row['Country'],
                            'Name_Of_Mine': row['Name_Of_Mine'],
                            'Unit': row['Unit'],
                            'Current_Production': row['Current_Production'],
                            'Potential_Stock': row['Potential_Stock'],
                            'Mining_Company_Name': row['Mining_Company_Name']
                        }
                        errors.append({'row_index': index, 'data': mining_data, 'reason': str(e)})
                        continue

            else:
                for index, row in df.iterrows():
                    mining_data = {
                        'Year': row['Year'].date().strftime('%Y-%m-%d'),
                        'Country': row['Country'],
                        'Name_Of_Mine': row['Name_Of_Mine'],
                        'Unit': row['Unit'],
                        'Current_Production': row['Current_Production'],
                        'Potential_Stock': row['Potential_Stock'],
                        'Mining_Company_Name': row['Mining_Company_Name']
                    }

                    if mining_data['Unit'] not in unit_options:
                        errors.append({'row_index': index,'data': mining_data, 'reason': f'Error inserting row {index}: Invalid unit value'})
                    else:
                        try:
                            calender_date = datetime.strptime(str(row['Year'].date().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                        except ValueError:
                             calender_date = datetime.strptime(f'{str(row["Year"].date().strftime("%Y-%m-%d"))}-01-01', '%Y-%m-%d').date()

                        country_instance = None
                        mine_instance = None

                        try:
                            Year = calender_date.strftime('%Y-%m-%d')
                            country_instance = Country_meta.objects.get(Country_Name=row['Country'])
                            mine_instance = Mine_Meta.objects.get(Mine_Type=row['Name_Of_Mine'])

                            mining_data = {
                                'Year': row['Year'],
                                'Country': country_instance,
                                'Name_Of_Mine': mine_instance,
                                'Unit': row['Unit'],
                                'Current_Production': row['Current_Production'],
                                'Potential_Stock': row['Potential_Stock'],
                                'Mining_Company_Name': row['Mining_Company_Name']
                            }
                        except Exception as e:
                            errors.append({'row_index': index, 'data': mining_data, 'reason': str(e)})
                            continue

                        existing_record = Mining.objects.filter(Q(Year=Year) & Q(Country=country_instance) & Q(Name_Of_Mine=mine_instance) & Q(Unit=row['Unit']) & Q(Current_Production= row['Current_Production']) & Q(Potential_Stock = row['Potential_Stock']) & Q(Mining_Company_Name = row['Mining_Company_Name'])).first()
                        if existing_record:
                            duplicate_data.append({
                                'row_index': index,
                                'data': mining_data,
                                'reason': 'Duplicate data found'
                            })
                        else:
                            try:
                
                                Miningdata=Mining(**mining_data)
                                Miningdata.save()
                                added_count += 1
                            except Exception as e:
                                errors.append({
                                    'row_index': index,
                                    'data': mining_data,
                                    'reason': f"Error inserting row {index}: {e}"
                                })
                                errors.append({'row_index': index, 'data': mining_data, 'reason': str(e)})

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
        form = UploadMiningForm()

    return render(request, 'general_data/upload_form.html', {'form': form, 'tables': tables})

def display_mining_meta(request):
    data = Mine_Meta.objects.all()
    total_data = data.count()

    column_names = Mine_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)
                
def update_selected_mining(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('mining_table')

    else:
        queryset = Mining.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        name_of_mine = F('Name_Of_Mine__Mine_Type'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','name_of_mine','Unit','Current_Production','Potential_Stock','Mining_Company_Name')))
        df.rename(columns={'country': 'Country','name_of_mine':'Name_Of_Mine'}, inplace=True)
        df = df[['id','Year','Country','Name_Of_Mine','Unit','Current_Production','Potential_Stock','Mining_Company_Name']]
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