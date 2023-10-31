from django.urls import include, path
from . import views

urlpatterns = [
    path('forest/', views.upload_forest_excel, name='upload_forest_excel')
]