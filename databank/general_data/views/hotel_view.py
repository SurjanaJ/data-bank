from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Hotel, Country_meta
from ..forms import UploadHotelDataForm,UploadHotelData
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse


def is_valid_queryparam(param):
    return param !='' and param is not None

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

def delete_hotel_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(Hotel, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('hotel_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")
       
def update_hotel_record(request,pk):
    hotel_record = Hotel.objects.get(id=pk)
    form = UploadHotelData(instance=hotel_record)

    if request.method == 'POST':
        form = UploadHotelData(request.POST, instance=hotel_record)
        if form.is_valid():
            form.save()
            return redirect('hotel_table')
        
    context={'form':form,}
    return render(request,'general_data/update_record.html',context)

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

            if 'id' in df.columns:
                cols = df.columns.to_list()
                for index,row in df.iterrows():
                    id_value = row['id']

                    try:
                        hotel_instance = Hotel.objects.get(id = id_value)
                    except Exception as e:
                        data = {col: row[col] for col in cols}
                        errors.append({
                            'row index': index,
                            'data':data,
                            'reason': f'Error inserting row  {index}: {e}'
                        })
                        continue

                    hotel_data = {
                        'Year': row['Year'].date().strftime('%Y-%m-%d'),
                        'Country': row['Country'],
                        'Name_Of_The_Hotel': row['Name_Of_The_Hotel'],
                        'Capacity_Room': row['Capacity_Room'],
                        'Occupancy_In_Year': row['Occupancy_In_Year'],
                        'City' : row['City'],                        
                    }

                    try:
                        Year = row['Year']
                        Country = row['Country']

                        calender_year = pd.to_datetime(Year).date()
                    except ValueError as e:
                        errors.append({'row_index': index, 'data': hotel_data, 'reason': str(e)})
                        continue    

                    try:               
                        Year =calender_year
                        Country = Country_meta.objects.get(Country_Name = Country)

                        hotel_instance.Year = Year
                        hotel_instance.Country = Country
                        hotel_instance.Name_Of_The_Hotel = row['Name_Of_The_Hotel']
                        hotel_instance.Capacity_Room = row['Capacity_Room']
                        hotel_instance.Occupancy_In_Year = row['Occupancy_In_Year']
                        hotel_instance.City = row['City']

                        hotel_instance.save()

                        updated_count +=1
                    except Exception as e:
                        hotel_data = {
                            'Year': row['Year'].date().strftime('%Y-%m-%d'),
                            'Country': row['Country'],
                            'Name_Of_The_Hotel': row['Name_Of_The_Hotel'],
                            'Capacity_Room': row['Capacity_Room'],
                            'Occupancy_In_Year': row['Occupancy_In_Year'],
                            'City' : row['City'],                        
                        }

                        errors.append({'row_index': index,'data': hotel_data,'reason':str(e)})
                        continue

            else:

                for index,row in df.iterrows():
                    hotel_data = {
                        'Year': row['Year'].date().strftime('%Y-%m-%d'),
                        'Country': row['Country'],
                        'Name_Of_The_Hotel': row['Name_Of_The_Hotel'],
                        'Capacity_Room': row['Capacity_Room'],
                        'Occupancy_In_Year': row['Occupancy_In_Year'],
                        'City' : row['City'],                        
                    }

                    try:
                        calender_date = datetime.strptime(str(row['Year'].date().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                    except:
                        calender_date = datetime.strptime(f'{str(row["Year"].date().strftime("%Y-%m-%d"))}-01-01', '%Y-%m-%d').date()

                    Country = None
                    try:
                        Year = calender_date.strftime('%Y-%m-%d')
                        Country = Country_meta.objects.get(Country_Name=row['Country'])

                        hotel_data = {
                            'Year':Year,
                            'Country':Country,
                            'Name_Of_The_Hotel': row['Name_Of_The_Hotel'],
                            'Capacity_Room': row['Capacity_Room'],
                            'Occupancy_In_Year': row['Occupancy_In_Year'],
                            'City' : row['City'],
                        }

                    except Exception as e:
                        errors.append({
                            'row index': index,
                            'data':hotel_data,
                            'reason': f'Error inserting row  {index}: {e}'
                        })
                        continue

                    existing_record = Hotel.objects.filter(Q(Year = Year) & Q(Country = Country) & Q(Name_Of_The_Hotel = hotel_data['Name_Of_The_Hotel'])& Q(Capacity_Room = hotel_data['Capacity_Room']) & Q(City = hotel_data['City']) & Q(Occupancy_In_Year = hotel_data['Occupancy_In_Year'])).first()

                    if existing_record:
                        duplicate_data.append({
                            'row_index':index,
                            'data':hotel_data,
                            'reason': 'Duplicate record found'
                        })

                    else:
                        try:
                            HotelData=Hotel(**hotel_data)
                            HotelData.save()
                            added_count +=1

                        except Exception as e:
                            errors.append({
                                'row_index': index,
                                'data': hotel_data,
                                'reason': f'Error inserting row  {index}: {e}'
                            })

            if added_count > 0:
                messages.success(request,str(added_count)+'records added')


            if updated_count > 0:
                messages.success(request,str(updated_count)+'records updated')

            if errors:
                request.session['errors']= errors
                return render(request, 'general_data/error_template.html', {'errors': errors})
            

            if duplicate_data:
                return  render (request,'general_data/duplicate_template.html',{'duplicate_data':duplicate_data})

    else:
        form = UploadHotelDataForm()

    return render(request,'general_data/upload_form.html',{'form':form}) 
                             
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
        df.rename(columns={'country': 'Country'}, inplace=True)
        df = df[['id','Year','Country','Name_Of_The_Hotel','Capacity_Room','Occupancy_In_Year','City']]
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