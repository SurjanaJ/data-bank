from ..models import Education_Degree_Meta, Education_Level_Meta

from trade_data import views
from django.shortcuts import render
from trade_data.views import tables



def display_education_level_meta(request):
    data = Education_Level_Meta.objects.all()
    total_data = data.count()

    column_names = Education_Level_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)

def display_education_degree_meta(request):
    data = Education_Degree_Meta.objects.all()
    total_data = data.count()

    column_names = Education_Degree_Meta._meta.fields
    
    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}

    return render(request, 'general_data/display_meta.html', context)

