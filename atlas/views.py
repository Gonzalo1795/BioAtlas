from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django.http import JsonResponse, Http404, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import (Continente, Pais, Especie, EspeciePais,
                     EspecieTerritorio, TerritorioEspecial,
                     Favorito, Avistamiento, BioLog, Suscripcion)
from .services import GBIFService, get_best_image

import json

LIMITE_FAVORITOS_FREE     = 20
LIMITE_AVISTAMIENTOS_FREE = 10

SUGERENCIAS = [
    "Panthera leo", "Aquila chrysaetos", "Quercus robur",
    "Ursus arctos", "Canis lupus", "Amanita muscaria"
]

REPTIL_CLASSES = ['Reptilia', 'Squamata', 'Testudines', 'Crocodylia', 'Rhynchocephalia']


# =======================================================================
# ÍNDICE Y GEOGRAFÍA
# =======================================================================

def index(request):
    continentes    = Continente.objects.all()
    paises         = Pais.objects.annotate(num_especies=Count("especies"))
    total_especies = Especie.objects.count()

    paises_data = [
        {
            "id":           p.id,
            "nombre":       p.nombre,
            "codigo":       p.codigo,
            "latitud":      p.latitud,
            "longitud":     p.longitud,
            "continente":   p.continente.nombre,
            "num_especies": p.num_especies,
        }
        for p in paises
    ]

    try:
        ant = TerritorioEspecial.objects.get(codigo='AQ')
        paises_data.append({
            "id":            f"territorio-{ant.pk}",
            "nombre":        ant.nombre,
            "codigo":        ant.codigo,
            "latitud":       ant.latitud,
            "longitud":      ant.longitud,
            "continente":    ant.continente.nombre if ant.continente else "Antártida",
            "num_especies":  Especie.objects.filter(territorios=ant).count(),
            "es_territorio": True,
        })
    except TerritorioEspecial.DoesNotExist:
        pass

    return render(request, "atlas/index.html", {
        "continentes":    continentes,
        "paises_json":    json.dumps(paises_data, ensure_ascii=True),
        "total_especies": total_especies,
    })


class ContinenteDetailView(DetailView):
    model               = Continente
    template_name       = "atlas/continente_detail.html"
    context_object_name = "continente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["paises"] = self.object.paises.annotate(
            num_especies=Count("especies")
        ).order_by("-num_especies")
        if self.object.codigo == 'AN':
            context["territorio_especial"] = TerritorioEspecial.objects.filter(
                continente=self.object
            ).first()
        return context


def _fetch_and_save_image(especie_pais):
    try:
        nombre = especie_pais.especie.canonical_name or especie_pais.especie.scientific_name
        result = get_best_image(
            scientific_name=nombre,
            country_name=especie_pais.pais.nombre,
            species_key=especie_pais.especie.species_key,
            country_code=especie_pais.pais.codigo,
        )
        especie_pais.image_url    = result["url"]
        especie_pais.image_source = result["source"] or "failed"
        especie_pais.save(update_fields=["image_url", "image_source"])
    except Exception as e:
        print(f"[imagen] Error para '{especie_pais.especie.scientific_name}': {e}")


