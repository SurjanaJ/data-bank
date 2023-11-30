
from django.contrib import admin
from django.urls import include, path



urlpatterns = [
    path('admin/', admin.site.urls),
    # path('import_export/',include('import_export.urls')),
    path('', include('trade_data.urls')),
    path('others/', include('general_data.urls'))
]
