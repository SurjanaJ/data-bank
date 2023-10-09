from django.urls import include, path
from . import views
urlpatterns = [
    path('', views.display_trade_table, name='display_trade_table'),
    path('upload_country_meta_excel/', views.upload_country_meta_excel, name='upload_country_meta_excel'),
    path('upload_unit_meta_excel/', views.upload_unit_meta_excel, name='upload_unit_meta_excel')
]
