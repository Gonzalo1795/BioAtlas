import requests
import time
from typing import Dict, Optional, List


# ═══════════════════════════════════════════════════════════════════════
# FILTROS DE CALIDAD DE IMAGEN
# Funciones que determinan si una imagen es una foto real en hábitat
# natural o si es una ilustración, espécimen de museo, montaje, etc.
# El objetivo es mostrar siempre fotos reales y atractivas.
# ═══════════════════════════════════════════════════════════════════════

# Keywords en la URL que indican imágenes NO reales
BAD_KEYWORDS = [
    # Especímenes de museo / colecciones
    "label", "specimen", "sheet", "collection", "herbarium", "museum",
    "holotype", "syntype", "paratype", "type specimen",
    # Ilustraciones y arte digital
    "illustration", "illustrat", "drawing", "painting", "artwork",
    "cartoon", "animated", "animation", "clipart", "vector",
    "diagram", "sketch", "render", "3d", "cgi",
    # Montajes / composites
    "composite", "montage", "collage", "photoshop", "manipulation",
    # Fondos blancos / estudio
    "white_background", "white-background", "cutout", "isolated",
    # Bancos de imágenes comerciales
    "shutterstock", "gettyimages", "alamy", "dreamstime",
    "depositphotos", "istockphoto", "123rf",
]

# Keywords en la atribución que indican ilustrador en vez de fotógrafo
BAD_ATTRIBUTION_KEYWORDS = [
    "illustrat", "drawn by", "painted by", "artwork by", "digital art",
]

# Mapa nombre de país → código ISO para iNaturalist
COUNTRY_CODE_MAP = {
    "Afghanistan": "AF", "Albania": "AL", "Algeria": "DZ", "Angola": "AO",
    "Argentina": "AR", "Australia": "AU", "Austria": "AT", "Bangladesh": "BD",
    "Belgium": "BE", "Bolivia": "BO", "Brazil": "BR", "Bulgaria": "BG",
    "Cambodia": "KH", "Cameroon": "CM", "Canada": "CA", "Chile": "CL",
    "China": "CN", "Colombia": "CO", "Congo": "CG", "Costa Rica": "CR",
    "Croatia": "HR", "Cuba": "CU", "Czech Republic": "CZ", "Denmark": "DK",
    "Ecuador": "EC", "Egypt": "EG", "El Salvador": "SV", "Ethiopia": "ET",
    "Finland": "FI", "France": "FR", "Germany": "DE", "Ghana": "GH",
    "Greece": "GR", "Guatemala": "GT", "Honduras": "HN", "Hungary": "HU",
    "India": "IN", "Indonesia": "ID", "Iran": "IR", "Iraq": "IQ",
    "Ireland": "IE", "Israel": "IL", "Italy": "IT", "Japan": "JP",
    "Jordan": "JO", "Kazakhstan": "KZ", "Kenya": "KE", "Madagascar": "MG",
    "Malaysia": "MY", "Mali": "ML", "Mexico": "MX", "Morocco": "MA",
    "Mozambique": "MZ", "Myanmar": "MM", "Nepal": "NP", "Netherlands": "NL",
    "New Zealand": "NZ", "Nicaragua": "NI", "Nigeria": "NG", "Norway": "NO",
    "Pakistan": "PK", "Panama": "PA", "Papua New Guinea": "PG", "Paraguay": "PY",
    "Peru": "PE", "Philippines": "PH", "Poland": "PL", "Portugal": "PT",
    "Romania": "RO", "Russia": "RU", "Rwanda": "RW", "Saudi Arabia": "SA",
    "Senegal": "SN", "Serbia": "RS", "Slovakia": "SK", "Slovenia": "SI",
    "Somalia": "SO", "South Africa": "ZA", "South Korea": "KR", "Spain": "ES",
    "Sri Lanka": "LK", "Sudan": "SD", "Sweden": "SE", "Switzerland": "CH",
    "Syria": "SY", "Taiwan": "TW", "Tanzania": "TZ", "Thailand": "TH",
    "Tunisia": "TN", "Turkey": "TR", "Uganda": "UG", "Ukraine": "UA",
    "United Kingdom": "GB", "United States": "US", "Uruguay": "UY",
    "Uzbekistan": "UZ", "Venezuela": "VE", "Vietnam": "VN", "Zambia": "ZM",
    "Zimbabwe": "ZW",
}


