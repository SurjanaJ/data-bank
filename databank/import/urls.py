from django.urls import include, path
from . import views
urlpatterns = [
<<<<<<< HEAD
    path('', views.display_trade_table, name='display_trade_table'),
    path('upload_country_meta_excel/', views.upload_country_meta_excel, name='upload_country_meta_excel'),
    path('upload_unit_meta_excel/', views.upload_unit_meta_excel, name='upload_unit_meta_excel'),
    path('upload_hs_code_meta_excel/', views.upload_hs_code_meta_excel, name='upload_hs_code_meta_excel'),
    path('upload_trade_excel/', views.upload_trade_excel, name='upload_trade_excel')

=======
    path('', views.display_trade_table, name='display_trade_table')
>>>>>>> parent of 914e7c6 (create upload links for country meta and unit meta)
]
