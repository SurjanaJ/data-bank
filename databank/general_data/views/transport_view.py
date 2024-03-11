from datetime import datetime
from django.db import DataError
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Transport, Country_meta,Transport_Meta
from ..forms import UploadTransportDataForm,UploadTransportData
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse

from trade_data import views

def is_valid_queryparam(param):
    return param !='' and param is not None


def display_transport_table(request):
    url = reverse('transport_table')
    data = Transport.objects.all()
    country_categories = Country_meta.objects.all()
    unit_options = [choice[1] for choice in Transport.Unit_Options]
    transport_classification_codes = Transport_Meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    transport_classification_code = request.GET.get('transport_classification_code')

    quantity_unit=request.GET.get('quantity_unit')
    min_quantity = request.GET.get('minimum_quantity')
    max_quantity = request.GET.get('maximum_quantity')

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(transport_classification_code) and transport_classification_code != '--':
        data = data.filter(Transport_Classification_Code_id=transport_classification_code)

    if is_valid_queryparam(quantity_unit) and quantity_unit != '--':
        data = data.filter(Unit=quantity_unit)

    if is_valid_queryparam(min_quantity):
        data = data.filter(Quantity__gte=min_quantity)

    if is_valid_queryparam(max_quantity):
        data = data.filter(Quantity__lt=max_quantity)



    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'page':page,
        'query_len': len(page),
        'country_categories':country_categories,
        'unit_options':unit_options,
        'transport_classification_codes':transport_classification_codes
    }
    return render(request, 'general_data/transport_templates/transport_table.html',context)

