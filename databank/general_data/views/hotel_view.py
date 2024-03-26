from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Hotel, Country_meta
from ..forms import UploadHotelDataForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse
from .energy_view import strip_spaces
from trade_data import views

from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users


def is_valid_queryparam(param):
    return param !='' and param is not None

@login_required(login_url = 'login')
def display_hotel_table(request):

    url = reverse('population_table')
    data = Hotel.objects.all()
    country_categories = Country_meta.objects.all()
    # age_group_options=[choice[1] for choice in Hotel.Age_Group_Options]

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    name_of_the_hotel=request.GET.get('name_of_the_hotel')
    name_of_the_city=request.GET.get('name_of_the_city')



    country_category = request.GET.get('country_category')

    if is_valid_queryparam (date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lte=date_max)

    if is_valid_queryparam(name_of_the_hotel):
        data=data.filter(Q(Name_Of_The_Hotel__icontains=name_of_the_hotel)).distinct()

    if is_valid_queryparam(name_of_the_city):
        data=data.filter(Q(City__icontains=name_of_the_city)).distinct()
 
    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)




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
    return render(request, 'general_data/hotel_templates/hotel_table.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
@require_POST
def delete_selected_hotel(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('hotel_table')
    try:
        Hotel.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('hotel_table')

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def delete_hotel_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(Hotel, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('hotel_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])       
def upload_hotel_excel(request):

    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadHotelDataForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['Hotel_data_file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

            # Check if required columns exist
            required_columns = ['Year', 'Country', 'Name Of The Hotel','Capacity Room','Occupancy In Year','City']  # Add your required column names here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing columns: {', '.join(missing_columns)}")
                return render(request,'general_data/invalid_upload.html', {'missing_columns': missing_columns, 'tables': tables, 'meta_tables': views.meta_tables,} )
            

            if 'id' in df.columns:
                for index,row in df.iterrows():
                    id = row.get('id')
                    data = {
                            'Year': row['Year'],
                            'Country': row['Country'],
                            'Name Of The Hotel': row['Name Of The Hotel'],
                            'Capacity Room': row['Capacity Room'],
                            'Occupancy In Year': row['Occupancy In Year'],
                            'City' : row['City'],                        
                        }
                    #get existing data
                    try:
                        hotel_instance = Hotel.objects.get(id = id)
                        hotel_data = data

                        #check if meta values exist
                        try:

                            Country = Country_meta.objects.get(Country_Name = row['Country'])

                            hotel_instance.Year = row['Year']
                            hotel_instance.Country = Country
                            hotel_instance.Name_Of_The_Hotel = row['Name Of The Hotel']
                            hotel_instance.Capacity_Room = row['Capacity Room']
                            hotel_instance.Occupancy_In_Year = row['Occupancy In Year']
                            hotel_instance.City = row['City']

                            hotel_instance.save()

                            updated_count +=1

                        #meta does not exist
                        except Exception as e:
                            hotel_data = data
                            errors.append({'row_index': index, 'data': hotel_data, 'reason': str(e)})
                            continue


                    except Exception as e:
                        hotel_data = data
                        errors.append({
                            'row index': index,
                            'data':hotel_data,
                            'reason': f'Error inserting row  {index}: {e}'
                        })
                        continue


            else:
                for index,row in df.iterrows():
                    data = {
                            'Year': row['Year'],
                            'Country': row['Country'],
                            'Name Of The Hotel': row['Name Of The Hotel'],
                            'Capacity Room': row['Capacity Room'],
                            'Occupancy In Year': row['Occupancy In Year'],
                            'City' : row['City'],                        
                        }

                    try:
                        Country = Country_meta.objects.get(Country_Name=row['Country'])

                        hotel_data = {
                            'Year':row['Year'],
                            'Country':Country,
                            'Name Of The Hotel': row['Name Of The Hotel'],
                            'Capacity Room': row['Capacity Room'],
                            'Occupancy In Year': row['Occupancy In Year'],
                            'City' : row['City'],
                        }

                    

                        existing_record = Hotel.objects.filter(
                            Q(Year = row['Year']) 
                            & Q(Country = Country) 
                            & Q(Name_Of_The_Hotel = row['Name Of The Hotel'])
                            & Q(Capacity_Room = row['Capacity Room']) 
                            & Q(City = row['City']) 
                            & Q(Occupancy_In_Year = row['Occupancy In Year'])).first()

                        if existing_record:
                            hotel_data = data
                            duplicate_data.append({
                                'row_index': index,
                                    'data': {key: str(value) for key, value in hotel_data.items()}
                            })
                            continue

                        else:
                            try:
                                hotel_data = {
                                'Year':row['Year'],
                                'Country':Country,
                                'Name_Of_The_Hotel': row['Name Of The Hotel'],
                                'Capacity_Room': row['Capacity Room'],
                                'Occupancy_In_Year': row['Occupancy In Year'],
                                'City' : row['City'],
                            }
                                HotelData=Hotel(**hotel_data)
                                HotelData.save()
                                added_count +=1

                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")

                    except Exception as e:
                        hotel_data = data
                        errors.append({'row_index': index, 'data': hotel_data, 'reason': str(e)})
                        continue

            if added_count > 0:
                messages.success(request,str(added_count)+'records added')


            if updated_count > 0:
                messages.success(request,str(updated_count)+'records updated')

            if errors:
                request.session['errors'] = errors
                return render(request, 'trade_data/error_template.html', {'errors': errors, 'tables': tables, 'meta_tables': views.meta_tables, })
            

            elif duplicate_data:
                request.session['duplicate_data'] = duplicate_data
                return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data, 'tables': tables, 'meta_tables': views.meta_tables,})
            
            else:
                return redirect('hotel_table')


    else:
        form = UploadHotelDataForm()

    return render(request,'general_data/upload_form.html',{'form':form}) 

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])                             
def update_selected_hotel(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('hotel_table')

    else:
        queryset = Hotel.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','Name_Of_The_Hotel','Capacity_Room','Occupancy_In_Year','City')))
        df.rename(columns={'country': 'Country','Name_Of_The_Hotel':'Name Of The Hotel','Capacity_Room':'Capacity Room','Occupancy_In_Year':'Occupancy In Year'}, inplace=True)
        df = df[['id','Year','Country','Name Of The Hotel','Capacity Room','Occupancy In Year','City']]
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