def _is_bad_image(url: str) -> bool:
    """Devuelve True si la URL contiene keywords de imágenes no reales."""
    if not url:
        return True
    url_lower = url.lower()
    return any(kw in url_lower for kw in BAD_KEYWORDS)


def _is_real_photo(url: str, attribution: str = "") -> bool:
    """
    Devuelve True si la imagen parece una foto real en hábitat natural.
    Filtra ilustraciones, montajes, especímenes de museo y bancos comerciales.
    """
    if not url:
        return False
    if _is_bad_image(url):
        return False
    attr_lower = attribution.lower()
    for kw in BAD_ATTRIBUTION_KEYWORDS:
        if kw in attr_lower:
            return False
    return True


def _upgrade_url_quality(url: str) -> str:
    """Sube la resolución de una URL de iNaturalist a la máxima disponible."""
    return (url
        .replace("/square.", "/large.")
        .replace("/medium.", "/large.")
        .replace("/small.", "/large.")
    )


# ═══════════════════════════════════════════════════════════════════════
# FUENTES DE IMÁGENES
# Pipeline de 6 fuentes ordenadas por calidad y especificidad geográfica.
# Se prioriza siempre la foto más específica del país y la más votada
# por la comunidad científica (observaciones verificadas).
# ═══════════════════════════════════════════════════════════════════════

def _get_image_inaturalist_by_country(scientific_name: str, country_name: str) -> Optional[str]:
    """
    FUENTE 1: iNaturalist observaciones verificadas del país.
    Busca fotos reales de la especie tomadas en ese país concreto,
    ordenadas por votos de la comunidad (las más espectaculares primero).
    """
    country_code = COUNTRY_CODE_MAP.get(country_name)
    if not country_code:
        return None

    try:
        # Paso 1: obtener el taxon_id de la especie
        r = requests.get(
            "https://api.inaturalist.org/v1/taxa",
            params={"q": scientific_name, "per_page": 1},
            timeout=5
        )
        r.raise_for_status()
        taxa = r.json().get("results", [])
        if not taxa:
            return None
        taxon_id = taxa[0]["id"]

        # Paso 2: observaciones verificadas en ese país, ordenadas por votos
        r2 = requests.get(
            "https://api.inaturalist.org/v1/observations",
            params={
                "taxon_id":      taxon_id,
                "country_code":  country_code.lower(),
                "photos":        "true",
                "per_page":      20,
                "order":         "votes",
                "order_by":      "votes",
                "quality_grade": "research",
                "photo_license": "cc-by,cc-by-nc,cc-by-sa,cc-by-nc-sa,cc0",
            },
            timeout=8
        )
        r2.raise_for_status()

        for obs in r2.json().get("results", []):
            for photo in obs.get("photos", []):
                url = photo.get("url", "")
                attribution = photo.get("attribution", "")
                if _is_real_photo(url, attribution):
                    return _upgrade_url_quality(url)

    except Exception:
        pass
    return None


