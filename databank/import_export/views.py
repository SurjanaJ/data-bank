from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def display_table(request):
    return render(request, 'import_export/display_table.html')