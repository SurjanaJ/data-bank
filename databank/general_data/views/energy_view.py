from io import BytesIO
from django.db import IntegrityError
from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from trade_data.models import Country_meta, Unit_meta
from trade_data.views import is_valid_queryparam, tables
from django.http import HttpResponse
from django.db.models import F, Q
from trade_data import views

from ..models import Energy, Energy_Meta
from ..forms import UploadEnergyForm

def strip_spaces(value):
    if isinstance(value, str):
        return value.strip()
    return value

def display_energy_meta(request):
    data = Energy_Meta.objects.all()
    total_data = data.count()

    column_names = Energy_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)

def upload_energy_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadEnergyForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data, dtype={'Power Code': str})
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

            # Update existing data
            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    try:
                        energy_instance = Energy.objects.get(id = id)
                        energy_data = {
                            'Country': row['Country'],
                            'Year': row['Year'],
                            'Power_Code':row['Power Code'],
                            'Potential_Unit': row['Potential Unit'],
                            'Potential_Capacity_MW': row['Potential Capacity MW'],
                            'Unit_Production':row['Unit Production'],
                            'Current_Production_In_MW':row['Current Production In MW'],
                            'Generating_Company':row['Generating Company']
                        }
                        
                        #Check if all the meta datas exist
                        try:
                            Country = Country_meta.objects.get(Country_Name = row['Country'])
                            Power_Code = Energy_Meta.objects.get(Code = row['Power Code'])
                            Potential_Unit = Unit_meta.objects.get(Unit_Code = row['Potential Unit'])
                            Unit_Production= Unit_meta.objects.get(Unit_Code = row['Unit Production'])

                            energy_instance.Country = Country
                            energy_instance.Year = row['Year']
                            energy_instance.Power_Code = Power_Code
                            energy_instance.Potential_Unit = Potential_Unit
                            energy_instance.Potential_Capacity_MW = row['Potential Capacity MW']
                            energy_instance.Unit_Production = Unit_Production
                            energy_instance.Current_Production_In_MW = row['Current Production In MW']
                            energy_instance.Generating_Company = row['Generating Company']

                            energy_instance.save()
                            updated_count += 1

                        except Exception as e:
                            energy_data  = {
                                        'Country': row['Country'],
                                        'Year': row['Year'],
                                        'Power_Code':row['Power Code'],
                                        'Energy Type': row['Energy Type'],
                                        'Potential_Unit': row['Potential Unit'],
                                        'Potential_Capacity_MW': row['Potential Capacity MW'],
                                        'Unit_Production':row['Unit Production'],
                                        'Current_Production_In_MW':row['Current Production In MW'],
                                        'Generating_Company':row['Generating Company']
                                    }
                            errors.append({'row_index': index, 'data': energy_data, 'reason': str(e)})
                            continue

                    except Exception as e:
                        energy_data = {
                            'Country': row['Country'],
                            'Year': row['Year'],
                            'Power_Code':row['Power Code'],
                            'Potential_Unit': row['Potential Unit'],
                            'Potential_Capacity_MW': row['Potential Capacity MW'],
                            'Unit_Production':row['Unit Production'],
                            'Current_Production_In_MW':row['Current Production In MW'],
                            'Generating_Company':row['Generating Company']
                        }
                        errors.append({
                                    'row_index': index,
                                    'data': energy_data,
                                    'reason': f'Error inserting row {index}: {e}'
                                })
                        continue
            else:
                # Add new data
                for index, row in df.iterrows():
                    try:
                        Country = Country_meta.objects.get(Country_Name = row['Country'])
                        Power_Code = Energy_Meta.objects.get(Code = row['Power Code'])
                        Potential_Unit = Unit_meta.objects.get(Unit_Code = row['Potential Unit'])
                        Unit_Production= Unit_meta.objects.get(Unit_Code = row['Unit Production'])
                        
                        energy_data = {
                                'Country': Country,
                                'Year': row['Year'],
                                'Power_Code': Power_Code,
                                'Potential_Unit': Potential_Unit,
                                'Potential_Capacity_MW': row['Potential Capacity MW'],
                                'Unit_Production':Unit_Production,
                                'Current_Production_In_MW':row['Current Production In MW'],
                                'Generating_Company':row['Generating Company']
                            }
                        
                        existing_record = Energy.objects.filter(
                            Q(Country = Country) 
                            & Q(Year = row['Year']) 
                            & Q(Power_Code = Power_Code) 
                            & Q(Potential_Unit = Potential_Unit)
                            & Q(Potential_Capacity_MW = row['Potential Capacity MW'])
                            & Q(Unit_Production = Unit_Production)
                            & Q(Current_Production_In_MW = row['Current Production In MW'])
                            & Q(Generating_Company = row['Generating Company'])
                        ).first()

                        if existing_record:
                            energy_data = {
                            'Country': row['Country'],
                            'Year': row['Year'],
                            'Power Code': row['Power Code'],
                            'Energy Type': row['Energy Type'],
                            'Potential Unit': row['Potential Unit'],
                            'Potential Capacity MW': row['Potential Capacity MW'],
                            'Unit Production':row['Unit Production'],
                            'Current Production In MW':row['Current Production In MW'],
                            'Generating Company':row['Generating Company']
                        }   
                           
                            duplicate_data.append({
                             'row_index': index,
                                'data': {key: str(value) for key, value in energy_data.items()}
                        })
                            
                        else:
                            try:
                                energyData = Energy(**energy_data)
                                energyData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")
                            
                    
                    except Exception as e:
                        energy_data  = {
                                'Country': row['Country'],
                                'Year': row['Year'],
                                'Power_Code':row['Power Code'],
                                'Energy Type': row['Energy Type'],
                                'Potential_Unit': row['Potential Unit'],
                                'Potential_Capacity_MW': row['Potential Capacity MW'],
                                'Unit_Production':row['Unit Production'],
                                'Current_Production_In_MW':row['Current Production In MW'],
                                'Generating_Company':row['Generating Company']
                            }
                        errors.append({'row_index': index, 'data': energy_data, 'reason': str(e)})
                        continue

        if added_count > 0:
            messages.success(request, str(added_count) + ' records added.')
            
        if updated_count > 0:
            messages.info(request, str(updated_count) + ' records updated.')

        if errors:
            request.session['errors'] = errors
            return render(request, 'trade_data/error_template.html', {'errors': errors, 'tables': tables, 'meta_tables': views.meta_tables, })
            
        elif duplicate_data:
            request.session['duplicate_data'] = duplicate_data
            return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data, 'tables': tables, 'meta_tables': views.meta_tables,})
            
        else:
            return redirect('energy_table')
    else:
        form = UploadEnergyForm()    

    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form, 'tables': tables, 'meta_tables': views.meta_tables,})
    
                    