class PaisDetailView(DetailView):
    model               = Pais
    template_name       = "atlas/pais_detail.html"
    context_object_name = "pais"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pais    = self.object

        if Especie.objects.filter(paises=pais).count() < 500:
            print(f"⚡ Sincronizando {pais.nombre} desde GBIF...")
            self._sync_especies(pais)

        especies_qs = Especie.objects.filter(paises=pais)

        kingdom     = self.request.GET.get("kingdom")
        phylum      = self.request.GET.get("phylum")
        class_name  = self.request.GET.get("class_name")
        order       = self.request.GET.get("order")
        family      = self.request.GET.get("family")
        search      = self.request.GET.get("search")
        iucn_status = self.request.GET.get('iucn_status')

        if iucn_status: especies_qs = especies_qs.filter(iucn_status=iucn_status)
        if kingdom:     especies_qs = especies_qs.filter(kingdom=kingdom)
        if phylum:      especies_qs = especies_qs.filter(phylum=phylum)
        if class_name:
            if class_name == 'Reptilia':
                especies_qs = especies_qs.filter(class_name__in=REPTIL_CLASSES)
            else:
                especies_qs = especies_qs.filter(class_name=class_name)
        if order:  especies_qs = especies_qs.filter(order=order)
        if family: especies_qs = especies_qs.filter(family=family)
        if search:
            especies_qs = especies_qs.filter(
                Q(scientific_name__icontains=search) |
                Q(canonical_name__icontains=search)  |
                Q(common_name__icontains=search)
            )

        especies_qs = especies_qs.order_by("scientific_name")

        try:
            page_number = int(self.request.GET.get("page", 1))
        except (ValueError, TypeError):
            page_number = 1

        paginator = Paginator(especies_qs, 25)
        page_obj  = paginator.get_page(page_number)

        keys_pagina = [e.species_key for e in page_obj.object_list]
        sin_imagen  = EspeciePais.objects.filter(
            pais=pais,
            especie__species_key__in=keys_pagina,
            image_url__isnull=True
        ).exclude(image_source="failed").select_related('especie', 'pais')

        if sin_imagen:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(_fetch_and_save_image, ep): ep for ep in sin_imagen}
                for future in as_completed(futures):
                    future.result()

        imagenes_pais = {}
        for ep in EspeciePais.objects.filter(pais=pais, especie__species_key__in=keys_pagina):
            if ep.image_url:
                imagenes_pais[ep.especie.species_key] = ep.image_url

        especies_favoritas = set()
        especies_biolog    = set()
        if self.request.user.is_authenticated:
            especies_favoritas = set(
                Favorito.objects.filter(
                    usuario=self.request.user,
                    especie__species_key__in=keys_pagina
                ).values_list('especie__species_key', flat=True)
            )
            especies_biolog = set(
                BioLog.objects.filter(
                    usuario=self.request.user,
                    pais=pais,
                    especie__species_key__in=keys_pagina
                ).values_list('especie__species_key', flat=True)
            )

        todas        = Especie.objects.filter(paises=pais)
        biolog_count = 0
        if self.request.user.is_authenticated:
            biolog_count = BioLog.objects.filter(
                usuario=self.request.user, pais=pais
            ).count()

        for especie in page_obj.object_list:
            especie._img_pais = imagenes_pais.get(especie.species_key) or especie.image_url

        context.update({
            "especies":           page_obj.object_list,
            "page_obj":           page_obj,
            "paginator":          paginator,
            "total_species":      todas.count(),
            "imagenes_pais":      imagenes_pais,
            "kingdoms":           todas.values_list("kingdom",    flat=True).distinct().order_by("kingdom"),
            "phylums":            todas.values_list("phylum",     flat=True).distinct().order_by("phylum"),
            "classes":            todas.values_list("class_name", flat=True).distinct().order_by("class_name"),
            "orders":             todas.values_list("order",      flat=True).distinct().order_by("order"),
            "families":           todas.values_list("family",     flat=True).distinct().order_by("family"),
            "especies_favoritas": especies_favoritas,
            "especies_biolog":    especies_biolog,
            "biolog_count":       biolog_count,
        })
        return context

    def _sync_especies(self, pais):
        total_guardadas = 0
        offset          = 0

        while total_guardadas < 5000:
            response_data = GBIFService.get_species_by_country_paginated(
                pais.codigo, limit=300, offset=offset
            )
            results = response_data.get("results", [])
            if not results:
                break

            for item in results:
                if item.get("kingdom") not in ["Animalia", "Plantae", "Fungi"]:
                    continue
                if not item.get("scientific_name") or not item.get("species_key"):
                    continue

                especie, _ = Especie.objects.get_or_create(
                    species_key=item["species_key"],
                    defaults={
                        "scientific_name": item["scientific_name"],
                        "canonical_name":  item.get("canonical_name", ""),
                        "kingdom":         item.get("kingdom", ""),
                        "phylum":          item.get("phylum", ""),
                        "class_name":      item.get("class_name", ""),
                        "order":           item.get("order", ""),
                        "family":          item.get("family", ""),
                        "genus":           item.get("genus", ""),
                        "iucn_status":     item.get("iucn_status"),
                        "image_url":       item.get("image_url"),
                        "image_source":    item.get("image_source"),
                    }
                )
                EspeciePais.objects.get_or_create(especie=especie, pais=pais)
                total_guardadas += 1
                if total_guardadas >= 5000:
                    break

            offset += 300


