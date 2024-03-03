from io import BytesIO
from django.db import IntegrityError
from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator

from ..forms import UploadProductionForm
from ..models import Production_Meta, Production
from .energy_view import strip_spaces
from trade_data.views import is_valid_queryparam, tables
from django.http import HttpResponse
from django.db.models import F, Q
from trade_data import views

def display_production_meta(request):
    data = Production_Meta.objects.all()
    total_data = data.count()

    column_names = Production_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)

def display_production_table(request):
    data = Production.objects.all()

    production_categories = Production_Meta.objects.all()

    code = request.GET.get('code')
    if is_valid_queryparam(code) and code != '--':
        data = data.filter(Code_id=code)

    
    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context ={'data_len':len(data),
              'page':page, 
              'query_len':len(page), 
              'tables': tables, 
              'meta_tables': views.meta_tables,
              'production_categories':production_categories,
                      }
    return render(request, 'general_data/production_templates/production_table.html', context)


def upload_production_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadProductionForm(request.POST, request.FILES)

        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data, dtype={'Code': str})
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

            #Update existing data
            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    data = {
                        'Code': row['Code'],
                        'Description':row['Description'],
                        'Producer Name': row['Producer Name'],
                        'Province': row['Province'],
                        'District':row['District'],
                    }

                    #get existing data
                    try:
                        production_instance = Production.objects.get(id = id)
                        production_data = data

                        #check if meta values exist
                        try:
                            Code = Production_Meta.objects.get(Code = row['Code'])

                            production_instance.Code = Code
                            production_instance.Producer_Name = row['Producer Name']
                            production_instance.Province = row['Province']
                            production_instance.District = row['District']

                            production_instance.save()
                            updated_count += 1

                        #meta does not exist
                        except Exception as e:
                            production_data = data
                            errors.append({'row_index': index, 'data': production_data, 'reason': str(e)})
                            continue

                    #instance does not exist
                    except Exception as e:
                        production_data = data
                        errors.append({
                                        'row_index': index,
                                        'data': production_data,
                                        'reason': f'Error inserting row {index}: {e}'
                                    })
                        continue
                    
            else:
            #add new data
                for index, row in df.iterrows():
                    data = {
                        'Code': row['Code'],
                        'Description':row['Description'],
                        'Producer Name': row['Producer Name'],
                        'Province': row['Province'],
                        'District':row['District'],
                    }

                    #check if the meta values exist
                    try:
                        Code = Production_Meta.objects.get(Code = row['Code'])
                        production_data = {
                            'Code': Code,
                            'Producer_Name': row['Producer Name'],
                            'Province': row['Province'],
                            'District':row['District'],
                        }

                        existing_record = Production.objects.filter(
                            Q(Code = Code)
                            & Q(Producer_Name = row['Producer Name'])
                            & Q(Province = row['Province'])
                            & Q(District = row['District'])
                        ).first()

                        # show duplicate data
                        if existing_record:
                            production_data = data
                            duplicate_data.append({
                                'row_index': index,
                                    'data': {key: str(value) for key, value in production_data.items()}
                            })
                            continue
                        else:
                            #add new record
                            try:
                                productionData = Production(**production_data)
                                productionData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")
                    
                    except Exception as e:
                        production_data = data
                        errors.append({'row_index': index, 'data': production_data, 'reason': str(e)})
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
            return redirect('production_table') 

    else:
        form = UploadProductionForm()   
    
    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form, 'tables': tables, 'meta_tables': views.meta_tables,})


def export_production_excel(request):
    code = request.GET.get('code')

    filter_conditions = {}
    if is_valid_queryparam(code) and code != '--':
        filter_conditions['Code'] = code

    queryset = Production.objects.filter(**filter_conditions)
    queryset = queryset.annotate(
        code = F('Code__Code'),
        description = F('Code__Description'),
    )

    data = pd.DataFrame(list(queryset.values('code','description','Producer_Name','Province','District')))
    data.rename(columns={
                         'code': 'Code',
                         'description':'Description',
                         'Producer_Name':'Producer Name',
                         }, inplace=True)
    
    column_order = ['Code','Description','Producer Name', 'Province','District']

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