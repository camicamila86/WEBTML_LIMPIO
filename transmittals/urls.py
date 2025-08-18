from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # DASHBOARD - página principal (puede ser dashboard o home)
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # DOCUMENTOS
    path('documentos/', views.lista_documentos, name='lista_documentos'),

    # GENERAR TRANSMITTAL (formulario para crear hoja de transmisión)
    path('generar/', views.generar_transmittal, name='generar_transmittal'),  # Esta es la ruta para el formulario

    # DESTINATARIOS (CRUD)
    path('destinatarios/', views.lista_destinatarios, name='lista_destinatarios'),
    path('destinatarios/agregar/', views.agregar_destinatario, name='agregar_destinatario'),
    path('destinatarios/editar/<int:destinatario_id>/', views.editar_destinatario, name='editar_destinatario'),
    path('destinatarios/eliminar/<int:destinatario_id>/', views.eliminar_destinatario, name='eliminar_destinatario'),

    # LOGIN/LOGOUT/RESET PASSWORD (si no usas accounts/)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
