"""Builds tourism.json from the official files listed in SOURCES (the
Ministry of Tourism and Office des Changes Excel files, downloaded into one
folder) plus the figures read from the official reports (Bank Al-Maghrib,
DEPF, Observatoire du Tourisme) and, where marked, press reports.

    python3 scripts/build_tourism_data.py <folder with the .xlsx files> tourism.json
    python3 scripts/tourism_forecast.py

Needs openpyxl. Office des Changes files are expected as oc_<name>.xlsx.
When a source is updated: download it again, update its "published" date
and any hand-entered figures below, rebuild, re-run the forecast and check
the cross-checks."""
import json, os, re, sys
import openpyxl

RAW = sys.argv[1]
OUT = sys.argv[2]
ACCESSED = '2026-11-12'

SOURCES = {
  'mt_ind': dict(publisher='Ministère du Tourisme, de l’Artisanat et de l’Economie Sociale et Solidaire', kind='official',
                 title='Chiffres clés: Indicateurs touristiques 2025 (arrivées aux postes frontières, nuitées EHTC, recettes)',
                 url='https://mtaess.gov.ma/wp-content/uploads/2026/03/Indicateurs-touristiques-2025.xlsx', published='2026-03-06'),
  'mt_pf': dict(publisher='Ministère du Tourisme', kind='official', title='Evolution par point d’entrée des arrivées des touristes aux postes frontières, 2019 et 2023–2025',
                url='https://mtaess.gov.ma/wp-content/uploads/2026/03/Tourisme-PF-2025.xlsx', published='2026-03-06'),
  'mt_dest': dict(publisher='Ministère du Tourisme', kind='official', title='Evolution par région des nuitées dans les établissements d’hébergement touristique classés, 2019 et 2023–2025',
                  url='https://mtaess.gov.ma/wp-content/uploads/2026/03/Tourisme-destination-2025.xlsx', published='2026-03-06'),
  'mt_nat': dict(publisher='Ministère du Tourisme', kind='official', title='Evolution par nationalité des arrivées des touristes aux postes frontières, 2019 et 2023–2025 (MRE counted under their country of residence)',
                 url='https://mtaess.gov.ma/wp-content/uploads/2026/03/Evolution_nationalite_PF-2025.xlsx', published='2026-03-06'),
  'mt_mkt': dict(publisher='Ministère du Tourisme', kind='official', title='Evolution par marché des nuitées dans les établissements d’hébergement touristique classés, 2019 et 2023–2025',
                 url='https://mtaess.gov.ma/wp-content/uploads/2026/03/Evolution_marche_nuitees-2025.xlsx', published='2026-03-06'),
  'mt_cp2025': dict(publisher='Ministère du Tourisme', kind='official', title='Communiqué: près de 20 millions de touristes en 2025',
                    url='https://mtaess.gov.ma/fr/tourisme-le-maroc-atteint-un-seuil-historique-de-pres-de-20-millions-de-touristes-en-2025/', published='2026-01-09'),
  'obs_home': dict(publisher='Observatoire du Tourisme', kind='official', title='Headline counters on the home page (arrivals Jan–Oct 2026, nights Jan–Sep 2026, receipts Jan–Sep 2026)',
                   url='https://observatoiredutourisme.ma/', published='2026-11-09'),
  'obs_roadmap': dict(publisher='Observatoire du Tourisme', kind='official', title='Feuille de route du tourisme 2023–2026 (targets for 2026 and the 2030 vision)',
                      url='https://observatoiredutourisme.ma/a-propos/feuille-de-route-du-tourisme/', published='2024-12-13'),
  'oc_monthly': dict(publisher='Office des Changes', kind='official', title='Recettes voyages mensuelles (MDH), 2004 – juin 2026',
                     url='https://www.oc.gov.ma/sites/default/files/Evol_recettes_Voyages_16.xlsx', published='2026-10-01'),
  'oc_country': dict(publisher='Office des Changes', kind='official', title='Recettes voyages par pays (MDH), 2005–2025 (2025 provisional)',
                     url='https://www.oc.gov.ma/sites/default/files/Recettes_Voyages%20par%20pays_1.xlsx', published='2026-07-31'),
  'oc_spend': dict(publisher='Office des Changes', kind='official', title='Dépenses voyages par nature (MDH)',
                   url='https://www.oc.gov.ma/sites/default/files/Dep_Voyages_Nature_0.xlsx', published='2026-05-11'),
  'oc_imee_2609': dict(publisher='Office des Changes', kind='official', title='Indicateurs mensuels des échanges extérieurs, septembre 2026 (provisional)',
                       url='https://www.oc.gov.ma/sites/default/files/2026-10/IMEE_Septembre_2026_0.pdf', published='2026-10-30'),
  'bam_ra2025': dict(publisher='Bank Al-Maghrib', kind='official', title='Rapport annuel 2025 (tables 1.2.2–1.2.4, from Ministry of Tourism data)',
                     url='https://www.bkam.ma/content/download/847720/9164323/RAPPORT%20FR%2025.pdf', published='2026-07-19'),
  'bam_ra2024': dict(publisher='Bank Al-Maghrib', kind='official', title='Rapport annuel 2024 (tables 1.2.2–1.2.4, from Ministry of Tourism data)',
                     url='https://www.bkam.ma/content/download/829011/9037410/Rapport%2024%20FR.pdf', published='2025-07-28'),
  'bam_ra2023': dict(publisher='Bank Al-Maghrib', kind='official', title='Rapport annuel 2023',
                     url='https://www.bkam.ma/content/download/809663/8903269/RAPPORT%20FR%20_23.pdf', published='2024-07-29'),
  'bam_ra2022': dict(publisher='Bank Al-Maghrib', kind='official', title='Rapport annuel 2022 (table 1.2.4 and statistical annex A2.9)',
                     url='https://www.bkam.ma/content/download/788536/8758333/RA-2022-FR.pdf', published='2023-07-21'),
  'depf_355': dict(publisher='DEPF, Ministère de l’Economie et des Finances', kind='official', title='Note de conjoncture n° 355, septembre 2026',
                   url='https://www.finances.gov.ma/Publication/depf/2026/nc355.pdf', published='2026-09'),
  'depf_356': dict(publisher='DEPF, Ministère de l’Economie et des Finances', kind='official', title='Note de conjoncture n° 356, octobre 2026',
                   url='https://www.finances.gov.ma/Publication/depf/2026/NC356.pdf', published='2026-10'),
  # Secondary: ONDA (Airports of Morocco) blocks automated access, so its own releases could not be read
  'sec_ecoactu_onda2025': dict(publisher='EcoActu, reporting ONDA figures announced by the Minister of Transport', kind='secondary',
                               title='Trafic aérien : plus de 36 millions de passagers en 2025 (ONDA)',
                               url='https://ecoactu.ma/trafic-aerien-plus-de-36-millions-de-passagers-en-2025-onda/', published='2026-05-26'),
  'sec_hespress_depf_air2025': dict(publisher='Hespress FR, reporting the DEPF', kind='secondary', title='DEPF : le transport aérien signe un record de 36,4 millions de passagers en 2025',
                                    url='https://fr.hespress.com/460529-460529.html', published=None),
  'sec_lavieeco_onda2024': dict(publisher='La Vie éco, reporting the ONDA board meeting of 2 April 2025', kind='secondary', title='ONDA : une dynamique sans précédent (32,7 millions de passagers en 2024, +21%; 2025 target 37,6 millions)',
                               url='https://www.lavieeco.com/affaires/onda-une-dynamique-sans-precedent-portee-par-la-strategie-aeroports-2030/', published='2025-04-02'),
  'sec_bladi_depf_air2024': dict(publisher='Bladi.net, reporting ONDA figures cited by the DEPF', kind='secondary', title='Trafic aérien au Maroc : l’année de tous les records (32,7 millions, +21%)',
                                 url='https://www.bladi.net/trafic-aerien-maroc-annee-tous-records,113395.html', published='2025-03-02'),
  'sec_hespress_air0826': dict(publisher='Hespress FR, reporting ONDA', kind='secondary', title='Aéroports : le Maroc dépasse les 26 millions de passagers à fin août (2026)',
                               url='https://fr.hespress.com/493214-aeroports-marocains-plus-de-26-millions-de-passagers-a-fin-aout.html', published='2026-10-20'),
  'sec_hespress_rak2025': dict(publisher='Hespress FR, reporting ONDA', kind='secondary', title='Marrakech-Menara : trafic en hausse de 10,09% en 2025',
                               url='https://fr.hespress.com/460832-marrakech-menara-le-trafic-international-des-passagers-en-hausse-de-1009-en-2025.html', published='2026-02-04'),
  'sec_hespress_aga2025': dict(publisher='Hespress FR, reporting ONDA', kind='secondary', title='Aéroport Agadir Al-Massira : trafic en hausse de 11,07% en 2025',
                               url='https://fr.hespress.com/461002-aeroport-agadir-al-massira-le-trafic-des-passagers-en-hausse-de-11-07-en-2025.html', published='2026-02-09'),
  'sec_hespress_rba2025': dict(publisher='Hespress FR, reporting ONDA', kind='secondary', title='Aéroport Rabat-Salé : hausse de plus de 25% du trafic des passagers en 2025',
                               url='https://fr.hespress.com/461315-aeroport-rabat-sale-hausse-de-plus-de-25-du-trafic-des-passagers-en-2025.html', published='2026-02-05'),
  'sec_mwn_cmn2025': dict(publisher='Morocco World News / North Africa Post, reporting an ONDA statement of 25 December 2025', kind='secondary',
                          title='Casablanca airport: 10.5 million in 2024 to 11.5 million in 2025 (+9.3%), year-end projection',
                          url='https://northafricapost.com/93604-casablanca-airport-hits-11-million-passengers-as-can-2025-spurs-record-traffic.html', published='2025-12-26'),
  'sec_telquel_ytd0926': dict(publisher='TelQuel, reporting the Ministry of Tourism', kind='secondary', title='15,7 millions de touristes accueillis au Maroc à fin septembre 2026',
                              url='https://telquel.ma/instant-t/2026/10/08/157-millions-de-touristes-accueillis-au-maroc-a-fin-septembre-2026_2012035/', published='2026-10-08'),
}
for s in SOURCES.values():
    s['accessed'] = ACCESSED


