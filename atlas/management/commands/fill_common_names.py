"""
Management command: fill_common_names
======================================
Rellena el campo common_name de las especies que no tienen nombre común
en español. Lo obtiene de dos fuentes:
1. iNaturalist API (preferred_common_name en español)
2. GBIF vernacularNames en español (spa)

Uso:
    python manage.py fill_common_names
    python manage.py fill_common_names --reset
    python manage.py fill_common_names --delay 0.3
"""

import time
import requests
from django.core.management.base import BaseCommand
from atlas.models import Especie


class Command(BaseCommand):
    help = "Rellena nombres comunes en español desde iNaturalist y GBIF"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            default=False,
            help='Sobreescribir nombres comunes existentes'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.3,
            help='Segundos de espera entre peticiones (default: 0.3)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Número máximo de especies a procesar'
        )

    def handle(self, *args, **options):
        reset = options['reset']
        delay = options['delay']
        limit = options['limit']

        if reset:
            qs = Especie.objects.all()
        else:
            qs = Especie.objects.filter(common_name__isnull=True) | \
                 Especie.objects.filter(common_name='')

        if limit:
            qs = qs[:limit]

        total      = qs.count()
        procesadas = 0
        ok         = 0
        sin_nombre = 0

        self.stdout.write(f"🏷️  {total} especies sin nombre común\n")

        for especie in qs.iterator():
            procesadas += 1
            nombre = especie.canonical_name or especie.scientific_name

            common_name = (
                self._get_from_inaturalist(nombre) or
                self._get_from_gbif(especie.species_key)
            )

            if common_name:
                especie.common_name = common_name
                especie.save(update_fields=["common_name"])
                ok += 1
                self.stdout.write(f"  [{procesadas}/{total}] ✓ {nombre} → {common_name}")
            else:
                sin_nombre += 1
                self.stdout.write(f"  [{procesadas}/{total}] ✗ {nombre} — sin nombre común")

            time.sleep(delay)

        self.stdout.write(f"\n✅ Completado: {ok} nombres encontrados, {sin_nombre} sin nombre")

    def _get_from_inaturalist(self, scientific_name: str):
        """Obtiene el nombre común en español desde iNaturalist."""
        try:
            r = requests.get(
                "https://api.inaturalist.org/v1/taxa",
                params={"q": scientific_name, "per_page": 1, "locale": "es"},
                timeout=5
            )
            r.raise_for_status()
            results = r.json().get("results", [])
            if results:
                name = (
                    results[0].get("preferred_common_name") or
                    results[0].get("english_common_name")
                )
                if name:
                    return name.capitalize()
        except Exception:
            pass
        return None

    def _get_from_gbif(self, species_key: int):
        """Obtiene el nombre común en español desde GBIF vernacularNames."""
        try:
            r = requests.get(
                f"https://api.gbif.org/v1/species/{species_key}/vernacularNames",
                timeout=5
            )
            r.raise_for_status()
            for v in r.json().get("results", []):
                if v.get("language") == "spa" and v.get("vernacularName"):
                    return v["vernacularName"].capitalize()
        except Exception:
            pass
        return None