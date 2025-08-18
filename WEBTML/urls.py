from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from transmittals.views import prueba_template, dashboard

def inicio(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('prueba/', prueba_template, name='prueba_template'),
    path('accounts/', include('django.contrib.auth.urls')),
    # Aquí incluyes todo lo de tu app transmittals:
    path('', include('transmittals.urls')),
    path('dashboard/', dashboard, name='dashboard'),
    path('', inicio, name='inicio'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
