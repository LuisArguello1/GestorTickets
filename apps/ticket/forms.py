from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import Ticket, TicketDetail
from apps.core.forms.base_form import BaseModelForm


class TicketDetailForm(BaseModelForm):
    """
    Formulario para detalles del ticket.
    Campos manuales: product, quantity, unit_price.
    Total se calcula automáticamente.
    """

    class Meta:
        model = TicketDetail
        fields = ['product', 'quantity', 'unit_price']  # Excluye total (calculado) y ticket (FK)
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '0.00000001', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.00000001', 'min': '0'}),
        }

    def clean_quantity(self):
        """Valida que la cantidad sea positiva."""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a 0.")
        return quantity

    def clean_unit_price(self):
        """Valida que el precio unitario sea positivo."""
        price = self.cleaned_data.get('unit_price')
        if price is not None and price < 0:
            raise forms.ValidationError("El precio unitario no puede ser negativo.")
        return price


class TicketForm(BaseModelForm):
    """
    Formulario para el modelo Ticket.
    Campos automáticos: date (auto_now_add), total (calculado), iva_percentage (copiado de company).
    Campos manuales: company, seller, client, ci_ruc, phone, plate.
    """

    class Meta:
        model = Ticket
        fields = ['seller', 'client', 'ci_ruc', 'phone', 'plate']  # Excluye date, total, iva_percentage, company
        widgets = {
            'ci_ruc': forms.TextInput(attrs={'maxlength': '20'}),
            'phone': forms.TextInput(attrs={'maxlength': '20'}),
            'plate': forms.TextInput(attrs={'maxlength': '20'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            if 'company' in self.fields:
                self.fields['company'].disabled = True  # No cambiar compañía en edición

    def clean_ci_ruc(self):
        """Valida formato básico del CI/RUC."""
        ci_ruc = self.cleaned_data.get('ci_ruc')
        if ci_ruc and len(ci_ruc) > 20:
            raise forms.ValidationError("El CI/RUC no puede exceder 20 caracteres.")
        return ci_ruc

    def save(self, commit=True):
        """Copia el IVA de la compañía y calcula total al guardar."""
        instance = super().save(commit=False)
        if not instance.pk:  # Solo en creación
            instance.iva_percentage = instance.company.iva_percentage
        if commit:
            instance.save()
            # Calcular total después de guardar detalles (si se usan formsets)
            instance.update_total()
        return instance


