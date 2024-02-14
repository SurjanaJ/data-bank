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
                return redirect('occupation_table')
    else:
        form = UploadOccupationForm()    

    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})
    
def display_occupation_table(request):
    data = Occupation.objects.all()

    code_categories = Occupation_Meta.objects.all()
    country_categories = Country_meta.objects.all()
    year_categories = Occupation.objects.values_list('Year', flat=True).distinct()

    country = request.GET.get('country')
    code = request.GET.get('code')
    year_min = request.GET.get('year_min')
    year_max = request.GET.get('year_max')

    if is_valid_queryparam(year_min) and year_min != '--':
        data = data.filter(Year__gte=year_min)

    if is_valid_queryparam(year_max) and year_max != '--':
        data = data.filter(Year__lt = year_max)

    if is_valid_queryparam(country) and country != '--':
        data = data.filter(Country = country)

    if is_valid_queryparam(code) and code != '--':
        data = data.filter(Code = code)

    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)


    context ={'data_len':len(data),'code_categories':code_categories, 'country_categories':country_categories, 'page':page, 'query_len':len(page), 'tables': tables, 'meta_tables': views.meta_tables, 'year_categories':year_categories}
    return render(request, 'general_data/occupation_templates/occupation_table.html', context)

def export_occupation_excel(request):
    country = request.GET.get('country')
    code = request.GET.get('code')
    year_min = request.GET.get('year_min')
    year_max = request.GET.get('year_max')

    filter_conditions = {}
    if is_valid_queryparam(year_min) and year_min != '--':
        filter_conditions['Year__gte'] = year_min

    if is_valid_queryparam(year_max) and year_max != '--':
        filter_conditions['Year__lt'] = year_max

    if is_valid_queryparam(country) and country != '--':
        filter_conditions['Country'] = country

    if is_valid_queryparam(code) and code != '--':
        filter_conditions['Code'] = code

    queryset = Occupation.objects.filter(**filter_conditions)
    queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        code = F('Code__SOC_Code'),
        Group = F('Code__SOC_Group'),
        Title = F('Code__SOC_Title'),
    )

    data = pd.DataFrame(list(queryset.values('country','code', 'Group','Title','Year', 'Number')))

    data.rename(columns={'country':'Country','code': 'Code'}, inplace=True)

    column_order = ['Country', 'Code', 'Group', 'Title', 'Year', 'Number']

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

def update_selected_occupation(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('occupation_table')
    else:
        queryset = Occupation.objects.filter(id__in = selected_ids)
        queryset = queryset.annotate(
            country = F('Country__Country_Name'),
            code = F('Code__SOC_Code'),
            title = F('Code__SOC_Title')
        )

        data = pd.DataFrame(list(queryset.values('id','Year','country','code', 'title','Number')))

        data.rename(columns= {
            'country': 'Country',
            'code':'Code',
            'title': 'SOC Title'
        }, inplace=True)

        column_order = ['id','Country','Year','Code','SOC Title','Number']
        
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