def sheet(name):
    wb = openpyxl.load_workbook(os.path.join(RAW, name), data_only=True)
    return [r for r in wb.worksheets[0].iter_rows(values_only=True) if any(c is not None for c in r)]


series = []
def add(id, metric, label, unit, freq, points, **kw):
    series.append(dict(id=id, metric=metric, label=label, unit=unit, freq=freq, points=points, **kw))

def pt(period, value, status, source, **kw):
    p = dict(period=str(period), value=value, status=status, source=source)
    if str(period) in ('2020', '2021'):
        p['covid'] = True
    p.update(kw)
    return p

# ── Arrivals at border posts, annual 2013–2025 (Ministry) ─────────────
rows = sheet('Indicateurs-touristiques-2025.xlsx')
blocks, cur = {}, None
for r in rows:
    a, b = r[0], r[1]
    if isinstance(a, str) and a.strip().isdigit():
        a = int(a.strip())       # 2019 and 2023+ nights are stored as text
    if isinstance(a, str) and a.strip() and b is None:
        cur = a.strip(); blocks[cur] = {}
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and cur:
        blocks[cur][int(a)] = b
arr = blocks['Arrivées des touristes aux postes frontières']
add('arrivals_total', 'arrivals', 'Arrivals at border posts (foreign tourists and MRE)', 'arrivals', 'A',
    [pt(y, int(v), 'final', 'mt_ind', **({'note': 'Borders closed 29 Nov 2021 – 7 Feb 2022'} if y == 2022 else {}))
     for y, v in sorted(arr.items())])

