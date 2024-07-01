from django.contrib import admin

from place.models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['address', 'lat', 'lon', 'geocode_date']
