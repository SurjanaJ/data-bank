from os import path

from django.http import HttpResponse
from . import views


def display_tables(request):
    return HttpResponse('success')

urlpatterns = [
    path('',views.display_tables,name='display_tables'),
]
