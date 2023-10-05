from django.urls import path

from . import views


urlpatterns = [
    path('',views.display_table, name='display_table'),
    path('upload/', views.upload_trade_excel, name='upload_trade_excel' ),
]