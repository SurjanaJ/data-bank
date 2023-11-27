from django.urls import include, path
from . import views
from . import export_views

urlpatterns = [
    path('forest', views.upload_forest_excel, name='upload_forest_excel'),
    path('forest_table', views.display_forest_table, name='forest_table'),
    path('delete_selected/', views.delete_selected, name='delete_selected'),
    path('update_forest_record/<int:pk>/',views.update_forest_record,name='update_forest_record'),
    path('export_forest_table_to_excel/', export_views.export_forest_table_to_excel, name='export_forest_table_to_excel'),
    path('delete_forest_record/<int:item_id>/', views.delete_forest_record, name='delete_forest_record'),

]