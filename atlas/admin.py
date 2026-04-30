from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html, mark_safe
from django.db.models import Count

from .models import (
    Continente, Pais, Especie, EspeciePais,
    TerritorioEspecial, EspecieTerritorio,
    Favorito, Avistamiento, BioLog, Suscripcion
)

# ── Personalización del panel ──
admin.site.site_header = '🌿 BioAtlas — Panel de Administración'
admin.site.site_title  = 'BioAtlas Admin'
admin.site.index_title = 'Panel de Control'


# ═══════════════════════════════════════════════════════════════
# CONTINENTE
# ═══════════════════════════════════════════════════════════════

@admin.register(Continente)
class ContinenteAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'codigo', 'num_paises')
    search_fields = ('nombre', 'codigo')
    ordering      = ('nombre',)

    def num_paises(self, obj):
        return obj.paises.count()
    num_paises.short_description = 'Países'


# ═══════════════════════════════════════════════════════════════
# PAÍS
# ═══════════════════════════════════════════════════════════════

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'codigo', 'continente', 'num_especies_badge')
    list_filter   = ('continente',)
    search_fields = ('nombre', 'codigo')
    ordering      = ('nombre',)
    list_per_page = 50

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(num_especies=Count('especies'))

    def num_especies_badge(self, obj):
        n = getattr(obj, 'num_especies', 0)
        color = '#2D8A4E' if n > 100 else ('#F59E0B' if n > 0 else '#DC2626')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:999px;font-size:0.75rem;font-weight:700;">{}</span>',
            color, f'{n:,}'
        )
    num_especies_badge.short_description = 'Especies'
    num_especies_badge.admin_order_field = 'num_especies'


# ═══════════════════════════════════════════════════════════════
# ESPECIE
# ═══════════════════════════════════════════════════════════════

@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display    = ('canonical_name', 'scientific_name', 'kingdom', 'class_name', 'iucn_badge', 'tiene_imagen')
    list_filter     = ('kingdom', 'iucn_status')
    search_fields   = ('canonical_name', 'scientific_name', 'common_name', 'family', 'genus')
    ordering        = ('scientific_name',)
    list_per_page   = 50
    readonly_fields = ('species_key', 'image_preview')

    fieldsets = (
        ('Identificación', {
            'fields': ('species_key', 'scientific_name', 'canonical_name', 'common_name')
        }),
        ('Taxonomía', {
            'fields': ('kingdom', 'phylum', 'class_name', 'order', 'family', 'genus')
        }),
        ('Conservación e imagen', {
            'fields': ('iucn_status', 'image_url', 'image_source', 'image_preview')
        }),
    )

    def iucn_badge(self, obj):
        colores = {
            'CR': '#DC2626', 'EN': '#EA580C', 'VU': '#CA8A04',
            'NT': '#2D8A4E', 'LC': '#6B7280', 'EX': '#000000', 'EW': '#1a1a1a'
        }
        if obj.iucn_status and obj.iucn_status in colores:
            return format_html(
                '<span style="background:{};color:#fff;padding:2px 6px;border-radius:4px;font-size:0.72rem;font-weight:700;">{}</span>',
                colores[obj.iucn_status], obj.iucn_status
            )
        return '—'
    iucn_badge.short_description = 'IUCN'

    def tiene_imagen(self, obj):
        if obj.image_url:
            return format_html('<span style="color:#2D8A4E;font-weight:700;">✓</span>')
        return format_html('<span style="color:#DC2626;">✗</span>')
    tiene_imagen.short_description = 'Imagen'

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-width:200px;max-height:150px;border-radius:8px;object-fit:cover;" />',
                obj.image_url
            )
        return '—'
    image_preview.short_description = 'Vista previa'


# ═══════════════════════════════════════════════════════════════
# TERRITORIO ESPECIAL
# ═══════════════════════════════════════════════════════════════

@admin.register(TerritorioEspecial)
class TerritorioEspecialAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'codigo', 'continente', 'num_especies')
    search_fields = ('nombre', 'codigo')

    def num_especies(self, obj):
        return obj.especies.count()
    num_especies.short_description = 'Especies'


# ═══════════════════════════════════════════════════════════════
# SUSCRIPCION
# ═══════════════════════════════════════════════════════════════

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display    = ('usuario', 'plan_badge', 'estado', 'stripe_customer_id')
    list_filter     = ('plan', 'estado')
    search_fields   = ('usuario__username', 'usuario__email', 'stripe_customer_id')
    ordering        = ('-id',)
    readonly_fields = ('stripe_customer_id', 'stripe_subscription_id')

    def plan_badge(self, obj):
        if obj.plan == 'premium':
            return mark_safe('<span style="background:linear-gradient(135deg,#D4AF37,#F0D060);color:#0A0F0D;padding:2px 10px;border-radius:999px;font-size:0.75rem;font-weight:700;">✨ Premium</span>')
        return mark_safe('<span style="background:#F0F0EE;color:#6B7280;padding:2px 10px;border-radius:999px;font-size:0.75rem;font-weight:700;">Free</span>')
    plan_badge.short_description = 'Plan'


# ═══════════════════════════════════════════════════════════════
# FAVORITO
# ═══════════════════════════════════════════════════════════════

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'especie_nombre', 'created_at')
    list_filter   = ('usuario',)
    search_fields = ('usuario__username', 'especie__canonical_name', 'especie__scientific_name')
    ordering      = ('-created_at',)

    def especie_nombre(self, obj):
        return obj.especie.canonical_name or obj.especie.scientific_name
    especie_nombre.short_description = 'Especie'


# ═══════════════════════════════════════════════════════════════
# AVISTAMIENTO
# ═══════════════════════════════════════════════════════════════

@admin.register(Avistamiento)
class AvistamientoAdmin(admin.ModelAdmin):
    list_display   = ('usuario', 'especie_nombre', 'lugar', 'fecha')
    list_filter    = ('usuario', 'fecha')
    search_fields  = ('usuario__username', 'especie__canonical_name', 'lugar')
    ordering       = ('-fecha',)
    date_hierarchy = 'fecha'

    def especie_nombre(self, obj):
        return obj.especie.canonical_name or obj.especie.scientific_name
    especie_nombre.short_description = 'Especie'


# ═══════════════════════════════════════════════════════════════
# BIOLOG (Mi Atlas)
# ═══════════════════════════════════════════════════════════════

@admin.register(BioLog)
class BioLogAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'especie_nombre', 'pais', 'created_at')
    list_filter   = ('pais', 'usuario')
    search_fields = ('usuario__username', 'especie__canonical_name', 'pais__nombre')
    ordering      = ('-created_at',)

    def especie_nombre(self, obj):
        return obj.especie.canonical_name or obj.especie.scientific_name
    especie_nombre.short_description = 'Especie'