# =======================================================================
# ANTÁRTIDA — Territorio Especial
# =======================================================================

def antartida_detail(request):
    territorio  = get_object_or_404(TerritorioEspecial, codigo='AQ')
    especies_qs = Especie.objects.filter(territorios=territorio)

    kingdom    = request.GET.get('kingdom')
    class_name = request.GET.get('class_name')
    search     = request.GET.get('search')

    if kingdom:    especies_qs = especies_qs.filter(kingdom=kingdom)
    if class_name: especies_qs = especies_qs.filter(class_name=class_name)
    if search:
        especies_qs = especies_qs.filter(
            Q(scientific_name__icontains=search) |
            Q(canonical_name__icontains=search)  |
            Q(common_name__icontains=search)
        )

    especies_qs = especies_qs.order_by('scientific_name')
    paginator   = Paginator(especies_qs, 25)
    page_obj    = paginator.get_page(request.GET.get('page', 1))
    keys        = [e.species_key for e in page_obj.object_list]

    imagenes_territorio = {
        et.especie.species_key: et.image_url
        for et in EspecieTerritorio.objects.filter(
            territorio=territorio,
            especie__species_key__in=keys
        ).select_related('especie')
        if et.image_url
    }

    especies_favoritas = set()
    if request.user.is_authenticated:
        especies_favoritas = set(
            Favorito.objects.filter(
                usuario=request.user,
                especie__species_key__in=keys
            ).values_list('especie__species_key', flat=True)
        )

    todas = Especie.objects.filter(territorios=territorio)

    return render(request, 'atlas/antartida_detail.html', {
        'territorio':           territorio,
        'especies':             page_obj.object_list,
        'page_obj':             page_obj,
        'paginator':            paginator,
        'total_species':        todas.count(),
        'imagenes_territorio':  imagenes_territorio,
        'especies_favoritas':   especies_favoritas,
        'kingdoms':             todas.values_list('kingdom',    flat=True).distinct().order_by('kingdom'),
        'classes':              todas.values_list('class_name', flat=True).distinct().order_by('class_name'),
    })


# =======================================================================
# BÚSQUEDA
# =======================================================================

def buscar_especie(request):
    query = request.GET.get("q", "").strip()[:100]

    if not query:
        return render(request, "atlas/buscar_especie.html", {
            "query": "", "resultados": [], "total": 0, "sugerencias": SUGERENCIAS,
        })

    resultados = Especie.objects.filter(
        Q(scientific_name__icontains=query) |
        Q(canonical_name__icontains=query)  |
        Q(common_name__icontains=query)
    ).order_by("scientific_name")[:50]

    if not resultados.exists():
        gbif_data = GBIFService.search_species(query)
        if gbif_data:
            especie, _ = Especie.objects.get_or_create(
                species_key=gbif_data["key"],
                defaults={
                    "scientific_name": gbif_data["scientific_name"],
                    "canonical_name":  gbif_data.get("canonical_name", ""),
                    "kingdom":         gbif_data.get("kingdom", ""),
                    "phylum":          gbif_data.get("phylum", ""),
                    "class_name":      gbif_data.get("class", ""),
                    "order":           gbif_data.get("order", ""),
                    "family":          gbif_data.get("family", ""),
                    "genus":           gbif_data.get("genus", ""),
                    "image_url":       gbif_data.get("image_url"),
                    "image_source":    gbif_data.get("image_source"),
                    "iucn_status":     gbif_data.get("iucn_status"),
                }
            )
            resultados = Especie.objects.filter(species_key=especie.species_key)

    resultados = list(resultados)
    return render(request, "atlas/buscar_especie.html", {
        "query": query, "resultados": resultados,
        "total": len(resultados), "sugerencias": SUGERENCIAS,
    })


