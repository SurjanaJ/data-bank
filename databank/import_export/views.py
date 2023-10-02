from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def importExcel(request):
    return HttpResponse('choose file page')