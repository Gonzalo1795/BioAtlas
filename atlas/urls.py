from django.urls import path
from . import views

app_name = 'atlas'

urlpatterns = [
    # Página principal
    path('', views.index, name='index'),

    # Autenticación
    path('login/',    views.login_view,  name='login'),
    path('registro/', views.registro,    name='registro'),
    path('logout/',   views.logout_view, name='logout'),

    # Perfil y colección personal
    path('perfil/',                              views.perfil,              name='perfil'),
    path('perfil/favoritos/',                    views.mis_favoritos,       name='mis_favoritos'),
    path('perfil/avistamientos/',                views.mis_avistamientos,   name='mis_avistamientos'),
    path('perfil/avistamientos/nuevo/<int:species_key>/', views.nuevo_avistamiento, name='nuevo_avistamiento'),
    path('perfil/avistamientos/eliminar/<int:pk>/',       views.eliminar_avistamiento, name='eliminar_avistamiento'),

    # Atlas
    path('atlas/',              views.biolog,      name='biolog'),
    path('atlas/pais/<int:pais_pk>/', views.biolog_pais, name='biolog_pais'),

    # Geografía
    path('continente/<int:pk>/', views.ContinenteDetailView.as_view(), name='continente_detail'),
    path('pais/<int:pk>/',       views.PaisDetailView.as_view(),       name='pais_detail'),

    # Búsqueda
    path('buscar/', views.buscar_especie, name='buscar_especie'),

    # Premium y Stripe
    path('premium/',           views.premium,          name='premium'),
    path('premium/checkout/',  views.premium_checkout, name='premium_checkout'),
    path('premium/success/',   views.premium_success,  name='premium_success'),
    path('premium/cancel/',    views.premium_cancel,   name='premium_cancel'),
    path('premium/cancelar/',  views.cancelar_suscripcion, name='cancelar_suscripcion'),
    path('premium/webhook/',   views.stripe_webhook,   name='stripe_webhook'),

    # APIs internas
    path('api/especie/<int:species_key>/', views.api_especie_detalle,  name='api_especie_detalle'),
    path('api/favorito/toggle/',           views.api_toggle_favorito,  name='api_toggle_favorito'),
    path('api/biolog/toggle/',             views.api_toggle_biolog,    name='api_toggle_biolog'),
    path('api/buscar/',                    views.api_buscar_especies,  name='api_buscar_especies'),
    path('api/pais-by-code/',              views.api_pais_by_code,     name='api_pais_by_code'),
    
    path('antartida/', views.antartida_detail, name='antartida_detail'),

    path('api/buscar-paises/', views.api_buscar_paises, name='api_buscar_paises'),


    path('terminos/', views.terminos, name='terminos'),
    path('privacidad/', views.privacidad, name='privacidad'),
    path('cookies/', views.cookies, name='cookies'),
    path('contacto/', views.contacto, name='contacto'),
]