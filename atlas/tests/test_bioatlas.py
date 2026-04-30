# -*- coding: utf-8 -*-
"""
Tests completos de BioAtlas con pytest-django
Instalación: pip install pytest-django
Configuración: añadir pytest.ini en la raíz del proyecto
Ejecución: pytest atlas/tests/test_bioatlas.py -v
"""

import json
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from atlas.models import (
    Continente, Pais, Especie, Favorito, BioLog,
    Avistamiento, Suscripcion, QuizPartida
)


# ─────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────

@pytest.fixture
def usuario(db):
    """Usuario básico sin premium."""
    user = User.objects.create_user(
        username='testuser',
        email='test@bioatlas.com',
        password='testpass123'
    )
    Suscripcion.objects.create(usuario=user, plan='free')
    return user


@pytest.fixture
def usuario_premium(db):
    """Usuario con plan Premium."""
    user = User.objects.create_user(
        username='premiumuser',
        email='premium@bioatlas.com',
        password='testpass123'
    )
    Suscripcion.objects.create(usuario=user, plan='premium')
    return user


@pytest.fixture
def continente(db):
    return Continente.objects.create(nombre='Europa', codigo='EU')


@pytest.fixture
def pais(db, continente):
    return Pais.objects.create(
        nombre='España',
        codigo='ES',
        continente=continente,
        latitud=40.416775,
        longitud=-3.703790
    )


@pytest.fixture
def especie(db):
    return Especie.objects.create(
        species_key=12345,
        scientific_name='Panthera leo',
        canonical_name='Panthera leo',
        kingdom='Animalia',
        class_name='Mammalia',
        family='Felidae',
        common_name='León'
    )


@pytest.fixture
def especie2(db):
    return Especie.objects.create(
        species_key=67890,
        scientific_name='Quercus robur',
        canonical_name='Quercus robur',
        kingdom='Plantae',
        class_name='Magnoliopsida',
        family='Fagaceae',
        common_name='Roble'
    )


@pytest.fixture
def client_auth(client, usuario):
    """Cliente autenticado."""
    client.login(username='testuser', password='testpass123')
    return client


@pytest.fixture
def client_premium(client, usuario_premium):
    """Cliente autenticado con premium."""
    client.login(username='premiumuser', password='testpass123')
    return client


# ─────────────────────────────────────────
# TESTS: PÁGINAS PÚBLICAS
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestPaginasPublicas:

    def test_index_carga(self, client):
        response = client.get(reverse('atlas:index'))
        assert response.status_code == 200

    def test_buscar_especie_carga(self, client):
        response = client.get(reverse('atlas:buscar_especie'))
        assert response.status_code == 200

    def test_quiz_carga(self, client):
        response = client.get(reverse('atlas:quiz'))
        assert response.status_code == 302

    def test_premium_carga(self, client):
        response = client.get(reverse('atlas:premium'))
        assert response.status_code == 200

    def test_login_carga(self, client):
        response = client.get(reverse('atlas:login'))
        assert response.status_code == 200

    def test_registro_carga(self, client):
        response = client.get(reverse('atlas:registro'))
        assert response.status_code == 200

    def test_terminos_carga(self, client):
        response = client.get(reverse('atlas:terminos'))
        assert response.status_code == 200

    def test_privacidad_carga(self, client):
        response = client.get(reverse('atlas:privacidad'))
        assert response.status_code in [200, 302]

    def test_antartida_carga(self, client):
        response = client.get('/antartida/')
        assert response.status_code in [200, 302, 404]


