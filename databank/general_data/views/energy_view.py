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
            df = pd.read_excel(excel_data, dtype={'Power_Code': str})
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)
            cols = df.columns.tolist()
            
            for index, row in df.iterrows():
                energy_data = {col: row[col] for col in cols}
                
                try:
                    Country = Country_meta.objects.get(Country_Name = row['Country'])
                    Power_Code = Energy_Meta.objects.get(Code = row['Power_Code'])
                    Potential_Unit = Unit_meta.objects.get(Unit_Code = row['Potential_Unit'])
                    Unit_Production= Unit_meta.objects.get(Unit_Code = row['Unit_Production'])
                    
                    energy_data = {
                            'Country': Country,
                            'Year': row['Year'],
                            'Power_Code': Power_Code,
                            'Potential_Unit': Potential_Unit,
                            'Potential_Capacity_MW': row['Potential_Capacity_MW'],
                            'Unit_Production':Unit_Production,
                            'Current_Production_In_MW':row['Current_Production_In_MW'],
                            'Generating_Company':row['Generating_Company']
                        }
                    
                except Exception as e:
                    errors.append({'row_index': index, 'data': energy_data, 'reason': str(e)})
                    continue

                existing_record = Energy.objects.filter(
                    Q(Country = Country) 
                    & Q(Year = row['Year']) 
                    & Q(Power_Code = Power_Code) 
                    & Q(Potential_Unit = Potential_Unit)
                    & Q(Unit_Production = Unit_Production)
                    & Q(Generating_Company = row['Generating_Company'])
                ).first()

                if existing_record:
                    existing_dict = model_to_dict(existing_record)
                    energy_data_dict = model_to_dict(Energy(**energy_data))

                    if all(existing_dict[key] == energy_data_dict[key] or (pd.isna(existing_dict[key]) and pd.isna(energy_data_dict[key])) for key in energy_data_dict if key != 'id'):
                        energy_data = {
                            'Country': row['Country'],
                            'Year': row['Year'],
                            'Power_Code': row['Power_Code'],
                            'Potential_Unit': row['Potential_Unit'],
                            'Potential_Capacity_MW': row['Potential_Capacity_MW'],
                            'Unit_Production':row['Unit_Production'],
                            'Current_Production_In_MW':row['Current_Production_In_MW'],
                            'Generating_Company':row['Generating_Company']
                        }

                        duplicate_data.append({
                             'row_index': index,
                                'data': {key: str(value) for key, value in energy_data.items()}
                        })

                    else:
                        for key, value in energy_data.items():
                                setattr(existing_record, key, value)
                        try:
                            existing_record.save()
                            updated_count += 1
                        except IntegrityError as e:
                                errors.append(f"Error updating row {index}: {e}")

                else:
                    try:
                        energyData = Energy(**energy_data)
                        energyData.save()
                        added_count += 1
                    except Exception as e:
                        errors.append(f"Error inserting row {index}: {e}")

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

    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context ={'data_len':len(data),
              'page':page, 
              'query_len':len(page), 
              'tables': tables, 
              'meta_tables': views.meta_tables,
                      }
    return render(request, 'general_data/energy_templates/energy_table.html', context)


