from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.db.models import Q
import pandas as pd
from ..models import ActivityData,Country_meta,Activity_Meta
from ..forms import UploadActivityDataForm
from trade_data.views import tables
from django.contrib import messages
from trade_data import views
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse

def is_valid_queryparam(param):
    return param !='' and  param is not None

def display_activity_table(request):
    data = ActivityData.objects.all()
    country_categories = Country_meta.objects.all()
    activity_codes = Activity_Meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    activity_code = request.GET.get('activity_code')
    district = request.GET.get('district')
    minimum_person = request.GET.get('minimum_person')
    maximum_person = request.GET.get('maximum_person')


    if is_valid_queryparam(date_min):
        data = data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data = data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(activity_code) and activity_code != '--':
        data = data.filter(Activity_Code=activity_code)

    if is_valid_queryparam(minimum_person):
        data = data.filter(Person__gte=minimum_person)

    if is_valid_queryparam(maximum_person):
        data = data.filter(Person__lt=maximum_person)
    
    if is_valid_queryparam(district):
        data=data.filter(Q(Districts__icontains=district)).distinct()

    


    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    context = {
        'tables':tables,
        'data_len': len(data),
        'query_len': len(page),
        'page': page,
        'country_categories': country_categories,
        'activity_codes': activity_codes,
    }

    return render(request, 'general_data/activity_templates/activity_table.html', context)
  
def upload_activity_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadActivityDataForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data,dtype={'Activity_Code': str})

            if 'id' in df.columns:
                cols = df.columns.tolist()
                for index, row in df.iterrows():
                    id_value = row.get('id')
                    try:
                        activity_instance = ActivityData.objects.get(id=id_value)
                    except Exception as e:
                        data = {col: row[col] for col in cols}
                        errors.append({
                            'row_index': index,
                            'data': data,
                            'reason': f'Error inserting row {index}:{e}'
                        })
                        continue

                    activity_data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Activity_Code': row['Activity_Code'],
                        'Person': row['Person'],
                        'Districts': row['Districts'],
                        'Text_Documents_Upload': row['Text_Documents_Upload']
                    }

                    country_instance = Country_meta.objects.filter(Country_Name=row['Country']).first()
                    activity_code_instance = Activity_Meta.objects.filter(Code=row['Activity_Code']).first()

                    if country_instance is None:
                        errors.append({
                            'row_index': index,
                            'data': activity_data,
                            'reason': f"Country not found"
                        })
                        continue

                    if activity_code_instance is None:
                        errors.append({
                            'row_index': index,
                            'data': activity_data,
                            'reason': f"activity_meta code not found"
                        })
                        continue

                    activity_instance.Year = row['Year']
                    activity_instance.Country = country_instance
                    activity_instance.Activity_Code = activity_code_instance
                    activity_instance.Person = row['Person']
                    activity_instance.Districts = row['Districts']
                    activity_instance.Text_Documents_Upload = row['Text_Documents_Upload']

                    activity_instance.save()
                    updated_count += 1

            else:
                for index, row in df.iterrows():
                    activity_data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Activity_Code': row['Activity_Code'],
                        'Person': row['Person'],
                        'Districts': row['Districts'],
                        'Text_Documents_Upload': row['Text_Documents_Upload']
                    }
                    country_instance = None
                    activity_code_instance = None
                    try:
                        country_instance = Country_meta.objects.get(Country_Name=row['Country'])
                        activity_code_instance = Activity_Meta.objects.get(Code=row['Activity_Code'])

                        existing_record = ActivityData.objects.filter(Q(Year=row['Year']) & Q(Country=country_instance) & Q(Activity_Code=activity_code_instance) & Q(Person=row['Person']) & Q(Districts = row['Districts']) &Q(Text_Documents_Upload= row['Text_Documents_Upload'])).first()
                        if existing_record:
                            duplicate_data.append({
                                'row_index': index,
                                'data': activity_data,
                                'reason': 'Duplicate data found'
                            })
                        else:
                            try:
                                activity_data = {
                                    'Year': row['Year'],
                                    'Country': country_instance,
                                    'Activity_Code': activity_code_instance,
                                    'Person': row['Person'],
                                    'Districts': row['Districts'],
                                    'Text_Documents_Upload': row['Text_Documents_Upload']
                                }
                                Activity_data=ActivityData(**activity_data)
                                Activity_data.save()
                                added_count += 1
                            except Exception as e:
                                errors.append({
                                    'row_index': index,
                                    'data': activity_data,
                                    'reason': f"Error inserting row {index}: {e}"
                                })
                    except Exception as e:
                        errors.append({'row_index': index, 'data': activity_data, 'reason': str(e)})
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
        form = UploadActivityDataForm()

    return render(request, 'general_data/transport_templates/upload_transport_form.html', {'form': form})

def display_activity_data_meta(request):
    data = Activity_Meta.objects.all()
    total_data = data.count()

    column_names = Activity_Meta._meta.fields

    context = {'data': data,'total_data':total_data,'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)

def update_selected_activity(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('activity_table')

    else:
        queryset = ActivityData.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        activity_code=F('Activity_Code__Code'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','activity_code', 'Person', 'Districts', 'Text_Documents_Upload')))
        df.rename(columns={'country': 'Country', 'activity_code': 'Activity_Code'}, inplace=True)
        df = df[['id','Year', 'Country', 'Activity_Code', 'Person', 'Districts', 'Text_Documents_Upload']]
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