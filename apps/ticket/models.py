from django.db import models
from apps.company.models import Company

# Create your models here.

class Ticket(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Compañía")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")  # Automática
    seller = models.CharField(max_length=255, verbose_name="Vendedor")  # Manual
    client = models.CharField(max_length=255, verbose_name="Cliente")  # Manual
    ci_ruc = models.CharField(max_length=20, verbose_name="CI/RUC")  # Manual
    phone = models.CharField(max_length=20, verbose_name="Teléfono")  # Manual
    plate = models.CharField(max_length=20, verbose_name="Placa")  # Manual
    iva_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=12.00, verbose_name="IVA Aplicado (%)")  # Guardado para historial
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total")  # Calculado

    def __str__(self):
        return f"Ticket {self.id} - {self.client}"

    @property
    def subtotal(self):
        """Calcula el subtotal sumando los totales de los detalles."""
        return sum(detail.total for detail in self.details.all())

    @property
    def iva_amount(self):
        """Calcula el monto del IVA aplicado al subtotal."""
        return self.subtotal * (self.iva_percentage / 100)

    @property
    def total_calculated(self):
        """Calcula el total final (subtotal + IVA)."""
        return self.subtotal + self.iva_amount

    def update_total(self):
        """Actualiza el campo total con el cálculo."""
        self.total = self.total_calculated
        self.save(update_fields=['total'])

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"


class TicketDetail(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='details', verbose_name="Ticket")
    product = models.CharField(max_length=255, verbose_name="Producto")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad")  # Decimal
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="P. Unitario")  # Decimal
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total")  # Calculado: quantity * unit_price

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} - {self.quantity}"

    class Meta:
        verbose_name = "Detalle del Ticket"
        verbose_name_plural = "Detalles del Ticket"
