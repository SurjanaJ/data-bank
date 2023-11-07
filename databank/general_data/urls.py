from django.urls import include, path
from . import views

urlpatterns = [
    path('forest', views.upload_forest_excel, name='upload_forest_excel'),
    path('forest_table', views.display_forest_table, name='forest_table')
]