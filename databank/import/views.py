from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def display_trade_table(request):
    return render(request,'import/display_trade_table.html')

