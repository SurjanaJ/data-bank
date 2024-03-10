from io import BytesIO
from django.db import IntegrityError
from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator

from general_data.forms import UploadBudgetForm
from .energy_view import strip_spaces
from trade_data.models import Country_meta, Unit_meta
from trade_data.views import is_valid_queryparam, tables
from django.http import HttpResponse
from django.db.models import F, Q
from trade_data import views


from ..models import Budgetary_Data

def display_budget_table(request):
    data = Budgetary_Data.objects.all()
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
    return render(request, 'general_data/budget_templates/budget_table.html', context)

def upload_budget_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    # if request.method == 'POST':
    if request.method == 'POST':
        form = UploadBudgetForm(request.POST, request.FILES) 

        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

                # Update existing data
            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    data = {
                        'Fiscal Year': row['Fiscal Year'],
                        'Country': row['Country'],
                        'Amount In USD': row['Amount In USD'],
                        'Prefered Denomination': row['Prefered Denomination']
                        }

                    #get the existing instance
                    try:
                        budget_instance = Budgetary_Data.objects.get(id= id)
                        budget_data = data

                        #check if the meta values exist
                        try:
                            Country = Country_meta.objects.get(Country_Name = row['Country'])
                                
                            budget_instance.Country = Country
                            budget_instance.Fiscal_Year = row['Fiscal Year']
                            budget_instance.Amount_In_USD = row['Amount In USD']
                            budget_instance.Prefered_Denomination = row['Prefered Denomination']

                            budget_instance.save()
                            updated_count += 1

                        except Exception as e:
                            #meta does not exist
                            budget_data = data
                            errors.append({'row_index': index, 'data': budget_data, 'reason': str(e)})
                            continue

                    except Exception as e:
                            # instance does not exist
                            budget_data = data
                            errors.append({
                                        'row_index': index,
                                        'data': budget_data,
                                        'reason': f'Error inserting row {index}: {e}'
                                    })
                            continue


            else:
                    #Add new data
                for index, row in df.iterrows():
                    data = {
                            'Fiscal Year': row['Fiscal Year'],
                            'Country': row['Country'],
                            'Amount In USD': row['Amount In USD'],
                            'Prefered Denomination': row['Prefered Denomination']
                        }
                    print('excel data: ', data)

                        #check if meta values exist
                    try:
                        Country = Country_meta.objects.get(Country_Name = row['Country'])
                        budget_data = {
                            'Fiscal_Year': row['Fiscal Year'],
                            'Country': Country,
                            'Amount_In_USD': row['Amount In USD'],
                            'Prefered_Denomination': row['Prefered Denomination']
                        }
                        print('budget_data: ', budget_data)

                        existing_record = Budgetary_Data.objects.filter(
                            Q(Country = Country)
                            & Q(Fiscal_Year = row['Fiscal Year'])
                            & Q(Amount_In_USD = row['Amount In USD'])
                            & Q(Prefered_Denomination = row['Prefered Denomination'])
                            ).first()

                            #show duplicate data
                        if existing_record:
                            budget_data = data
                            duplicate_data.append({
                                    'row_index': index,
                                    'data': {key: str(value) for key, value in budget_data.items()}
                                })
                            continue

                        else:
                                # add new record
                            try:
                                budgetData = Budgetary_Data(**budget_data)
                                print('budgetData: ', budgetData)
                                budgetData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")


                    except Exception as e:
                        #meta values don't exist
                        budget_data = data
                        errors.append({'row_index': index, 'data': budget_data, 'reason': str(e)})
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
            return redirect('budget_table')                        

    else:
        form = UploadBudgetForm()
    return render(request, 'general_data/transport_templates/upload_transport_form.html', {'form':form, 'tables': tables, 'meta_tables': views.meta_tables,})

def export_budget_excel(request):
    country = request.GET.get('country')
    filter_conditions = {}
    if is_valid_queryparam(country) and country != '--':
        filter_conditions['Country'] = country

    queryset = Budgetary_Data.objects.filter(**filter_conditions)
    queryset = queryset.annotate(
        country = F('Country__Country_Name'),
    )

    data = pd.DataFrame(list(queryset.values('Fiscal_Year','country','Amount_In_USD','Prefered_Denomination')))

    data.rename(columns = {
        'country':'Country',
        'Fiscal_Year':'Fiscal Year',
        'Amount_In_USD':'Amount In USD',
        'Prefered_Denomination':'Prefered Denomination'
    }, inplace=True)

    column_order = ['Country','Fiscal Year','Amount In USD','Prefered Denomination']
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

def update_selected_budget(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('budget_table')
    else:
        queryset = Budgetary_Data.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'))

        data = pd.DataFrame(list(queryset.values('id','Fiscal_Year','country','Amount_In_USD','Prefered_Denomination')))

        data.rename(columns = {
        'country':'Country',
        'Fiscal_Year':'Fiscal Year',
        'Amount_In_USD':'Amount In USD',
        'Prefered_Denomination':'Prefered Denomination'
    }, inplace=True)

    column_order = ['id','Country','Fiscal Year','Amount In USD','Prefered Denomination']


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
   