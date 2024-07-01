from django.db import models


from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField(verbose_name='Адрес', max_length=255)
    lat = models.DecimalField(verbose_name='Широта', max_digits=10, decimal_places=6, null=True, blank=True)
    lon = models.DecimalField(verbose_name='Долгота', max_digits=10, decimal_places=6, null=True, blank=True)
    geocode_date = models.DateField(verbose_name='Дата обновления', default=timezone.now,)

    class Meta:
        unique_together = ['lat', 'lon', 'address']

    def __str__(self):
        return self.address
