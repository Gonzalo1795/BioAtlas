# -*- coding: utf-8 -*-

old_view = '''def antartida_detail(request):
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
    })'''

new_view = '''def antartida_detail(request):
    territorio  = get_object_or_404(TerritorioEspecial, codigo='AQ')
    especies_qs = Especie.objects.filter(territorios=territorio)

    kingdom     = request.GET.get('kingdom')
    phylum      = request.GET.get('phylum')
    class_name  = request.GET.get('class_name')
    order       = request.GET.get('order')
    family      = request.GET.get('family')
    iucn_status = request.GET.get('iucn_status')
    search      = request.GET.get('search')

    if kingdom:     especies_qs = especies_qs.filter(kingdom=kingdom)
    if phylum:      especies_qs = especies_qs.filter(phylum=phylum)
    if class_name:
        if class_name == 'Reptilia':
            especies_qs = especies_qs.filter(class_name__in=REPTIL_CLASSES)
        else:
            especies_qs = especies_qs.filter(class_name=class_name)
    if order:       especies_qs = especies_qs.filter(order=order)
    if family:      especies_qs = especies_qs.filter(family=family)
    if iucn_status: especies_qs = especies_qs.filter(iucn_status=iucn_status)
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
        'phylums':              todas.values_list('phylum',     flat=True).distinct().order_by('phylum'),
        'classes':              todas.values_list('class_name', flat=True).distinct().order_by('class_name'),
        'orders':               todas.values_list('order',      flat=True).distinct().order_by('order'),
        'families':             todas.values_list('family',     flat=True).distinct().order_by('family'),
    })'''

with open('atlas/views.py', encoding='utf-8') as f:
    content = f.read()

if old_view in content:
    content = content.replace(old_view, new_view)
    with open('atlas/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK: vista antartida_detail actualizada")
else:
    print("ERROR: no encontrado")
