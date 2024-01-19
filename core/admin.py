from django.contrib import admin
from core.models import Period, Timeslot, Booking

# Register your models here.

admin.site.register(Period)
admin.site.register(Timeslot)
admin.site.register(Booking)
