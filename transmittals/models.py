from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, URLValidator
from django.utils import timezone

class Destinatario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()  # si tus datos lo permiten, puedes pasar a unique=True
    cargo = models.CharField(max_length=100, blank=True, null=True)
    organizacion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.correo})"


class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Documento(models.Model):
    # NUEVOS: identificador y metadatos
    codigo = models.CharField(max_length=50, blank=True, null=True)   # puedes volverlo unique=True más adelante
    nombre = models.CharField(max_length=100)
    fecha = models.DateField()
    revision = models.CharField(max_length=3, default="A")

    extension = models.CharField(max_length=10, blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True)

    # Adjuntar archivo O link (URL). Ambos opcionales aquí; se valida en el formulario.
    archivo = models.FileField(
        upload_to='documentos/',
        validators=[FileExtensionValidator(
            allowed_extensions=['dwg','xls','xlsx','xlsm','doc','docx','pdf','jpg','jpeg','png']
        )],
        blank=True,
        null=True
    )
    url = models.URLField(blank=True, null=True, validators=[URLValidator()])

    def __str__(self):
        return f"{self.codigo or ''} {self.nombre}".strip()


class Transmittal(models.Model):
    codigo = models.CharField(max_length=20, unique=True)

    # NUEVO: fecha de emisión que viene del formulario
    fecha_emision = models.DateField(blank=True, null=True)

    # si quieres conservar cuándo se envió realmente (automático), deja este:
    fecha_envio = models.DateField(auto_now_add=True)

    asunto = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    observacion_general = models.TextField(blank=True, null=True)

    # reemplaza “estatus de envío” por propósito (lo que se imprime en la hoja)
    PROPOSITO = [
        ('APROBACION', 'Solicita Aprobación'),
        ('REVISION',   'Requiere Revisión'),
        ('RESPUESTA',  'Requiere Respuesta'),
        ('INFO',       'Informativo'),
    ]
    proposito_envio = models.CharField(max_length=15, choices=PROPOSITO, default='INFO')

    documentos = models.ManyToManyField(Documento, related_name='transmittals', blank=True)
    destinatarios = models.ManyToManyField(Destinatario, related_name='transmittals', blank=True)

    # (opcional) quién lo crea
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transmittals_creados', null=True, blank=True)

    # control de tiempo (conserva los tuyos)
    creado_en = models.DateTimeField(default=timezone.now, editable=False)
    actualizado_en = models.DateTimeField(auto_now=True)

    # si quieres mantener un estado interno de workflow además del propósito, deja tu campo:
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('recibido', 'Recibido'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Transmittal {self.codigo} - {self.asunto or ''}".strip()


class HistorialAccion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    transmittal = models.ForeignKey('Transmittal', on_delete=models.CASCADE, null=True, blank=True)
    accion = models.CharField(max_length=255)  # 'envió', 'editó', 'visualizó', etc.
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.accion} ({self.fecha})"


class Comentario(models.Model):
    documento = models.ForeignKey('Documento', on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.documento.nombre}"


class EstadoNotificacion(models.Model):
    destinatario = models.ForeignKey('Destinatario', on_delete=models.CASCADE)
    transmittal = models.ForeignKey('Transmittal', on_delete=models.CASCADE)
    leido = models.BooleanField(default=False)
    confirmado = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField()
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Notificación a {self.destinatario.nombre} sobre {self.transmittal.codigo}"