# =======================================================================
# APIs INTERNAS
# =======================================================================

def api_especie_detalle(request, species_key):
    especie = Especie.objects.filter(species_key=species_key).first()

    if not especie:
        gbif_data = GBIFService.get_species_detail(int(species_key))
        if gbif_data:
            return JsonResponse({"success": True, "es_favorito": False, "en_biolog": False, "especie": gbif_data})
        return JsonResponse({"success": False, "error": "Especie no encontrada"}, status=404)

    if not especie.image_url and especie.image_source != "failed":
        nombre = especie.canonical_name or especie.scientific_name
        result = get_best_image(nombre)
        especie.image_url    = result["url"]
        especie.image_source = result["source"] or "failed"
        especie.save(update_fields=["image_url", "image_source"])

    vernacular_data = GBIFService.safe_request(
        f"https://api.gbif.org/v1/species/{species_key}/vernacularNames"
    )
    spanish_names, other_names = [], []
    if vernacular_data:
        for v in vernacular_data.get("results", []):
            name = v.get("vernacularName")
            lang = v.get("language", "")
            if not name:
                continue
            if lang == "spa":
                spanish_names.append({"name": name, "language": "es"})
            else:
                other_names.append({"name": name, "language": lang})
    common_names = (spanish_names + other_names)[:10]

    lang        = request.GET.get("lang", "es")
    descripcion = especie.get_descripcion(lang)

    es_favorito = False
    en_biolog   = False
    pais_id     = None
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, especie=especie).exists()
        pais_id = request.GET.get("pais_id")
        if pais_id:
            en_biolog = BioLog.objects.filter(
                usuario=request.user, especie=especie, pais_id=pais_id
            ).exists()

    return JsonResponse({
        "success": True, "es_favorito": es_favorito,
        "en_biolog": en_biolog, "pais_id": pais_id,
        "especie": {
            "scientific_name": especie.scientific_name,
            "canonical_name":  especie.canonical_name,
            "common_name":     especie.common_name or "",
            "iucn_status":     especie.iucn_status or "",
            "kingdom":         especie.kingdom,
            "phylum":          especie.phylum,
            "class":           especie.class_name,
            "order":           especie.order,
            "family":          especie.family,
            "genus":           especie.genus,
            "image_url":       especie.image_url,
            "image_source":    especie.image_source,
            "common_names":    common_names,
            "description":     descripcion,
        }
    })


