from datetime import date
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

from ..models import Currency_Meta, Exchange
from ..forms import UploadCurrencyForm, UploadExchangeForm

def strip_spaces(value):
    if isinstance(value, str):
        return value.strip()
    return value

def display_currency_meta(request):
    data = Currency_Meta.objects.all()
    total_data = data.count()

    column_names = Currency_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)

def upload_currency_meta_excel(request):
    errors = []
    duplicate_data = []
    added_count = 0
    updated_count = 0

    if request.method == 'POST':
        form = UploadCurrencyForm(request.POST, request.FILES)

        if form.is_valid():
            excel_data = request.FILES['meta_file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace= True)
            df = df.map(strip_spaces)

            for index, row in df.iterrows():
                currency_data = {
                    'Country': row['Country'],
                    'Currency_Code': row['Currency_Code'],
                    'Currency_Name': row['Currency_Name']
                }

                try:
                    Country = Country_meta.objects.get(Country_Name = row['Country'])

                    currency_data = {
                        'Country': Country,
                        'Currency_Code': row['Currency_Code'],
                        'Currency_Name': row['Currency_Name']
                    }

                except Exception as e:
                    errors.append({'row_index': index, 'data': currency_data, 'reason': str(e)})
                    continue

                existing_record = Currency_Meta.objects.filter(
                        Q(Country=Country)).first()
                
                if existing_record:
                    existing_dict = model_to_dict(existing_record)
                    currency_data_dict = model_to_dict(Currency_Meta(**currency_data))

                    if all(existing_dict[key] == currency_data_dict[key] or (pd.isna(existing_dict[key]) and pd.isna(currency_data_dict[key])) for key in currency_data_dict if key != 'id'):
                        currency_data = {
                            'Country': Country.Country_Name,
                            'Currency_Code': row['Currency_Code'],
                            'Currency_Name': row['Currency_Name']
                        }

                        duplicate_data.append({
                             'row_index': index,
                                'data': {key: str(value) for key, value in currency_data.items()}
                        })

                    else:
                        for key, value in currency_data.items():
                                setattr(existing_record, key, value)
                        try:
                            existing_record.save()
                            updated_count += 1
                        except IntegrityError as e:
                                errors.append(f"Error updating row {index}: {e}")

                else:
                    try:
                        currencyData = Currency_Meta(**currency_data)
                        currencyData.save()
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
                return redirect('place_meta')
    else:
        form = UploadCurrencyForm()

    return render(request, 'general_data/transport_templates/upload_transport_form.html', {'form':form})


def upload_exchange_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadExchangeForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

            # update the data
            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    try:
                        # find instance 
                        exchange_instance = Exchange.objects.get(id = id)
                        exchange_data = {
                            'Country': row['Country'],
                            'Selling' : row['Selling Against USD'],
                            'Buying' : row ['Buying Against USD'],
                            'Currency' : row['Currency'],
                        }
                        # check if all the meta datas exist
                        try:
                            Country  = Country_meta.objects.get(Country_Name = row['Country'])
                            Currency = Currency_Meta.objects.get(Currency_Name = row['Currency'] )

                            # Updating the values
                            exchange_instance.Country = Country
                            exchange_instance.Selling = row['Selling Against USD']
                            exchange_instance.Buying = row['Buying Against USD']
                            exchange_instance.Currency = Currency

                            exchange_instance.save()
                            updated_count +=1
                        
                        # error : meta data does not exist
                        except Exception as e:
                            exchange_data = {
                            'Country': row['Country'],
                            'Selling' : row['Selling Against USD'],
                            'Buying' : row ['Buying Against USD'],
                            'Currency' : row['Currency'],
                        }
                            errors.append({'row_index': index, 'data': exchange_data, 'reason': str(e)})
                            continue
                    
                    # instance does not exist
                    except Exception as e:
                        exchange_data = {
                            'Country': row['Country'],
                            'Selling' : row['Selling Against USD'],
                            'Buying' : row ['Buying Against USD'],
                            'Currency' : row['Currency'],
                        }

                        errors.append({
                                    'row_index': index,
                                    'data': exchange_data,
                                    'reason': f'Error inserting row {index}: {e}'
                                })
                        continue
            # Add new data
            else:
                for index, row in df.iterrows():
                    # Find if the meta data exists
                    try:
                        Country  = Country_meta.objects.get(Country_Name = row['Country'])
                        Currency = Currency_Meta.objects.get(Currency_Name = row['Currency'] )

                        exchange_data = {
                            'Country': Country,
                            'Selling' : row['Selling Against USD'],
                            'Buying' : row ['Buying Against USD'],
                            'Currency' : Currency,
                        }

                        if Country.id != Currency.Country.id:
                            exchange_data = {
                                'Country': row['Country'],
                                'Selling Against USD' : row['Selling Against USD'],
                                'Buying Against USD' : row ['Buying Against USD'],
                                'Currency' : row['Currency'],
                    }
                            raise ValueError(f"Country value and Currency Value Mismatch")


                        existing_record = Exchange.objects.filter(
                            Q(Country = Country)
                            & Q(Selling = row['Selling Against USD'])
                            & Q(Buying = row['Buying Against USD'])
                            & Q(Currency = Currency)
                            ).first()
                        
                        if existing_record:
                            exchange_data = {
                                'Country': row['Country'],
                                'Selling Against USD' : row['Selling Against USD'],
                                'Buying Against USD' : row ['Buying Against USD'],
                                'Currency' : row['Currency'],
                            }       
                            duplicate_data.append({
                                'row_index': index,
                                'data': {key: str(value) for key, value in exchange_data.items()}
                            })
                        else:
                            try:
                                exchangeData = Exchange(**exchange_data)
                                exchangeData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}:{e}")
                    
                    # Meta data doesnt exist
                    except Exception as e:
                        exchange_data = {
                                'Country': row['Country'],
                                'Selling Against USD' : row['Selling Against USD'],
                                'Buying Against USD' : row ['Buying Against USD'],
                                'Currency' : row['Currency'],
                            }  

                        errors.append({'row_index': index, 'data': exchange_data, 'reason': str(e)})
                        continue
            

        if added_count > 0:
            messages.success(request, str(added_count) + ' records added.')
            
        if updated_count > 0:
            messages.info(request, str(updated_count) + ' records updated.')

        if errors:
            request.session['errors'] = errors
            return render(request, 'trade_data/error_template.html', {'errors': errors, 'tables':tables, 'meta_tables':views.meta_tables,})
            
        elif duplicate_data:
            request.session['duplicate_data'] = duplicate_data
            return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data, 'tables':tables, 'meta_tables':views.meta_tables,})
                
        else:
            return redirect('exchange_table') 

    else:
        form = UploadExchangeForm()

    return render(request, 'general_data/transport_templates/upload_transport_form.html',{'form': form, 'meta_tables':views.meta_tables, 'tables':tables,})


