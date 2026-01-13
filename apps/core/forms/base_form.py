"""
Clases base reutilizables para formularios del sistema de gestión de tickets.
Estilo profesional, contable y administrativo, similar a sistemas ERP.
Tema claro con Tailwind CSS, colores neutros (slate, gray, zinc).
Incluye soporte completo para widgets comunes en aplicaciones administrativas.
"""
from django import forms


class BaseFormMixin:
    """
    Mixin base para formularios que aplica clases CSS automáticamente a los widgets.
    Diseñado para sistemas ERP/administrativos: detecta tipo de widget, agrega placeholders,
    maneja estados readonly/disabled, y asegura consistencia visual cross-browser.
    No sobreescribe clases existentes si el widget ya las tiene.
    """

    # Clases base para tamaños - modificables para inputs compactos o grandes
    INPUT_SIZE_CLASSES = 'px-3 py-2 text-sm'  # Tamaño estándar administrativo

    # Configuración de placeholders
    PLACEHOLDER_FORMAT = 'ej_label'  # Opciones: 'label', 'ej_label', None

    # Clases para iconos opcionales en date/time (estilo ERP)
    DATE_ICON_CLASSES = ''  # Ej: 'bg-calendar-icon' si se agrega
    TIME_ICON_CLASSES = ''  # Ej: 'bg-clock-icon' si se agrega

    # Clases para estados especiales
    READONLY_CLASSES = 'bg-gray-50 cursor-not-allowed opacity-75'
    DISABLED_CLASSES = 'bg-gray-100 cursor-not-allowed opacity-50'

    def get_input_classes(self):
        """Devuelve clases para inputs, permitiendo override en subclases."""
        return (
            f'w-full {self.INPUT_SIZE_CLASSES} border border-gray-300 rounded-md '
            'bg-white text-gray-900 placeholder-gray-500 '
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 '
            'transition duration-150 ease-in-out'
        )

    def get_textarea_classes(self):
        """Devuelve clases para textareas."""
        return (
            f'w-full {self.INPUT_SIZE_CLASSES} border border-gray-300 rounded-md '
            'bg-white text-gray-900 placeholder-gray-500 '
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 '
            'transition duration-150 ease-in-out resize-vertical'
        )

    def get_select_classes(self):
        """Devuelve clases para selects."""
        return (
            f'w-full {self.INPUT_SIZE_CLASSES} border border-gray-300 rounded-md '
            'bg-white text-gray-900 appearance-none cursor-pointer '  # appearance-none para consistencia cross-browser
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 '
            'transition duration-150 ease-in-out '
            'bg-no-repeat bg-right bg-contain pr-8'  # Espacio para flecha custom si se agrega
        )

    def get_select_multiple_classes(self):
        """Devuelve clases para select multiple (sin appearance-none para estilo nativo)."""
        return (
            f'w-full {self.INPUT_SIZE_CLASSES} border border-gray-300 rounded-md '
            'bg-white text-gray-900 '  # Sin appearance-none para mantener estilo nativo administrativo
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 '
            'transition duration-150 ease-in-out'
        )

    # Propiedades para compatibilidad backward
    @property
    def INPUT_CLASSES(self):
        return self.get_input_classes()

    @property
    def TEXTAREA_CLASSES(self):
        return self.get_textarea_classes()

    @property
    def SELECT_CLASSES(self):
        return self.get_select_classes()

    @property
    def SELECT_MULTIPLE_CLASSES(self):
        return self.get_select_multiple_classes()

    PASSWORD_CLASSES = INPUT_CLASSES  # Mismo estilo que inputs normales

    CHECKBOX_CLASSES = (
        'w-4 h-4 text-indigo-600 bg-white border-gray-300 rounded align-middle '  # align-middle para alineación vertical
        'focus:ring-indigo-500 focus:ring-2 cursor-pointer'
    )

    FILE_CLASSES = (
        'w-full text-sm text-gray-900 '
        'file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 '
        'file:text-sm file:font-medium file:bg-slate-100 file:text-slate-700 '
        'file:hover:bg-slate-200 file:cursor-pointer '
        'border border-gray-300 rounded-md bg-white cursor-pointer '
        'focus:outline-none focus:ring-2 focus:ring-indigo-500'
    )

    COLOR_CLASSES = (
        'w-full h-10 border border-gray-300 rounded-md cursor-pointer '
        'focus:outline-none focus:ring-2 focus:ring-indigo-500'
    )

    NUMBER_CLASSES = INPUT_CLASSES  # Mismo estilo que inputs normales

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_widget_classes()

    def get_widget_classes(self, widget):
        """
        Método helper para obtener clases CSS según el tipo de widget.
        Centraliza la lógica y evita repetición.
        """
        if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.URLInput)):
            return self.get_input_classes()
        elif isinstance(widget, forms.PasswordInput):
            return self.PASSWORD_CLASSES
        elif isinstance(widget, forms.NumberInput):
            return self.NUMBER_CLASSES
        elif isinstance(widget, forms.Textarea):
            return self.get_textarea_classes()
        elif isinstance(widget, forms.Select):
            return self.get_select_classes()
        elif isinstance(widget, forms.SelectMultiple):
            return self.get_select_multiple_classes()
        elif isinstance(widget, forms.CheckboxInput):
            return self.CHECKBOX_CLASSES
        elif isinstance(widget, forms.FileInput):
            return self.FILE_CLASSES
        elif isinstance(widget, (forms.DateInput, forms.TimeInput, forms.DateTimeInput)):
            return self.get_input_classes()  # Consistencia visual, type se setea después
        return ''

    def add_classes_to_widget(self, widget, classes_to_add):
        """
        Helper para agregar clases a un widget sin duplicados y manejando espacios.
        """
        existing = widget.attrs.get('class', '').strip()
        if existing:
            # Evitar duplicados
            existing_set = set(existing.split())
            to_add_set = set(classes_to_add.split())
            combined = existing_set | to_add_set
            widget.attrs['class'] = ' '.join(sorted(combined))
        else:
            widget.attrs['class'] = classes_to_add

    def apply_widget_classes(self):
        """
        Aplica clases CSS a los widgets según su tipo.
        Maneja placeholders, tipos de input, y estados readonly/disabled.
        No sobreescribe clases existentes. Ignora HiddenInput.
        """
        for field_name, field in self.fields.items():
            widget = field.widget

            # Ignorar HiddenInput explícitamente
            if isinstance(widget, forms.HiddenInput):
                continue

            # Obtener clases existentes del widget
            existing_classes = widget.attrs.get('class', '')

            # Aplicar clases base solo si no existen
            if not existing_classes:
                base_classes = self.get_widget_classes(widget)
                if base_classes:
                    widget.attrs['class'] = base_classes

                # Configuraciones específicas por tipo
                if isinstance(widget, forms.Textarea) and 'rows' not in widget.attrs:
                    widget.attrs['rows'] = 3
                elif isinstance(widget, forms.DateInput):
                    widget.attrs['type'] = 'date'
                    if self.DATE_ICON_CLASSES:
                        self.add_classes_to_widget(widget, self.DATE_ICON_CLASSES)
                elif isinstance(widget, forms.TimeInput):
                    widget.attrs['type'] = 'time'
                    if self.TIME_ICON_CLASSES:
                        self.add_classes_to_widget(widget, self.TIME_ICON_CLASSES)
                elif isinstance(widget, forms.DateTimeInput):
                    widget.attrs['type'] = 'datetime-local'

            # Agregar placeholder si no existe y hay label (configurable)
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.URLInput, forms.NumberInput, forms.PasswordInput, forms.Textarea)):
                if 'placeholder' not in widget.attrs and field.label and self.PLACEHOLDER_FORMAT:
                    if self.PLACEHOLDER_FORMAT == 'label':
                        widget.attrs['placeholder'] = field.label
                    elif self.PLACEHOLDER_FORMAT == 'ej_label':
                        widget.attrs['placeholder'] = f'Ej: {field.label}'

            # Manejar estados readonly y disabled usando helper
            if widget.attrs.get('readonly'):
                self.add_classes_to_widget(widget, self.READONLY_CLASSES)
            if widget.attrs.get('disabled'):
                self.add_classes_to_widget(widget, self.DISABLED_CLASSES)


class BaseModelForm(BaseFormMixin, forms.ModelForm):
    """
    Formulario base para modelos en sistemas administrativos/ERP.
    Agrega asterisco (*) a labels de campos requeridos para indicar obligatoriedad.
    Hereda estilos consistentes del BaseFormMixin.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Marcar campos requeridos con asterisco en el label
        for field_name, field in self.fields.items():
            if field.required and field.label:
                field.label = f'{field.label} *'

    class Meta:
        abstract = True


class BaseForm(BaseFormMixin, forms.Form):
    """
    Formulario base (no modelo) para formularios simples en aplicaciones administrativas.
    Incluye el mixin de estilos para consistencia visual.
    """
    pass
