from django.urls import include, path
from . import views
urlpatterns = [
    path('', views.view_trade_table, name='view_trade_table')
]
