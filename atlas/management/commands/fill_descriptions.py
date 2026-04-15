"""
Management command: fill_descriptions
======================================
Rellena el campo descripcion (JSONField) de cada especie con el primer
párrafo de Wikipedia en los tres idiomas del proyecto (ES, EN, FR).

El campo descripcion almacena:
    {"es": "...", "en": "...", "fr": "..."}

Uso:
    python manage.py fill_descriptions
    python manage.py fill_descriptions --reset
    python manage.py fill_descriptions --lang es
    python manage.py fill_descriptions --delay 0.5
"""

import time
from django.core.management.base import BaseCommand
from atlas.models import Especie
from atlas.services import get_wikipedia_description


class Command(BaseCommand):
    help = "Rellena descripciones multiidioma desde Wikipedia"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            default=False,
            help='Sobreescribir descripciones existentes'
        )
        parser.add_argument(
            '--lang',
            type=str,
            default=None,
            help='Solo rellenar un idioma concreto (es, en, fr)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.5,
            help='Segundos de espera entre peticiones (default: 0.5)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Número máximo de especies a procesar'
        )

    def handle(self, *args, **options):
        reset = options['reset']
        lang  = options['lang']
        delay = options['delay']
        limit = options['limit']

        # ── Construir queryset ──
        if reset:
            qs = Especie.objects.all()
            self.stdout.write("🔄 Modo reset: sobreescribiendo todas las descripciones")
        else:
            # Solo las que no tienen descripción o les falta algún idioma
            qs = Especie.objects.filter(descripcion={}) | Especie.objects.filter(descripcion__isnull=True)

        if limit:
            qs = qs[:limit]

        total      = qs.count() if not limit else min(qs.count(), limit)
        procesadas = 0
        ok         = 0
        sin_desc   = 0

        self.stdout.write(f"📖 {total} especies a procesar\n")

        for especie in qs.iterator():
            procesadas += 1
            nombre = especie.canonical_name or especie.scientific_name

            # Obtener descripciones de Wikipedia
            nuevas = get_wikipedia_description(nombre, especie.common_name)

            if not nuevas:
                sin_desc += 1
                self.stdout.write(f"  [{procesadas}/{total}] ✗ {nombre} — sin Wikipedia")
                time.sleep(delay)
                continue

            # Si se especifica un idioma concreto, solo actualizar ese
            if lang:
                if lang in nuevas:
                    descripcion_actual = especie.descripcion or {}
                    descripcion_actual[lang] = nuevas[lang]
                    especie.descripcion = descripcion_actual
                else:
                    sin_desc += 1
                    self.stdout.write(f"  [{procesadas}/{total}] ✗ {nombre} — sin '{lang}' en Wikipedia")
                    time.sleep(delay)
                    continue
            else:
                if reset:
                    especie.descripcion = nuevas
                else:
                    # Mezclar con las existentes sin sobreescribir las que ya tienen
                    descripcion_actual = especie.descripcion or {}
                    for l, texto in nuevas.items():
                        if l not in descripcion_actual or not descripcion_actual[l]:
                            descripcion_actual[l] = texto
                    especie.descripcion = descripcion_actual

            especie.save(update_fields=["descripcion"])
            ok += 1

            idiomas_ok = list(especie.descripcion.keys())
            self.stdout.write(
                f"  [{procesadas}/{total}] ✓ {nombre} — {idiomas_ok}"
            )

            time.sleep(delay)

        self.stdout.write(f"\n✅ Completado: {ok} descripciones rellenadas, {sin_desc} sin Wikipedia")