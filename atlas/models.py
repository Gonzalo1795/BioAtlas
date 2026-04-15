from django.db import models
from django.contrib.auth.models import User


# ═══════════════════════════════════════════════════════════════════════
# GEOGRAFÍA
# Modelos que representan la estructura geográfica del atlas:
# continentes y países. Son la base sobre la que se organiza
# toda la biodiversidad del proyecto.
# ═══════════════════════════════════════════════════════════════════════

class Continente(models.Model):
    """
    Representa un continente del mundo.
    Agrupa países y sirve como primer nivel de navegación en el atlas.
    """
    nombre      = models.CharField(max_length=100, unique=True)
    codigo      = models.CharField(max_length=2, unique=True,
                                   help_text="Código de 2 letras (EU, AF, AS...)")
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name        = "Continente"
        verbose_name_plural = "Continentes"
        ordering            = ['nombre']

    def __str__(self):
        return self.nombre


class Pais(models.Model):
    """
    Representa un país o territorio geográfico.
    Cada país tiene un código ISO único que usamos para sincronizar
    sus especies desde GBIF.
    """
    nombre      = models.CharField(max_length=100)
    codigo      = models.CharField(max_length=2, unique=True,
                                   help_text="Código ISO 3166-1 Alpha-2 (ES, FR, AQ...)")
    continente  = models.ForeignKey(Continente, on_delete=models.CASCADE,
                                    related_name='paises')
    latitud     = models.FloatField(help_text="Latitud del centro del país")
    longitud    = models.FloatField(help_text="Longitud del centro del país")
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name        = "País"
        verbose_name_plural = "Países"
        ordering            = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

class TerritorioEspecial(models.Model):
    """
    Territorios que albergan biodiversidad pero no son países.
    Ejemplo: Antártida, Alta Mar, territorios disputados.
    """
    nombre      = models.CharField(max_length=100)
    codigo      = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField(blank=True, default="")
    latitud     = models.FloatField(null=True, blank=True)
    longitud    = models.FloatField(null=True, blank=True)
    continente  = models.ForeignKey(Continente, on_delete=models.SET_NULL, null=True, related_name="territorios")
    especies    = models.ManyToManyField('Especie', through='EspecieTerritorio', blank=True, related_name='territorios')

    class Meta:
        verbose_name        = "Territorio Especial"
        verbose_name_plural = "Territorios Especiales"
        ordering            = ['nombre']

    def __str__(self):
        return self.nombre


