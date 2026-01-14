from django import forms
from .models import Company
from apps.core.forms.base_form import BaseModelForm


class CompanyForm(BaseModelForm):
    """
    Formulario para el modelo Company.
    Todos los campos son manuales, con validaciones básicas.
    """

    class Meta:
        model = Company
        fields = ['name', 'ruc', 'phone', 'sri_access_key', 'address', 'iva_percentage']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'iva_percentage': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
        }

    def clean_ruc(self):
        """Valida que el RUC sea único y tenga formato básico."""
        ruc = self.cleaned_data.get('ruc')
        if not ruc:
            raise forms.ValidationError("El RUC es obligatorio.")
        if len(ruc) < 10 or len(ruc) > 20:
            raise forms.ValidationError("El RUC debe tener entre 10 y 20 caracteres.")

        if Company.objects.filter(ruc=ruc).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError("Este RUC ya está registrado.")
        return ruc

    def clean_iva_percentage(self):
        """Valida que el IVA esté en rango válido."""
        iva = self.cleaned_data.get('iva_percentage')
        if iva is not None and (iva < 0 or iva > 100):
            raise forms.ValidationError("El porcentaje de IVA debe estar entre 0 y 100.")
        return iva