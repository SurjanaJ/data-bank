from django.urls import path

from . import views


urlpatterns = [
    path('display/',views.display_table, name='display_table'),
    
    path('', views.upload_trade_excel, name='upload_trade_excel' )
]