class EspecieTerritorio(models.Model):
    """Tabla intermedia entre Especie y TerritorioEspecial."""
    especie     = models.ForeignKey('Especie', on_delete=models.CASCADE)
    territorio  = models.ForeignKey(TerritorioEspecial, on_delete=models.CASCADE)
    image_url   = models.URLField(max_length=500, null=True, blank=True)
    image_source= models.CharField(max_length=50, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('especie', 'territorio')
        verbose_name        = "Especie-Territorio"
        verbose_name_plural = "Especies-Territorio"


# ═══════════════════════════════════════════════════════════════════════
# BIODIVERSIDAD
# El corazón del proyecto. Especie es una entidad única e independiente
# que existe una sola vez en la base de datos, sin importar en cuántos
# países se haya observado. Su relación con los países se gestiona
# a través de EspeciePais, que además guarda una foto específica
# de cada especie en cada país.
# ═══════════════════════════════════════════════════════════════════════

class Especie(models.Model):
    """
    Entidad única de una especie biológica.
    No está vinculada directamente a ningún país — existe una sola vez
    en la base de datos. Su presencia por país se gestiona a través
    de la tabla intermedia EspeciePais.

    Incluye descripciones multiidioma almacenadas en un JSONField:
    {"es": "...", "en": "...", "fr": "..."}
    obtenidas automáticamente desde la API de Wikipedia.
    """

    # ── Identificación GBIF ──
    species_key     = models.IntegerField(unique=True,
                                          help_text="ID único de la especie en GBIF")
    scientific_name = models.CharField(max_length=255,
                                       help_text="Nombre científico completo")
    canonical_name  = models.CharField(max_length=255, blank=True, null=True,
                                       help_text="Nombre canónico sin autor ni año")
    common_name     = models.CharField(max_length=255, blank=True, null=True,
                                       help_text="Nombre común principal en español")

    # ── Clasificación taxonómica ──
    kingdom    = models.CharField(max_length=100, blank=True, help_text="Reino")
    phylum     = models.CharField(max_length=100, blank=True, help_text="Filo")
    class_name = models.CharField(max_length=100, blank=True, help_text="Clase")
    order      = models.CharField(max_length=100, blank=True, help_text="Orden")
    family     = models.CharField(max_length=100, blank=True, help_text="Familia")
    genus      = models.CharField(max_length=100, blank=True, help_text="Género")

    # ── Estado de conservación ──
    iucn_status = models.CharField(
        max_length=10, blank=True, null=True,
        help_text="Estado IUCN: EX, EW, CR, EN, VU, NT, LC, DD"
    )

    # ── Descripción multiidioma ──
    # Almacena el primer párrafo de Wikipedia en cada idioma.
    # Formato: {"es": "...", "en": "...", "fr": "..."}
    descripcion = models.JSONField(
        default=dict, blank=True,
        help_text="Descripción en múltiples idiomas obtenida de Wikipedia"
    )

    # ── Imagen genérica (fallback) ──
    # Se usa cuando no hay imagen específica del país en EspeciePais.
    image_url    = models.URLField(blank=True, null=True)
    image_source = models.CharField(max_length=50, blank=True, null=True)

    # ── Relación con países (ManyToMany a través de EspeciePais) ──
    paises = models.ManyToManyField(
        Pais,
        through='EspeciePais',
        related_name='especies',
        blank=True
    )

    # ── Fechas ──
    created_at   = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Especie"
        verbose_name_plural = "Especies"
        ordering            = ['scientific_name']
        indexes = [
            models.Index(fields=["species_key"]),
            models.Index(fields=["scientific_name"]),
            models.Index(fields=["canonical_name"]),
            models.Index(fields=["kingdom"]),
            models.Index(fields=["family"]),
        ]

    def __str__(self):
        return self.canonical_name or self.scientific_name

    def get_descripcion(self, lang='es'):
        """
        Devuelve la descripción en el idioma solicitado.
        Si no existe en ese idioma, hace fallback a español y luego a inglés.
        """
        if isinstance(self.descripcion, dict):
            return (
                self.descripcion.get(lang) or
                self.descripcion.get('es') or
                self.descripcion.get('en') or
                ''
            )
        return ''

    def get_image_for_country(self, pais):
        """
        Devuelve la foto más específica disponible para este país.
        Primero busca una foto tomada en ese país (EspeciePais).
        Si no existe, devuelve la imagen genérica de la especie.
        """
        try:
            ep = self.especie_paises.get(pais=pais)
            if ep.image_url:
                return ep.image_url
        except EspeciePais.DoesNotExist:
            pass
        return self.image_url


class EspeciePais(models.Model):
    """
    Tabla intermedia entre Especie y Pais.
    Registra que una especie ha sido observada en un país concreto
    y guarda una foto específica tomada en ese país (geolocada).

    Esta es la clave de la arquitectura: permite que cada especie
    tenga una foto diferente según el país donde fue fotografiada.
    Por ejemplo, el León (Panthera leo) tiene una foto en Kenya
    y otra distinta en Tanzania.
    """

    especie = models.ForeignKey(
        Especie, on_delete=models.CASCADE,
        related_name='especie_paises'
    )
    pais = models.ForeignKey(
        Pais, on_delete=models.CASCADE,
        related_name='especie_paises'
    )

    # ── Foto específica de esta especie en este país ──
    image_url    = models.URLField(blank=True, null=True)
    image_source = models.CharField(max_length=50, blank=True, null=True)

    # ── Fechas ──
    primera_vez  = models.DateTimeField(auto_now_add=True,
                                        help_text="Fecha del primer registro en este país")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Especie en País"
        verbose_name_plural = "Especies en Países"
        unique_together     = ('especie', 'pais')
        ordering            = ['especie__scientific_name']
        indexes = [
            models.Index(fields=["pais"]),
            models.Index(fields=["especie"]),
            models.Index(fields=["pais", "especie"]),
        ]

    def __str__(self):
        return f"{self.especie} — {self.pais.nombre}"


# ═══════════════════════════════════════════════════════════════════════
# SUSCRIPCIÓN
# Gestiona el plan de cada usuario (gratuito o premium).
# Se integra con Stripe para procesar pagos recurrentes mensuales.
# Los usuarios premium no tienen límites en favoritos, avistamientos
# ni en su colección de Mi Atlas.
# ═══════════════════════════════════════════════════════════════════════

class Suscripcion(models.Model):
    """
    Plan de suscripción vinculado a un usuario.
    Relación OneToOne — cada usuario tiene exactamente una suscripción.
    Se crea automáticamente al registrarse con plan 'free'.
    """

    PLAN_CHOICES = [
        ("free",    "Gratuito"),
        ("premium", "Premium"),
    ]
    ESTADO_CHOICES = [
        ("active",    "Activa"),
        ("cancelled", "Cancelada"),
        ("expired",   "Expirada"),
    ]

    usuario                = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='suscripcion'
    )
    plan                   = models.CharField(max_length=20,
                                              choices=PLAN_CHOICES, default="free")
    estado                 = models.CharField(max_length=20,
                                              choices=ESTADO_CHOICES, default="active")

    # ── Campos de Stripe (se rellenan al pagar) ──
    stripe_customer_id     = models.CharField(max_length=100, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)

    # ── Fechas ──
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin    = models.DateTimeField(blank=True, null=True,
                                        help_text="Fecha de expiración del plan premium")

    class Meta:
        verbose_name        = "Suscripción"
        verbose_name_plural = "Suscripciones"

    def __str__(self):
        return f"{self.usuario.username} — {self.get_plan_display()}"

    @property
    def es_premium(self):
        """
        Devuelve True si el usuario tiene plan premium activo y no expirado.
        Se usa en templates y vistas para controlar el acceso a funciones premium.
        """
        from django.utils import timezone
        if self.plan != "premium" or self.estado != "active":
            return False
        if self.fecha_fin and self.fecha_fin < timezone.now():
            return False
        return True

    @classmethod
    def get_or_create_for_user(cls, user):
        """
        Obtiene o crea la suscripción de un usuario.
        Útil en vistas para asegurarse de que siempre existe una suscripción.
        """
        suscripcion, _ = cls.objects.get_or_create(usuario=user)
        return suscripcion