@require_POST
def api_toggle_favorito(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Debes iniciar sesión"}, status=401)

    try:
        data        = json.loads(request.body)
        species_key = int(data.get("species_key"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"success": False, "error": "Datos inválidos"}, status=400)

    especie = Especie.objects.filter(species_key=species_key).first()
    if not especie:
        return JsonResponse({"success": False, "error": "Especie no encontrada"}, status=404)

    favorito = Favorito.objects.filter(usuario=request.user, especie=especie).first()
    if favorito:
        favorito.delete()
        return JsonResponse({"success": True, "action": "removed", "es_favorito": False})

    suscripcion = Suscripcion.get_or_create_for_user(request.user)
    if not suscripcion.es_premium:
        if Favorito.objects.filter(usuario=request.user).count() >= LIMITE_FAVORITOS_FREE:
            return JsonResponse({
                "success": False, "limite": True,
                "error": f"Con el plan gratuito puedes tener hasta {LIMITE_FAVORITOS_FREE} favoritos. Hazte Premium para tener favoritos ilimitados.",
            }, status=403)

    Favorito.objects.create(usuario=request.user, especie=especie)
    return JsonResponse({"success": True, "action": "added", "es_favorito": True})


@require_POST
def api_toggle_biolog(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Debes iniciar sesión"}, status=401)

    try:
        data        = json.loads(request.body)
        species_key = int(data.get("species_key"))
        pais_id     = int(data.get("pais_id"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"success": False, "error": "Datos inválidos"}, status=400)

    especie = Especie.objects.filter(species_key=species_key).first()
    pais    = Pais.objects.filter(id=pais_id).first()

    if not especie or not pais:
        return JsonResponse({"success": False, "error": "Especie o país no encontrado"}, status=404)

    entrada = BioLog.objects.filter(usuario=request.user, especie=especie, pais=pais).first()
    if entrada:
        entrada.delete()
        return JsonResponse({"success": True, "action": "removed", "en_biolog": False})

    puede, motivo = BioLog.puede_agregar(request.user, pais)
    if not puede:
        return JsonResponse({"success": False, "limite": True, "error": motivo}, status=403)

    BioLog.objects.create(usuario=request.user, especie=especie, pais=pais)
    total = BioLog.objects.filter(usuario=request.user, pais=pais).count()
    return JsonResponse({"success": True, "action": "added", "en_biolog": True, "total_pais": total})


def api_buscar_especies(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 1:
        return JsonResponse({"resultados": []})

    especies = list(Especie.objects.filter(
        Q(scientific_name__istartswith=query) |
        Q(canonical_name__istartswith=query)  |
        Q(common_name__istartswith=query)
    ).values("species_key", "scientific_name", "canonical_name", "kingdom", "image_url"
    ).order_by("scientific_name").distinct()[:10])

    if len(especies) < 10:
        keys_vistos = {e["species_key"] for e in especies}
        mas = list(Especie.objects.filter(
            Q(scientific_name__icontains=query) |
            Q(canonical_name__icontains=query)  |
            Q(common_name__icontains=query)
        ).exclude(species_key__in=keys_vistos
        ).values("species_key", "scientific_name", "canonical_name", "kingdom", "image_url"
        ).order_by("scientific_name").distinct()[:10 - len(especies)])
        especies += mas

    return JsonResponse({"resultados": especies}, headers={"Cache-Control": "no-store"})


def api_pais_by_code(request):
    code = request.GET.get('code', '').upper()
    pais = Pais.objects.filter(codigo=code).first()
    if pais:
        return JsonResponse({'pais_id': pais.id, 'nombre': pais.nombre})
    return JsonResponse({'pais_id': None})


# =======================================================================
# AUTENTICACIÓN
# =======================================================================

def registro(request):
    if request.user.is_authenticated:
        return redirect('atlas:perfil')

    error = None
    if request.method == "POST":
        username  = request.POST.get("username", "").strip()
        email     = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not username or not password1:
            error = "El nombre de usuario y la contraseña son obligatorios."
        elif password1 != password2:
            error = "Las contraseñas no coinciden."
        elif len(password1) < 6:
            error = "La contraseña debe tener al menos 6 caracteres."
        elif User.objects.filter(username=username).exists():
            error = "Ese nombre de usuario ya está en uso."
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            Suscripcion.objects.create(usuario=user)
            login(request, user)
            return redirect('atlas:perfil')

    return render(request, "atlas/registro.html", {"error": error})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('atlas:perfil')

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user     = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get("next", "/perfil/"))
        else:
            error = "Usuario o contraseña incorrectos."

    return render(request, "atlas/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect('atlas:index')


# =======================================================================
# PERFIL Y COLECCIÓN PERSONAL
# =======================================================================

@login_required(login_url='/login/')
def perfil(request):
    suscripcion           = Suscripcion.get_or_create_for_user(request.user)
    num_favoritos         = Favorito.objects.filter(usuario=request.user).count()
    num_avistamientos     = Avistamiento.objects.filter(usuario=request.user).count()
    num_biolog            = BioLog.objects.filter(usuario=request.user).count()
    paises_biolog         = BioLog.objects.filter(usuario=request.user).values('pais').distinct().count()
    ultimos_avistamientos = Avistamiento.objects.filter(
        usuario=request.user
    ).select_related('especie').order_by('-fecha')[:5]

    return render(request, "atlas/perfil.html", {
        "suscripcion":           suscripcion,
        "num_favoritos":         num_favoritos,
        "num_avistamientos":     num_avistamientos,
        "num_biolog":            num_biolog,
        "paises_biolog":         paises_biolog,
        "ultimos_avistamientos": ultimos_avistamientos,
        "limite_favoritos":      LIMITE_FAVORITOS_FREE,
        "limite_avistamientos":  LIMITE_AVISTAMIENTOS_FREE,
        "limite_paises_atlas":   BioLog.LIMITE_PAISES_FREE,
        "limite_especies_atlas": BioLog.LIMITE_ESPECIES_FREE,
    })


@login_required(login_url='/login/')
def mis_favoritos(request):
    favoritos = Favorito.objects.filter(
        usuario=request.user
    ).select_related('especie').order_by('-created_at')
    paginator = Paginator(favoritos, 25)
    page_obj  = paginator.get_page(request.GET.get("page", 1))
    return render(request, "atlas/mis_favoritos.html", {
        "page_obj": page_obj, "paginator": paginator, "total": favoritos.count(),
    })


@login_required(login_url='/login/')
def mis_avistamientos(request):
    avistamientos = Avistamiento.objects.filter(
        usuario=request.user
    ).select_related('especie').order_by('-fecha')
    paginator = Paginator(avistamientos, 20)
    page_obj  = paginator.get_page(request.GET.get("page", 1))
    return render(request, "atlas/mis_avistamientos.html", {
        "page_obj": page_obj, "paginator": paginator, "total": avistamientos.count(),
    })


@login_required(login_url='/login/')
def nuevo_avistamiento(request, species_key):
    especie = Especie.objects.filter(species_key=species_key).first()
    if not especie:
        raise Http404

    suscripcion      = Suscripcion.get_or_create_for_user(request.user)
    limite_alcanzado = (
        not suscripcion.es_premium and
        Avistamiento.objects.filter(usuario=request.user).count() >= LIMITE_AVISTAMIENTOS_FREE
    )

    error = None
    if request.method == "POST":
        if limite_alcanzado:
            error = f"Con el plan gratuito puedes registrar hasta {LIMITE_AVISTAMIENTOS_FREE} avistamientos."
        else:
            fecha = request.POST.get("fecha", "").strip()
            lugar = request.POST.get("lugar", "").strip()
            notas = request.POST.get("notas", "").strip()
            foto  = request.FILES.get("foto")
            if not fecha or not lugar:
                error = "La fecha y el lugar son obligatorios."
            else:
                Avistamiento.objects.create(
                    usuario=request.user, especie=especie,
                    fecha=fecha, lugar=lugar, notas=notas, foto=foto,
                )
                return redirect('atlas:mis_avistamientos')

    return render(request, "atlas/nuevo_avistamiento.html", {
        "especie": especie, "error": error,
        "limite_alcanzado": limite_alcanzado,
        "suscripcion": suscripcion, "limite": LIMITE_AVISTAMIENTOS_FREE,
    })


@login_required(login_url='/login/')
@require_POST
def eliminar_avistamiento(request, pk):
    avistamiento = get_object_or_404(Avistamiento, pk=pk, usuario=request.user)
    avistamiento.delete()
    return redirect('atlas:mis_avistamientos')


@login_required(login_url='/login/')
def biolog(request):
    suscripcion = Suscripcion.get_or_create_for_user(request.user)

    paises_data = (
        BioLog.objects.filter(usuario=request.user)
        .values('pais__id', 'pais__nombre', 'pais__codigo')
        .annotate(num_especies=Count('id'))
        .order_by('-num_especies')
    )

    paises_enriquecidos = []
    for p in paises_data:
        total_pais = Especie.objects.filter(paises__id=p['pais__id']).count()
        paises_enriquecidos.append({
            "pais_id":       p['pais__id'],
            "nombre":        p['pais__nombre'],
            "codigo":        p['pais__codigo'],
            "coleccionadas": p['num_especies'],
            "total":         total_pais,
            "porcentaje":    round(p['num_especies'] / total_pais * 100, 1) if total_pais else 0,
        })

    return render(request, "atlas/biolog.html", {
        "suscripcion":     suscripcion,
        "paises":          paises_enriquecidos,
        "total_especies":  BioLog.objects.filter(usuario=request.user).count(),
        "total_paises":    len(paises_enriquecidos),
        "limite_paises":   BioLog.LIMITE_PAISES_FREE,
        "limite_especies": BioLog.LIMITE_ESPECIES_FREE,
    })


@login_required(login_url='/login/')
def biolog_pais(request, pais_pk):
    pais        = get_object_or_404(Pais, pk=pais_pk)
    suscripcion = Suscripcion.get_or_create_for_user(request.user)

    entradas = (
        BioLog.objects.filter(usuario=request.user, pais=pais)
        .select_related('especie').order_by('-created_at')
    )

    kingdom    = request.GET.get("kingdom", "")
    class_name = request.GET.get("class_name", "")
    iucn       = request.GET.get("iucn_status", "")
    search     = request.GET.get("search", "").strip()[:100]

    if kingdom: entradas = entradas.filter(especie__kingdom=kingdom)
    if class_name:
        if class_name == 'Reptilia':
            entradas = entradas.filter(especie__class_name__in=REPTIL_CLASSES)
        else:
            entradas = entradas.filter(especie__class_name=class_name)
    if iucn:   entradas = entradas.filter(especie__iucn_status=iucn)
    if search:
        entradas = entradas.filter(
            Q(especie__scientific_name__icontains=search) |
            Q(especie__canonical_name__icontains=search)  |
            Q(especie__common_name__icontains=search)
        )

    paginator           = Paginator(entradas, 24)
    page_obj            = paginator.get_page(request.GET.get("page", 1))
    total_coleccionadas = BioLog.objects.filter(usuario=request.user, pais=pais).count()
    total_pais          = Especie.objects.filter(paises=pais).count()
    porcentaje          = round(total_coleccionadas / total_pais * 100, 1) if total_pais else 0

    keys_pagina   = [e.especie.species_key for e in page_obj.object_list]
    imagenes_pais = {}
    for ep in EspeciePais.objects.filter(pais=pais, especie__species_key__in=keys_pagina):
        if ep.image_url:
            imagenes_pais[ep.especie.species_key] = ep.image_url

    especies_favoritas = set(
        Favorito.objects.filter(
            usuario=request.user,
            especie__species_key__in=keys_pagina
        ).values_list('especie__species_key', flat=True)
    )

    todas_entradas = BioLog.objects.filter(usuario=request.user, pais=pais)
    kingdoms_disponibles = (
        todas_entradas.values_list('especie__kingdom', flat=True)
        .distinct().order_by('especie__kingdom')
    )
    classes_disponibles = (
        todas_entradas.values_list('especie__class_name', flat=True)
        .distinct().order_by('especie__class_name')
    )

    return render(request, "atlas/biolog_pais.html", {
        "pais":                  pais,
        "suscripcion":           suscripcion,
        "page_obj":              page_obj,
        "paginator":             paginator,
        "total_coleccionadas":   total_coleccionadas,
        "total_pais":            total_pais,
        "porcentaje":            porcentaje,
        "imagenes_pais":         imagenes_pais,
        "especies_favoritas":    especies_favoritas,
        "kingdoms_disponibles":  kingdoms_disponibles,
        "classes_disponibles":   classes_disponibles,
        "kingdom_filtro":        kingdom,
        "class_name_filtro":     class_name,
        "iucn_filtro":           iucn,
        "search_filtro":         search,
        "limite_especies":       BioLog.LIMITE_ESPECIES_FREE,
    })


# =======================================================================
# PREMIUM Y STRIPE
# =======================================================================

def premium(request):
    suscripcion = None
    if request.user.is_authenticated:
        suscripcion = Suscripcion.get_or_create_for_user(request.user)
    return render(request, "atlas/premium.html", {"suscripcion": suscripcion})


@login_required(login_url='/login/')
def premium_checkout(request):
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        suscripcion    = Suscripcion.get_or_create_for_user(request.user)

        if not suscripcion.stripe_customer_id:
            customer = stripe.Customer.create(
                email=request.user.email or f"{request.user.username}@bioatlas.com",
                name=request.user.username,
                metadata={"user_id": request.user.id},
            )
            suscripcion.stripe_customer_id = customer.id
            suscripcion.save(update_fields=["stripe_customer_id"])

        session = stripe.checkout.Session.create(
            customer=suscripcion.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
            mode="subscription",
            success_url=request.build_absolute_uri("/premium/success/") + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri("/premium/cancel/"),
            metadata={"user_id": request.user.id},
        )
        return redirect(session.url)

    except Exception as e:
        return render(request, "atlas/premium.html", {
            "error": f"Error al iniciar el pago: {e}",
            "suscripcion": Suscripcion.get_or_create_for_user(request.user),
        })


@login_required(login_url='/login/')
def premium_success(request):
    return render(request, "atlas/premium_success.html")


@login_required(login_url='/login/')
def premium_cancel(request):
    return redirect('atlas:premium')


@login_required(login_url='/login/')
@require_POST
def cancelar_suscripcion(request):
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        suscripcion    = Suscripcion.get_or_create_for_user(request.user)
        if suscripcion.stripe_subscription_id:
            stripe.Subscription.modify(
                suscripcion.stripe_subscription_id, cancel_at_period_end=True
            )
        suscripcion.estado = "cancelled"
        suscripcion.save(update_fields=["estado"])
    except Exception:
        pass
    return redirect('atlas:perfil')


@csrf_exempt
def stripe_webhook(request):
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(
            request.body,
            request.META.get("HTTP_STRIPE_SIGNATURE", ""),
            settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session     = event["data"]["object"]
        customer_id = session.get("customer")
        sub_id      = session.get("subscription")
        try:
            suscripcion = Suscripcion.objects.get(stripe_customer_id=customer_id)
            suscripcion.plan                   = "premium"
            suscripcion.estado                 = "active"
            suscripcion.stripe_subscription_id = sub_id
            suscripcion.save()
        except Suscripcion.DoesNotExist:
            pass

    elif event["type"] == "customer.subscription.deleted":
        sub_id = event["data"]["object"]["id"]
        try:
            suscripcion = Suscripcion.objects.get(stripe_subscription_id=sub_id)
            suscripcion.plan   = "free"
            suscripcion.estado = "cancelled"
            suscripcion.save()
        except Suscripcion.DoesNotExist:
            pass

    return HttpResponse(status=200)


def api_buscar_paises(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'paises': []})
    paises = Pais.objects.filter(nombre__icontains=q).annotate(
        num_especies=Count('especies')
    ).values('id', 'nombre', 'codigo', 'continente__nombre', 'num_especies')[:8]
    return JsonResponse({'paises': [
        {
            'id':           p['id'],
            'nombre':       p['nombre'],
            'codigo':       p['codigo'],
            'continente':   p['continente__nombre'] or '',
            'num_especies': p['num_especies'] or 0,
        } for p in paises
    ]})


def error_404(request, exception=None):
    return render(request, '404.html', status=404)


def error_500(request):
    return render(request, '500.html', status=500)

def terminos(request):
    return render(request, 'atlas/terminos.html')

def privacidad(request):
    return render(request, 'atlas/privacidad.html')

def cookies(request):
    return render(request, 'atlas/cookies.html')

def contacto(request):
    return render(request, 'atlas/contacto.html')