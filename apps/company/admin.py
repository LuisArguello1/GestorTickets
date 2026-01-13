from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'ruc', 'phone', 'iva_percentage', 'address')
    search_fields = ('name', 'ruc')
    list_filter = ('iva_percentage',)
    ordering = ('name',)
