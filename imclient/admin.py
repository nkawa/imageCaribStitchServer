from django.contrib import admin

# Register your models here.

from .models import ImFile
from .models import CaribImage

admin.site.register(ImFile)
#admin.site.register(CaribImage)


@admin.register(CaribImage)
class CaribAdmin(admin.ModelAdmin):
    list_display=("cam", "cfile","time")


