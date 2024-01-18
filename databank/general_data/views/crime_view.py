from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages


from trade_data.models import Country_meta
from ..forms import UploadCrimeForm
from trade_data import views
from ..models import Crime, Crime_Meta
from trade_data.views import is_valid_queryparam, tables
from django.db.models import Q


def display_crime_meta(request):
    data = Crime_Meta.objects.all()
    total_data = data.count()

    column_names = Crime_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)


def upload_crime_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadCrimeForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df['Year'] = pd.to_datetime(df['Year']).dt.date

            for index, row in df.iterrows():
                try: 
                    Year = row['Year']
                    Country = Country_meta.objects.get(Country_Name = row['Country'])
                    Code = Crime_Meta.objects.get(Code = row['Code'])
                    gender = row['Gender']

                    if gender not in ['Male', 'Female']:
                        raise ValueError(
                            f"Invalid Direction at row {index} : {gender}"
                        )
                    crime_data = {
                        'Country':Country,
                        'Year':Year,
                        'Offence_Code':Code,
                        'Gender': row['Gender'],
                        'Age': row['Age'],
                        'District': row['District']
                    }

                except Exception as e:
                    crime_data['Year']=Year.isoformat()
                    errors.append({'row_index': index, 'data': crime_data, 'reason': str(e)})
                    continue
                
                try:
                    crimeData = Crime(**crime_data)
                    crimeData.save()
                    added_count +=1
                        
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
                return redirect('crime_table')  
            
    else:
        form = UploadCrimeForm()

    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})
