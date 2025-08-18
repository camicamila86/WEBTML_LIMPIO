# forms.py
from django import forms
from django.forms import modelformset_factory
from .models import (
    Transmittal, Documento, Destinatario, Especialidad
)

# --------------------------
# Helpers
# --------------------------
class BaseStyledModelForm(forms.ModelForm):
    """
    Aplica 'form-control' a todos los campos visibles (como ya hacías).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.visible_fields():
            # para checkbox o file, ajusta levemente
            if isinstance(f.field.widget, (forms.CheckboxInput,)):
                f.field.widget.attrs['class'] = 'form-check-input'
            else:
                f.field.widget.attrs['class'] = 'form-control'


# --------------------------
# Transmittal (HU5)
# --------------------------
class TransmittalForm(BaseStyledModelForm):
    class Meta:
        model = Transmittal
        # Incluye los campos que llenas desde el formulario
        fields = [
            'codigo',
            'fecha_emision',
            'asunto',
            'descripcion',
            'observacion_general',
            'proposito_envio',
        ]
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 2}),
            'observacion_general': forms.Textarea(attrs={'rows': 2}),
        }


# --------------------------
# Documento (HU7)
# --------------------------
class DocumentoForm(BaseStyledModelForm):
    # Si tienes Especialidad, se mostrará como select; si no, se ignora
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.all(),
        required=False,
        empty_label="(Sin especialidad)"
    )

    class Meta:
        model = Documento
        fields = [
            'codigo',
            'nombre',
            'fecha',
            'revision',
            'extension',
            'comentario',
            'especialidad',
            'archivo',
            'url',        # <- link alternativo al archivo
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'comentario': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        """
        Regla HU7:
        - Debe existir 'archivo' o 'url' (uno de los dos).
        - No pueden venir ambos al mismo tiempo.
        - Si no informan 'extension' pero hay archivo, se intenta deducir.
        """
        data = super().clean()
        archivo = data.get('archivo')
        url = data.get('url')
        extension = data.get('extension')

        if not archivo and not url:
            raise forms.ValidationError("Debes adjuntar un archivo o indicar un enlace (URL).")
        if archivo and url:
            raise forms.ValidationError("Adjunta archivo o URL, pero no ambos.")

        # Deducir extensión simple si viene archivo y no informaron 'extension'
        if archivo and not extension:
            nombre = getattr(archivo, 'name', '')
            if '.' in nombre:
                data['extension'] = nombre.split('.')[-1].lower()

        return data


# --------------------------
# Destinatario (HU6)
# --------------------------
class DestinatarioForm(BaseStyledModelForm):
    class Meta:
        model = Destinatario
        fields = ['nombre', 'cargo', 'correo', 'organizacion']


# --------------------------
# Formsets (múltiples ítems)
# --------------------------
DocumentoFormSet = modelformset_factory(
    Documento,
    form=DocumentoForm,
    extra=1,            # cuántos formularios vacíos aparecen
    can_delete=True     # permite marcar para eliminar
)

DestinatarioFormSet = modelformset_factory(
    Destinatario,
    form=DestinatarioForm,
    extra=1,
    can_delete=True
)
