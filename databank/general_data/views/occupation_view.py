from io import BytesIO
from django.db import IntegrityError
from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from trade_data.models import Country_meta
from trade_data.views import is_valid_queryparam, tables
from django.http import HttpResponse
from django.db.models import F, Q
from trade_data import views


from ..models import Occupation, Occupation_Meta
from ..forms import UploadOccupationForm



def display_occupation_meta(request):
    data = Occupation_Meta.objects.all()
    total_data = data.count()

    column_names = Occupation_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)

def upload_occupation_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadOccupationForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data, dtype={'Code': str})
            cols = df.columns.tolist()
            df.fillna('', inplace= True)

            for index, row in df.iterrows():
                occupation_data = {col: row[col] for col in cols}
                try:
                    Code = Occupation_Meta.objects.get(SOC_Code = row['Code'])
                    Country = Country_meta.objects.get(Country_Name = row['Country'])

                    occupation_data = {
                        'Country': Country,
                        'Year': row['Year'],
                        'Code': Code,
                        'Number': row['Number']
                    }
                except Exception as e:
                    errors.append({'row_index': index, 'data': occupation_data, 'reason': str(e)})
                    continue

                existing_record = Occupation.objects.filter(
                    Q(Country = Country) & Q(Year = row['Year']) & Q(Code = Code)
                ).first()

                if existing_record:
                    existing_dict = model_to_dict(existing_record)
                    occupation_data_dict = model_to_dict(Occupation(**occupation_data))

                    if all(existing_dict[key] == occupation_data_dict[key] or (pd.isna(existing_dict[key]) and pd.isna(occupation_data_dict[key])) for key in occupation_data_dict if key != 'id'):
                        occupation_data = {
                            'Country': Country,
                            'Year' : row['Year'],
                            'Code': Code,
                            'Number':row['Number']
                        }
                        duplicate_data.append({
                             'row_index': index,
                                'data': {key: str(value) for key, value in occupation_data.items()}
                        })

                    else:
                        for key, value in occupation_data.items():
                                setattr(existing_record, key, value)
                        try:
                            existing_record.save()
                            updated_count += 1
                        except IntegrityError as e:
                                errors.append(f"Error updating row {index}: {e}")

                else:
                    try:
                        occupationData = Occupation(**occupation_data)
                        occupationData.save()
                        added_count += 1
                    except Exception as e:
                        errors.append(f"Error inserting row {index}: {e}")

            if added_count > 0:
                messages.success(request, str(added_count) + ' records added.')
            
            if updated_count > 0:
                messages.info(request, str(updated_count) + ' records updated.')

            if errors:
                request.session['errors'] = errors
                return render(request, 'trade_data/error_template.html', {'errors': errors})
            
            elif duplicate_data:
                request.session['duplicate_data'] = duplicate_data
                return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data})
            
            else:
                return redirect('education_table')
    else:
        form = UploadOccupationForm()    

    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})
    
def display_occupation_table(request):
    data = Occupation.objects.all()

    code_categories = Occupation_Meta.objects.all()
    country_categories = Country_meta.objects.all()

    country = request.GET.get('country')
    code = request.GET.get('code')

    if is_valid_queryparam(country) and country != '--':
        data = data.filter(Country = country)

    if is_valid_queryparam(code) and code != '--':
        data = data.filter(Code = code)

    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)


    context ={'data_len':len(data),'code_categories':code_categories, 'country_categories':country_categories, 'page':page, 'query_len':len(page), 'tables': tables, 'meta_tables': views.meta_tables}
    return render(request, 'general_data/occupation_templates/occupation_table.html', context)
