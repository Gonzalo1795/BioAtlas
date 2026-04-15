from atlas.models import TerritorioEspecial, Especie, EspecieTerritorio
from atlas.services import GBIFService

territorio = TerritorioEspecial.objects.get(codigo='AQ')
total = 0

data = GBIFService.safe_request('https://api.gbif.org/v1/occurrence/search?country=AQ&facet=speciesKey&facetLimit=200&limit=0')

if data:
    facets = data.get('facets', [])
    for facet in facets:
        if facet.get('field') == 'SPECIES_KEY':
            for count in facet.get('counts', []):
                key = int(count.get('name'))
                detalle = GBIFService.safe_request(f'https://api.gbif.org/v1/species/{key}')
                if not detalle:
                    continue
                if detalle.get('kingdom') not in ['Animalia', 'Plantae', 'Fungi']:
                    continue
                especie, _ = Especie.objects.get_or_create(
                    species_key=key,
                    defaults={
                        'scientific_name': detalle.get('scientificName', ''),
                        'canonical_name':  detalle.get('canonicalName', ''),
                        'kingdom':         detalle.get('kingdom', ''),
                        'phylum':          detalle.get('phylum', ''),
                        'class_name':      detalle.get('class', ''),
                        'order':           detalle.get('order', ''),
                        'family':          detalle.get('family', ''),
                        'genus':           detalle.get('genus', ''),
                    }
                )
                EspecieTerritorio.objects.get_or_create(especie=especie, territorio=territorio)
                total += 1
                print(f'{total}: {detalle.get("canonicalName", "")}')

print(f'TOTAL: {total} especies antarticas')