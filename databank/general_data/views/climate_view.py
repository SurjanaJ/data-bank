from django.db import IntegrityError
from ..forms import UploadClimatePlaceMeta
from ..models import Climate_Place_Meta
from trade_data.models import Country_meta

from trade_data import views
from io import BytesIO
from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from trade_data.views import is_valid_queryparam, tables
from django.http import HttpResponse
from django.db.models import F, Q

def upload_climate_place_meta_excel(request):
    errors = []
    duplicate_data = []
    added_count = 0
    updated_count = 0

    if request.method == 'POST':
        form = UploadClimatePlaceMeta(request.POST, request.FILES)

        if form.is_valid():
            excel_data = request.FILES['meta_file']
            df = pd.read_excel(excel_data, dtype={'Place_Code':str})
            df.fillna('', inplace= True)


            for index, row in df.iterrows():
                place_data = {
                    'Country': row['Country'],
                    'Place_Code': row['Place_Code'],
                    'Place_Name': row['Place_Name']
                }
                
                try:
                    Country = Country_meta.objects.get(Country_Name = row['Country'])

                    place_data = {
                        'Country': Country,
                        'Place_Code': row['Place_Code'],
                        'Place_Name': row['Place_Name']
                    }
                    
                except Exception as e:
                    errors.append({'row_index': index, 'data': place_data, 'reason': str(e)})
                    continue

                existing_record = Climate_Place_Meta.objects.filter(
                        Q(Country=Country) & Q(Place_Code=row['Place_Code']) 
                        ).first()
                
                if existing_record:
                    existing_dict = model_to_dict(existing_record)
                    place_data_dict = model_to_dict(Climate_Place_Meta(**place_data))

                    if all(existing_dict[key] == place_data_dict[key] or (pd.isna(existing_dict[key]) and pd.isna(place_data_dict[key])) for key in place_data_dict if key != 'id'):
                        place_data = {
                            'Country': Country.Country_Name,
                            'Place_Code': row['Place_Code'],
                            'Place_Name': row['Place_Name']
                        }

                        duplicate_data.append({
                             'row_index': index,
                                'data': {key: str(value) for key, value in place_data.items()}
                        })

                    else:
                        for key, value in place_data.items():
                                setattr(existing_record, key, value)
                        try:
                            existing_record.save()
                            updated_count += 1
                        except IntegrityError as e:
                                errors.append(f"Error updating row {index}: {e}")
                
                else:
                    try:
                        placeData = Climate_Place_Meta(**place_data)
                        placeData.save()
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
        form = UploadClimatePlaceMeta()

    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})


def display_climate_place_meta(request):
    data = Climate_Place_Meta.objects.all()
    total_data = data.count()
    
    column_names = Climate_Place_Meta._meta.fields

    context = {'data':data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}

    return render(request, 'general_data/display_meta.html', context)