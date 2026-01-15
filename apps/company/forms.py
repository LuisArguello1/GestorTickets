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
        fields = ['name', 'ruc', 'phone', 'sri_access_key', 'address', 'iva_percentage', 'client_name', 'client_ruc']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'iva_percentage': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
            'client_name': forms.TextInput(attrs={'placeholder': 'Ej: Universidad Estatal de Milagro'}),
            'client_ruc': forms.TextInput(attrs={'maxlength': '20', 'placeholder': 'RUC del cliente'}),
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

    def clean_client_ruc(self):
        """Valida que el RUC del cliente tenga formato básico."""
        client_ruc = self.cleaned_data.get('client_ruc')
        if client_ruc and len(client_ruc) > 20:
            raise forms.ValidationError("El RUC del cliente no puede exceder 20 caracteres.")
        return client_ruc