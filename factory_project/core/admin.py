from .models import Product, RawMaterial, UserProfile
from django.contrib import admin

# Register your models here so they appear in the admin panel:
admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(RawMaterial)