# Year to date 2026
add('arrivals_ytd', 'arrivals', 'Arrivals at border posts, year to date', 'arrivals', 'YTD', [
    pt('2026-01/2026-08', 14_100_000, 'provisional', 'depf_355', yoy_pct=4.5, rounded=True),
    pt('2026-01/2026-09', 15_700_000, 'provisional', 'depf_356', yoy_pct=5.0, rounded=True, also=['sec_telquel_ytd0926']),
    pt('2026-01/2026-10', 17_400_000, 'provisional', 'obs_home', yoy_pct=5.0, rounded=True),
])

# Foreign tourists vs MRE (no longer split from 2025)
tes = {2019: 7_043_006, 2020: 1_407_994, 2021: 1_284_335, 2022: 5_064_774, 2023: 7_150_000, 2024: 8_798_000}
mre = {2019: 5_889_254, 2020: 1_369_808, 2021: 2_437_367, 2022: 5_804_000, 2023: 7_375_000, 2024: 8_614_000}
srcs = {2019: 'bam_ra2022', 2020: 'bam_ra2022', 2021: 'bam_ra2022', 2022: 'bam_ra2022', 2023: 'bam_ra2024', 2024: 'bam_ra2024'}
add('arrivals_tes', 'arrivals', 'Arrivals: foreign tourists (TES)', 'arrivals', 'A',
    [pt(y, v, 'final', srcs[y], **({'rounded': True} if y >= 2022 else {})) for y, v in tes.items()],
    note='From 2025 the Ministry no longer splits arrivals into foreign tourists and MRE (Bank Al-Maghrib, Rapport annuel 2025, note 1, p. 36).')