# ═══════════════════════════════════════════════════════════════════════
# COLECCIÓN PERSONAL
# Modelos que permiten al usuario construir su experiencia personal
# dentro del atlas: marcar favoritos, registrar avistamientos propios
# y coleccionar especies en su Mi Atlas por país.
# ═══════════════════════════════════════════════════════════════════════

class Favorito(models.Model):
    """
    El usuario marca una especie como favorita.
    Plan gratuito: máximo 20 favoritos.
    Plan premium: ilimitado.
    """
    usuario    = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='favoritos')
    especie    = models.ForeignKey(Especie, on_delete=models.CASCADE,
                                   related_name='favoritos')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Favorito"
        verbose_name_plural = "Favoritos"
        unique_together     = ('usuario', 'especie')
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.usuario.username} → {self.especie}"


class Avistamiento(models.Model):
    """
    El usuario registra haber visto una especie en la vida real.
    Puede incluir fecha, lugar, coordenadas, notas y una foto propia.
    Plan gratuito: máximo 10 avistamientos.
    Plan premium: ilimitado.
    """
    usuario    = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='avistamientos')
    especie    = models.ForeignKey(Especie, on_delete=models.CASCADE,
                                   related_name='avistamientos')

    # ── Datos del avistamiento ──
    fecha    = models.DateField(help_text="Fecha en que se vio la especie")
    lugar    = models.CharField(max_length=255, help_text="Lugar del avistamiento")
    latitud  = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    notas    = models.TextField(blank=True)
    foto     = models.ImageField(upload_to='avistamientos/', blank=True, null=True,
                                 help_text="Foto opcional tomada por el usuario")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Avistamiento"
        verbose_name_plural = "Avistamientos"
        ordering            = ['-fecha', '-created_at']

    def __str__(self):
        return f"{self.usuario.username} vio {self.especie} en {self.lugar} ({self.fecha})"


class BioLog(models.Model):
    """
    Especie coleccionada por el usuario en un país concreto.
    Es la feature estrella del proyecto — el 'Mi Atlas' personal.
    El usuario va completando su colección de especies vistas
    en cada país del mundo, como un diario de biodiversidad.

    Plan gratuito: máximo 3 países y 20 especies por país.
    Plan premium: países y especies ilimitados.
    """

    # Límites del plan gratuito
    LIMITE_PAISES_FREE   = 3
    LIMITE_ESPECIES_FREE = 20

    usuario    = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='biolog_entries')
    especie    = models.ForeignKey(Especie, on_delete=models.CASCADE,
                                   related_name='biolog_entries')
    pais       = models.ForeignKey(Pais, on_delete=models.CASCADE,
                                   related_name='biolog_entries')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Mi Atlas"
        verbose_name_plural = "Mi Atlas"
        unique_together     = ('usuario', 'especie', 'pais')
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.usuario.username} — {self.especie} en {self.pais.nombre}"

    @classmethod
    def puede_agregar(cls, usuario, pais):
        """
        Comprueba si el usuario puede añadir una especie de este país
        respetando los límites del plan gratuito.
        Devuelve (puede: bool, motivo: str)
        """
        suscripcion = Suscripcion.get_or_create_for_user(usuario)

        # Premium: sin ningún límite
        if suscripcion.es_premium:
            return True, ""

        # Verificar límite de países
        paises_ids = list(
            cls.objects.filter(usuario=usuario)
            .values_list('pais_id', flat=True)
            .distinct()
        )
        if pais.id not in paises_ids and len(paises_ids) >= cls.LIMITE_PAISES_FREE:
            return False, (
                f"Con el plan gratuito puedes coleccionar especies de hasta "
                f"{cls.LIMITE_PAISES_FREE} países. "
                f"Hazte Premium para desbloquear todos los países."
            )

        # Verificar límite de especies por país
        especies_en_pais = cls.objects.filter(usuario=usuario, pais=pais).count()
        if especies_en_pais >= cls.LIMITE_ESPECIES_FREE:
            return False, (
                f"Con el plan gratuito puedes coleccionar hasta "
                f"{cls.LIMITE_ESPECIES_FREE} especies por país. "
                f"Hazte Premium para coleccionar sin límite."
            )

        return True, ""
