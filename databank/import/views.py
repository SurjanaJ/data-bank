from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadCountryMetaForm, UploadUnitMetaForm
import pandas as pd
from .models import Country_meta, Unit_meta

def display_trade_table(request):
    return render(request,'import/display_trade_table.html')

def upload_country_meta_excel(request):
    if request.method =='POST':
        form = UploadCountryMetaForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['country_meta_file']
            df = pd.read_excel(excel_data)

            for index,row in df.iterrows():
                country_meta = Country_meta(
                    Country_Name = row['Country_Name'],
                    Country_Code_2 = row['Country_Code_2'],
                    Country_Code_3 =row['Country_Code_3']
                )

                country_meta.save()

            return HttpResponse('success')
    else:
        form = UploadCountryMetaForm()
    return render(request, 'import/upload_form.html', {'form':form})


def upload_unit_meta_excel(request):
    if request.method =='POST':
        form = UploadUnitMetaForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['unit_meta_file']
            df = pd.read_excel(excel_data)

            for index,row in df.iterrows():
                unit_meta = Unit_meta(
                    Unit_Code = row['Unit_Code'],
                    Unit_Name = row['Unit_Name']
                )

                unit_meta.save()

            return HttpResponse('success')
    else:
        form = UploadUnitMetaForm()
    return render(request, 'import/upload_form.html', {'form':form})
