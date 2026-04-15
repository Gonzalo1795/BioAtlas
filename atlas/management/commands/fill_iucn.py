"""
Management command: fill_iucn
==============================
Rellena el estado de conservación IUCN de las especies que no lo tienen.
Intenta obtenerlo de dos fuentes:
1. GBIF species API (campo iucnRedListCategory)
2. GBIF occurrence search (campo iucnRedListCategory en occurrences)

Estados IUCN válidos:
    EX  = Extinta
    EW  = Extinta en estado silvestre
    CR  = En peligro crítico
    EN  = En peligro
    VU  = Vulnerable
    NT  = Casi amenazada
    LC  = Preocupación menor
    DD  = Datos insuficientes

Uso:
    python manage.py fill_iucn
    python manage.py fill_iucn --reset
    python manage.py fill_iucn --delay 0.5
"""

import time
import requests
from django.core.management.base import BaseCommand
from atlas.models import Especie


VALID_IUCN = {"EX", "EW", "CR", "EN", "VU", "NT", "LC", "DD"}


class Command(BaseCommand):
    help = "Rellena estados de conservación IUCN desde GBIF"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            default=False,
            help='Sobreescribir estados IUCN existentes'
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
        delay = options['delay']
        limit = options['limit']

        if reset:
            qs = Especie.objects.all()
        else:
            qs = Especie.objects.filter(iucn_status__isnull=True) | \
                 Especie.objects.filter(iucn_status='')

        if limit:
            qs = qs[:limit]

        total      = qs.count()
        procesadas = 0
        ok         = 0
        sin_estado = 0

        self.stdout.write(f"🔴 {total} especies sin estado IUCN\n")

        for especie in qs.iterator():
            procesadas += 1
            nombre = especie.canonical_name or especie.scientific_name

            iucn = (
                self._get_from_gbif_species(especie.species_key) or
                self._get_from_gbif_occurrence(especie.species_key)
            )

            if iucn:
                especie.iucn_status = iucn
                especie.save(update_fields=["iucn_status"])
                ok += 1
                self.stdout.write(f"  [{procesadas}/{total}] ✓ {nombre} → {iucn}")
            else:
                sin_estado += 1
                self.stdout.write(f"  [{procesadas}/{total}] ✗ {nombre} — sin IUCN")

            time.sleep(delay)

        self.stdout.write(f"\n✅ Completado: {ok} estados encontrados, {sin_estado} sin IUCN")

    def _get_from_gbif_species(self, species_key: int):
        """Obtiene el estado IUCN desde la API de especies de GBIF."""
        try:
            r = requests.get(
                f"https://api.gbif.org/v1/species/{species_key}",
                timeout=5
            )
            r.raise_for_status()
            data  = r.json()
            iucn  = data.get("iucnRedListCategory", "")
            if iucn and iucn.upper() in VALID_IUCN:
                return iucn.upper()
        except Exception:
            pass
        return None

    def _get_from_gbif_occurrence(self, species_key: int):
        """Obtiene el estado IUCN desde los occurrences de GBIF."""
        try:
            r = requests.get(
                "https://api.gbif.org/v1/occurrence/search",
                params={"taxonKey": species_key, "limit": 5},
                timeout=5
            )
            r.raise_for_status()
            for occ in r.json().get("results", []):
                iucn = occ.get("iucnRedListCategory", "")
                if iucn and iucn.upper() in VALID_IUCN:
                    return iucn.upper()
        except Exception:
            pass
        return None