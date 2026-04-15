"""
Management command: fill_images
===============================
Rellena las imágenes que faltan en la tabla EspeciePais.

En la arquitectura ManyToMany, cada especie tiene una foto específica
por país almacenada en EspeciePais.image_url. Este comando recorre
todos los registros EspeciePais sin imagen y los rellena usando
el pipeline completo de imágenes (iNaturalist → GBIF → Wikimedia → EOL).

Uso:
    python manage.py fill_images
    python manage.py fill_images --pais ES
    python manage.py fill_images --reset-failed
    python manage.py fill_images --delay 0.5
"""

import time
from django.core.management.base import BaseCommand
from atlas.models import EspeciePais, Pais
from atlas.services import get_best_image


class Command(BaseCommand):
    help = "Rellena imágenes faltantes en EspeciePais"

    def add_arguments(self, parser):
        parser.add_argument(
            '--pais',
            type=str,
            default=None,
            help='Código ISO del país a procesar (ej: ES, FR). Si no se indica, procesa todos.'
        )
        parser.add_argument(
            '--reset-failed',
            action='store_true',
            default=False,
            help='Reintentar los registros que fallaron anteriormente (image_source=failed)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.3,
            help='Segundos de espera entre peticiones (default: 0.3)'
        )

    def handle(self, *args, **options):
        pais_codigo  = options['pais']
        reset_failed = options['reset_failed']
        delay        = options['delay']

        # ── Construir queryset base ──
        qs = EspeciePais.objects.select_related('especie', 'pais')

        if pais_codigo:
            pais = Pais.objects.filter(codigo=pais_codigo.upper()).first()
            if not pais:
                self.stderr.write(f"❌ País no encontrado: {pais_codigo}")
                return
            qs = qs.filter(pais=pais)
            self.stdout.write(f"🌍 Procesando país: {pais.nombre}")

        if reset_failed:
            # Reintentar los que fallaron + los que no tienen imagen
            qs = qs.filter(image_url__isnull=True)
            self.stdout.write("🔄 Modo reset-failed: reintentando todos sin imagen")
        else:
            # Solo los que no tienen imagen y nunca se han intentado
            qs = qs.filter(image_url__isnull=True).exclude(image_source="failed")

        total    = qs.count()
        procesados = 0
        ok       = 0
        fallidos = 0

        self.stdout.write(f"📸 {total} registros sin imagen a procesar\n")

        for ep in qs.iterator():
            procesados += 1
            nombre = ep.especie.canonical_name or ep.especie.scientific_name

            result = get_best_image(
                scientific_name=nombre,
                country_name=ep.pais.nombre,
                species_key=ep.especie.species_key,
                country_code=ep.pais.codigo,
            )

            if result["url"]:
                ep.image_url    = result["url"]
                ep.image_source = result["source"]
                ep.save(update_fields=["image_url", "image_source"])
                ok += 1
                self.stdout.write(
                    f"  [{procesados}/{total}] ✓ {nombre} ({ep.pais.codigo}) — {result['source']}"
                )
            else:
                ep.image_source = "failed"
                ep.save(update_fields=["image_source"])
                fallidos += 1
                self.stdout.write(
                    f"  [{procesados}/{total}] ✗ {nombre} ({ep.pais.codigo}) — sin imagen"
                )

            # También actualizar la imagen genérica de la especie si no tiene
            if result["url"] and not ep.especie.image_url:
                ep.especie.image_url    = result["url"]
                ep.especie.image_source = result["source"]
                ep.especie.save(update_fields=["image_url", "image_source"])

            time.sleep(delay)

        self.stdout.write(f"\n✅ Completado: {ok} imágenes encontradas, {fallidos} sin imagen")