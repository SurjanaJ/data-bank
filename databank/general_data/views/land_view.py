from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
import pandas as pd
from ..models import Land, Country_meta,Land_Code_Meta
from ..forms import UploadLandDataForm, UploadLandMetaForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import F, Q
from io import BytesIO
from django.http import HttpResponse

from .energy_view import strip_spaces


from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users

from trade_data import views

def is_valid_queryparam(param):
    return param !='' and param is not None

@login_required(login_url = 'login')
def display_land_table(request):

    data = Land.objects.all()
    land_codes=Land_Code_Meta.objects.all()

    country_categories = Country_meta.objects.all()
    Land_Unit_Options = [choice[1] for choice in Land.Land_Unit_Options]

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    Land_Code = request.GET.get('land_code')
    unit = request.GET.get('land_unit')
    min_value = request.GET.get('minimum_area')
    max_value = request.GET.get('maximum_area')

  

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(Land_Code) and Land_Code != '--':
        data=data.filter(Land_Code = Land_Code)
     

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)
        

    if is_valid_queryparam(unit)  and unit != '--':
        data=data.filter(Unit=unit)

    if is_valid_queryparam(min_value):
        data = data.filter(Area__gte=min_value)

    if is_valid_queryparam(max_value):
        data = data.filter(Area__lt=max_value)


    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'country_categories':country_categories,
        'Land_Unit_Options':Land_Unit_Options,
        'land_codes':land_codes,

    }
    return render(request, 'general_data/land_templates/land_table.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
@require_POST
def delete_selected_land(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('land_table')
    try:
        Land.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('land_table')

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def delete_land_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(Land, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('land_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")

    
# def update_land_record(request,pk):
#     land_record = Land.objects.get(id=pk)
#     form = UploadLandData(instance=land_record)

#     if request.method == 'POST':
#         form = UploadLandData(request.POST, instance=land_record)
#         if form.is_valid():
#             form.save()
#             return redirect('land_table')
        
#     context={'form':form,}
#     return render(request,'general_data/update_record.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_land_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0
    
    if request.method == 'POST':
        form = UploadLandDataForm(request.POST,request.FILES)
        
        if form.is_valid():
            excel_data = request.FILES['Land_data_file']
            df = pd.read_excel(excel_data,dtype={'Land Code':str})
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

             # Check if required columns exist
            required_columns = ['Year', 'Country', 'Land Code','Unit','Area']  # Add your required column names here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing columns: {', '.join(missing_columns)}")
                return render(request,'general_data/invalid_upload.html', {'missing_columns': missing_columns, 'tables': tables, 'meta_tables': views.meta_tables,} )
            
            
            if 'id' in df.columns:
                for index,row in df.iterrows():
                    id = row.get('id')
                    data={
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Land Code': row['Land Code'],
                        'Land Type': row['Land Type'],
                        'Unit': row['Unit'],
                        'Area': row['Area']
                    }   

                    try:
                        land_instance = Land.objects.get(id = id)
                        land_data = data

                        #check if meta values exist
                        try:
                            Country = Country_meta.objects.get(Country_Name = row['Country'])
                            Code = Land_Code_Meta.objects.get(Code = row['Land Code'])
                                
                            land_instance.Year = row['Year']
                            land_instance.Country = Country
                            land_instance.Land_Code = Code
                            land_instance.Unit = row['Unit']
                            land_instance.Area = row['Area']
                            
                            land_instance.save()
                            updated_count +=1
                        #meta does not exist
                        except Exception as e:
                            land_data = data
                            errors.append({'row_index': index, 'data': land_data, 'reason': str(e)})
                            continue

                    except Exception as e:
                        land_data = data
                        errors.append({
                            'row_index':index,
                            'data':land_data,
                            'reason':f'Error inserting row {index}:{e}'
                        })
                        continue

            else:
                for index,row in df.iterrows():
                    data={
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Land Code': row['Land Code'],
                        'Land Type': row['Land Type'],
                        'Unit': row['Unit'],
                        'Area': row['Area']
                    }  

                    #check if the meta values exist
                    try:
                        Country = Country_meta.objects.get(Country_Name=row['Country'])
                        Code = Land_Code_Meta.objects.get(Code = row['Land Code'])
                        
                        existing_record = Land.objects.filter(
                            Q(Year = row['Year'])
                            & Q(Country = Country)
                            & Q(Land_Code = Code)
                            & Q(Unit = row['Unit'])
                            & Q(Area = row['Area'])
                        ).first()
                        
                        if existing_record:
                            land_data = data
                            duplicate_data.append({
                                'row_index': index,
                                    'data': {key: str(value) for key, value in land_data.items()}
                            })
                            continue
                        else:
                            #add new record
                            try:
                                land_data={
                                'Year': row['Year'],
                                'Country': Country,
                                'Land_Code': Code,
                                'Unit': row['Unit'],
                                'Area': row['Area']
                            }
                                landData = Land(**land_data)
                                landData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")
                    
                    except Exception as e:
                        land_data = data
                        errors.append({
                                'row_index': index,
                                'data': land_data, 
                                'reason': f'Error inserting row  {index}: {e}'
                            })
                        continue
            
        if added_count> 0 :
            messages.success(request,str(added_count)+ 'records addad')
                                
        if updated_count > 0:
            messages.info(request,str(updated_count)+'records updated') 

        if errors:
            request.session['errors'] = errors
            return render(request, 'trade_data/error_template.html', {'errors': errors, 'tables': tables, 'meta_tables': views.meta_tables, })

        if duplicate_data:
            request.session['duplicate_data'] = duplicate_data
            return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data, 'tables': tables, 'meta_tables': views.meta_tables,})

        else:
           # form is not valid
            return redirect('land_table') 
              
    else:
        form = UploadLandDataForm()
    return render(request,'general_data/land_templates/upload_land_form.html',{'form':form})

@login_required(login_url = 'login')
def display_land_meta(request):
    data = Land_Code_Meta.objects.all()
    total_data = data.count()

    column_names = Land_Code_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def update_selected_land(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('land_table')

    else:
        queryset = Land.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        land_code=F('Land_Code__Code'),
        land_type=F('Land_Code__Land_Type'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','land_code','land_type','Unit','Area')))
        df.rename(columns={'country': 'Country', 'land_code':'Land Code','land_type':'Land Type'}, inplace=True)
        df = df[['id','Year','Country','Land Code','Land Type','Unit','Area']]
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