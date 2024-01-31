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

from ..models import Currency_Meta
from ..forms import UploadCurrencyForm

def strip_spaces(value):
    return value.lstrip()

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
            df = df.applymap(strip_spaces)

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