def display_energy_table(request):
    data = Energy.objects.all()

    country_categories = Country_meta.objects.all()
    power_code_categories = Energy_Meta.objects.all()
    unit_categories = Unit_meta.objects.all()

    power_code = request.GET.get('power_code')
    country = request.GET.get('country')
    potential_unit = request.GET.get('potential_unit')
    unit_production = request.GET.get('unit_production')

    if is_valid_queryparam(country) and country != '--':
        data = data.filter(Country_id=country)

    if is_valid_queryparam(power_code) and power_code != '--':
        data = data.filter(Power_Code_id=power_code)

    if is_valid_queryparam(potential_unit) and potential_unit != '--':
        data = data.filter(Potential_Unit_id=potential_unit)

    if is_valid_queryparam(unit_production) and unit_production != '--':
        data = data.filter(Unit_Production_id=unit_production)

    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context ={'data_len':len(data),
              'page':page, 
              'query_len':len(page), 
              'tables': tables, 
              'meta_tables': views.meta_tables,
              'country_categories':country_categories,
              'power_code_categories':power_code_categories,
              'unit_categories':unit_categories,
                      }
    return render(request, 'general_data/energy_templates/energy_table.html', context)

def export_energy_excel(request):
    power_code = request.GET.get('power_code')
    country = request.GET.get('country')
    potential_unit = request.GET.get('potential_unit')
    unit_production = request.GET.get('unit_production')

    filter_conditions = {}
    if is_valid_queryparam(country) and country != '--':
        filter_conditions['Country'] = country

    if is_valid_queryparam(power_code) and power_code != '--':
        filter_conditions['Power_Code'] = power_code

    if is_valid_queryparam(potential_unit) and potential_unit != '--':
        filter_conditions['Potential_Unit'] = potential_unit

    if is_valid_queryparam(unit_production) and unit_production != '--':
        filter_conditions['Unit_Production'] = unit_production

    queryset = Energy.objects.filter(**filter_conditions)
    queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        power_code = F('Power_Code__Code'),
        energy_type = F('Power_Code__Energy_Type'),
        potential_unit = F('Potential_Unit__Unit_Code'),
        unit_production = F('Unit_Production__Unit_Code'),
    )
   
    data = pd.DataFrame(list(queryset.values('Year','country','power_code', 'energy_type','potential_unit','Potential_Capacity_MW','unit_production','Current_Production_In_MW', 'Generating_Company')))

    data.rename(columns={
                         'country':'Country',
                         'power_code': 'Power Code',
                         'energy_type':'Energy Type',
                         'potential_unit':'Potential Unit',
                         'Potential_Capacity_MW':'Potential Capacity MW',
                         'unit_production' : 'Unit Production',
                         'Current_Production_In_MW':'Current Production In MW',
                         'Generating_Company':'Generating Company'
                         }, inplace=True)

    column_order = ['Year','Country','Power Code','Energy Type',
                    'Potential Unit','Potential Capacity MW','Unit Production','Current Production In MW','Generating Company']
    data = data[column_order]
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')  
    data.to_excel(writer, sheet_name='Sheet1', index=False)

    writer.close()  
    output.seek(0)

    response = HttpResponse(
        output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
    return response


def update_selected_energy(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('energy_table')
    else:
        queryset = Energy.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        power_code = F('Power_Code__Code'),
        energy_type = F('Power_Code__Energy_Type'),
        potential_unit = F('Potential_Unit__Unit_Code'),
        unit_production = F('Unit_Production__Unit_Code'),
    )
        
        data = pd.DataFrame(list(queryset.values('id','Year','country','power_code', 'energy_type','potential_unit','Potential_Capacity_MW','unit_production','Current_Production_In_MW', 'Generating_Company')))

        data.rename(columns={
                         'country':'Country',
                         'power_code': 'Power Code',
                         'energy_type':'Energy Type',
                         'potential_unit':'Potential Unit',
                         'Potential_Capacity_MW':'Potential Capacity MW',
                         'unit_production' : 'Unit Production',
                         'Current_Production_In_MW':'Current Production In MW',
                         'Generating_Company':'Generating Company'
                         }, inplace=True)

        column_order = ['id','Year','Country','Power Code','Energy Type',
                        'Potential Unit','Potential Capacity MW','Unit Production','Current Production In MW','Generating Company']
        data = data[column_order]
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')  
        data.to_excel(writer, sheet_name='Sheet1', index=False)

        writer.close()  
        output.seek(0)

        response = HttpResponse(
            output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
        return response

