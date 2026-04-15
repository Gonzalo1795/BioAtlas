"""
Management command: sync_all_countries
=======================================
Sincroniza las especies de todos los países desde GBIF.
Los países se procesan en orden de prioridad (mayor biodiversidad primero)
para que los más importantes estén listos cuanto antes.

Puede interrumpirse y reanudarse — usa --skip para saltar países ya procesados.

Uso:
    python manage.py sync_all_countries
    python manage.py sync_all_countries --delay 0.5
    python manage.py sync_all_countries --skip-done
    python manage.py sync_all_countries --solo BR,ES,MX
"""

import time
from django.core.management.base import BaseCommand
from atlas.models import Pais, Especie
from atlas.services import GBIFService


# Orden de prioridad: países con mayor biodiversidad conocida primero
PRIORIDAD = [
    # Megadiversos
    "BR", "ID", "CO", "MX", "PE", "EC", "VE", "IN", "AU", "CN",
    "MG", "ZA", "CD", "CM", "PG", "MY", "PH", "TZ", "KE", "ET",
    # Alta biodiversidad
    "US", "AR", "BO", "GT", "CR", "PA", "HN", "NI", "SV", "CL",
    "RU", "JP", "TH", "VN", "MM", "LA", "KH", "BD", "LK", "NP",
    "UG", "RW", "BI", "MZ", "ZM", "ZW", "BW", "NA", "AO", "GH",
    "NG", "CI", "SN", "GA", "CG", "GN", "SL", "LR", "TG", "BJ",
    "NZ", "FJ", "PW", "SB", "VU", "WS", "TO",
    # Europa
    "ES", "PT", "FR", "IT", "GR", "TR", "HR", "BA", "RS", "MK",
    "AL", "BG", "RO", "UA", "BY", "PL", "CZ", "SK", "HU", "AT",
    "DE", "CH", "LI", "BE", "NL", "LU", "DK", "NO", "SE", "FI",
    "EE", "LV", "LT", "IS", "IE", "GB", "MT", "CY", "MD", "ME",
    "SI", "SM", "AD", "MC", "VA", "XK",
    # Asia resto
    "KZ", "UZ", "TM", "TJ", "KG", "AZ", "GE", "AM", "IR", "IQ",
    "SY", "LB", "JO", "IL", "PS", "SA", "AE", "OM", "QA", "KW",
    "BH", "YE", "AF", "PK", "MN", "KP", "KR", "TW", "SG", "BN",
    "TL", "BT", "MV",
    # África resto
    "EG", "LY", "TN", "MA", "DZ", "MR", "ML", "BF", "NE", "TD",
    "SD", "SS", "SO", "DJ", "ER", "MW", "LS", "SZ", "CV", "KM",
    "SC", "MU", "ST", "GW", "GQ", "CF", "GM",
    # América resto
    "CA", "CU", "HT", "DO", "JM", "TT", "BB", "GD", "DM", "LC",
    "VC", "KN", "AG", "BS", "BZ", "GY", "SR", "PY", "UY",
    # Oceanía resto
    "KI", "FM", "MH", "NR", "TV",
    # Antártida
    "AQ",
]


class Command(BaseCommand):
    help = "Sincroniza las especies de todos los países desde GBIF"

    def add_arguments(self, parser):
        parser.add_argument(
            '--delay',
            type=float, default=0.5,
            help='Segundos de espera entre países (default: 0.5)'
        )
        parser.add_argument(
            '--skip-done',
            action='store_true', default=False,
            help='Saltar países que ya tienen especies sincronizadas'
        )
        parser.add_argument(
            '--solo',
            type=str, default=None,
            help='Sincronizar solo estos países (códigos separados por coma, ej: BR,ES,MX)'
        )
        parser.add_argument(
            '--min-especies',
            type=int, default=0,
            help='Saltar países que ya tienen más de N especies'
        )

    def handle(self, *args, **options):
        delay       = options['delay']
        skip_done   = options['skip_done']
        solo        = options['solo']
        min_especies = options['min_especies']

        # ── Construir lista de países a procesar ──
        if solo:
            codigos = [c.strip().upper() for c in solo.split(',')]
            paises_qs = Pais.objects.filter(codigo__in=codigos)
            # Ordenar según la lista
            paises_dict = {p.codigo: p for p in paises_qs}
            paises_lista = [paises_dict[c] for c in codigos if c in paises_dict]
        else:
            # Todos los países en orden de prioridad
            todos = {p.codigo: p for p in Pais.objects.all()}

            # Primero los de la lista de prioridad, luego el resto
            paises_lista = []
            for codigo in PRIORIDAD:
                if codigo in todos:
                    paises_lista.append(todos.pop(codigo))
            # Añadir los que no están en la lista de prioridad
            paises_lista.extend(todos.values())

        total    = len(paises_lista)
        hechos   = 0
        saltados = 0
        errores  = 0

        self.stdout.write(f"\n🌍 Sincronizando {total} países...\n")
        self.stdout.write(f"   Delay: {delay}s | Skip-done: {skip_done} | Min-especies: {min_especies}\n")
        self.stdout.write("─" * 60 + "\n")

        for i, pais in enumerate(paises_lista, 1):
            # Contar especies actuales
            num_actual = Especie.objects.filter(paises=pais).count()

            # Saltar si ya tiene suficientes especies
            if skip_done and num_actual > min_especies:
                saltados += 1
                self.stdout.write(
                    f"  [{i}/{total}] ⏭️  {pais.nombre} ({pais.codigo}) — ya tiene {num_actual} especies"
                )
                continue

            self.stdout.write(f"\n  [{i}/{total}] 🌍 {pais.nombre} ({pais.codigo})")
            if num_actual > 0:
                self.stdout.write(f"         (actualmente {num_actual} especies)")

            try:
                antes = Especie.objects.filter(paises=pais).count()
                GBIFService.sync_country_species(pais.codigo)
                despues = Especie.objects.filter(paises=pais).count()
                nuevas  = despues - antes
                hechos += 1
                self.stdout.write(
                    f"  ✅ {pais.nombre}: {despues} especies totales (+{nuevas} nuevas)"
                )
            except Exception as e:
                errores += 1
                self.stderr.write(f"  ❌ Error en {pais.nombre}: {e}")

            time.sleep(delay)

        self.stdout.write("\n" + "═" * 60)
        self.stdout.write(
            f"\n🎉 Completado:"
            f"\n   ✅ Procesados: {hechos}"
            f"\n   ⏭️  Saltados:   {saltados}"
            f"\n   ❌ Errores:    {errores}"
            f"\n   🌿 Total especies en BD: {Especie.objects.count()}"
        )