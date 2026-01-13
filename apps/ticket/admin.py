from django.contrib import admin
from .models import Ticket, TicketDetail

class TicketDetailInline(admin.TabularInline):
    model = TicketDetail
    extra = 1  # Número de filas vacías para agregar detalles
    fields = ('product', 'quantity', 'unit_price', 'total')
    readonly_fields = ('total',)  # El total se calcula automáticamente

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'seller', 'date', 'total', 'iva_percentage')
    search_fields = ('client', 'seller', 'ci_ruc')
    list_filter = ('date', 'company', 'iva_percentage')
    ordering = ('-date',)
    inlines = [TicketDetailInline]

    def save_model(self, request, obj, form, change):
        # Copiar IVA de la compañía si es un nuevo ticket
        if not change:  # Si es creación
            obj.iva_percentage = obj.company.iva_percentage
        super().save_model(request, obj, form, change)
        # Actualizar el total después de guardar
        obj.update_total()