add('arrivals_mre', 'arrivals', 'Arrivals: Moroccans resident abroad (MRE)', 'arrivals', 'A',
    [pt(y, v, 'final', srcs[y], **({'rounded': True} if y >= 2022 else {})) for y, v in mre.items()],
    note='From 2025 the Ministry no longer splits arrivals into foreign tourists and MRE.')

# Foreign tourists (TES only) by nationality, thousands (BAM 2024 table 1.2.2)
tes_nat = {'France': (1991, 1505, 1999, 2422), 'Spain': (881, 902, 1304, 1498), 'United Kingdom': (551, 482, 679, 999),
           'Italy': (352, 240, 335, 452), 'Germany': (413, 171, 281, 361), 'United States': (347, 231, 332, 351),
           'Canada': (131, 72, 108, 126), 'China': (141, 28, 60, 106), 'Senegal': (58, 57, 69, 86),
           'Mauritania': (49, 44, 61, 74), 'Ireland': (26, 30, 43, 56), 'Tunisia': (58, 36, 48, 56),
           'Russia': (40, 18, 33, 53), 'Algeria': (117, 35, 47, 51), 'India': (17, 13, 29, 41)}
for c, vals in tes_nat.items():
    add(f'arrivals_tes_{c}', 'arrivals_tes_by_nationality', f'Foreign tourists (TES) from {c}', 'arrivals', 'A',
        [pt(y, v * 1000, 'final', 'bam_ra2024', rounded=True) for y, v in zip((2019, 2022, 2023, 2024), vals)], dim={'market': c})

EN = {'France': 'France', 'Espagne': 'Spain', 'Belgique': 'Belgium', 'Royaume-Uni': 'United Kingdom', 'Italie': 'Italy',
      'Hollande': 'Netherlands', 'Allemagne': 'Germany', 'Etats Unis': 'United States', 'Canada': 'Canada', 'Portugal': 'Portugal',
      'Suisse': 'Switzerland', 'Arabie saoudite': 'Saudi Arabia', 'Pologne': 'Poland', 'Chine': 'China', 'Turquie': 'Turkey',
      'Autres': 'Other', 'Non résidents': 'Non-residents', 'Résidents': 'Residents (Moroccans living in Morocco)'}

def table4(name, src, metric, label_fmt, idp, unit, extra=None):
    rows = sheet(name)
    hdr = next(r for r in rows if str(r[1]).strip() == '2019')
    years = [int(c) for c in hdr[1:5]]
    for r in rows:
        if r is hdr or not isinstance(r[0], str) or not isinstance(r[1], (int, float)):
            continue
        key = r[0].strip()
        if key.lower() == 'total':
            continue
        name_en = EN.get(key, key)
        add(f'{idp}_{name_en}', metric, label_fmt.format(name_en), unit, 'A',
            [pt(y, int(v), 'final', src) for y, v in zip(years, r[1:5])], dim={'key': name_en, **(extra or {})})

table4('Evolution_nationalite_PF-2025.xlsx', 'mt_nat', 'arrivals_by_market', 'Arrivals from {} (residence, MRE included)', 'arrivals_mkt', 'arrivals')
table4('Evolution_marche_nuitees-2025.xlsx', 'mt_mkt', 'nights_by_market', 'Nights in classified accommodation: {}', 'nights_mkt', 'nights')

# Entry points (air / sea / land and each point)
rows = sheet('Tourisme-PF-2025.xlsx')
MODE = {'T.AIR': 'Air', 'T.MER': 'Sea', 'T.TERRE': 'Land'}
mode = None
for r in rows:
    if not isinstance(r[0], str) or not isinstance(r[1], (int, float)):
        continue
    k = r[0].strip()
    if k == 'Total':
        continue
    if k in MODE:
        mode = MODE[k]
        add(f'arrivals_mode_{mode}', 'arrivals_by_mode', f'Arrivals by {mode.lower()}', 'arrivals', 'A',
            [pt(y, int(v), 'final', 'mt_pf') for y, v in zip((2019, 2023, 2024, 2025), r[1:5])], dim={'mode': mode})
    else:
        nm = re.sub(r'^(A|T) ', '', k)
        add(f'arrivals_entry_{nm}', 'arrivals_by_entry', f'Arrivals through {nm}', 'arrivals', 'A',
            [pt(y, int(v), 'final', 'mt_pf') for y, v in zip((2019, 2023, 2024, 2025), r[1:5])], dim={'mode': mode, 'entry': nm})

# ── Nights in classified accommodation (EHTC) ──────────────────────
nt = blocks['Nuitées dans les EHTC']
add('nights_total', 'nights', 'Nights in classified tourist accommodation (EHTC), current basis', 'nights', 'A',
    [pt(y, int(nt[y]), 'final', 'mt_ind') for y in (2019, 2023, 2024, 2025)],
    basis='current',
    note='Current, wider basis. Comparable years: 2019 and 2023 onwards. 2020–2022 exist only on the previous basis.')
