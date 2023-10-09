from django.urls import include, path
from . import views
urlpatterns = [
    path('', views.display_trade_table, name='display_trade_table')
]
