from io import BytesIO
from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from trade_data.views import is_valid_queryparam, tables
from django.http import HttpResponse
from django.db.models import F
from trade_data import views


from ..models import Occupation_Meta


def display_occupation_meta(request):
    data = Occupation_Meta.objects.all()
    total_data = data.count()

    column_names = Occupation_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)
