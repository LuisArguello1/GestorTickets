from django.db import models, transaction
from apps.company.models import Company

# Create your models here.

class Ticket(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Compañía")

    document_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        verbose_name="Número de Documento"
    )

    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")  # Automática
    seller = models.CharField(max_length=255, verbose_name="Vendedor")  # Manual
    client = models.CharField(max_length=255, verbose_name="Cliente")  # Manual
    ci_ruc = models.CharField(max_length=20, verbose_name="CI/RUC")  # Manual
    phone = models.CharField(max_length=20, verbose_name="Teléfono")  # Manual
    plate = models.CharField(max_length=20, verbose_name="Placa")  # Manual
    iva_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=15.00, verbose_name="IVA Aplicado (%)")  # Guardado para historial
    total = models.DecimalField(max_digits=15, decimal_places=8, default=0.00000000, verbose_name="Total")  # Calculado con 8 decimales

    def __str__(self):
        return f"Ticket {self.document_number} - {self.client}"

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

    def generate_document_number(self):
        """Genera el número de documento secuencial fiscal."""
        with transaction.atomic():
            # Bloquear el último registro para evitar duplicados
            last_ticket = Ticket.objects.select_for_update().order_by('-id').first()
            if last_ticket and last_ticket.document_number:
                try:
                    # Extraer el número secuencial
                    last_number = int(last_ticket.document_number)
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
            # Formatear con ceros a la izquierda (9 dígitos)
            self.document_number = f"{new_number:09d}"

    def save(self, *args, **kwargs):
        if not self.document_number:
            self.generate_document_number()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"


class TicketDetail(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='details', verbose_name="Ticket")
    product = models.CharField(max_length=255, verbose_name="Producto")
    quantity = models.DecimalField(max_digits=15, decimal_places=8, verbose_name="Cantidad")  # Decimal con 8 decimales para gasolineras
    unit_price = models.DecimalField(max_digits=15, decimal_places=8, verbose_name="P. Unitario")  # Decimal con 8 decimales
    total = models.DecimalField(max_digits=15, decimal_places=8, default=0.00000000, verbose_name="Total")  # Calculado con 8 decimales: quantity * unit_price

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} - {self.quantity}"

    class Meta:
        verbose_name = "Detalle del Ticket"
        verbose_name_plural = "Detalles del Ticket"
