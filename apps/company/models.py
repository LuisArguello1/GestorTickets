from django.db import models

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre de la Compañía")
    ruc = models.CharField(max_length=20, unique=True, verbose_name="RUC")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    sri_access_key = models.CharField(max_length=255, verbose_name="Clave de Acceso SRI")
    address = models.TextField(verbose_name="Dirección")  # Para usar automáticamente en tickets
    iva_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=12.00, verbose_name="Porcentaje de IVA")  # Ej: 12.00 para 12%

    def __str__(self):
        return self.name

    @property
    def get_current_iva(self):
        """Devuelve el porcentaje de IVA actual de la compañía."""
        return self.iva_percentage

    class Meta:
        verbose_name = "Compañía"
        verbose_name_plural = "Compañías"