prev = {y: int(v) for y, v in nt.items() if y not in (2019, 2023, 2024, 2025)}
prev_pts = [pt(y, v, 'final', 'mt_ind') for y, v in sorted(prev.items())]
prev_pts += [pt(2019, 25_244_000, 'final', 'bam_ra2024', rounded=True), pt(2023, 25_641_000, 'final', 'bam_ra2024', rounded=True),
             pt(2024, 28_685_000, 'final', 'bam_ra2024', rounded=True)]
add('nights_total_previous_basis', 'nights', 'Nights in classified accommodation, previous basis (not comparable with the current basis)', 'nights', 'A',
    sorted(prev_pts, key=lambda p: p['period']), basis='previous', display=False,
    note='The Ministry’s current file mixes both bases: 2013–2018 and 2020–2022 are on the previous basis, 2019 and 2023+ on the current one. '
         'On the current basis 2024 is 39.9 million; on the previous basis 28.7 million. Kept for reference only, not shown on screens.')
add('nights_ytd', 'nights', 'Nights in classified accommodation, year to date', 'nights', 'YTD', [
    pt('2026-01/2026-08', 30_800_000, 'provisional', 'depf_356', yoy_pct=8.0, rounded=True),
    pt('2026-01/2026-09', 34_800_000, 'provisional', 'obs_home', yoy_pct=7.0, rounded=True),
], basis='current')
table4('Tourisme-destination-2025.xlsx', 'mt_dest', 'nights_by_region', 'Nights in classified accommodation, {} region', 'nights_region', 'nights')

# ── Occupancy (classified accommodation) ───────────────────────────
occ_cur = {'Morocco': (55, 58), 'Marrakech': (71, 73), 'Agadir': (69, 72), 'Casablanca': (53, 57), 'Tanger': (54, 54),
           'Fès': (52, 56), 'Al Haouz': (74, 78), 'Essaouira': (54, 57), 'Rabat': (51, 54), 'Ouarzazate': (39, 47), 'Errachidia': (38, 41)}
for c, (a, b) in occ_cur.items():
    add(f'occupancy_{c}', 'occupancy', f'Occupancy rate, classified accommodation: {c}', '%', 'A',
        [pt(2024, a, 'final', 'bam_ra2025'), pt(2025, b, 'final', 'bam_ra2025')], basis='current', dim={'city': c})
occ_prev = {'Morocco': {2019: 48, 2020: 26, 2021: 25, 2022: 41, 2023: 48, 2024: 51}, 'Marrakech': {2019: 64, 2020: 32, 2021: 28, 2022: 55, 2023: 67, 2024: 72},
            'Agadir': {2019: 58, 2020: 36, 2021: 29, 2022: 52, 2023: 61, 2024: 69}, 'Casablanca': {2019: 50, 2020: 22, 2021: 23, 2022: 37, 2023: 43, 2024: 47},
            'Tanger': {2019: 55, 2020: 25, 2021: 33, 2022: 48, 2023: 52, 2024: 52}, 'Rabat': {2019: 55, 2020: 27, 2021: 27, 2022: 46, 2023: 52, 2024: 52},
            'Fès': {2019: 42, 2020: 24, 2021: 37, 2022: 42, 2023: 43, 2024: 43}}
for c, d in occ_prev.items():
    add(f'occupancy_prev_{c}', 'occupancy', f'Occupancy rate, previous basis: {c}', '%', 'A',
        [pt(y, v, 'final', 'bam_ra2022' if y <= 2021 else ('bam_ra2023' if y == 2023 and c != 'Morocco' else 'bam_ra2024')) for y, v in d.items()],
        basis='previous', display=False, dim={'city': c},
        note='Previous basis. Bank Al-Maghrib’s 2025 report restates 2024 on the current basis (Morocco 51% → 55%), so these are not comparable with 2024–2025 above.')

# ── Travel receipts (Office des Changes) ───────────────────────────
rows = sheet('oc_Evol_recettes_Voyages_16.xlsx')
monthly, annual = [], {}
for r in rows:
    vals = r[2:14]
    if not all(isinstance(v, (int, float)) or v is None for v in vals):
        continue
    if r[1] is None and isinstance(r[2], (int, float)):   # 2026 row has no year label
        yr = 2026
    elif isinstance(r[1], (int, float)):
        yr = int(r[1])
    else:
        continue
    for m, v in enumerate(vals, 1):
        if isinstance(v, (int, float)):
            monthly.append(pt(f'{yr}-{m:02d}', round(float(v), 1), 'provisional' if yr >= 2025 else 'final', 'oc_monthly'))
    if isinstance(r[14], (int, float)) and yr < 2026:
        annual[yr] = round(float(r[14]), 1)
