/**
 * map.js — Mapa coroplético de BioAtlas
 */

(function () {
    'use strict';

    const map = L.map('world-map', {
        center:             [20, 0],
        zoom:               2,
        minZoom:            1,
        maxZoom:            7,
        zoomControl:        true,
        attributionControl: true,
        worldCopyJump:      false,
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19,
    }).addTo(map);

    // ── Datos de países desde Django ──
    const paises = window.paisesData || [];

    // Lookup por código ISO-2
    const paisPorCodigo = {};
    paises.forEach(p => { paisPorCodigo[p.codigo] = p; });

    // Lookup por nombre en español
    const paisPorNombre = {};
    paises.forEach(p => { paisPorNombre[p.nombre.toLowerCase()] = p; });

    // Códigos del GeoJSON que deben redirigir al país matriz
    const CODIGO_REDIRECCION = {
        'GL': 'DK',   // Groenlandia → Dinamarca
        'GF': 'FR',   // Guayana Francesa → Francia
        'MQ': 'FR',   // Martinica → Francia
        'GP': 'FR',   // Guadalupe → Francia
        'RE': 'FR',   // Reunión → Francia
        'PM': 'FR',   // San Pedro y Miquelón → Francia
        'NC': 'FR',   // Nueva Caledonia → Francia
        'PF': 'FR',   // Polinesia Francesa → Francia
        'YT': 'FR',   // Mayotte → Francia
        'TF': 'FR',   // Tierras Australes Francesas → Francia
        'BL': 'FR',   // San Bartolomé → Francia
        'MF': 'FR',   // San Martín → Francia
        'WF': 'FR',   // Wallis y Futuna → Francia
        'SJ': 'NO',   // Svalbard → Noruega
        'AX': 'FI',   // Islas Åland → Finlandia
    };

    // Traducciones nombre GeoJSON → nombre en BD (para países con código -99)
    const NOMBRE_TRADUCCION = {
        'france':           'Francia',
        'norway':           'Noruega',
        'northern cyprus':  'Chipre',
        'somaliland':       'Somalia',
        'kosovo':           'Kosovo',
        'western sahara':   'Marruecos',
    };

    // ── Resolver datos para un feature del GeoJSON ──
    function resolverDatos(codigo, geojsonName) {
        // 1. Buscar por código ISO directo
        if (codigo && codigo !== '-99') {
            const d = paisPorCodigo[codigo];
            if (d) return d;
        }

        // 2. Redirigir por código (territorios → país matriz)
        if (codigo && codigo !== '-99' && CODIGO_REDIRECCION[codigo]) {
            const d = paisPorCodigo[CODIGO_REDIRECCION[codigo]];
            if (d) return d;
        }

        // 3. Fallback por nombre traducido (para códigos -99)
        if (geojsonName) {
            const nombreEs = NOMBRE_TRADUCCION[geojsonName.toLowerCase()];
            if (nombreEs) {
                const d = paisPorNombre[nombreEs.toLowerCase()];
                if (d) return d;
            }
        }

        return null;
    }

    // ── Idioma activo ──
    function getLang() {
        return localStorage.getItem('bioatlas-lang') || 'es';
    }

    function getNombre(datos, geojsonName) {
        const lang = getLang();
        if (!datos) return geojsonName || '';
        if (lang === 'es') return datos.nombre;
        return geojsonName || datos.nombre;
    }

    // ── Estilos ──
    function style(feature) {
        const codigo      = feature.properties['ISO3166-1-Alpha-2'] || '';
        const geojsonName = feature.properties.name || '';
        const datos       = resolverDatos(codigo, geojsonName);
        return {
            fillColor:   datos ? '#2D8A4E' : '#BBBBBB',
            fillOpacity: datos ? 0.55 : 0.25,
            color:       '#ffffff',
            weight:      0.8,
            opacity:     1,
        };
    }

    function styleHover(tieneDatos) {
        return {
            fillColor:   tieneDatos ? '#4ADE80' : '#AAAAAA',
            fillOpacity: tieneDatos ? 0.85 : 0.35,
            color:       '#ffffff',
            weight:      1.5,
            opacity:     1,
        };
    }

    // ── Tooltip ──
    let tooltipEl = null;

    function showTooltip(e, nombre, continente, numEspecies) {
        if (!tooltipEl) {
            tooltipEl = document.createElement('div');
            tooltipEl.style.cssText = `
                position:fixed; z-index:9999; pointer-events:none;
                background:rgba(10,15,13,0.95);
                border:1px solid rgba(74,222,128,0.2);
                border-radius:10px; padding:10px 14px;
                font-family:'DM Sans',sans-serif;
                box-shadow:0 8px 24px rgba(0,0,0,0.3);
                max-width:220px;
            `;
            document.body.appendChild(tooltipEl);
        }
        tooltipEl.innerHTML = `
            <div style="font-weight:700;color:#F0F4F1;font-size:0.88rem;margin-bottom:2px;">${nombre}</div>
            ${continente ? `<div style="color:#8A9E8E;font-size:0.75rem;">${continente}</div>` : ''}
            ${numEspecies > 0
                ? `<div style="color:#4ADE80;font-size:0.78rem;font-weight:600;margin-top:5px;">🌿 ${numEspecies.toLocaleString('es-ES')} especies</div>`
                : ''
            }
        `;
        tooltipEl.style.display = 'block';
        moveTooltip(e);
    }

    function moveTooltip(e) {
        if (!tooltipEl) return;
        const x = e.originalEvent ? e.originalEvent.clientX : e.clientX;
        const y = e.originalEvent ? e.originalEvent.clientY : e.clientY;
        tooltipEl.style.left = (x + 16) + 'px';
        tooltipEl.style.top  = (y - 10) + 'px';
    }

    function hideTooltip() {
        if (tooltipEl) tooltipEl.style.display = 'none';
    }

    // ── Eventos GeoJSON ──
    let geojsonLayer = null;

    function onEachFeature(feature, layer) {
        const codigo      = feature.properties['ISO3166-1-Alpha-2'] || '';
        const geojsonName = feature.properties.name || '';
        const datos       = resolverDatos(codigo, geojsonName);
        const tieneDatos  = !!datos;

        layer.on({
            mouseover: function (e) {
                layer.setStyle(styleHover(tieneDatos));
                layer.bringToFront();
                const nombre = getNombre(datos, geojsonName);
                const num    = datos ? datos.num_especies : 0;
                const cont   = datos ? datos.continente : '';
                showTooltip(e, nombre, cont, num);
                if (layer._path) {
                    layer._path.style.cursor = tieneDatos ? 'pointer' : 'default';
                }
            },
            mousemove: moveTooltip,
            mouseout: function () {
                geojsonLayer.resetStyle(layer);
                hideTooltip();
                if (layer._path) layer._path.style.cursor = '';
            },
            click: function () {
                if (!datos) return;
                if (datos.es_territorio || String(datos.id).startsWith('territorio')) {
                    window.location.href = '/antartida/';
                } else {
                    window.location.href = '/pais/' + datos.id + '/';
                }
            }
        });
    }

    // ── Spinner ──
    const mapEl  = document.getElementById('world-map');
    const loader = document.createElement('div');
    loader.style.cssText = `
        position:absolute; inset:0; z-index:500;
        display:flex; align-items:center; justify-content:center;
        background:rgba(250,250,248,0.85); backdrop-filter:blur(4px);
        font-family:'DM Sans',sans-serif; color:#6B7280; font-size:0.9rem; gap:10px;
    `;
    loader.innerHTML = `<span style="animation:spin 1s linear infinite;display:inline-block;">🌍</span> Cargando mapa...`;
    mapEl.style.position = 'relative';
    mapEl.appendChild(loader);

    // ── Cargar GeoJSON ──
    fetch('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson')
        .then(r => { if (!r.ok) throw new Error(); return r.json(); })
        .then(data => {
            loader.remove();
            geojsonLayer = L.geoJSON(data, {
                style:         style,
                onEachFeature: onEachFeature,
            }).addTo(map);

            // Antártida — marcador circular
            const antartida = paisPorCodigo['AQ'];
            if (antartida) {
                let found = false;
                geojsonLayer.eachLayer(l => {
                    if ((l.feature?.properties['ISO3166-1-Alpha-2'] || '') === 'AQ') found = true;
                });
                if (!found) {
                    const m = L.circleMarker([-75, 0], {
                        radius: 14, fillColor: '#2D8A4E', fillOpacity: 0.55,
                        color: '#ffffff', weight: 0.8,
                    }).addTo(map);
                    m.on({
                        mouseover: e => {
                            m.setStyle({ fillColor: '#4ADE80', fillOpacity: 0.85 });
                            showTooltip(e, 'Antártida', 'Territorio especial', antartida.num_especies || 0);
                            m._path && (m._path.style.cursor = 'pointer');
                        },
                        mousemove: moveTooltip,
                        mouseout:  () => { m.setStyle({ fillColor: '#2D8A4E', fillOpacity: 0.55 }); hideTooltip(); },
                        click:     () => { window.location.href = '/antartida/'; }
                    });
                }
            }
        })
        .catch(() => {
            loader.innerHTML = '⚠️ Error cargando el mapa. Recarga la página.';
            loader.style.color = '#DC2626';
        });

    // ── CSS ──
    const styleEl = document.createElement('style');
    styleEl.textContent = `
        .leaflet-container { background:#F0F0EB !important; font-family:'DM Sans',sans-serif; }
        .leaflet-control-zoom { border:1px solid #E8E8E4 !important; border-radius:8px !important; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08) !important; }
        .leaflet-control-zoom a { background:#ffffff !important; color:#6B7280 !important; border-bottom:1px solid #E8E8E4 !important; }
        .leaflet-control-zoom a:hover { background:#F0FAF4 !important; color:#2D8A4E !important; }
        .leaflet-control-attribution { background:rgba(255,255,255,0.8) !important; color:#9CA3AF !important; font-size:0.65rem !important; }
        .leaflet-control-attribution a { color:#2D8A4E !important; }
        @keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
    `;
    document.head.appendChild(styleEl);

    window.addEventListener('bioatlas-lang-changed', hideTooltip);

})();