@require_POST
def delete_selected_transport(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('transport_table')
    try:
        Transport.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('transport_table')


def delete_transport_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(Transport, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('transport_table')
    except Exception as e:
       messages.error(request, f'Error deleting item: {e}')
    


def update_transport_record(request,pk):
    transport_record = Transport.objects.get(id=pk)
    form = UploadTransportData(instance=transport_record)

    if request.method == 'POST':
        form = UploadTransportData(request.POST, instance=transport_record)
        if form.is_valid():
            form.save()
            return redirect('transport_table')
        
    context={'form':form,}
    return render(request,'general_data/transport_templates/update_transport_record.html',context)


def upload_transport_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0


    if request.method == 'POST':
        form = UploadTransportDataForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.FILES['Transport_data_file']
            df = pd.read_excel(excel_data,dtype={'Transport_Classification_Code':str})
            unit_options = [option[0] for option in Transport.Unit_Options]
            if 'id' in df.columns:
                for index,row in df.iterrows():
                    cols = df.columns.to_list()
                    id_value = row['id']

                    try:
                        transport_instance = Transport.objects.get(id = id_value)
                    except Exception as e:
                        data = {col: row[col] for col in cols}
                        errors.append({
                            'row_index':index,
                            'data':data,
                            'reason':f'Error inserting row {index}:{e}'
                        })
                        continue
                    transport_data = {
                            'Year': row['Year'].date().strftime('%Y-%m-%d'),
                            'Country': row['Country'],
                            'Transport_Classification_Code': row['Transport_Classification_Code'],
                            'Unit': row['Unit'],
                            'Quantity': row['Quantity']
                        }


                    try:
                        Year = row['Year']
                        Country = row['Country']
                        Transport_Classification_Code = row['Transport_Classification_Code']
                        calender_year = pd.to_datetime(Year).date()
                    except Exception as e:
                        errors.append({'row_index': index, 'data': transport_data, 'reason': str(e)})
                        continue
                    # Handle the date conversion error, such as logging a message or skipping the row
                    try:

                        if transport_data['Unit'] not in unit_options:
                            transport_data = {
                                'Year': row['Year'].date().strftime('%Y-%m-%d'),
                                'Country': row['Country'],
                                'Transport_Classification_Code': row['Transport_Classification_Code'],
                                'Unit': row['Unit'],
                                'Quantity': row['Quantity']
                            }
                            errors.append({'row_index': index, 'data': transport_data, 'reason': f'Error inserting row {index}: Invalid unit value'})
                        else:
                            Year = calender_year
                            Country = Country_meta.objects.get(Country_Name = Country )
                            Transport_Classification_Code = Transport_Meta.objects.get(Code = Transport_Classification_Code)


                            transport_instance.Year = Year
                            transport_instance.Country = Country
                            transport_instance.Transport_Classification_Code = Transport_Classification_Code
                            transport_instance.Unit = row['Unit']
                            transport_instance.Quantity = row['Quantity']
                            transport_instance.save()

                            updated_count += 1 
                    except Exception as e:
                        transport_data = {
                            'Year': row['Year'].date().strftime('%Y-%m-%d'),
                            'Country': row['Country'],
                            'Transport_Classification_Code': row['Transport_Classification_Code'],
                            'Unit': row['Unit'],
                            'Quantity': row['Quantity']
                        
                        }
                        errors.append({'row_index': index, 'data': transport_data, 'reason': str(e)})
                        continue
            else:
                for index, row in df.iterrows():
                    transport_data = {
                        'Year': row['Year'].date().strftime('%Y-%m-%d'),
                        'Country': row['Country'],
                        'Transport_Classification_Code': row['Transport_Classification_Code'],
                        'Unit': row['Unit'],
                        'Quantity': row['Quantity'],
                    }
                        # Check if the 'Unit' value is in the predefined options
                    if transport_data['Unit'] not in unit_options:
                        errors.append({
                            'row_index': index,
                            'data': transport_data,
                            'reason': f'Error inserting row {index}: Invalid unit value'
                        })
                    else:
                        
                        try:
                            calender_date = datetime.strptime(str(row['Year'].date().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                        except:
                            calender_date = datetime.strptime(f'{str(row["Year"].date().strftime("%Y-%m-%d"))}-01-01', '%Y-%m-%d').date()
                        
                        # if not initialize it shows server error else shows in error template
                        Country = None
                        Transport_Classification_Code = None
                        try:
                            Year = calender_date.strftime('%Y-%m-%d')
                            Country = Country_meta.objects.get(Country_Name=row['Country'])
                            Transport_Classification_Code = Transport_Meta.objects.get(Code=row['Transport_Classification_Code'])

                            transport_data = {
                                'Year': Year,
                                'Country': Country,
                                'Transport_Classification_Code': Transport_Classification_Code,
                                'Unit': row['Unit'],
                                'Quantity': row['Quantity']
                            }

                        except Exception as e:
                            errors.append({
                                'row_index': index,
                                'data': transport_data,
                                'reason': f'Error inserting row  {index}: {e}'
                            })
                            continue

                        existing_record = Transport.objects.filter(
                            Q(Year=Year) & Q(Country=Country) & Q(Transport_Classification_Code=Transport_Classification_Code)
                            & Q(Unit=transport_data['Unit']) & Q(Quantity=transport_data['Quantity'])).first()

                        if existing_record:
                            duplicate_data.append({
                                'row_index': index,
                                'data': transport_data,
                                'reason': 'Duplicate record found'
                            })

                        else:
                            try:
                                TransportData = Transport(**transport_data)
                                TransportData.save()
                                added_count += 1

                            except Exception as e:
                                errors.append({
                                    'row_index': index,
                                    'data': transport_data,
                                    'reason': f'Error inserting row  {index}: {e}'
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
        form = UploadTransportDataForm()

    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})


def display_transport_meta(request):
    data = Transport_Meta.objects.all()
    total_data = data.count()

    column_names = Transport_Meta._meta.fields
    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)


def update_selected_transport(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('transport_table')

    else:
        queryset = Transport.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        transport_classification_code = F('Transport_Classification_Code__Code'),
 
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','transport_classification_code','Unit','Quantity')))
        df.rename(columns={'country': 'Country','transport_classification_code':'Transport_Classification_Code'}, inplace=True)
        df = df[['id','Year','Country','Transport_Classification_Code','Unit','Quantity']]
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
