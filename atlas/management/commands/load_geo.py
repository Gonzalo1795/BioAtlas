"""
Management command: load_geo
=============================
Carga todos los continentes y países del mundo en la base de datos
con sus coordenadas geográficas y códigos ISO.

Solo se ejecuta una vez al inicio del proyecto.
Usa get_or_create para que sea seguro ejecutarlo varias veces.

Uso:
    python manage.py load_geo
"""

from django.core.management.base import BaseCommand
from atlas.models import Continente, Pais


# ── Datos geográficos ──

CONTINENTES = [
    {"nombre": "Europa",        "codigo": "EU"},
    {"nombre": "África",        "codigo": "AF"},
    {"nombre": "Asia",          "codigo": "AS"},
    {"nombre": "América",       "codigo": "AM"},
    {"nombre": "Oceanía",       "codigo": "OC"},
    {"nombre": "Antártida",     "codigo": "AN"},
]

PAISES = [
    # ── EUROPA ──
    {"nombre": "Albania",               "codigo": "AL", "continente": "EU", "lat": 41.15,  "lon": 20.17},
    {"nombre": "Alemania",              "codigo": "DE", "continente": "EU", "lat": 51.17,  "lon": 10.45},
    {"nombre": "Andorra",               "codigo": "AD", "continente": "EU", "lat": 42.55,  "lon": 1.58},
    {"nombre": "Austria",               "codigo": "AT", "continente": "EU", "lat": 47.52,  "lon": 14.55},
    {"nombre": "Bélgica",               "codigo": "BE", "continente": "EU", "lat": 50.85,  "lon": 4.35},
    {"nombre": "Bielorrusia",           "codigo": "BY", "continente": "EU", "lat": 53.71,  "lon": 27.95},
    {"nombre": "Bosnia y Herzegovina",  "codigo": "BA", "continente": "EU", "lat": 44.16,  "lon": 17.68},
    {"nombre": "Bulgaria",              "codigo": "BG", "continente": "EU", "lat": 42.73,  "lon": 25.48},
    {"nombre": "Chipre",                "codigo": "CY", "continente": "EU", "lat": 35.13,  "lon": 33.43},
    {"nombre": "Croacia",               "codigo": "HR", "continente": "EU", "lat": 45.10,  "lon": 15.20},
    {"nombre": "Dinamarca",             "codigo": "DK", "continente": "EU", "lat": 56.26,  "lon": 9.50},
    {"nombre": "Eslovaquia",            "codigo": "SK", "continente": "EU", "lat": 48.67,  "lon": 19.70},
    {"nombre": "Eslovenia",             "codigo": "SI", "continente": "EU", "lat": 46.15,  "lon": 14.99},
    {"nombre": "España",                "codigo": "ES", "continente": "EU", "lat": 40.46,  "lon": -3.74},
    {"nombre": "Estonia",               "codigo": "EE", "continente": "EU", "lat": 58.60,  "lon": 25.01},
    {"nombre": "Finlandia",             "codigo": "FI", "continente": "EU", "lat": 61.92,  "lon": 25.74},
    {"nombre": "Francia",               "codigo": "FR", "continente": "EU", "lat": 46.23,  "lon": 2.21},
    {"nombre": "Grecia",                "codigo": "GR", "continente": "EU", "lat": 39.07,  "lon": 21.82},
    {"nombre": "Hungría",               "codigo": "HU", "continente": "EU", "lat": 47.16,  "lon": 19.50},
    {"nombre": "Irlanda",               "codigo": "IE", "continente": "EU", "lat": 53.41,  "lon": -8.24},
    {"nombre": "Islandia",              "codigo": "IS", "continente": "EU", "lat": 64.96,  "lon": -19.02},
    {"nombre": "Italia",                "codigo": "IT", "continente": "EU", "lat": 41.87,  "lon": 12.57},
    {"nombre": "Kosovo",                "codigo": "XK", "continente": "EU", "lat": 42.60,  "lon": 20.90},
    {"nombre": "Letonia",               "codigo": "LV", "continente": "EU", "lat": 56.88,  "lon": 24.60},
    {"nombre": "Liechtenstein",         "codigo": "LI", "continente": "EU", "lat": 47.14,  "lon": 9.55},
    {"nombre": "Lituania",              "codigo": "LT", "continente": "EU", "lat": 55.17,  "lon": 23.88},
    {"nombre": "Luxemburgo",            "codigo": "LU", "continente": "EU", "lat": 49.82,  "lon": 6.13},
    {"nombre": "Malta",                 "codigo": "MT", "continente": "EU", "lat": 35.94,  "lon": 14.37},
    {"nombre": "Moldavia",              "codigo": "MD", "continente": "EU", "lat": 47.41,  "lon": 28.37},
    {"nombre": "Mónaco",                "codigo": "MC", "continente": "EU", "lat": 43.73,  "lon": 7.40},
    {"nombre": "Montenegro",            "codigo": "ME", "continente": "EU", "lat": 42.71,  "lon": 19.37},
    {"nombre": "Noruega",               "codigo": "NO", "continente": "EU", "lat": 60.47,  "lon": 8.47},
    {"nombre": "Países Bajos",          "codigo": "NL", "continente": "EU", "lat": 52.13,  "lon": 5.29},
    {"nombre": "Polonia",               "codigo": "PL", "continente": "EU", "lat": 51.92,  "lon": 19.15},
    {"nombre": "Portugal",              "codigo": "PT", "continente": "EU", "lat": 39.40,  "lon": -8.22},
    {"nombre": "Reino Unido",           "codigo": "GB", "continente": "EU", "lat": 55.38,  "lon": -3.44},
    {"nombre": "República Checa",       "codigo": "CZ", "continente": "EU", "lat": 49.82,  "lon": 15.47},
    {"nombre": "Rumanía",               "codigo": "RO", "continente": "EU", "lat": 45.94,  "lon": 24.97},
    {"nombre": "Rusia",                 "codigo": "RU", "continente": "EU", "lat": 61.52,  "lon": 105.32},
    {"nombre": "San Marino",            "codigo": "SM", "continente": "EU", "lat": 43.94,  "lon": 12.46},
    {"nombre": "Serbia",                "codigo": "RS", "continente": "EU", "lat": 44.02,  "lon": 21.01},
    {"nombre": "Suecia",                "codigo": "SE", "continente": "EU", "lat": 60.13,  "lon": 18.64},
    {"nombre": "Suiza",                 "codigo": "CH", "continente": "EU", "lat": 46.82,  "lon": 8.23},
    {"nombre": "Turquía",               "codigo": "TR", "continente": "EU", "lat": 38.96,  "lon": 35.24},
    {"nombre": "Ucrania",               "codigo": "UA", "continente": "EU", "lat": 48.38,  "lon": 31.17},
    {"nombre": "Ciudad del Vaticano",   "codigo": "VA", "continente": "EU", "lat": 41.90,  "lon": 12.45},

    # ── ÁFRICA ──
    {"nombre": "Algeria",               "codigo": "DZ", "continente": "AF", "lat": 28.03,  "lon": 1.66},
    {"nombre": "Angola",                "codigo": "AO", "continente": "AF", "lat": -11.20, "lon": 17.87},
    {"nombre": "Benín",                 "codigo": "BJ", "continente": "AF", "lat": 9.31,   "lon": 2.32},
    {"nombre": "Botsuana",              "codigo": "BW", "continente": "AF", "lat": -22.33, "lon": 24.68},
    {"nombre": "Burkina Faso",          "codigo": "BF", "continente": "AF", "lat": 12.36,  "lon": -1.53},
    {"nombre": "Burundi",               "codigo": "BI", "continente": "AF", "lat": -3.37,  "lon": 29.92},
    {"nombre": "Cabo Verde",            "codigo": "CV", "continente": "AF", "lat": 16.54,  "lon": -23.04},
    {"nombre": "Camerún",               "codigo": "CM", "continente": "AF", "lat": 7.37,   "lon": 12.35},
    {"nombre": "Chad",                  "codigo": "TD", "continente": "AF", "lat": 15.45,  "lon": 18.73},
    {"nombre": "Comoras",               "codigo": "KM", "continente": "AF", "lat": -11.64, "lon": 43.33},
    {"nombre": "Congo",                 "codigo": "CG", "continente": "AF", "lat": -0.23,  "lon": 15.83},
    {"nombre": "Costa de Marfil",       "codigo": "CI", "continente": "AF", "lat": 7.54,   "lon": -5.55},
    {"nombre": "Djibouti",              "codigo": "DJ", "continente": "AF", "lat": 11.83,  "lon": 42.59},
    {"nombre": "Egipto",                "codigo": "EG", "continente": "AF", "lat": 26.82,  "lon": 30.80},
    {"nombre": "Eritrea",               "codigo": "ER", "continente": "AF", "lat": 15.18,  "lon": 39.78},
    {"nombre": "Etiopía",               "codigo": "ET", "continente": "AF", "lat": 9.15,   "lon": 40.49},
    {"nombre": "Gabón",                 "codigo": "GA", "continente": "AF", "lat": -0.80,  "lon": 11.61},
    {"nombre": "Gambia",                "codigo": "GM", "continente": "AF", "lat": 13.44,  "lon": -15.31},
    {"nombre": "Ghana",                 "codigo": "GH", "continente": "AF", "lat": 7.95,   "lon": -1.02},
    {"nombre": "Guinea",                "codigo": "GN", "continente": "AF", "lat": 9.95,   "lon": -11.24},
    {"nombre": "Guinea-Bisáu",          "codigo": "GW", "continente": "AF", "lat": 11.80,  "lon": -15.18},
    {"nombre": "Guinea Ecuatorial",     "codigo": "GQ", "continente": "AF", "lat": 1.65,   "lon": 10.27},
    {"nombre": "Kenia",                 "codigo": "KE", "continente": "AF", "lat": -0.02,  "lon": 37.91},
    {"nombre": "Lesoto",                "codigo": "LS", "continente": "AF", "lat": -29.61, "lon": 28.23},
    {"nombre": "Liberia",               "codigo": "LR", "continente": "AF", "lat": 6.43,   "lon": -9.43},
    {"nombre": "Libia",                 "codigo": "LY", "continente": "AF", "lat": 26.34,  "lon": 17.23},
    {"nombre": "Madagascar",            "codigo": "MG", "continente": "AF", "lat": -18.77, "lon": 46.87},
    {"nombre": "Malawi",                "codigo": "MW", "continente": "AF", "lat": -13.25, "lon": 34.30},
    {"nombre": "Mali",                  "codigo": "ML", "continente": "AF", "lat": 17.57,  "lon": -3.99},
    {"nombre": "Marruecos",             "codigo": "MA", "continente": "AF", "lat": 31.79,  "lon": -7.09},
    {"nombre": "Mauritania",            "codigo": "MR", "continente": "AF", "lat": 21.01,  "lon": -10.94},
    {"nombre": "Mauricio",              "codigo": "MU", "continente": "AF", "lat": -20.35, "lon": 57.55},
    {"nombre": "Mozambique",            "codigo": "MZ", "continente": "AF", "lat": -18.67, "lon": 35.53},
    {"nombre": "Namibia",               "codigo": "NA", "continente": "AF", "lat": -22.96, "lon": 18.49},
    {"nombre": "Níger",                 "codigo": "NE", "continente": "AF", "lat": 17.61,  "lon": 8.08},
    {"nombre": "Nigeria",               "codigo": "NG", "continente": "AF", "lat": 9.08,   "lon": 8.68},
    {"nombre": "República Centroafricana", "codigo": "CF", "continente": "AF", "lat": 6.61, "lon": 20.94},
    {"nombre": "República del Congo",   "codigo": "CD", "continente": "AF", "lat": -4.04,  "lon": 21.76},
    {"nombre": "Ruanda",                "codigo": "RW", "continente": "AF", "lat": -1.94,  "lon": 29.87},
    {"nombre": "Santo Tomé y Príncipe", "codigo": "ST", "continente": "AF", "lat": 0.19,   "lon": 6.61},
    {"nombre": "Senegal",               "codigo": "SN", "continente": "AF", "lat": 14.50,  "lon": -14.45},
    {"nombre": "Seychelles",            "codigo": "SC", "continente": "AF", "lat": -4.68,  "lon": 55.49},
    {"nombre": "Sierra Leona",          "codigo": "SL", "continente": "AF", "lat": 8.46,   "lon": -11.78},
    {"nombre": "Somalia",               "codigo": "SO", "continente": "AF", "lat": 5.15,   "lon": 46.20},
    {"nombre": "Sudáfrica",             "codigo": "ZA", "continente": "AF", "lat": -30.56, "lon": 22.94},
    {"nombre": "Sudán",                 "codigo": "SD", "continente": "AF", "lat": 12.86,  "lon": 30.22},
    {"nombre": "Sudán del Sur",         "codigo": "SS", "continente": "AF", "lat": 6.88,   "lon": 31.31},
    {"nombre": "Suazilandia",           "codigo": "SZ", "continente": "AF", "lat": -26.52, "lon": 31.47},
    {"nombre": "Tanzania",              "codigo": "TZ", "continente": "AF", "lat": -6.37,  "lon": 34.89},
    {"nombre": "Togo",                  "codigo": "TG", "continente": "AF", "lat": 8.62,   "lon": 0.82},
    {"nombre": "Túnez",                 "codigo": "TN", "continente": "AF", "lat": 33.89,  "lon": 9.54},
    {"nombre": "Uganda",                "codigo": "UG", "continente": "AF", "lat": 1.37,   "lon": 32.29},
    {"nombre": "Zambia",                "codigo": "ZM", "continente": "AF", "lat": -13.13, "lon": 27.85},
    {"nombre": "Zimbabue",              "codigo": "ZW", "continente": "AF", "lat": -19.02, "lon": 29.15},

    # ── ASIA ──
    {"nombre": "Afganistán",            "codigo": "AF", "continente": "AS", "lat": 33.94,  "lon": 67.71},
    {"nombre": "Arabia Saudí",          "codigo": "SA", "continente": "AS", "lat": 23.89,  "lon": 45.08},
    {"nombre": "Armenia",               "codigo": "AM", "continente": "AS", "lat": 40.07,  "lon": 45.04},
    {"nombre": "Azerbaiyán",            "codigo": "AZ", "continente": "AS", "lat": 40.14,  "lon": 47.58},
    {"nombre": "Baréin",                "codigo": "BH", "continente": "AS", "lat": 26.00,  "lon": 50.55},
    {"nombre": "Bangladés",             "codigo": "BD", "continente": "AS", "lat": 23.68,  "lon": 90.36},
    {"nombre": "Brunéi",                "codigo": "BN", "continente": "AS", "lat": 4.54,   "lon": 114.73},
    {"nombre": "Bután",                 "codigo": "BT", "continente": "AS", "lat": 27.51,  "lon": 90.43},
    {"nombre": "Camboya",               "codigo": "KH", "continente": "AS", "lat": 12.57,  "lon": 104.99},
    {"nombre": "China",                 "codigo": "CN", "continente": "AS", "lat": 35.86,  "lon": 104.20},
    {"nombre": "Corea del Norte",       "codigo": "KP", "continente": "AS", "lat": 40.34,  "lon": 127.51},
    {"nombre": "Corea del Sur",         "codigo": "KR", "continente": "AS", "lat": 35.91,  "lon": 127.77},
    {"nombre": "Emiratos Árabes Unidos","codigo": "AE", "continente": "AS", "lat": 23.42,  "lon": 53.85},
    {"nombre": "Filipinas",             "codigo": "PH", "continente": "AS", "lat": 12.88,  "lon": 121.77},
    {"nombre": "Georgia",               "codigo": "GE", "continente": "AS", "lat": 42.32,  "lon": 43.36},
    {"nombre": "India",                 "codigo": "IN", "continente": "AS", "lat": 20.59,  "lon": 78.96},
    {"nombre": "Indonesia",             "codigo": "ID", "continente": "AS", "lat": -0.79,  "lon": 113.92},
    {"nombre": "Irak",                  "codigo": "IQ", "continente": "AS", "lat": 33.22,  "lon": 43.68},
    {"nombre": "Irán",                  "codigo": "IR", "continente": "AS", "lat": 32.43,  "lon": 53.69},
    {"nombre": "Israel",                "codigo": "IL", "continente": "AS", "lat": 31.05,  "lon": 34.85},
    {"nombre": "Japón",                 "codigo": "JP", "continente": "AS", "lat": 36.20,  "lon": 138.25},
    {"nombre": "Jordania",              "codigo": "JO", "continente": "AS", "lat": 30.59,  "lon": 36.24},
    {"nombre": "Kazajistán",            "codigo": "KZ", "continente": "AS", "lat": 48.02,  "lon": 66.92},
    {"nombre": "Kirguistán",            "codigo": "KG", "continente": "AS", "lat": 41.20,  "lon": 74.77},
    {"nombre": "Kuwait",                "codigo": "KW", "continente": "AS", "lat": 29.31,  "lon": 47.48},
    {"nombre": "Laos",                  "codigo": "LA", "continente": "AS", "lat": 19.86,  "lon": 102.50},
    {"nombre": "Líbano",                "codigo": "LB", "continente": "AS", "lat": 33.85,  "lon": 35.86},
    {"nombre": "Malasia",               "codigo": "MY", "continente": "AS", "lat": 4.21,   "lon": 108.96},
    {"nombre": "Maldivas",              "codigo": "MV", "continente": "AS", "lat": 3.20,   "lon": 73.22},
    {"nombre": "Mongolia",              "codigo": "MN", "continente": "AS", "lat": 46.86,  "lon": 103.85},
    {"nombre": "Myanmar",               "codigo": "MM", "continente": "AS", "lat": 21.91,  "lon": 95.96},
    {"nombre": "Nepal",                 "codigo": "NP", "continente": "AS", "lat": 28.39,  "lon": 84.12},
    {"nombre": "Omán",                  "codigo": "OM", "continente": "AS", "lat": 21.51,  "lon": 55.92},
    {"nombre": "Pakistán",              "codigo": "PK", "continente": "AS", "lat": 30.38,  "lon": 69.35},
    {"nombre": "Palestina",             "codigo": "PS", "continente": "AS", "lat": 31.95,  "lon": 35.23},
    {"nombre": "Qatar",                 "codigo": "QA", "continente": "AS", "lat": 25.35,  "lon": 51.18},
    {"nombre": "Singapur",              "codigo": "SG", "continente": "AS", "lat": 1.35,   "lon": 103.82},
    {"nombre": "Siria",                 "codigo": "SY", "continente": "AS", "lat": 34.80,  "lon": 38.99},
    {"nombre": "Sri Lanka",             "codigo": "LK", "continente": "AS", "lat": 7.87,   "lon": 80.77},
    {"nombre": "Tailandia",             "codigo": "TH", "continente": "AS", "lat": 15.87,  "lon": 100.99},
    {"nombre": "Taiwán",                "codigo": "TW", "continente": "AS", "lat": 23.70,  "lon": 120.96},
    {"nombre": "Tayikistán",            "codigo": "TJ", "continente": "AS", "lat": 38.86,  "lon": 71.28},
    {"nombre": "Timor Oriental",        "codigo": "TL", "continente": "AS", "lat": -8.87,  "lon": 125.73},
    {"nombre": "Turkmenistán",          "codigo": "TM", "continente": "AS", "lat": 38.97,  "lon": 59.56},
    {"nombre": "Uzbekistán",            "codigo": "UZ", "continente": "AS", "lat": 41.38,  "lon": 64.59},
    {"nombre": "Vietnam",               "codigo": "VN", "continente": "AS", "lat": 14.06,  "lon": 108.28},
    {"nombre": "Yemen",                 "codigo": "YE", "continente": "AS", "lat": 15.55,  "lon": 48.52},

    # ── AMÉRICA ──
    {"nombre": "Antigua y Barbuda",     "codigo": "AG", "continente": "AM", "lat": 17.06,  "lon": -61.80},
    {"nombre": "Argentina",             "codigo": "AR", "continente": "AM", "lat": -38.42, "lon": -63.62},
    {"nombre": "Bahamas",               "codigo": "BS", "continente": "AM", "lat": 25.03,  "lon": -77.40},
    {"nombre": "Barbados",              "codigo": "BB", "continente": "AM", "lat": 13.19,  "lon": -59.54},
    {"nombre": "Belice",                "codigo": "BZ", "continente": "AM", "lat": 17.19,  "lon": -88.50},
    {"nombre": "Bolivia",               "codigo": "BO", "continente": "AM", "lat": -16.29, "lon": -63.59},
    {"nombre": "Brasil",                "codigo": "BR", "continente": "AM", "lat": -14.24, "lon": -51.93},
    {"nombre": "Canadá",                "codigo": "CA", "continente": "AM", "lat": 56.13,  "lon": -106.35},
    {"nombre": "Chile",                 "codigo": "CL", "continente": "AM", "lat": -35.68, "lon": -71.54},
    {"nombre": "Colombia",              "codigo": "CO", "continente": "AM", "lat": 4.57,   "lon": -74.30},
    {"nombre": "Costa Rica",            "codigo": "CR", "continente": "AM", "lat": 9.75,   "lon": -83.75},
    {"nombre": "Cuba",                  "codigo": "CU", "continente": "AM", "lat": 21.52,  "lon": -77.78},
    {"nombre": "Dominica",              "codigo": "DM", "continente": "AM", "lat": 15.41,  "lon": -61.37},
    {"nombre": "Ecuador",               "codigo": "EC", "continente": "AM", "lat": -1.83,  "lon": -78.18},
    {"nombre": "El Salvador",           "codigo": "SV", "continente": "AM", "lat": 13.79,  "lon": -88.90},
    {"nombre": "Estados Unidos",        "codigo": "US", "continente": "AM", "lat": 37.09,  "lon": -95.71},
    {"nombre": "Granada",               "codigo": "GD", "continente": "AM", "lat": 12.11,  "lon": -61.68},
    {"nombre": "Guatemala",             "codigo": "GT", "continente": "AM", "lat": 15.78,  "lon": -90.23},
    {"nombre": "Guyana",                "codigo": "GY", "continente": "AM", "lat": 4.86,   "lon": -58.93},
    {"nombre": "Haití",                 "codigo": "HT", "continente": "AM", "lat": 18.97,  "lon": -72.29},
    {"nombre": "Honduras",              "codigo": "HN", "continente": "AM", "lat": 15.20,  "lon": -86.24},
    {"nombre": "Jamaica",               "codigo": "JM", "continente": "AM", "lat": 18.11,  "lon": -77.30},
    {"nombre": "México",                "codigo": "MX", "continente": "AM", "lat": 23.63,  "lon": -102.55},
    {"nombre": "Nicaragua",             "codigo": "NI", "continente": "AM", "lat": 12.87,  "lon": -85.21},
    {"nombre": "Panamá",                "codigo": "PA", "continente": "AM", "lat": 8.54,   "lon": -80.78},
    {"nombre": "Paraguay",              "codigo": "PY", "continente": "AM", "lat": -23.44, "lon": -58.44},
    {"nombre": "Perú",                  "codigo": "PE", "continente": "AM", "lat": -9.19,  "lon": -75.02},
    {"nombre": "República Dominicana",  "codigo": "DO", "continente": "AM", "lat": 18.74,  "lon": -70.16},
    {"nombre": "San Cristóbal y Nieves","codigo": "KN", "continente": "AM", "lat": 17.36,  "lon": -62.78},
    {"nombre": "San Vicente y Granadinas","codigo": "VC", "continente": "AM", "lat": 13.25, "lon": -61.20},
    {"nombre": "Santa Lucía",           "codigo": "LC", "continente": "AM", "lat": 13.91,  "lon": -60.98},
    {"nombre": "Surinam",               "codigo": "SR", "continente": "AM", "lat": 3.92,   "lon": -56.03},
    {"nombre": "Trinidad y Tobago",     "codigo": "TT", "continente": "AM", "lat": 10.69,  "lon": -61.22},
    {"nombre": "Uruguay",               "codigo": "UY", "continente": "AM", "lat": -32.52, "lon": -55.77},
    {"nombre": "Venezuela",             "codigo": "VE", "continente": "AM", "lat": 6.42,   "lon": -66.59},

    # ── OCEANÍA ──
    {"nombre": "Australia",             "codigo": "AU", "continente": "OC", "lat": -25.27, "lon": 133.78},
    {"nombre": "Fiyi",                  "codigo": "FJ", "continente": "OC", "lat": -17.71, "lon": 178.06},
    {"nombre": "Islas Marshall",        "codigo": "MH", "continente": "OC", "lat": 7.13,   "lon": 171.18},
    {"nombre": "Islas Salomón",         "codigo": "SB", "continente": "OC", "lat": -9.64,  "lon": 160.16},
    {"nombre": "Kiribati",              "codigo": "KI", "continente": "OC", "lat": -3.37,  "lon": -168.73},
    {"nombre": "Micronesia",            "codigo": "FM", "continente": "OC", "lat": 7.43,   "lon": 150.55},
    {"nombre": "Nauru",                 "codigo": "NR", "continente": "OC", "lat": -0.53,  "lon": 166.93},
    {"nombre": "Nueva Zelanda",         "codigo": "NZ", "continente": "OC", "lat": -40.90, "lon": 174.89},
    {"nombre": "Palaos",                "codigo": "PW", "continente": "OC", "lat": 7.51,   "lon": 134.58},
    {"nombre": "Papúa Nueva Guinea",    "codigo": "PG", "continente": "OC", "lat": -6.31,  "lon": 143.96},
    {"nombre": "Samoa",                 "codigo": "WS", "continente": "OC", "lat": -13.76, "lon": -172.10},
    {"nombre": "Tonga",                 "codigo": "TO", "continente": "OC", "lat": -21.18, "lon": -175.20},
    {"nombre": "Tuvalu",                "codigo": "TV", "continente": "OC", "lat": -7.11,  "lon": 177.64},
    {"nombre": "Vanuatu",               "codigo": "VU", "continente": "OC", "lat": -15.38, "lon": 166.96},

    # ── ANTÁRTIDA ──
    {"nombre": "Antártida",             "codigo": "AQ", "continente": "AN", "lat": -90.00, "lon": 0.00},
]