for p in monthly:
    if p['period'][:4] in ('2020', '2021'):
        p['covid'] = True
add('receipts_monthly', 'receipts', 'Travel receipts, monthly', 'MAD million', 'M', sorted(monthly, key=lambda p: p['period']))
add('receipts_total', 'receipts', 'Travel receipts (spending by non-residents and MRE in Morocco)', 'MAD million', 'A',
    [pt(y, v, 'provisional' if y == 2025 else 'final', 'oc_monthly') for y, v in sorted(annual.items())])
add('receipts_ytd', 'receipts', 'Travel receipts, year to date', 'MAD million', 'YTD', [
    pt('2026-01/2026-08', 97_900, 'provisional', 'depf_356', yoy_pct=9.7, rounded=True),
    pt('2026-01/2026-09', 115_257, 'provisional', 'oc_imee_2609', yoy_pct=12.1, prior=102_848, also=['obs_home']),
])
rows = sheet('oc_Recettes_Voyages_par_pays_1.xlsx')
hdr = next(r for r in rows if r[1] == '(En MDH)')
yrs = [int(str(c).split()[0]) for c in hdr[2:23] if c is not None]
CEN = {'FRANCE': 'France', 'ESPAGNE': 'Spain', 'ITALIE': 'Italy', 'ROYAUME-UNI': 'United Kingdom', 'ALLEMAGNE': 'Germany',
       'BELGIQUE': 'Belgium', 'ÉTATS-UNIS': 'United States', 'PAYS-BAS': 'Netherlands', 'ARABIE SAOUDITE': 'Saudi Arabia',
       'CANADA': 'Canada', 'ÉMIRATS ARABES UNIS': 'United Arab Emirates', 'SUISSE': 'Switzerland', 'CHINE': 'China'}
for r in rows:
    if isinstance(r[1], str) and r[1].strip() in CEN:
        c = CEN[r[1].strip()]
        add(f'receipts_country_{c}', 'receipts_by_country', f'Travel receipts from {c}', 'MAD million', 'A',
            [pt(y, round(float(v), 1), 'provisional' if y == 2025 else 'final', 'oc_country') for y, v in zip(yrs, r[2:23]) if y >= 2019], dim={'country': c})
rows = sheet('oc_Dep_Voyages_Nature_0.xlsx')
spend = {}
for r in rows:
    if isinstance(r[1], (int, float)) and 2013 <= r[1] <= 2025:
        spend[int(r[1])] = round(float(r[9] if r[9] is not None else 0), 1)
add('travel_spending', 'travel_spending', 'Travel spending by Moroccan residents abroad', 'MAD million', 'A',
    [pt(y, v, 'final', 'oc_spend') for y, v in sorted(spend.items())])

# ── Air passengers (ONDA, via secondary sources) ───────────────────
add('air_passengers_total', 'air_passengers', 'Passengers at Moroccan airports (all airports)', 'passengers', 'A', [
    pt(2024, 32_700_000, 'final', 'sec_lavieeco_onda2024', rounded=True, also=['sec_bladi_depf_air2024']),
    pt(2025, 36_300_000, 'final', 'sec_ecoactu_onda2025', rounded=True, international=32_400_000, domestic=3_900_000, also=['sec_hespress_depf_air2025']),
], secondary=True, note='ONDA (Airports of Morocco) blocks automated access to its statistics; figures are ONDA’s as reported by the press.')
add('air_passengers_ytd', 'air_passengers', 'Passengers at Moroccan airports, year to date', 'passengers', 'YTD', [
    pt('2026-01/2026-08', 26_040_927, 'provisional', 'sec_hespress_air0826', yoy_pct=8.81, international=23_228_711, domestic=2_812_216, also=['depf_356'])],
    secondary=True, note='Growth +8.8% to end-August also in the DEPF note n° 356 (official).')
ap = {'Casablanca CMN': ((10_500_000, 'sec_mwn_cmn2025', True, 'final'), (11_500_000, 'sec_mwn_cmn2025', True, 'estimate')),
      'Marrakech RAK': ((9_263_261, 'sec_hespress_rak2025', False, 'final'), (10_197_736, 'sec_hespress_rak2025', False, 'final')),
      'Agadir AGA': ((3_129_257, 'sec_hespress_aga2025', False, 'final'), (3_495_277, 'sec_hespress_aga2025', False, 'final')),
      'Rabat RBA': ((1_725_812, 'sec_hespress_rba2025', False, 'final'), (2_169_189, 'sec_hespress_rba2025', False, 'final'))}
