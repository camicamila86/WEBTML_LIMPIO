from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .models import Documento, Destinatario, Transmittal
from .forms import (
    TransmittalForm,
    DocumentoFormSet,   # formset para múltiples documentos
    DestinatarioFormSet,  # formset para múltiples destinatarios
    DestinatarioForm,
)

# --- Permiso de rol (Control Documental o superusuario)
def es_control_documental(user):
    return user.is_superuser or user.groups.filter(name='Control Documental').exists()


# --- Home / Dashboard
@login_required
def dashboard(request):
    return render(request, 'transmittals/dashboard.html')

def home(request):
    return render(request, 'transmittals/home.html')


# --- Listas simples
@login_required
def lista_documentos(request):
    if request.method == 'POST':
        # Demo mínima para crear rápido desde la lista (puedes quitarlo si usarás form formal)
        nombre = request.POST.get('nombre')
        fecha = request.POST.get('fecha')
        if nombre and fecha:
            Documento.objects.create(nombre=nombre, fecha=fecha)
            return redirect('lista_documentos')
    documentos = Documento.objects.all().order_by('-fecha')
    return render(request, 'transmittals/lista_documentos.html', {'documentos': documentos})

@login_required
def lista_destinatarios(request):
    destinatarios = Destinatario.objects.all().order_by('nombre')
    es_control = es_control_documental(request.user)
    return render(request, 'transmittals/lista_destinatarios.html', {
        'destinatarios': destinatarios,
        'es_control': es_control
    })


# --- Crear Transmittal con documentos y destinatarios (HU5, HU6, HU7)
@login_required
@user_passes_test(es_control_documental)
@transaction.atomic
def generar_transmittal(request):
    if request.method == 'POST':
        t_form = TransmittalForm(request.POST)
        doc_formset = DocumentoFormSet(request.POST, request.FILES, prefix='docs')
        dest_formset = DestinatarioFormSet(request.POST, prefix='dests')

        if t_form.is_valid() and doc_formset.is_valid() and dest_formset.is_valid():
            transmittal = t_form.save(commit=False)
            if hasattr(transmittal, 'creado_por') and transmittal.creado_por is None:
                transmittal.creado_por = request.user
            transmittal.save()

            # Asociar documentos
            for f in doc_formset:
                if not f.cleaned_data or f.cleaned_data.get('DELETE'):
                    continue
                doc = f.save()  # crea o actualiza el Documento
                transmittal.documentos.add(doc)(
                    
                )

            # Asociar destinatarios
            for f in dest_formset:
                if not f.cleaned_data or f.cleaned_data.get('DELETE'):
                    continue
                dest = f.save()
                transmittal.destinatarios.add(dest)
                (
            
                )

            messages.success(request, f"Transmittal {transmittal.codigo} creado correctamente.")
            return redirect('transmittals:detalle', pk=transmittal.pk)
        else:
            messages.error(request, "Revisa los errores en el formulario.")
    else:
        t_form = TransmittalForm()
        doc_formset = DocumentoFormSet(queryset=Documento.objects.none(), prefix='docs')
        dest_formset = DestinatarioFormSet(queryset=Destinatario.objects.none(), prefix='dests')

    return render(request, 'transmittals/generar_transmittal.html', {
        't_form': t_form,
        'doc_formset': doc_formset,
        'dest_formset': dest_formset
    })


# --- Detalle de Transmittal (para revisar lo creado)
@login_required
def detalle_transmittal(request, pk):
    transmittal = get_object_or_404(Transmittal, pk=pk)
    documentos = transmittal.documentos.all()
    destinatarios = transmittal.destinatarios.all()
    return render(request, 'transmittals/detalle_transmittal.html', {
        't': transmittal,
        'documentos': documentos,
        'destinatarios': destinatarios,
    })


# ---- CRUD Destinatario (solo control documental)
@login_required
@user_passes_test(es_control_documental)
def agregar_destinatario(request):
    if request.method == 'POST':
        form = DestinatarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Destinatario agregado.")
            return redirect('lista_destinatarios')
    else:
        form = DestinatarioForm()
    return render(request, 'transmittals/agregar_destinatario.html', {'form': form})

@login_required
@user_passes_test(es_control_documental)
def editar_destinatario(request, destinatario_id):
    destinatario = get_object_or_404(Destinatario, id=destinatario_id)
    if request.method == 'POST':
        form = DestinatarioForm(request.POST, instance=destinatario)
        if form.is_valid():
            form.save()
            messages.success(request, "Destinatario actualizado.")
            return redirect('lista_destinatarios')
    else:
        form = DestinatarioForm(instance=destinatario)
    return render(request, 'transmittals/editar_destinatario.html', {'form': form, 'destinatario': destinatario})

@login_required
@user_passes_test(es_control_documental)
def eliminar_destinatario(request, destinatario_id):
    destinatario = get_object_or_404(Destinatario, id=destinatario_id)
    if request.method == 'POST':
        destinatario.delete()
        messages.success(request, "Destinatario eliminado.")
        return redirect('lista_destinatarios')
    return render(request, 'transmittals/eliminar_destinatario.html', {'destinatario': destinatario})


# Vista de prueba
def prueba_template(request):
    return render(request, 'transmittals/prueba.html')
