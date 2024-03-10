from django.db import IntegrityError
from ..forms import UploadEducationForm
from ..models import Education, Education_Degree_Meta, Education_Level_Meta

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

from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users

@login_required(login_url = 'login')
def display_education_level_meta(request):
    data = Education_Level_Meta.objects.all()
    total_data = data.count()

    column_names = Education_Level_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)

@login_required(login_url = 'login')
def display_education_degree_meta(request):
    data = Education_Degree_Meta.objects.all()
    total_data = data.count()

    column_names = Education_Degree_Meta._meta.fields
    
    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}

    return render(request, 'general_data/display_meta.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_education_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadEducationForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data, dtype={'Level_Code': str, 'Degree_Code':str})
            cols = df.columns.tolist()
            df.fillna('', inplace= True)

            for index,row in df.iterrows():
                education_data = {col: row[col] for col in cols}
                try:
                    Level_Code = Education_Level_Meta.objects.get(Code = row['Level_Code'])
                    Degree_Code = Education_Degree_Meta.objects.get(Code = row['Degree_Code'])

                    education_data = {
                        'Level_Code':Level_Code,
                        'Degree_Code': Degree_Code,
                        'Male':row['Male'],
                        'Female': row['Female']
                    }
                except Exception as e:
                    errors.append({'row_index': index, 'data': education_data, 'reason': str(e)})
                    continue

                existing_record = Education.objects.filter(
                    Q(Level_Code = Level_Code) & Q(Degree_Code = Degree_Code)).first()
                
                if existing_record:
                    existing_dict = model_to_dict(existing_record)
                    education_data_dict = model_to_dict(Education(**education_data))

                    if all(existing_dict[key] == education_data_dict[key] or (pd.isna(existing_dict[key]) and pd.isna(education_data_dict[key])) for key in education_data_dict if key != 'id'):
                        education_data = {
                            'Level_Code':Level_Code,
                            'Degree_Code': Degree_Code,
                            'Male':row['Male'],
                            'Female': row['Female']
                        }

                        duplicate_data.append({
                             'row_index': index,
                                'data': {key: str(value) for key, value in education_data.items()}
                        })
                
                    else:
                        for key, value in education_data.items():
                                setattr(existing_record, key, value)
                        try:
                            existing_record.save()
                            updated_count += 1
                        except IntegrityError as e:
                                errors.append(f"Error updating row {index}: {e}")

                else:
                    try:
                        educationData = Education(**education_data)
                        educationData.save()
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
                return redirect('education_table')
    else:
        form = UploadEducationForm()

    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})

@login_required(login_url = 'login')
def display_education_table(request):
    data = Education.objects.all()

    level_categories = Education_Level_Meta.objects.all()
    degree_categories = Education_Degree_Meta.objects.all()

    education_level = request.GET.get('education_level')
    education_degree = request.GET.get('education_degree')

    if is_valid_queryparam(education_level) and education_level != '--':
        data = data.filter(Level_Code_id = education_level)

    if is_valid_queryparam(education_degree) and education_degree != '--':
        data = data.filter(Degree_Code_id = education_degree)
    
    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context ={'data_len':len(data),'level_categories':level_categories, 'degree_categories':degree_categories, 'page':page, 'query_len':len(page), 'tables': tables, 'meta_tables': views.meta_tables}
    return render(request, 'general_data/education_templates/education_table.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def export_education_excel(request):
    education_level = request.GET.get('education_level')
    education_degree = request.GET.get('education_degree')

    filter_conditions = {}
    if is_valid_queryparam(education_level) and education_level != '--':
        filter_conditions['Level_Code']=education_level

    if is_valid_queryparam(education_degree) and education_degree != '--':
        filter_conditions['Degree_Code']=education_degree

    queryset = Education.objects.filter(**filter_conditions)
    queryset = queryset.annotate(
        education_level = F('Level_Code__Code'),
        level_name = F('Level_Code__Level'),
        education_degree = F('Degree_Code__Code'),
        degree_name = F('Degree_Code__Degree'),
    )

    data = pd.DataFrame(list(queryset.values('education_level','level_name', 'education_degree','degree_name','Male', 'Female')))

    data.rename(columns={'education_degree':'Degree Code','education_level': 'Level Code', 'level_name':'Level Code Name', 'degree_name':'Degree Code Name'}, inplace=True)

    column_order = ['Level Code', 'Level Code Name', 'Degree Code', 'Degree Code Name', 'Male', 'Female']

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