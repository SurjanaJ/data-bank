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

from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users

from ..models import Publication
from ..forms import UploadPublicationForm

@login_required(login_url = 'login')
def display_publication_table(request):
    data = Publication.objects.all()
    country_categories = Country_meta.objects.all()

    country = request.GET.get('country')
    year_min = request.GET.get('year_min')
    year_max = request.GET.get('year_max')

    if is_valid_queryparam(year_min):
        data = data.filter(Year__gte=year_min)

    if is_valid_queryparam(year_max):
        data = data.filter(Year__lt=year_max)  

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
    return render(request, 'general_data/publication_templates/publication_table.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_publication_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadPublicationForm(request.POST, request.FILES)

        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

            # Check if required columns exist
            required_columns = ['Year', 'Country', 'Book Name','Writer Name']  # Add your required column names here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing columns: {', '.join(missing_columns)}")
                return render(request,'general_data/invalid_upload.html', {'missing_columns': missing_columns, 'tables': tables, 'meta_tables': views.meta_tables,} )
            
            # Update existing data
            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Book Name': row['Book Name'],
                        'Writer Name':row['Writer Name'],
                    }

                    #get the existing instance
                    try:
                        publication_instance = Publication.objects.get(id = id)
                        publication_data = data

                        #check if all the meta values exist
                        try:
                            Country = Country_meta.objects.get(Country_Name = row['Country'])

                            publication_instance.Year = row['Year']
                            publication_instance.Country = Country
                            publication_instance.Book_Name = row['Book Name']
                            publication_instance.Writer_Name = row['Writer Name']

                            publication_instance.save()
                            updated_count += 1

                        #meta value does not exist
                        except Exception as e:
                            publication_data= data
                            errors.append({'row_index': index, 'data': publication_data, 'reason': str(e)})
                            continue


                    #instance does not exist
                    except Exception as e:
                        publication_data = data
                        errors.append({
                                        'row_index': index,
                                        'data': publication_data,
                                        'reason': f'Error inserting row {index}: {e}'
                                    })
                        continue

            
            else:
            # Add new data
                for index, row in df.iterrows():
                    data = {
                        'Year': row['Year'],
                        'Country': row['Country'],
                        'Book Name': row['Book Name'],
                        'Writer Name':row['Writer Name'],
                    }

                    #check if the meta values exist
                    try:
                        Country = Country_meta.objects.get(Country_Name = row['Country'])
                        publication_data = {
                        'Year': row['Year'],
                        'Country': Country,
                        'Book_Name': row['Book Name'],
                        'Writer_Name':row['Writer Name'],
                    }
                        
                        existing_record = Publication.objects.filter(
                            Q(Country = Country)
                            & Q(Year = row['Year'])
                            & Q(Book_Name = row['Book Name'])
                            & Q(Writer_Name = row['Writer Name'])
                        ).first()

                        # show duplicate data
                        if existing_record:
                            publication_data = data
                            duplicate_data.append({
                                'row_index': index,
                                    'data': {key: str(value) for key, value in publication_data.items()}
                            })
                            continue
                        else:
                            #add new record
                            try:
                                publicationData = Publication(**publication_data)
                                publicationData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")
                    

                    #meta value does not exists    
                    except Exception as e:
                        publication_data = data
                        errors.append({'row_index': index, 'data': publication_data, 'reason': str(e)})
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
           # form is not valid
            return redirect('publication_table') 

    else:
        form = UploadPublicationForm()   
    
    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form, 'tables': tables, 'meta_tables': views.meta_tables,})

@login_required(login_url = 'login')
def export_publication_excel(request):
    country = request.GET.get('country')

    filter_conditions = {}
    if is_valid_queryparam(country) and country != '--':
        filter_conditions['Country'] = country

    queryset = Publication.objects.filter(**filter_conditions)
    queryset = queryset.annotate(
        country = F('Country__Country_Name'),
    )

    data = pd.DataFrame(list(queryset.values('Year','country','Book_Name','Writer_Name')))

    data.rename(columns = {
        'country':'Country',
        'Book_Name':'Book Name',
        'Writer_Name':'Writer Name'
    }, inplace=True)

    column_order = ['Year','Country','Book Name','Writer Name']

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

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def update_selected_publication(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('publication_table')
    else:
        queryset = Publication.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'))

        data = pd.DataFrame(list(queryset.values('id','Year','country','Book_Name','Writer_Name')))

        data.rename(columns = {
            'country':'Country',
            'Book_Name':'Book Name',
            'Writer_Name':'Writer Name'
        }, inplace=True)

        column_order = ['id','Year','Country','Book Name','Writer Name']

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
