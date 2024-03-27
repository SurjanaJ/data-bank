from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd

from .energy_view import strip_spaces
from ..models import Political_Data, Country_meta
from ..forms import UploadPoliticalForm
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
def display_political_table(request):

    data = Political_Data.objects.all()
    country_categories = Country_meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    political_party_name = request.GET.get('political_party_name')    
    min_no_of_members = request.GET.get('minimum_no_of_members')
    max_no_of_members = request.GET.get('maximum_no_of_members')
    province = request.GET.get('view_province')
    district = request.GET.get('district')
    municipality = request.GET.get('municipality')
    ward = request.GET.get('ward')  

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(political_party_name):
        data=data.filter(Q(Political_Party_Name__icontains=political_party_name)).distinct()

    if is_valid_queryparam(min_no_of_members):
        data = data.filter(Number_Of_Member__gte=min_no_of_members)

    if is_valid_queryparam(max_no_of_members):
        data = data.filter(Number_Of_Member__lt=max_no_of_members)

    if is_valid_queryparam(province):
        data=data.filter(Q(Province__icontains=province)).distinct()

    if is_valid_queryparam(district):
        data=data.filter(Q(District__icontains=district)).distinct()

    if is_valid_queryparam(municipality):
        data=data.filter(Q(Municipality__icontains=municipality)).distinct()

    if is_valid_queryparam(ward):
        data=data.filter(Q(Wards__icontains=ward)).distinct()

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'country_categories':country_categories,
    }
    return render(request, 'general_data/political_templates/political_table.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_political_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0 
    if request.method == 'POST':
        form = UploadPoliticalForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

             # Check if required columns exist
            required_columns = ['Year', 'Country', 'Political Party Name','Number Of Member','Province','District','Municipality','Wards']  # Add your required column names here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing columns: {', '.join(missing_columns)}")
                return render(request,'general_data/invalid_upload.html', {'missing_columns': missing_columns, 'tables': tables, 'meta_tables': views.meta_tables,} )
            
            #Update existing data
            if 'id' in df.columns:
                for index,row in df.iterrows():
                    id_value = row.get('id')
                    data = {
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'Political Party Name': row['Political Party Name'],
                        'No Of Member':row['No Of Member'],
                        'Province':row['Province'],
                        'District':row['District'],
                        'Municipality':row['Municipality'],
                        'Wards':row['Wards'], 
                    }

                    #get existing data
                    try: 
                        political_instance = Political_Data.objects.get(id = id_value)
                        political_data = data

                        #check if meta values exist
                        try:
                            Country = Country_meta.objects.get(Country_Name=row['Country'])
                            
                            political_instance.Year = row['Year']
                            political_instance.Country = Country
                            political_instance.Political_Party_Name = row['Political Party Name']
                            political_instance.Number_Of_Member = row['No Of Member']
                            political_instance.Province= row['Province']
                            political_instance.District = row['District']
                            political_instance.Municipality = row['Municipality']
                            political_instance.Wards = row['Wards']
                            
                            political_instance.save()
                            updated_count += 1

                        #meta does not exist
                        except Exception as e:
                            political_data = data
                            errors.append({'row_index': index, 'data': political_data, 'reason': str(e)})
                            continue    

                    except Exception as e:
                        political_data = data
                        errors.append({
                            'row_index': index,
                            'data':data,
                            'reason':f'Error inserting row {index}:{e}'
                        })
                        continue

            else:
                #add new data
                for index,row in df.iterrows():
                    data = {
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'Political Party Name': row['Political Party Name'],
                        'No Of Member':row['No Of Member'],
                        'Province':row['Province'],
                        'District':row['District'],
                        'Municipality':row['Municipality'],
                        'Wards':row['Wards'], 
                    }
                    
                    #check if the meta values exist
                    try:
                        Country = Country_meta.objects.get(Country_Name=row['Country'])
                        political_data = {
                            'Year':row['Year'],
                            'Country':Country,
                            'Political Party Name': row['Political Party Name'],
                            'No Of Member':row['No Of Member'],
                            'Province':row['Province'],
                            'District':row['District'],
                            'Municipality':row['Municipality'],
                            'Wards':row['Wards'], 
                        }

                        existing_record = Political_Data.objects.filter(
                            Q(Year = row['Year'])
                            & Q(Country = Country)
                            & Q(Political_Party_Name = row['Political Party Name'])
                            & Q(Number_Of_Member = row['No Of Member'])
                            & Q(Province = row['Province'])
                            & Q(District = row['District'])
                            & Q(Municipality = row['Municipality'])
                            & Q(Wards = row['Wards'])
                        ).first()

                        if existing_record:
                            political_data = data
                            duplicate_data.append({
                                'row_index': index,
                                    'data': {key: str(value) for key, value in political_data.items()}
                            })
                            continue
                        else:
                            #add new record
                            try:
                                political_data = {
                                    'Year':row['Year'],
                                    'Country':Country,
                                    'Political_Party_Name': row['Political Party Name'],
                                    'Number_Of_Member':row['No Of Member'],
                                    'Province':row['Province'],
                                    'District':row['District'],
                                    'Municipality':row['Municipality'],
                                    'Wards':row['Wards'], 
                                }
                                politicalData = Political_Data(**political_data)
                                politicalData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")

                    except Exception as e:
                        political_data = data
                        errors.append({
                            'row_index': index, 
                            'data': political_data,
                            'reason': f'Error inserting row {index}: {e}'
                        })
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
            return redirect('political_table') 
    else:
        form = UploadPoliticalForm()

    return render(request, 'general_data/upload_form.html', {'form': form, 'tables':tables})

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def update_selected_political(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('political_table')

    else:
        queryset = Political_Data.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        )

        data = pd.DataFrame(list(queryset.values('id','Year','country','Political_Party_Name','Number_Of_Member','Province','District','Municipality','Wards')))

        data.rename(columns={
            'country': 'Country',
            'Political_Party_Name':'Political Party Name',
            'Number_Of_Member':'No Of Member'
            }, inplace=True)
        column_order = ['id','Year','Country','Political Party Name','No Of Member','Province','District','Municipality','Wards']
        
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

