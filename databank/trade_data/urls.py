from django.urls import include, path
from . import views
from . import export_views
urlpatterns = [
    path('', views.display_trade_table, name='display_trade_table'),
    path('upload_country_meta_excel', views.upload_country_meta_excel, name='upload_country_meta_excel'),
    path('upload_unit_meta_excel', views.upload_unit_meta_excel, name='upload_unit_meta_excel'),
    path('upload_hs_code_meta_excel',views.upload_hs_code_meta_excel, name='upload_hs_code_meta_excel'),
    path('upload_trade_excel', views.upload_trade_excel, name='upload_trade_excel'),
    path('time_series_analysis', views.time_series_analysis, name='time_series_analysis'),
    path('export_to_excel', export_views.export_to_excel, name='export_to_excel'),
    path('trade_record_to_excel', export_views.trade_record_to_excel, name='trade_record_to_excel'),
    path('delete_selected_trade', views.delete_selected_trade, name='delete_selected_trade'),
    path('upload_trade_record',views.upload_trade_record, name='upload_trade_record'),
    path('delete_trade_record/<int:pk>/', views.delete_trade_record ,name='delete_trade_trade'),
    path('update_trade_record/<int:pk>/',views.update_trade_record, name='update_trade_record'),


]
