from .models import Property
from django.contrib import admin
from .models import CustomUser

admin.site.register(CustomUser)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'place', 'area',
                    'bedrooms', 'bathrooms', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'place')