class Command(BaseCommand):
    help = "Carga continentes y países en la base de datos"

    def handle(self, *args, **options):
        self.stdout.write("🌍 Cargando datos geográficos...\n")

        # ── Crear continentes ──
        continentes_creados = 0
        continentes_map     = {}

        for datos in CONTINENTES:
            continente, created = Continente.objects.get_or_create(
                codigo=datos["codigo"],
                defaults={"nombre": datos["nombre"]}
            )
            continentes_map[datos["codigo"]] = continente
            if created:
                continentes_creados += 1
                self.stdout.write(f"  ✓ Continente: {continente.nombre}")

        self.stdout.write(f"\n✅ {continentes_creados} continentes creados\n")

        # ── Crear países ──
        paises_creados = 0
        errores        = 0

        for datos in PAISES:
            continente = continentes_map.get(datos["continente"])
            if not continente:
                self.stderr.write(f"  ❌ Continente no encontrado: {datos['continente']} para {datos['nombre']}")
                errores += 1
                continue

            pais, created = Pais.objects.get_or_create(
                codigo=datos["codigo"],
                defaults={
                    "nombre":     datos["nombre"],
                    "continente": continente,
                    "latitud":    datos["lat"],
                    "longitud":   datos["lon"],
                }
            )
            if created:
                paises_creados += 1

        self.stdout.write(f"✅ {paises_creados} países creados")
        if errores:
            self.stderr.write(f"⚠️  {errores} errores")

        self.stdout.write(
            f"\n🎉 Datos geográficos cargados: "
            f"{Continente.objects.count()} continentes, "
            f"{Pais.objects.count()} países"
        )