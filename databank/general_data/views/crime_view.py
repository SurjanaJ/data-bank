from io import BytesIO
from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from trade_data.views import is_valid_queryparam, tables
from django.http import HttpResponse
from django.db.models import F

from trade_data.models import Country_meta
from ..forms import UploadCrimeForm
from trade_data import views
from ..models import Crime, Crime_Meta



def display_crime_meta(request):
    data = Crime_Meta.objects.all()
    total_data = data.count()

    column_names = Crime_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)


def upload_crime_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadCrimeForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data, dtype={'Code': str})
            df.fillna('', inplace=True)
            df['Year'] = pd.to_datetime(df['Year']).dt.date

            for index, row in df.iterrows():
                try: 
                    Year = row['Year']
                    Country = Country_meta.objects.get(Country_Name = row['Country'])
                    Code = Crime_Meta.objects.get(Code = row['Code'])
                    gender = row['Gender']

                    if gender not in ['Male', 'Female']:
                        raise ValueError(
                            f"Invalid Direction at row {index} : {gender}"
                        )
                    crime_data = {
                        'Country':Country,
                        'Year':Year,
                        'Code':Code,
                        'Gender': row['Gender'],
                        'Age': row['Age'],
                        'District': row['District']
                    }

                except Exception as e:
                    crime_data = {
                        'Country':Country,
                        'Year':Year.isoformat(),
                        'Code':Code,
                        'Gender': row['Gender'],
                        'Age': row['Age'],
                        'District': row['District']
                    }
                    errors.append({'row_index': index, 'data': crime_data, 'reason': str(e)})
                    continue
                
                try:
                    crimeData = Crime(**crime_data)
                    crimeData.save()
                    added_count +=1
                        
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
                return redirect('services_table')  
            
    else:
        form = UploadCrimeForm()

    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})


def display_crime_table(request):
    data = Crime.objects.all()
    column_names = Crime._meta.fields

    country_categories = Country_meta.objects.all()
    gender_categories = [choice[1] for choice in Crime.GENDER_OPTIONS]
    crime_code = Crime_Meta.objects.all()

    year_min = request.GET.get('year_min')
    year_max = request.GET.get('year_max')
    age_min = request.GET.get('age_min')
    age_max = request.GET.get('age_max')
    gender = request.GET.get('gender')
    country = request.GET.get('country')
    code = request.GET.get('code')

    if is_valid_queryparam(year_min):
        data = data.filter(Year__gte=year_min)

    if is_valid_queryparam(year_max):
        data = data.filter(Year__lt = year_max)

    if is_valid_queryparam(country) and country != '--':
        data = data.filter(Country_id=country)

    if is_valid_queryparam(age_min):
        data = data.filter(Age__gte=age_min)

    if is_valid_queryparam(age_max):
        data = data.filter(Age__lt=age_max)

    if is_valid_queryparam(gender) and gender != '--':
        data = data.filter(Gender = gender)

    if is_valid_queryparam(code) and code != '--':
        data = data.filter(Code = code)

    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {'data_len': len(data), 'country_categories': country_categories, 'gender_categories': gender_categories, 'crime_code':crime_code ,'page':page, 'query_len': len(page), 'tables':tables, 'meta_tables':views.meta_tables, 'column_names':column_names}

    return render(request, 'general_data/crime_templates/crime_table.html', context)

def export_excel(request):

    year_min = request.GET.get('year_min')
    year_max = request.GET.get('year_max')
    age_min = request.GET.get('age_min')
    age_max = request.GET.get('age_max')
    gender = request.GET.get('gender')
    country = request.GET.get('country')
    code = request.GET.get('code')

    filter_conditions = {}
    if is_valid_queryparam(year_min):
        filter_conditions['Year__gte'] = year_min
    if is_valid_queryparam(year_max):
        filter_conditions['Year__lt'] = year_max
    if is_valid_queryparam(age_min):
        filter_conditions['Age__gte'] = age_min
    if is_valid_queryparam(age_max):
        filter_conditions['Age__lt'] = age_max
    if is_valid_queryparam(gender) and gender != '--':
        filter_conditions['Gender'] = gender
    if is_valid_queryparam(country) and country != '--':
        filter_conditions['Country'] = country
    if is_valid_queryparam(code) and code != '--':
        filter_conditions['Code'] = code

    queryset = Crime.objects.filter(**filter_conditions)
    queryset = queryset.annotate(
        country_name = F('Country__Country_Name'),
        code_name = F('Code__Code')
    )
    data = pd.DataFrame(list(queryset.values('country_name','Year','code_name', 'Gender','Age', 'District')))
    
    data.rename(columns={'country_name': 'Country', 'code_name': 'Code'}, inplace=True)


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