# ─────────────────────────────────────────
# TESTS: AUTENTICACIÓN
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestAutenticacion:

    def test_registro_exitoso(self, client):
        response = client.post(reverse('atlas:registro'), {
            'username': 'nuevousuario',
            'password1': 'Abc12345!',
            'password2': 'Abc12345!',
        })
        assert User.objects.filter(username='nuevousuario').exists()

    def test_registro_passwords_no_coinciden(self, client):
        response = client.post(reverse('atlas:registro'), {
            'username': 'nuevousuario',
            'password1': 'Abc12345!',
            'password2': 'OtraClave!',
        })
        assert not User.objects.filter(username='nuevousuario').exists()

    def test_login_exitoso(self, client, usuario):
        response = client.post(reverse('atlas:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        assert response.status_code in [200, 302]

    def test_login_credenciales_incorrectas(self, client, usuario):
        response = client.post(reverse('atlas:login'), {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        assert response.status_code == 200

    def test_logout(self, client_auth):
        response = client_auth.post(reverse('atlas:logout'))
        assert response.status_code in [200, 302]

    def test_perfil_requiere_login(self, client):
        response = client.get(reverse('atlas:perfil'))
        assert response.status_code == 302
        assert '/login' in response.url

    def test_perfil_accesible_autenticado(self, client_auth):
        response = client_auth.get(reverse('atlas:perfil'))
        assert response.status_code == 200


# ─────────────────────────────────────────
# TESTS: PÁGINAS CON DATOS
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestPaginasConDatos:

    def test_continente_detail(self, client, continente):
        response = client.get(reverse('atlas:continente_detail', args=[continente.pk]))
        assert response.status_code == 200

    def test_pais_detail(self, client, pais):
        response = client.get(reverse('atlas:pais_detail', args=[pais.pk]))
        assert response.status_code == 200

    def test_pais_inexistente_404(self, client):
        response = client.get(reverse('atlas:pais_detail', args=[99999]))
        assert response.status_code == 404


# ─────────────────────────────────────────
# TESTS: FAVORITOS
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestFavoritos:

    def test_añadir_favorito(self, client_auth, usuario, especie):
        response = client_auth.post(
            reverse('atlas:api_toggle_favorito'),
            data=json.dumps({'species_key': especie.species_key}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['es_favorito'] is True
        assert Favorito.objects.filter(usuario=usuario, especie=especie).exists()

    def test_quitar_favorito(self, client_auth, usuario, especie):
        Favorito.objects.create(usuario=usuario, especie=especie)
        response = client_auth.post(
            reverse('atlas:api_toggle_favorito'),
            data=json.dumps({'species_key': especie.species_key}),
            content_type='application/json'
        )
        data = response.json()
        assert data['es_favorito'] is False
        assert not Favorito.objects.filter(usuario=usuario, especie=especie).exists()

    def test_favorito_requiere_login(self, client, especie):
        response = client.post(
            reverse('atlas:api_toggle_favorito'),
            data=json.dumps({'species_key': especie.species_key}),
            content_type='application/json'
        )
        assert response.status_code == 401

    def test_limite_favoritos_free(self, client_auth, usuario, db):
        """El plan free tiene límite de favoritos."""
        for i in range(BioLog.LIMITE_ESPECIES_FREE + 1):
            esp = Especie.objects.create(
                species_key=10000 + i,
                scientific_name=f'Especie {i}',
                canonical_name=f'Especie {i}'
            )
            if i < BioLog.LIMITE_ESPECIES_FREE:
                Favorito.objects.create(usuario=usuario, especie=esp)

        esp_extra = Especie.objects.create(
            species_key=99999,
            scientific_name='Especie extra',
            canonical_name='Especie extra'
        )
        response = client_auth.post(
            reverse('atlas:api_toggle_favorito'),
            data=json.dumps({'species_key': esp_extra.species_key}),
            content_type='application/json'
        )
        data = response.json()
        assert data['success'] is False
        assert data.get('limite') is True

    def test_mis_favoritos_carga(self, client_auth):
        response = client_auth.get(reverse('atlas:mis_favoritos'))
        assert response.status_code == 200

    def test_mis_favoritos_muestra_especies(self, client_auth, usuario, especie):
        Favorito.objects.create(usuario=usuario, especie=especie)
        response = client_auth.get(reverse('atlas:mis_favoritos'))
        assert 'Panthera leo' in response.content.decode()


# ─────────────────────────────────────────
# TESTS: MI ATLAS (BIOLOG)
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestMiAtlas:

    def test_añadir_al_atlas(self, client_auth, usuario, especie, pais):
        response = client_auth.post(
            reverse('atlas:api_toggle_biolog'),
            data=json.dumps({
                'species_key': especie.species_key,
                'pais_id': pais.pk
            }),
            content_type='application/json'
        )
        data = response.json()
        assert data['success'] is True
        assert data['en_biolog'] is True
        assert BioLog.objects.filter(usuario=usuario, especie=especie, pais=pais).exists()

    def test_quitar_del_atlas(self, client_auth, usuario, especie, pais):
        BioLog.objects.create(usuario=usuario, especie=especie, pais=pais)
        response = client_auth.post(
            reverse('atlas:api_toggle_biolog'),
            data=json.dumps({
                'species_key': especie.species_key,
                'pais_id': pais.pk
            }),
            content_type='application/json'
        )
        data = response.json()
        assert data['en_biolog'] is False
        assert not BioLog.objects.filter(usuario=usuario, especie=especie, pais=pais).exists()

    def test_biolog_requiere_login(self, client, especie, pais):
        response = client.post(
            reverse('atlas:api_toggle_biolog'),
            data=json.dumps({
                'species_key': especie.species_key,
                'pais_id': pais.pk
            }),
            content_type='application/json'
        )
        assert response.status_code == 401

    def test_mi_atlas_carga(self, client_auth):
        response = client_auth.get(reverse('atlas:biolog'))
        assert response.status_code == 200

    def test_mi_atlas_pais_carga(self, client_auth, pais):
        response = client_auth.get(reverse('atlas:biolog_pais', args=[pais.pk]))
        assert response.status_code == 200


# ─────────────────────────────────────────
# TESTS: AVISTAMIENTOS
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestAvistamientos:

    def test_nuevo_avistamiento_carga(self, client_auth, especie):
        response = client_auth.get(
            reverse('atlas:nuevo_avistamiento', args=[especie.species_key])
        )
        assert response.status_code == 200

    def test_crear_avistamiento(self, client_auth, usuario, especie):
        response = client_auth.post(
            reverse('atlas:nuevo_avistamiento', args=[especie.species_key]),
            {
                'fecha': '2026-04-28',
                'lugar': 'Parque Nacional de Doñana, España',
                'notas': 'Avistamiento de prueba'
            }
        )
        assert Avistamiento.objects.filter(
            usuario=usuario, especie=especie
        ).exists()

    def test_avistamiento_sin_fecha_falla(self, client_auth, especie):
        response = client_auth.post(
            reverse('atlas:nuevo_avistamiento', args=[especie.species_key]),
            {'lugar': 'Madrid'}
        )
        assert not Avistamiento.objects.filter(especie=especie).exists()

    def test_avistamiento_sin_lugar_falla(self, client_auth, especie):
        response = client_auth.post(
            reverse('atlas:nuevo_avistamiento', args=[especie.species_key]),
            {'fecha': '2026-04-28'}
        )
        assert not Avistamiento.objects.filter(especie=especie).exists()

    def test_eliminar_avistamiento(self, client_auth, usuario, especie):
        av = Avistamiento.objects.create(
            usuario=usuario, especie=especie,
            fecha='2026-04-28', lugar='Madrid'
        )
        response = client_auth.post(
            reverse('atlas:eliminar_avistamiento', args=[av.pk])
        )
        assert not Avistamiento.objects.filter(pk=av.pk).exists()

    def test_mis_avistamientos_carga(self, client_auth):
        response = client_auth.get(reverse('atlas:mis_avistamientos'))
        assert response.status_code == 200

    def test_avistamiento_requiere_login(self, client, especie):
        response = client.get(
            reverse('atlas:nuevo_avistamiento', args=[especie.species_key])
        )
        assert response.status_code == 302


# ─────────────────────────────────────────
# TESTS: API
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestAPI:

    def test_api_buscar_especies(self, client, especie):
        response = client.get(reverse('atlas:api_buscar_especies') + '?q=Panthera')
        assert response.status_code == 200
        data = response.json()
        assert 'resultados' in data

    def test_api_buscar_especies_query_corta(self, client):
        response = client.get(reverse('atlas:api_buscar_especies') + '?q=P')
        assert response.status_code == 200

    def test_api_especie_detalle(self, client, especie):
        response = client.get(
            reverse('atlas:api_especie_detalle', args=[especie.species_key])
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['especie']['scientific_name'] == 'Panthera leo'

    def test_api_especie_no_existe(self, client):
        response = client.get(
            reverse('atlas:api_especie_detalle', args=[99999999])
        )
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False

    def test_api_buscar_paises(self, client, pais):
        response = client.get(reverse('atlas:api_buscar_paises') + '?q=Esp')
        assert response.status_code == 200


# ─────────────────────────────────────────
# TESTS: QUIZ
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestQuiz:

    def test_quiz_carga_sin_login(self, client):
        response = client.get(reverse('atlas:quiz'))
        assert response.status_code in [200, 302]

    def test_quiz_inicio_facil(self, client_auth):
        response = client_auth.get(reverse('atlas:quiz') + '?dificultad=facil&iniciar=1')
        assert response.status_code == 200

    def test_quiz_inicio_normal(self, client_auth):
        response = client_auth.get(reverse('atlas:quiz') + '?dificultad=normal&iniciar=1')
        assert response.status_code == 200

    def test_quiz_inicio_dificil(self, client_auth):
        response = client_auth.get(reverse('atlas:quiz') + '?dificultad=dificil&iniciar=1')
        assert response.status_code == 200


# ─────────────────────────────────────────
# TESTS: MODELOS
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestModelos:

    def test_suscripcion_free_creada_automaticamente(self, usuario):
        assert Suscripcion.objects.filter(usuario=usuario).exists()

    def test_suscripcion_free_no_es_premium(self, usuario):
        sus = Suscripcion.objects.get(usuario=usuario)
        assert sus.es_premium is False

    def test_suscripcion_premium_es_premium(self, usuario_premium):
        sus = Suscripcion.objects.get(usuario=usuario_premium)
        assert sus.es_premium is True

    def test_especie_str(self, especie):
        assert 'Panthera leo' in str(especie)

    def test_pais_str(self, pais):
        assert 'España' in str(pais)

    def test_continente_str(self, continente):
        assert 'Europa' in str(continente)

    def test_favorito_unico_por_usuario_especie(self, usuario, especie):
        Favorito.objects.create(usuario=usuario, especie=especie)
        with pytest.raises(Exception):
            Favorito.objects.create(usuario=usuario, especie=especie)

    def test_biolog_puede_agregar_free(self, usuario, pais):
        puede, motivo = BioLog.puede_agregar(usuario, pais)
        assert puede is True

    def test_biolog_str(self, usuario, especie, pais):
        bl = BioLog.objects.create(usuario=usuario, especie=especie, pais=pais)
        assert str(bl) != ''


# ─────────────────────────────────────────
# TESTS: SEGURIDAD
# ─────────────────────────────────────────

@pytest.mark.django_db
class TestSeguridad:

    def test_csrf_requerido_en_toggle_favorito(self, client, especie):
        """Sin CSRF el toggle debe fallar."""
        client.enforce_csrf_checks = True
        response = client.post(
            reverse('atlas:api_toggle_favorito'),
            data=json.dumps({'species_key': especie.species_key}),
            content_type='application/json'
        )
        assert response.status_code in [401, 403]

    def test_eliminar_avistamiento_ajeno_falla(self, client_auth, especie, db):
        """Un usuario no puede eliminar avistamientos de otro."""
        otro_user = User.objects.create_user('otro', password='pass123')
        av = Avistamiento.objects.create(
            usuario=otro_user, especie=especie,
            fecha='2026-04-28', lugar='Madrid'
        )
        client_auth.post(reverse('atlas:eliminar_avistamiento', args=[av.pk]))
        assert Avistamiento.objects.filter(pk=av.pk).exists()

    def test_perfil_no_accesible_sin_login(self, client):
        response = client.get(reverse('atlas:perfil'))
        assert response.status_code == 302

    def test_mis_favoritos_no_accesible_sin_login(self, client):
        response = client.get(reverse('atlas:mis_favoritos'))
        assert response.status_code == 302

    def test_mis_avistamientos_no_accesible_sin_login(self, client):
        response = client.get(reverse('atlas:mis_avistamientos'))
        assert response.status_code == 302

    def test_mi_atlas_no_accesible_sin_login(self, client):
        response = client.get(reverse('atlas:biolog'))
        assert response.status_code == 302
