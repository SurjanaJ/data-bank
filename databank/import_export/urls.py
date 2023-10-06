from django.urls import path

from . import views


urlpatterns = [
    path('',views.display_table, name='display_table'),
    path('upload/', views.upload_trade_excel, name='upload_trade_excel' ),
    path('upload_trade_record/', views.upload_trade_record, name='upload_trade_record'),
    path('update_trade_record/<int:pk>/', views.update_trade_record, name = 'update_trade_record'),
    path('delete_trade_record/<int:pk>/', views.delete_trade_record, name='delete_trade_record')
]