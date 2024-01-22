from django.urls import include, path


from .views import occupation_view,education_view, view,population_view,hotel_view,land_view,tourism_view,water_view,transport_view,services_view, crime_view
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
    path('upload_water_meta_excel', view.upload_meta_excel, name="upload_water_meta_excel"),



    path('land_table', land_view.display_land_table, name='land_table'),
    path('delete_selected_land/', land_view.delete_selected_land, name='delete_selected_land'),
    path('delete_land_record/<int:item_id>/', land_view.delete_land_record, name='delete_land_record'),
    path('update_land_record/<int:pk>/',land_view.update_land_record,name='update_land_record'),
    path('export_land_table_to_excel/', export_views.export_land_table_to_excel, name='export_land_table_to_excel'),
    path('upload_land_excel', land_view.upload_land_excel, name='upload_land_excel'),
    path('land_meta', land_view.display_land_meta, name='land_meta'),
    path('upload_land_meta_excel', view.upload_meta_excel, name="upload_land_meta_excel"),
    

    path('tourism_table', tourism_view.display_tourism_table, name='tourism_table'),
    path('delete_selected_tourism/', tourism_view.delete_selected_tourism, name='delete_selected_tourism'),
    path('delete_tourism_record/<int:item_id>/', tourism_view.delete_tourism_record, name='delete_tourism_record'),
    path('update_tourism_record/<int:pk>/',tourism_view.update_tourism_record,name='update_tourism_record'),
    path('export_tourism_table_to_excel/', export_views.export_tourism_table_to_excel, name='export_tourism_table_to_excel'),
    path('upload_tourism_excel', tourism_view.upload_tourism_excel, name='upload_tourism_excel'),
    path('tourism_meta', tourism_view.display_tourism_meta, name='tourism_meta'),
    path('upload_tourism_meta_excel', view.upload_meta_excel, name="upload_tourism_meta_excel"),


    path('transport_table', transport_view.display_transport_table, name='transport_table'),    
    path('delete_selected_transport/', transport_view.delete_selected_transport, name='delete_selected_transport'),
    path('delete_transport_record/<int:item_id>/', transport_view.delete_transport_record, name='delete_transport_record'),
    path('update_transport_record/<int:pk>/',transport_view.update_transport_record,name='update_transport_record'),
    path('export_transport_table_to_excel/', export_views.export_transport_table_to_excel, name='export_transport_table_to_excel'),
    path('upload_transport_excel', transport_view.upload_transport_excel, name='upload_transport_excel'),
    path('transport_meta',  transport_view.display_transport_meta, name='transport_meta'),
    path('upload_transport_meta_excel', view.upload_meta_excel, name="upload_transport_meta_excel"),

    
    path('upload_services_meta_excel', view.upload_meta_excel, name="upload_services_meta_excel"),
    path('services_meta',  services_view.display_services_meta, name='services_meta'),
    path('services_table', services_view.display_services_table, name='services_table'),    
    path('upload_services_excel', services_view.upload_services_excel, name="upload_services_excel"),
    path('update_services_record/<int:pk>/', view.update_record, name = 'update_services_record'),
    path('delete_services_record/<int:pk>/', view.delete_record, name ='delete_services_record' ),
    path('delete_selected_services/', view.delete_selected, name='delete_selected_services'),

    
    path('upload_crime_meta_excel', view.upload_meta_excel, name='upload_crime_meta_excel'),
    path('crime_meta',  crime_view.display_crime_meta, name='crime_meta'),
    path('upload_crime_excel', crime_view.upload_crime_excel, name = 'upload_crime_excel'),
    path('crime_table', crime_view.display_crime_table, name='crime_table'),    
    path('delete_selected_crime/', view.delete_selected, name='delete_selected_crime'),
    path('delete_crime_record/<int:pk>/', view.delete_record, name ='delete_crime_record' ),
    path('update_crime_record/<int:pk>/', view.update_record, name = 'update_crime_record'),
    path('export_excel', crime_view.export_excel, name='export_excel'),
    
    path('upload_education_level_meta_excel', view.upload_meta_excel, name = 'upload_education_level_meta_excel'),
    path('upload_education_degree_meta_excel', view.upload_meta_excel, name = 'upload_education_degree_meta_excel'),
    path('education_level_meta',  education_view.display_education_level_meta, name='education_level_meta'),
    path('education_degree_meta',  education_view.display_education_degree_meta, name='education_degree_meta'),
    path('upload_education_excel', education_view.upload_education_excel, name = 'upload_education_excel'),
    path('education_table', education_view.display_education_table, name='education_table'),    
    path('delete_selected_education/', view.delete_selected, name='delete_selected_education'),
    path('delete_education_record/<int:pk>/', view.delete_record, name ='delete_education_record' ),
    path('update_education_record/<int:pk>/', view.update_record, name = 'update_education_record'),
    path('export_education_excel', education_view.export_education_excel, name='export_education_excel'),

    path('upload_occupation_meta_excel', view.upload_meta_excel, name='upload_occupation_meta_excel'),
    path('occupation_meta',  occupation_view.display_occupation_meta, name='occupation_meta'),
    path('upload_occupation_excel', occupation_view.upload_occupation_excel, name = 'upload_occupation_excel'),



]   