from django.urls import include, path

from .views import publication_view,index_view,climate_view,occupation_view,health_diseases_views,education_view, view,population_view,hotel_view,land_view,political_views,tourism_view,mining_views,water_view,housing_views,road_views,transport_view,services_view, crime_view,public_unitillity_views,disaster_views, energy_view,exchange_view,climate_view,occupation_view,education_view, view,population_view,hotel_view,land_view,tourism_view,water_view,transport_view,services_view, crime_view
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


    path('public_unitillity_table', public_unitillity_views.display_public_unitillity_table, name='public_unitillity_table'),    
    path('delete_selected_public_unitillity/', public_unitillity_views.delete_selected_public_unitillity, name='delete_selected_public_unitillity'),
    path('delete_public_unitillity_record/<int:item_id>/', public_unitillity_views.delete_public_unitillity_record, name='delete_public_unitillity_record'),
    path('update_public_unitillity_record/<int:pk>/',public_unitillity_views.update_public_unitillity_record,name='update_public_unitillity_record'),
    path('export_public_unitillity_table_to_excel/', export_views.export_public_unitillity_table_to_excel, name='export_public_unitillity_table_to_excel'),
    path('upload_public_unitillity_excel', public_unitillity_views.upload_public_unitillity_excel, name='upload_public_unitillity_excel'),


    path('health_diseases_table',health_diseases_views.display_health_disease_table, name='health_disease_table'),
    path('update_health_disease_record/<int:pk>/', view.update_record, name = 'update_health_disease_record'),
    path('delete_health_disease_record/<int:pk>/', view.delete_record, name ='delete_health_disease_record' ),
    path('delete_selected_health_disease/', view.delete_selected, name='delete_selected_health_disease'),
    path('export_health_diseases_table_to_excel/', export_views.export_health_diseases_table_to_excel, name='export_health_diseases_table_to_excel'),
    path('upload_health_diseases_excel', health_diseases_views.upload_health_diseases_excel, name = 'upload_health_diseases_excel'),


    path('disaster_table',disaster_views.display_disaster_table, name='disaster_table'),
    path('update_disaster_record/<int:pk>/', view.update_record, name = 'update_disaster_record'),
    path('delete_disaster_record/<int:pk>/', view.delete_record, name ='delete_disaster_record' ),
    path('delete_selected_disaster/', view.delete_selected, name='delete_selected_disaster'),
    path('export_disaster_table_to_excel/', export_views.export_disaster_table_to_excel, name='export_disaster_table_to_excel'),
    path('upload_disaster_excel', disaster_views.upload_disaster_excel, name = 'upload_disaster_excel'),


    
    path('road_table',road_views.display_road_table, name='road_table'),
    path('update_road_record/<int:pk>/', view.update_record, name = 'update_road_record'),
    path('delete_road_record/<int:pk>/', view.delete_record, name ='delete_road_record' ),
    path('delete_road_disease/', view.delete_selected, name='delete_selected_road'),
    path('export_road_table_to_excel/', export_views.export_road_table_to_excel, name='export_road_table_to_excel'),


    path('housing_table',housing_views.display_housing_table, name='housing_table'),
    path('update_housing_record/<int:pk>/', view.update_record, name = 'update_housing_record'),
    path('delete_housing_record/<int:pk>/', view.delete_record, name ='delete_housing_record' ),
    path('delete_selected_housing/', view.delete_selected, name='delete_selected_housing'),
    path('export_housing_table_to_excel/', export_views.export_housing_table_to_excel, name='export_housing_table_to_excel'),
    path('upload_housing_excel', housing_views.upload_housing_excel, name = 'upload_housing_excel'),


    path('mining_table',mining_views.display_mining_table, name='mining_table'),
    path('update_mining_record/<int:pk>/', view.update_record, name = 'update_mining_record'),
    path('delete_mining_record/<int:pk>/', view.delete_record, name ='delete_mining_record'),
    path('delete_selected_mining/', view.delete_selected, name='delete_selected_mining'),
    path('export_mining_table_to_excel/', export_views.export_mining_table_to_excel, name='export_mining_table_to_excel'),


    path('political_table',political_views.display_political_table, name='political_table'),
    path('update_political_record/<int:pk>/', view.update_record, name = 'update_political_record'),
    path('delete_political_record/<int:pk>/', view.delete_record, name ='delete_political_record' ),
    path('delete_selected_political/', view.delete_selected, name='delete_selected_political'),    
    path('export_political_table_to_excel/', export_views.export_political_table_to_excel, name='export_political_table_to_excel'),
   
    
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
    path('update_selected_crime/', crime_view.update_selected_crime, name='update_selected_crime'),

    
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
    path('occupation_table', occupation_view.display_occupation_table, name='occupation_table'),    
    path('delete_occupation_record/<int:pk>/', view.delete_record, name ='delete_occupation_record' ),
    path('delete_selected_occupation/', view.delete_selected, name='delete_selected_occupation'),
    path('update_occupation_record/<int:pk>/', view.update_record, name = 'update_occupation_record'),
    path('export_occupation_excel', occupation_view.export_occupation_excel, name='export_occupation_excel'),
    path('update_selected_occupation/', occupation_view.update_selected_occupation, name='update_selected_occupation'),


    path('upload_climate_place_meta_excel', climate_view.upload_climate_place_meta_excel, name='upload_climate_place_meta_excel'),
    path('place_meta',  climate_view.display_climate_place_meta, name='place_meta'),
    path('upload_climate_excel', climate_view.upload_climate_excel, name = 'upload_climate_excel'),
    path('climate_table', climate_view.display_climate_table, name='climate_table'),    
    path('update_climate_record/<int:pk>/', view.update_record, name = 'update_climate_record'),
    path('delete_climate_record/<int:pk>/', view.delete_record, name ='delete_climate_record' ),
    path('delete_selected_climate/', view.delete_selected, name='delete_selected_climate'),
    path('export_climate_excel', climate_view.export_climate_excel, name='export_climate_excel'),
    path('update_selected_climate/', climate_view.update_selected_climate, name='update_selected_climate'),


    path('upload_currency_excel', exchange_view.upload_currency_meta_excel, name='upload_currency_excel'),
    path('currency_meta',  exchange_view.display_currency_meta, name='currency_meta'),
    path('upload_exchange_excel', exchange_view.upload_exchange_excel, name = 'upload_exchange_excel'),
    path('exchange_table', exchange_view.display_exchange_table, name='exchange_table'),    
    path('update_exchange_record/<int:pk>/', view.update_record, name = 'update_exchange_record'),
    path('delete_exchange_record/<int:pk>/', view.delete_record, name ='delete_exchange_record' ),
    path('delete_selected_exchange/', view.delete_selected, name='delete_selected_exchange'),
    path('export_exchange_excel', exchange_view.export_exchange_excel, name='export_exchange_excel'),
    path('update_selected_exchange/', exchange_view.update_selected_exchange, name='update_selected_exchange'),


    path('upload_energy_meta_excel', view.upload_meta_excel, name='upload_energy_meta_excel'),
    path('energy_meta',  energy_view.display_energy_meta, name='energy_meta'),
    path('upload_energy_excel', energy_view.upload_energy_excel, name = 'upload_energy_excel'),
    path('energy_table', energy_view.display_energy_table, name='energy_table'), 
    path('update_energy_record/<int:pk>/', view.update_record, name = 'update_energy_record'),
    path('delete_energy_record/<int:pk>/', view.delete_record, name ='delete_energy_record' ),
    path('delete_selected_energy/', view.delete_selected, name='delete_selected_energy'),
    path('export_energy_excel', energy_view.export_energy_excel, name='export_energy_excel'),
    path('update_selected_energy/', energy_view.update_selected_energy, name='update_selected_energy'),

    path('upload_index_excel', index_view.upload_index_excel, name = 'upload_index_excel'),
    path('index_table', index_view.display_index_table, name='index_table'), 
    path('update_index_record/<int:pk>/', view.update_record, name = 'update_index_record'),
    path('delete_index_record/<int:pk>/', view.delete_record, name ='delete_index_record' ),
    path('delete_selected_index/', view.delete_selected, name='delete_selected_index'),
    path('export_index_excel', index_view.export_index_excel, name='export_index_excel'),
    path('update_selected_index/', index_view.update_selected_index, name='update_selected_index'),
    
    path('publication_table', publication_view.display_publication_table, name='publication_table'), 
    path('upload_publication_excel', publication_view.upload_publication_excel, name = 'upload_publication_excel'),
    path('update_publication_record/<int:pk>/', view.update_record, name = 'update_publication_record'),
    path('delete_publication_record/<int:pk>/', view.delete_record, name ='delete_publication_record' ),
    path('delete_selected_publication/', view.delete_selected, name='delete_selected_publication'),
    path('export_publication_excel', publication_view.export_publication_excel, name='export_publication_excel'),
    path('update_selected_publication/', publication_view.update_selected_publication, name='update_selected_publication'),

]   