for a, ((v24, s24, r24, st24), (v25, s25, r25, st25)) in ap.items():
    p24 = pt(2024, v24, st24, s24, **({'rounded': True} if r24 else {}))
    p25 = pt(2025, v25, st25, s25, **({'rounded': True} if r25 else {}))
    if a.startswith('Casablanca'):
        p25['note'] = 'ONDA statement published 26 Dec 2025, before the year end; rounded. Consistent with Mohammed V’s 32% share of 36.3 million (11.6 million) reported in Feb 2026.'
    add(f'airport_{a}', 'airport_passengers', f'Passengers, {a}', 'passengers', 'A', [p24, p25], secondary=True, dim={'airport': a})
for a, v in (('Casablanca CMN', 8_252_410), ('Marrakech RAK', 7_235_705), ('Agadir AGA', 2_498_637), ('Tanger TNG', 2_058_606), ('Rabat RBA', 1_695_890)):
    add(f'airport_ytd_{a}', 'airport_passengers', f'Passengers Jan–Aug 2026, {a}', 'passengers', 'YTD',
        [pt('2026-01/2026-08', v, 'provisional', 'sec_hespress_air0826')], secondary=True, dim={'airport': a})

# ── Cross-checks (headline figures, two or more sources) ───────────
def pct(a, b):
    return round((a / b - 1) * 100, 2)
crosschecks = [
    dict(metric='Arrivals 2025', used=19_792_594, values=[['mt_ind', 19_792_594], ['bam_ra2025', 19_793_000], ['mt_cp2025', 19_800_000]], max_diff_pct=0.04, note='Agree.'),
    dict(metric='Arrivals 2024', used=17_411_949, values=[['mt_ind', 17_411_949], ['bam_ra2024', 17_412_000], ['bam_ra2025', 17_412_000]], max_diff_pct=0.0, note='Agree.'),
    dict(metric='Arrivals 2023', used=14_524_727, values=[['mt_ind', 14_524_727], ['bam_ra2023', 14_525_000]], max_diff_pct=0.0, note='Agree.'),
    dict(metric='Arrivals 2019', used=12_932_734, values=[['mt_ind', 12_932_734], ['bam_ra2022', 12_932_260]], max_diff_pct=0.004, note='Agree (474 arrivals apart).'),
    dict(metric='Arrivals Jan–Sep 2026', used=15_700_000, values=[['depf_356', 15_700_000], ['sec_telquel_ytd0926', 15_700_000]], max_diff_pct=0.0, note='Agree.'),
    dict(metric='Nights 2025 (current basis)', used=43_426_930, values=[['mt_ind', 43_426_930], ['bam_ra2025', 43_427_000]], max_diff_pct=0.0, note='Agree.'),
    dict(metric='Nights 2024', used=39_915_548, values=[['mt_ind', 39_915_548], ['bam_ra2025', 39_916_000], ['bam_ra2024', 28_685_000]], max_diff_pct=pct(28_685_000, 39_915_548),
         note='Bank Al-Maghrib’s 2024 report (previous basis) gives 28.7 million; the Ministry’s 2026 file and Bank Al-Maghrib’s 2025 report give 39.9 million on the current, wider basis. A change of basis, not an error: the current basis is used and the previous one is not shown.'),
    dict(metric='Nights 2019', used=34_722_176, values=[['mt_ind', 34_722_176], ['bam_ra2025', 34_722_000], ['bam_ra2024', 25_244_000]], max_diff_pct=pct(25_244_000, 34_722_176),
         note='Same change of basis as 2024.'),
    dict(metric='Receipts 2025', used=138_583, values=[['oc_monthly', 138_583], ['oc_country', 138_583], ['mt_ind', 138_101], ['bam_ra2025', 138_600]], max_diff_pct=pct(138_101, 138_583),
         note='Ministry file (March 2026) is 0.35% lower than the Office des Changes’ later release; the Office des Changes figure is used (still provisional).'),
    dict(metric='Receipts 2024', used=114_475, values=[['oc_monthly', 114_475], ['mt_ind', 114_475], ['bam_ra2024', 112_500]], max_diff_pct=pct(112_500, 114_475),
         note='Bank Al-Maghrib’s 2024 report used the first estimate (112.5 billion); the Office des Changes revised it to 114.5 billion.'),
    dict(metric='Receipts 2023', used=107_562, values=[['oc_monthly', 107_562], ['mt_ind', 107_562], ['bam_ra2023', 104_700]], max_diff_pct=pct(104_700, 107_562),
         note='Same: first estimate 104.7 billion, revised 107.6 billion.'),
    dict(metric='Receipts Jan–Sep 2026', used=115_257, values=[['oc_imee_2609', 115_257], ['obs_home', 115_300]], max_diff_pct=0.04, note='Agree.'),
    dict(metric='Airport passengers 2025', used=36_300_000, values=[['sec_ecoactu_onda2025', 36_300_000], ['sec_hespress_depf_air2025', 36_400_000]], max_diff_pct=0.28, note='Agree within rounding.'),
    dict(metric='Airport passengers 2024', used=32_700_000, values=[['sec_lavieeco_onda2024', 32_700_000], ['sec_bladi_depf_air2024', 32_700_000]], max_diff_pct=0.0, note='Agree.'),
    dict(metric='Airport passengers Jan–Aug 2026 growth', used=8.81, values=[['sec_hespress_air0826', 8.81], ['depf_356', 8.8]], max_diff_pct=0.0, note='Agree.'),
]

