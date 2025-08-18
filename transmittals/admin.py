from django.contrib import admin
from .models import Destinatario, Documento, Transmittal, HistorialAccion, Comentario, EstadoNotificacion

admin.site.register(Destinatario)
admin.site.register(Documento)
admin.site.register(Transmittal)
admin.site.register(HistorialAccion)
admin.site.register(Comentario)
admin.site.register(EstadoNotificacion)
