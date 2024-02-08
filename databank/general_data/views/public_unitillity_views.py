from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Public_Unitillity, Country_meta
from ..forms import UploadPublicUnitillityDataForm,UploadPublicUnitillityData
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST



def is_valid_queryparam(param):
    return param !='' and param is not None


def display_public_unitillity_table(request):

    data = Public_Unitillity.objects.all()
    country_categories = Country_meta.objects.all()


    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    public_unitillity_type_category = request.GET.get('public_unitillity_type_category')
    min_number  = request.GET.get('minimum_number')
    max_number = request.GET.get('maximum_number')

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(public_unitillity_type_category):
        data=data.filter(Q(Type_Of_Public_Utility__icontains=public_unitillity_type_category)).distinct()

    if is_valid_queryparam(min_number):
        data = data.filter(Number__gte=min_number)

    if is_valid_queryparam(max_number):
        data = data.filter(Number__lt=max_number)

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context={
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'country_categories':country_categories,
        'tables':tables
    }

    return render(request, 'general_data/public_unitillity_templates/public_unitillity_table.html', context)

def delete_public_unitillity_record(request, item_id):
    try:
        item_to_delete = get_object_or_404(Public_Unitillity, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('public_unitillity_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")

@require_POST
def delete_selected_public_unitillity(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('public_unitillity_table')
    try:
        Public_Unitillity.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('public_unitillity_table')

def duplicate_data_to_excel(duplicate_data):
    column_names = list(duplicate_data[0]['data'].keys())
    duplicate_df = pd.DataFrame([d['data'] for d in duplicate_data], columns=column_names)

    # Create a response object with Excel content
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=duplicate_data.xlsx'

    duplicate_df.to_excel(response, index=False, sheet_name='duplicate_data')

    return response

def download_duplicate_excel(request):
    duplicate_data = request.session.get('duplicate_data', [])
    print('DUPLICATE DATA!!!!')
    print(duplicate_data)
    print()
    if duplicate_data:
        response = duplicate_data_to_excel(duplicate_data)
        request.session.pop('duplicate_data', None)
        return response
    else:
        return HttpResponse('No data to export.')
    
def update_public_unitillity_record(request,pk):
    public_unitillity_record = Public_Unitillity.objects.get(id=pk)
    form = UploadPublicUnitillityData(instance=public_unitillity_record)

    if request.method == 'POST':
        form = UploadPublicUnitillityData(request.POST, instance=public_unitillity_record)
        if form.is_valid():
            form.save()
            return redirect('public_unitillity_table')
        
    context={'form':form,}
    return render(request,'general_data/public_unitillity_templates/update_public_unitillity_record.html',context)

def upload_public_unitillity_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadPublicUnitillityDataForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['public_unitillity_data_file']
            df = pd.read_excel(excel_data)
            if 'id' in df.columns or 'ID' in df.columns:
                for index,row in df.iterows():
                    id_value = row['ID']

                    try:
                        public_unitillity_instance = Public_Unitillity.objects.get(id = id_value)
                    except:
                        public_unitillity_instance =Public_Unitillity()

                    Year = row['Year']
                    Country = row['Country']

                    try:
                        calender_year = pd.to_datetime(Year).date()

                    except ValueError as e:
                        print(f'Error converting date in row {index}:{e}')
                        print(f"Problematic row data:{row}")
                        continue

                    try:
                        Year = calender_year
                        Country = Country_meta.objects.get(Country_name = Country)

                    except DataError as e:
                        print(f"Error handling the row at {index}:{e}")

                    public_unitillity_instance.Year = Year
                    public_unitillity_instance.Country = Country
                    public_unitillity_instance.Type_Of_Public_Utility=row['Type_Of_Public_Utility']
                    public_unitillity_instance.Number=row['Number']
                    public_unitillity_instance.save()

                    updated_count +=1
                
            else:

                for index, row in df.iterrows():
                    public_unitillity_data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Name_of_the_plant': row['Type_Of_Public_Utility'],
                        'Number' : row['Number'],
                    }


                    try:
                        calender_date = datetime.strptime(str(row['Year'].date().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                    except:
                        calender_date = datetime.strptime(f'{str(row["Year"].date().strftime("%Y-%m-%d"))}-01-01', '%Y-%m-%d').date()
                    
                    Country = None

                    try:
                        Year = calender_date.strftime('%Y-%m-%d')
                        Country = Country_meta.objects.get(Country_Name=row['Country'])
                        public_unitillity_data = {
                            'Year': Year,
                            'Country': Country,
                            'Type_Of_Public_Unitillity': row['Type_Of_Public_Unitillity'],
                            'Number' : row['Number'],
                            }
                    except Exception as e:
                            errors.append({
                                'row_index': index,
                                'data': public_unitillity_data,
                                'reason': f'Error inserting row {index}: {e}'
                            })
                            continue

                    existing_record = Public_Unitillity.objects.filter(
                        Q(Year=Year) & Q(Country=Country) & Q(Type_Of_Public_Unitillity = public_unitillity_data['Type_Of_Public_Unitillity']) & Q(Number = public_unitillity_data['Number']) ).first()        

                    if existing_record:
                        duplicate_data.append({
                            'row_index':index,
                            'data': public_unitillity_data,
                            'reason': 'Duplicate data found'
                        })


                    else:
                        try:
                            public_unitillity =Public_Unitillity(**public_unitillity_data)
                            public_unitillity.save()
                            added_count +=1

                        except Exception as e:
                            errors.append({
                                'row_index': index,
                                'data': public_unitillity_data,
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
        form = UploadPublicUnitillityDataForm()

    return render(request, 'general_data/upload_form.html', {'form': form, 'tables':tables})