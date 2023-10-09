from django.contrib import admin
from .models import Country_meta, Unit_meta
# Register your models here.

admin.site.register(Country_meta)
admin.site.register(Unit_meta)

