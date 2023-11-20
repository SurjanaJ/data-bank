from django.urls import include, path
from . import views

urlpatterns = [
    path('forest', views.upload_forest_excel, name='upload_forest_excel'),
    path('forest_table', views.display_forest_table, name='forest_table'),
    path('delete_selected/', views.delete_selected_records, name='delete_selected_records'),
    path('update_forest_record/<int:pk>/',views.update_forest_record,name='update_forest_record')
]