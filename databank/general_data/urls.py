from django.urls import include, path
from . import views

urlpatterns = [
    path('forest/', views.display_forest_table, name='forest')
]