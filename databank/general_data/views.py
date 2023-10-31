from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def display_forest_table(request):
    return HttpResponse('Forest Table')