def _get_inaturalist_data(scientific_name: str) -> Dict:
    """
    FUENTE 2: iNaturalist foto global del taxón.
    Obtiene la mejor foto global de la especie y su nombre común.
    Primero intenta la observación más votada, luego la foto por defecto.
    """
    try:
        r = requests.get(
            "https://api.inaturalist.org/v1/taxa",
            params={"q": scientific_name, "per_page": 1, "locale": "es"},
            timeout=5
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return {"image_url": None, "common_name": None}

        taxon       = results[0]
        taxon_id    = taxon["id"]
        common_name = (
            taxon.get("preferred_common_name") or
            taxon.get("english_common_name") or None
        )
        if common_name:
            common_name = common_name.capitalize()

        # Intentar la observación más votada globalmente
        r2 = requests.get(
            "https://api.inaturalist.org/v1/observations",
            params={
                "taxon_id":      taxon_id,
                "photos":        "true",
                "per_page":      10,
                "order":         "votes",
                "order_by":      "votes",
                "quality_grade": "research",
            },
            timeout=6
        )
        r2.raise_for_status()

        for obs in r2.json().get("results", []):
            for photo in obs.get("photos", []):
                url         = photo.get("url", "")
                attribution = photo.get("attribution", "")
                if _is_real_photo(url, attribution):
                    return {"image_url": _upgrade_url_quality(url), "common_name": common_name}

        # Fallback: foto por defecto del taxón
        photo = taxon.get("default_photo")
        if photo:
            url = photo.get("medium_url") or photo.get("square_url") or ""
            if _is_real_photo(url):
                return {"image_url": _upgrade_url_quality(url), "common_name": common_name}

    except Exception:
        pass
    return {"image_url": None, "common_name": None}


def _get_image_inaturalist(scientific_name: str) -> Optional[str]:
    """Wrapper que solo devuelve la URL de imagen de iNaturalist."""
    return _get_inaturalist_data(scientific_name).get("image_url")


def _get_image_wikimedia(scientific_name: str, country_name: Optional[str] = None) -> Optional[str]:
    """
    FUENTE 3: Wikimedia Commons.
    Busca la mejor foto disponible en Commons. Si se pasa country_name,
    intenta primero con el país para una foto más específica.
    """
    queries = []
    if country_name:
        queries.append(f"{scientific_name} {country_name}")
    queries.append(scientific_name)

    for query in queries:
        try:
            r = requests.get(
                "https://commons.wikimedia.org/w/api.php",
                params={
                    "action":        "query",
                    "generator":     "search",
                    "gsrsearch":     f"filetype:bitmap {query}",
                    "gsrnamespace":  6,
                    "gsrlimit":      10,
                    "prop":          "imageinfo",
                    "iiprop":        "url|mime|size",
                    "iiurlwidth":    800,
                    "format":        "json",
                },
                timeout=6
            )
            r.raise_for_status()
            pages = r.json().get("query", {}).get("pages", {})

            best_url  = None
            best_size = 0

            for page in pages.values():
                imageinfo = page.get("imageinfo", [{}])[0]
                mime      = imageinfo.get("mime", "")
                url       = imageinfo.get("thumburl") or imageinfo.get("url", "")
                size      = imageinfo.get("size", 0)

                if mime not in ("image/jpeg", "image/png"):
                    continue
                if not _is_real_photo(url):
                    continue
                if size > best_size:
                    best_size = size
                    best_url  = url

            if best_url:
                return best_url

        except Exception:
            pass

    # Fallback: Wikipedia pageimages
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action":      "query",
                "titles":      scientific_name,
                "prop":        "pageimages",
                "pithumbsize": 800,
                "format":      "json",
                "redirects":   1,
            },
            timeout=4
        )
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            thumb = page.get("thumbnail", {}).get("source")
            if thumb and _is_real_photo(thumb):
                return thumb
    except Exception:
        pass

    return None


def _get_image_gbif_by_country(species_key: int, country_code: str) -> Optional[str]:
    """
    FUENTE 4: GBIF occurrences geolocalizadas del país.
    Las fotos de GBIF son fotos de campo reales tomadas por observadores.
    """
    try:
        r = requests.get(
            "https://api.gbif.org/v1/occurrence/search",
            params={
                "taxonKey":  species_key,
                "country":   country_code.upper(),
                "mediaType": "StillImage",
                "limit":     10,
            },
            timeout=6
        )
        r.raise_for_status()
        for occ in r.json().get("results", []):
            for m in occ.get("media", []):
                url = m.get("identifier", "")
                if url and _is_real_photo(url):
                    return url
    except Exception:
        pass
    return None


