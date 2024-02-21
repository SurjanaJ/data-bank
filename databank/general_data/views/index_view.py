from io import BytesIO
from django.db import IntegrityError
from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from .energy_view import strip_spaces
from trade_data.models import Country_meta, Unit_meta
from trade_data.views import is_valid_queryparam, tables
from django.http import HttpResponse
from django.db.models import F, Q
from trade_data import views

from ..forms import UploadIndexForm
from ..models import Index

def upload_index_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadIndexForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

            #Update existing data
            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id') 
                    data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Index_Name': row['Index Name'],
                        'Score':row['Score'],
                        'Rank': row['Rank'],
                        'No_Of_Countries': row['No Of Countries']
                    }
                    #get the existing instance
                    try:
                        index_instance = Index.objects.get(id = id)
                        index_data = data

                        #check if all the meta values exist
                        try:
                            Country = Country_meta.objects.get(Country_Name = row['Country'])

                            index_instance.Year = row['Year']
                            index_instance.Country = Country
                            index_instance.Index_Name = row['Index Name']
                            index_instance.Score = row['Score']
                            index_instance.Rank = row['Rank']
                            index_instance.No_Of_Countries = row['No Of Countries']

                            index_instance.save()
                            updated_count += 1

                        #meta value does not
                        except Exception as e:
                            index_data= data
                            errors.append({'row_index': index, 'data': index_data, 'reason': str(e)})
                            continue

                    #instance does not exist
                    except Exception as e:
                        index_data= data
                        errors.append({
                                        'row_index': index,
                                        'data': index_data,
                                        'reason': f'Error inserting row {index}: {e}'
                                    })
                        continue
            
            #Add new
            else:
                for index, row in df.iterrows():
                    data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Index_Name': row['Index Name'],
                        'Score':row['Score'],
                        'Rank': row['Rank'],
                        'No_Of_Countries': row['No Of Countries']
                    }

                    #check if the meta values exist
                    try:
                        Country = Country_meta.objects.get(Country_Name = row['Country'])
                        index_data = {
                        'Year': row['Year'],
                        'Country': Country,
                        'Index_Name': row['Index Name'],
                        'Score':row['Score'],
                        'Rank': row['Rank'],
                        'No_Of_Countries': row['No Of Countries']
                    }

                        existing_record =Index.objects.filter(
                            Q(Country = Country) 
                            & Q(Year = row['Year']) 
                            & Q(Index_Name = row['Index Name'])
                            & Q(Score = row['Score'])
                            & Q(Rank = row['Rank'])
                            & Q(No_Of_Countries = row['No Of Countries'])
                        ).first()

                        # show duplicate
                        if existing_record:
                            index_data = data
                            duplicate_data.append({
                                'row_index': index,
                                    'data': {key: str(value) for key, value in index_data.items()}
                            })
                            continue
                        
                        # add new record
                        else:
                            try:
                                indexData = Index(**index_data)
                                indexData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")
                    
                    #meta does not exist
                    except Exception as e:
                        index_data = data
                        errors.append({'row_index': index, 'data': index_data, 'reason': str(e)})
                        continue
        
        if added_count > 0:
            messages.success(request, str(added_count) + ' records added.')
            
        if updated_count > 0:
            messages.info(request, str(updated_count) + ' records updated.')

        if errors:
            request.session['errors'] = errors
            return render(request, 'trade_data/error_template.html', {'errors': errors, 'tables': tables, 'meta_tables': views.meta_tables, })
            
        elif duplicate_data:
            request.session['duplicate_data'] = duplicate_data
            return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data, 'tables': tables, 'meta_tables': views.meta_tables,})
            
        else:
            return redirect('index_table')
    
    else:
        form = UploadIndexForm()

    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form, 'tables': tables, 'meta_tables': views.meta_tables,})
    
def display_index_table(request):
    data = Index.objects.all()

    country_categories = Country_meta.objects.all()

    country = request.GET.get('country')

    if is_valid_queryparam(country) and country != '--':
        data = data.filter(Country_id=country)

    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context ={'data_len':len(data),
              'page':page, 
              'query_len':len(page), 
              'tables': tables, 
              'meta_tables': views.meta_tables,
              'country_categories':country_categories,
            }
    return render(request, 'general_data/index_templates/index_table.html', context)

def export_index_excel(request):
    country = request.GET.get('country')

    filter_conditions = {}
    if is_valid_queryparam(country) and country != '--':
        filter_conditions['Country'] = country

    queryset = Index.objects.filter(**filter_conditions)
    queryset = queryset.annotate(
        country = F('Country__Country_Name'),
    )

    data = pd.DataFrame(list(queryset.values('Year','country','Index_Name','Score','Rank','No_Of_Countries')))

    data.rename(columns = {
        'country':'Country',
        'Index_Name':'Index Name',
        'No_Of_Countries':'No Of Countries'
    }, inplace=True)

    column_order = ['Year','Country','Index Name','Score','Rank','No Of Countries']

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