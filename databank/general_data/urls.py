from django.urls import include, path
from .views import view,population_view,hotel_view,land_view,tourism_view,water_view,transport_view
from .views import export_views

urlpatterns = [


    path('forest_table', view.display_forest_table, name='forest_table'),
    path('upload_forest_excel', view.upload_forest_excel, name='upload_forest_excel'),
    path('delete_selected_forest/', view.delete_selected_forest, name='delete_selected_forest'),
    path('update_forest_record/<int:pk>/',view.update_forest_record,name='update_forest_record'),
    path('export_forest_table_to_excel/', export_views.export_forest_table_to_excel, name='export_forest_table_to_excel'),
    path('delete_forest_record/<int:item_id>/', view.delete_forest_record, name='delete_forest_record'),


    path('download_duplicate_excel',view.download_duplicate_excel, name='download_duplicate_excel'),

    path('population_table',population_view.display_population_table, name='population_table'),
    path('delete_selected_population/', population_view.delete_selected_population, name='delete_selected_population'),
    path('delete_population_record/<int:item_id>/', population_view.delete_population_record, name='delete_population_record'),
    path('export_population_table_to_excel/', export_views.export_population_table_to_excel, name='export_population_table_to_excel'),
    path('update_population_record/<int:pk>/',population_view.update_population_record,name='update_population_record'),
    path('upload_population_excel', population_view.upload_population_excel, name='upload_population_excel'),


    path('hotel_table', hotel_view.display_hotel_table, name='hotel_table'),
    path('delete_hotel_record/<int:item_id>/', hotel_view.delete_hotel_record, name='delete_hotel_record'),
    path('delete_selected_hotel/', hotel_view.delete_selected_hotel, name='delete_selected_hotel'),
    path('update_hotel_record/<int:pk>/',hotel_view.update_hotel_record,name='update_hotel_record'),
    path('export_hotel_table_to_excel/', export_views.export_hotel_table_to_excel, name='export_hotel_table_to_excel'),
    path('upload_hotel_excel', hotel_view.upload_hotel_excel, name='upload_hotel_excel'),


    path('water_table', water_view.display_water_table, name='water_table'),
    path('delete_selected_water/', water_view.delete_selected_water, name='delete_selected_water'),
    path('delete_water_record/<int:item_id>/', water_view.delete_water_record, name='delete_water_record'),
    path('update_water_record/<int:pk>/',water_view.update_water_record,name='update_water_record'),
    path('export_water_table_to_excel/', export_views.export_water_table_to_excel, name='export_water_table_to_excel'),
    path('upload_water_excel', water_view.upload_water_excel, name='upload_water_excel'),
    path('water_meta', water_view.display_water_meta, name='water_meta'),


    path('land_table', land_view.display_land_table, name='land_table'),
    path('delete_selected_land/', land_view.delete_selected_land, name='delete_selected_land'),
    path('delete_land_record/<int:item_id>/', land_view.delete_land_record, name='delete_land_record'),
    path('update_land_record/<int:pk>/',land_view.update_land_record,name='update_land_record'),
    path('export_land_table_to_excel/', export_views.export_land_table_to_excel, name='export_land_table_to_excel'),
    path('upload_land_excel', land_view.upload_land_excel, name='upload_land_excel'),
    path('land_meta', land_view.display_land_meta, name='land_meta'),

    path('tourism_table', tourism_view.display_tourism_table, name='tourism_table'),
    path('delete_selected_tourism/', tourism_view.delete_selected_tourism, name='delete_selected_tourism'),
    path('delete_tourism_record/<int:item_id>/', tourism_view.delete_tourism_record, name='delete_tourism_record'),
    path('update_tourism_record/<int:pk>/',tourism_view.update_tourism_record,name='update_tourism_record'),
    path('export_tourism_table_to_excel/', export_views.export_tourism_table_to_excel, name='export_tourism_table_to_excel'),
    path('upload_tourism_excel', tourism_view.upload_tourism_excel, name='upload_tourism_excel'),
    path('tourism_meta', tourism_view.display_tourism_meta, name='tourism_meta'),


    path('transport_table', transport_view.display_transport_table, name='transport_table'),    
    path('delete_selected_transport/', transport_view.delete_selected_transport, name='delete_selected_transport'),
    path('delete_transport_record/<int:item_id>/', transport_view.delete_transport_record, name='delete_transport_record'),
    path('update_transport_record/<int:pk>/',transport_view.update_transport_record,name='update_transport_record'),
    path('export_transport_table_to_excel/', export_views.export_transport_table_to_excel, name='export_transport_table_to_excel'),
    path('upload_transport_excel', transport_view.upload_transport_excel, name='upload_transport_excel'),
    path('transport_meta',  transport_view.display_transport_meta, name='transport_meta'),

]