def display_exchange_table(request):
    data = Exchange.objects.all()

    country_categories = Country_meta.objects.all()

    country = request.GET.get('country')
    min_buying_amt = request.GET.get('min_buying_amt')
    max_buying_amt = request.GET.get('max_buying_amt')
    min_selling_amt = request.GET.get('min_selling_amt')
    max_selling_amt = request.GET.get('max_selling_amt')

    if is_valid_queryparam(country) and country != '--':
        data = data.filter(Country_id=country)

    if is_valid_queryparam(max_buying_amt):
        data = data.filter(Buying__lt=max_buying_amt)

    if is_valid_queryparam(min_buying_amt):
        data = data.filter(Buying__gte=min_buying_amt)
    
    if is_valid_queryparam(max_selling_amt):
        data = data.filter(Selling__lt=max_selling_amt)
        
    if is_valid_queryparam(min_selling_amt):
        data = data.filter(Selling__gte=min_selling_amt)

    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context ={'data_len':len(data),
              'page':page, 
              'query_len':len(page), 
              'tables': tables,
              'country_categories':country_categories, 
              'meta_tables':views.meta_tables, 
              'tables':tables,
                      }
    return render(request, 'general_data/exchange_templates/exchange_table.html', context)


def export_exchange_excel(request):
    country = request.GET.get('country')
    min_buying_amt = request.GET.get('min_buying_amt')
    max_buying_amt = request.GET.get('max_buying_amt')
    min_selling_amt = request.GET.get('min_selling_amt')
    max_selling_amt = request.GET.get('max_selling_amt')

    filter_conditions = {}
    if is_valid_queryparam(country) and country != '--':
        filter_conditions['Country']= country

    if is_valid_queryparam(max_buying_amt):
        filter_conditions['Buying__lt'] =max_buying_amt

    if is_valid_queryparam(min_buying_amt):
        filter_conditions['Buying__gte'] =min_buying_amt

    if is_valid_queryparam(max_selling_amt):
        filter_conditions['Selling__lt'] =max_selling_amt
        
    if is_valid_queryparam(min_selling_amt):
        filter_conditions['Selling__gte'] =min_selling_amt

    queryset = Exchange.objects.filter(**filter_conditions)
    queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        currency = F('Currency__Currency_Name'),
    )

    data = pd.DataFrame(list(queryset.values('country','currency', 'Selling','Buying')))
    data.rename(columns={'country':'Country','currency': 'Currency','Selling': 'Selling Against USD', 'Buying': 'Buying Against USD'}, inplace=True)
    column_order = ['Country', 'Currency','Selling Against USD', 'Buying Against USD']

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

def update_selected_exchange(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('exchange_table')
    else:
        queryset = Exchange.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        currency = F('Currency__Currency_Name'),
    )
        
        data = pd.DataFrame(list(queryset.values('id','country','currency','Buying','Selling')))

        data.rename(columns={
                         'country':'Country',
                         'currency': 'Currency',
                         'Buying':'Buying Against USD',
                         'Selling':'Selling Against USD',
                         }, inplace=True)

        column_order = ['id','Country','Currency','Selling Against USD','Buying Against USD']
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