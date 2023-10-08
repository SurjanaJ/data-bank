from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def display_tables(request):
    return HttpResponse( 'success')