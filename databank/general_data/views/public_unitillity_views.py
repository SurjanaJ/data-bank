from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd

from trade_data import views

from .energy_view import strip_spaces
from ..models import Public_Unitillity, Country_meta
from ..forms import UploadPublicUnitillityDataForm,UploadPublicUnitillityData
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users


def is_valid_queryparam(param):
    return param !='' and param is not None

@login_required(login_url = 'login')
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

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def delete_public_unitillity_record(request, item_id):
    try:
        item_to_delete = get_object_or_404(Public_Unitillity, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('public_unitillity_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
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

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
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

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_public_unitillity_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadPublicUnitillityDataForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['Public_Unitillity_data_file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)
            
            # Check if required columns exist
            required_columns = ['Year', 'Country', 'Type Of Public Utility','Number']  # Add your required column names here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing columns: {', '.join(missing_columns)}")
                return render(request,'general_data/invalid_upload.html', {'missing_columns': missing_columns, 'tables': tables, 'meta_tables': views.meta_tables,} )
            

            #Update existing data
            if 'id' in df.columns:
                for index,row in df.iterrows():
                    id = row.get('id')
                    data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Type Of Public Utility': row['Type Of Public Utility'],
                        'Number' : row['Number'],
                    }
                    


                    #get existing data
                    try:
                        public_utillity_instance = Public_Unitillity.objects.get(id = id)
                        utility_data = data

                        #check if meta values exist
                        try:
                            Country = Country_meta.objects.get(Country_Name = row['Country'])
                            public_utillity_instance.Year = row['Year']
                            public_utillity_instance.Country = Country
                            public_utillity_instance.Type_Of_Public_Utility=row['Type Of Public Utility']
                            public_utillity_instance.Number=row['Number']
                            
                            public_utillity_instance.save()
                            updated_count += 1


                        #meta does not exist
                        except Exception as e:
                            utility_data = data
                            errors.append({'row_index': index, 'data': utility_data, 'reason': str(e)})
                            continue
                    
                    # no existing data
                    except Exception as e:
                        utility_data = data
                        errors.append({
                                        'row_index': index,
                                        'data': utility_data,
                                        'reason': f'Error inserting row {index}: {e}'
                                    })
                        continue
                    

            else:

                for index, row in df.iterrows():
                    data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Type Of Public Utility': row['Type Of Public Utility'],
                        'Number' : row['Number'],
                    }

                    #check if the meta values exist
                    try:
                        Country = Country_meta.objects.get(Country_Name = row['Country'])

                        utility_data = {
                                'Year': row['Year'],
                                'Country': row['Country'],
                                'Type Of Public Utility': row['Type Of Public Utility'],
                                'Number' : row['Number'],
                        }

                        existing_record = Public_Unitillity.objects.filter(
                            Q(Country = Country)
                            & Q(Year = row['Year'])
                            & Q(Type_Of_Public_Utility = row['Type Of Public Utility'])
                            & Q(Number = row['Number'])
                        ).first()
                        

                        # show duplicate data
                        if existing_record:
                            utility_data = data
                            duplicate_data.append({
                                'row_index': index,
                                    'data': {key: str(value) for key, value in utility_data.items()}
                            })
                            continue
                        else:
                            #add new record
                            try:
                                utility_data = {
                                'Year': row['Year'],
                                'Country':Country,
                                'Type_Of_Public_Utility': row['Type Of Public Utility'],
                                'Number' : row['Number'],
                        }
                                utilityData = Public_Unitillity(**utility_data)
                                utilityData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")
                    

                        #meta does not exist
                    except Exception as e:
                        utility_data = data
                        errors.append({'row_index': index, 'data': utility_data, 'reason': str(e)})
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
           # form is not valid
                return redirect('public_unitillity_table')
            
    else:
        form = UploadPublicUnitillityDataForm()

    return render(request, 'general_data/upload_form.html', {'form': form, 'tables':tables})

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def update_selected_public_unitillity(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('public_unitillity_table')

    else:
        queryset = Public_Unitillity.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','Type_Of_Public_Utility','Number')))
        df.rename(columns={'country': 'Country','Type_Of_Public_Utility':'Type Of Public Utility'}, inplace=True)
        df = df[['id','Year','Country','Type Of Public Utility','Number']]
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