def _get_image_eol(scientific_name: str) -> Optional[str]:
    """
    FUENTE 5: Encyclopedia of Life (EOL).
    Fuente de último recurso con una gran colección de imágenes de especies.
    """
    try:
        r = requests.get(
            "https://eol.org/api/search/1.0.json",
            params={"q": scientific_name, "page": 1},
            timeout=4
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return None

        eol_id = results[0]["id"]
        r2 = requests.get(
            f"https://eol.org/api/pages/1.0/{eol_id}.json",
            params={"images_per_page": 5, "videos_per_page": 0, "details": True},
            timeout=4
        )
        r2.raise_for_status()
        for obj in r2.json().get("taxonConcept", {}).get("dataObjects", []):
            if obj.get("dataType") == "http://purl.org/dc/dcmitype/StillImage":
                img = obj.get("eolMediaURL") or obj.get("mediaURL")
                if img and _is_real_photo(img):
                    return img
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL DE IMÁGENES
# Orquesta las 5 fuentes en orden de prioridad.
# Siempre prioriza fotos específicas del país antes que fotos globales.
# ═══════════════════════════════════════════════════════════════════════

def get_best_image(scientific_name: str,
                   gbif_image_url: Optional[str] = None,
                   country_name: Optional[str] = None,
                   species_key: Optional[int] = None,
                   country_code: Optional[str] = None) -> Dict:
    """
    Pipeline completo de imágenes. Orden de prioridad:
    1. iNaturalist observaciones verificadas del país (más votadas)
    2. GBIF occurrences del país (fotos de campo geolocalizadas)
    3. iNaturalist observaciones verificadas globales
    4. Foto GBIF genérica pasada como parámetro
    5. Wikimedia Commons (con y sin país)
    6. EOL
    """
    # 1. iNaturalist por país
    if country_name:
        url = _get_image_inaturalist_by_country(scientific_name, country_name)
        if url:
            return {"url": url, "source": "inaturalist_country"}

    # 2. GBIF fotos del país
    if species_key and country_code:
        url = _get_image_gbif_by_country(species_key, country_code)
        if url:
            return {"url": url, "source": "gbif_country"}

    # 3. iNaturalist global
    url = _get_image_inaturalist(scientific_name)
    if url:
        return {"url": url, "source": "inaturalist"}

    # 4. Foto GBIF genérica
    if gbif_image_url and _is_real_photo(gbif_image_url):
        return {"url": gbif_image_url, "source": "gbif"}

    # 5. Wikimedia Commons
    url = _get_image_wikimedia(scientific_name, country_name)
    if url:
        return {"url": url, "source": "wikimedia"}

    # 6. EOL
    url = _get_image_eol(scientific_name)
    if url:
        return {"url": url, "source": "eol"}

    return {"url": None, "source": None}


def get_best_image_and_common_name(scientific_name: str,
                                   gbif_image_url: Optional[str] = None,
                                   country_name: Optional[str] = None,
                                   species_key: Optional[int] = None,
                                   country_code: Optional[str] = None) -> Dict:
    """
    Como get_best_image pero también devuelve el nombre común en español.
    Se usa al crear una especie nueva para guardar nombre común e imagen a la vez.
    """
    inat_data   = _get_inaturalist_data(scientific_name)
    common_name = inat_data.get("common_name")
    inat_url    = inat_data.get("image_url")

    if country_name:
        url = _get_image_inaturalist_by_country(scientific_name, country_name)
        if url:
            return {"url": url, "source": "inaturalist_country", "common_name": common_name}

    if species_key and country_code:
        url = _get_image_gbif_by_country(species_key, country_code)
        if url:
            return {"url": url, "source": "gbif_country", "common_name": common_name}

    if inat_url:
        return {"url": inat_url, "source": "inaturalist", "common_name": common_name}

    if gbif_image_url and _is_real_photo(gbif_image_url):
        return {"url": gbif_image_url, "source": "gbif", "common_name": common_name}

    url = _get_image_wikimedia(scientific_name, country_name)
    if url:
        return {"url": url, "source": "wikimedia", "common_name": common_name}

    url = _get_image_eol(scientific_name)
    if url:
        return {"url": url, "source": "eol", "common_name": common_name}

    return {"url": None, "source": None, "common_name": common_name}


# ═══════════════════════════════════════════════════════════════════════
# WIKIPEDIA — DESCRIPCIONES MULTIIDIOMA
# Obtiene el primer párrafo del artículo de Wikipedia de una especie
# en los tres idiomas del proyecto (ES, EN, FR).
# ═══════════════════════════════════════════════════════════════════════

def get_wikipedia_description(scientific_name: str, common_name: Optional[str] = None) -> Dict:
    """
    Obtiene el primer párrafo de Wikipedia para una especie en ES, EN y FR.
    Intenta primero con el nombre científico y luego con el nombre común.
    Devuelve un dict: {"es": "...", "en": "...", "fr": "..."}
    """
    descripciones = {}
    idiomas = {
        "es": ["es.wikipedia.org", scientific_name, common_name],
        "en": ["en.wikipedia.org", scientific_name, common_name],
        "fr": ["fr.wikipedia.org", scientific_name, common_name],
    }

    for lang, (dominio, sci_name, com_name) in idiomas.items():
        texto = _get_wiki_extract(dominio, sci_name)
        if not texto and com_name:
            texto = _get_wiki_extract(dominio, com_name)
        if texto:
            descripciones[lang] = texto

    return descripciones


def _get_wiki_extract(dominio: str, titulo: str) -> Optional[str]:
    """
    Obtiene el primer párrafo de un artículo de Wikipedia.
    Limpia el texto eliminando paréntesis de pronunciación y referencias.
    """
    if not titulo:
        return None
    try:
        r = requests.get(
            f"https://{dominio}/w/api.php",
            params={
                "action":        "query",
                "titles":        titulo,
                "prop":          "extracts",
                "exintro":       True,
                "explaintext":   True,
                "exsentences":   3,   # Solo las primeras 3 frases
                "redirects":     1,
                "format":        "json",
            },
            timeout=5
        )
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            if page.get("pageid", -1) == -1:
                continue
            extract = page.get("extract", "").strip()
            if extract and len(extract) > 50:
                return extract
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════════
# GBIF SERVICE
# Clase principal para interactuar con la API de GBIF.
# Gestiona la sincronización de especies por país adaptada a la
# nueva arquitectura ManyToMany (sin duplicados).
# ═══════════════════════════════════════════════════════════════════════

class GBIFService:

    BASE_URL       = "https://api.gbif.org/v1"
    VALID_KINGDOMS = {"Animalia", "Plantae", "Fungi"}

    @staticmethod
    def safe_request(url: str, params: Optional[Dict] = None, retries: int = 5) -> Optional[Dict]:
        """
        Petición HTTP con reintentos automáticos y manejo de rate limiting.
        Espera progresivamente más tiempo entre reintentos.
        """
        for intento in range(retries):
            try:
                response = requests.get(url, params=params, timeout=20)
                if response.status_code == 429:
                    wait = 5 + intento * 2
                    print(f"⚠️ Rate limit → esperando {wait}s")
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException:
                wait = 3 + intento * 2
                print(f"⚠️ Error API → reintentando en {wait}s")
                time.sleep(wait)
        return None

    @staticmethod
    def get_species_by_country_paginated(country_code: str,
                                          limit: int = 300,
                                          offset: int = 0) -> Dict:
        """
        Obtiene una página de especies de un país desde GBIF.
        Filtra por reinos válidos y extrae la foto del occurrence si existe.
        """
        data = GBIFService.safe_request(
            f"{GBIFService.BASE_URL}/occurrence/search",
            params={
                "country":   country_code.upper(),
                "mediaType": "StillImage",
                "limit":     limit,
                "offset":    offset,
            }
        )

        if not data:
            return {"count": 0, "results": []}

        results = []
        for record in data.get("results", []):
            species_key = record.get("speciesKey")
            if not species_key:
                continue
            if record.get("kingdom") not in GBIFService.VALID_KINGDOMS:
                continue

            # Extraer foto del occurrence (ya geolocada en el país)
            gbif_image = None
            for m in record.get("media", []):
                identifier = m.get("identifier", "")
                if identifier and _is_real_photo(identifier):
                    gbif_image = identifier
                    break

            results.append({
                "species_key":     species_key,
                "scientific_name": record.get("scientificName", ""),
                "canonical_name":  record.get("species") or record.get("scientificName", ""),
                "common_name":     record.get("vernacularName") or None,
                "kingdom":         record.get("kingdom", ""),
                "phylum":          record.get("phylum", ""),
                "class_name":      record.get("class", ""),
                "order":           record.get("order", ""),
                "family":          record.get("family", ""),
                "genus":           record.get("genus", ""),
                "image_url":       gbif_image,
                "image_source":    "gbif" if gbif_image else None,
                "iucn_status":     record.get("iucnRedListCategory") or None,
            })

        return {"count": data.get("count", 0), "results": results}

    @staticmethod
    def get_species_detail(species_key: int) -> Optional[Dict]:
        """
        Obtiene los detalles completos de una especie desde GBIF,
        incluyendo taxonomía, nombres comunes, imagen y descripción.
        """
        data = GBIFService.safe_request(f"{GBIFService.BASE_URL}/species/{species_key}")
        if not data:
            return None

        # Buscar foto en occurrences
        occ_data = GBIFService.safe_request(
            f"{GBIFService.BASE_URL}/occurrence/search",
            params={"taxonKey": species_key, "mediaType": "StillImage", "limit": 10}
        )
        gbif_image = None
        if occ_data:
            for occ in occ_data.get("results", []):
                for m in occ.get("media", []):
                    identifier = m.get("identifier", "")
                    if identifier and _is_real_photo(identifier):
                        gbif_image = identifier
                        break
                if gbif_image:
                    break

        canonical    = data.get("canonicalName") or data.get("scientificName", "")
        image_result = get_best_image_and_common_name(canonical, gbif_image)

        # Obtener nombres vernáculos
        vernacular_data = GBIFService.safe_request(
            f"{GBIFService.BASE_URL}/species/{species_key}/vernacularNames"
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

        common_names     = (spanish_names + other_names)[:10]
        main_common_name = (
            spanish_names[0]["name"] if spanish_names
            else image_result.get("common_name")
        )

        return {
            "key":             data.get("key"),
            "scientific_name": data.get("scientificName", ""),
            "canonical_name":  canonical,
            "common_name":     main_common_name,
            "kingdom":         data.get("kingdom", ""),
            "phylum":          data.get("phylum", ""),
            "class":           data.get("class", ""),
            "order":           data.get("order", ""),
            "family":          data.get("family", ""),
            "genus":           data.get("genus", ""),
            "description":     "",
            "image_url":       image_result["url"],
            "image_source":    image_result["source"],
            "common_names":    common_names,
        }

    @staticmethod
    def search_species(query: str) -> Optional[Dict]:
        """Busca una especie por nombre en GBIF y devuelve sus detalles completos."""
        data = GBIFService.safe_request(
            f"{GBIFService.BASE_URL}/species/search",
            params={"q": query, "limit": 1, "rank": "SPECIES"}
        )
        if not data or not data.get("results"):
            return None
        result      = data["results"][0]
        species_key = result.get("key")
        if not species_key:
            return None
        return GBIFService.get_species_detail(species_key)

    @staticmethod
    def sync_country_species(country_code: str):
        """
        Sincroniza todas las especies de un país desde GBIF.

        ARQUITECTURA MANYTOMANY:
        - Cada especie se crea UNA SOLA VEZ en la BD (get_or_create por species_key)
        - Luego se vincula al país mediante EspeciePais (sin duplicados)
        - Si la especie ya existe de otro país, solo se añade la vinculación nueva

        Esto es la diferencia clave respecto al proyecto anterior donde
        se creaba una especie distinta por cada país.
        """
        from .models import Pais, Especie, EspeciePais

        try:
            pais = Pais.objects.get(codigo=country_code.upper())
        except Pais.DoesNotExist:
            print(f"❌ País no encontrado: {country_code}")
            return

        offset        = 0
        limit         = 300
        total_nuevas  = 0
        total_vinc    = 0
        species_seen  = set()

        print(f"\n🌍 Sincronizando {pais.nombre} ({pais.codigo})...")

        while True:
            data    = GBIFService.get_species_by_country_paginated(country_code, limit=limit, offset=offset)
            results = data.get("results", [])
            if not results:
                break

            for item in results:
                key = item["species_key"]
                if key in species_seen:
                    continue
                species_seen.add(key)

                # Crear la especie si no existe (sin duplicados)
                especie, created = Especie.objects.get_or_create(
                    species_key=key,
                    defaults={
                        "scientific_name": item["scientific_name"],
                        "canonical_name":  item["canonical_name"],
                        "common_name":     item["common_name"],
                        "kingdom":         item["kingdom"],
                        "phylum":          item["phylum"],
                        "class_name":      item["class_name"],
                        "order":           item["order"],
                        "family":          item["family"],
                        "genus":           item["genus"],
                        "iucn_status":     item["iucn_status"],
                        "image_url":       item["image_url"],
                        "image_source":    item["image_source"],
                    }
                )
                if created:
                    total_nuevas += 1

                # Vincular la especie al país con su foto específica
                ep, vinc_created = EspeciePais.objects.get_or_create(
                    especie=especie,
                    pais=pais,
                    defaults={
                        "image_url":    item["image_url"],
                        "image_source": item["image_source"],
                    }
                )
                if vinc_created:
                    total_vinc += 1

            print(f"  Offset {offset} → {total_nuevas} especies nuevas, {total_vinc} vínculos")
            offset += limit
            time.sleep(0.5)

        print(f"✅ {pais.nombre}: {total_nuevas} especies nuevas, {total_vinc} vínculos creados")