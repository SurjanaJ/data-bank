from django.http import JsonResponse
from django.db.models import Sum
from django.shortcuts import render

from trade_data.models import Country_meta
from trade_data.views import find_country_name, is_valid_queryparam

from .. import models



def analysis_forest(request):
    data = models.ForestData.objects.values('Year', 'Country__Country_Name').annotate(total_area=Sum('Area_Covered'))
   
    country_categories = Country_meta.objects.all()

    selected_country = request.GET.get('country')

    if is_valid_queryparam(selected_country) and selected_country != '--':
        data = data.filter(Country_id=selected_country)

    # Reorganizing the data to have years as column headers and countries as the first column
    years = sorted(set(item['Year'] for item in data))
    countries = sorted(set(item['Country__Country_Name'] for item in data))
    reorganized_data = {}
    for country in countries:
        reorganized_data[country] = {year: 0 for year in years}
    for item in data:
        reorganized_data[item['Country__Country_Name']][item['Year']] = item['total_area']

    # Calculate total area for each year irrespective of country
    # total_area_per_year = {year: sum(reorganized_data[country][year] for country in countries) for year in years}
    total_area_per_year = {year: sum(item['total_area'] for item in data if item['Year'] == year) for year in years}
    # total_area_per_year = {item['Year']: item['total_area'] for item in data}


    # Building the context to pass to the template
    context = {
        'reorganized_data': reorganized_data,
        'total_area_per_year':total_area_per_year,
        'queryset_length':len(data),
        'years': years,
        'country_categories': country_categories,
        'selected_country': find_country_name(selected_country)
    }

    return render(request, 'general_data/analysis_templates/forest_analysis.html', context)