withheld = [
    dict(item='Tanger Ibn Battouta and national airport passengers 2023 (27.1 million), Tanger 2024–2025', reason='Could not be read on a source page (only in search-engine summaries, one of which matched an unrelated figure). Not published; Tanger is shown for Jan–Aug 2026 only.'),
    dict(item='Fès-Saïss airport passengers 2025', reason='Sources conflict by more than 5%: 1.77 million (Hespress), 1.92 million (Infomédiaire, reporting ONDA), close to 2.5 million (Fes News). ONDA’s own release could not be read.'),
    dict(item='Foreign tourists vs MRE for 2025 and 2026', reason='No longer published: from 2025 the Ministry does not split arrivals (Bank Al-Maghrib, Rapport annuel 2025). The split is shown for 2019–2024 only and is not forecast.'),
    dict(item='Nights in classified accommodation before 2023 (except 2019)', reason='Only on the previous basis, which differs from the current one by more than 25% (e.g. 2024: 28.7 vs 39.9 million). Kept in the file for reference, not shown.'),
    dict(item='Occupancy by city 2019–2023', reason='Previous basis; Bank Al-Maghrib restated 2024 from 51% to 55% (Morocco) on the current basis. Kept for reference, not shown.'),
    dict(item='Monthly arrivals, monthly nights, average length of stay, bed capacity, classified hotels and guesthouses by city and category', reason='Published by the Observatoire du Tourisme in its monthly dashboards and annual report, which are behind an account sign-up (free). Not read.'),
    dict(item='Monthly airport traffic by airport, international vs domestic by airport, aircraft movements by airport', reason='ONDA (Airports of Morocco) blocks automated access to its statistics pages and reports.'),
    dict(item='A claim that the final 2025 figure is 18.2 million arrivals (2024: 15.9 million)', reason='Single aggregator site (wafir.ma); contradicted by the Ministry’s own March 2026 file and by Bank Al-Maghrib. Disregarded.'),
]

targets = [
    dict(id='arrivals_2026', label='Arrivals target, roadmap 2023–2026', period='2026', value=17_500_000, unit='arrivals', source='obs_roadmap', also=['bam_ra2025']),
    dict(id='receipts_2026', label='Foreign-currency tourism receipts target, roadmap 2023–2026', period='2026', value=120_000, unit='MAD million', source='obs_roadmap'),
    dict(id='jobs_2026', label='New direct and indirect jobs target, roadmap 2023–2026', period='2026', value=200_000, unit='jobs', source='obs_roadmap'),
    dict(id='arrivals_2030', label='Arrivals target, 2030 vision', period='2030', value=26_000_000, unit='arrivals', source='obs_roadmap'),
]

out = dict(format='kodo-tourism-1', updated=ACCESSED,
           notes=['Arrivals at border posts include Moroccans resident abroad (MRE). The Ministry’s "by nationality" table counts MRE under their country of residence, so "France" there (5.76 million in 2025) is far above foreign French tourists alone (2.42 million in 2024).',
                  'Nights and occupancy are for classified tourist accommodation (EHTC) only, not all accommodation.',
                  'All figures are calendar years. 2020 and 2021 are flagged as COVID years; borders were also closed from 29 Nov 2021 to 7 Feb 2022.',
                  'Receipts are travel receipts in the balance of payments (Office des Changes), in MAD million, current prices.'],
           sources=SOURCES, series=series, targets=targets, crosschecks=crosschecks, withheld=withheld)
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('series', len(series), 'points', sum(len(s['points']) for s in series))
