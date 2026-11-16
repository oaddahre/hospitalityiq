KODO - HOTEL FIGURES TEMPLATE / MODELE DE DONNEES HOTEL
========================================================

ENGLISH

What to send: one row per month, for complete months only (for example the
last 12 months). Your figures are confidential: Kodo uses them only to check
and improve its occupancy model. They are never shown to other clients,
by name or otherwise.

Columns (file: kodo_hotel_figures_en.csv or .xlsx):
  month            the month, as 2026-10 (or 10/2026)
  occupancy_pct    occupancy for the month, in %: rooms sold / rooms available (e.g. 72.5)
  adr_mad          average daily rate in Moroccan dirhams: rooms revenue / rooms sold,
                   excluding taxes (e.g. 1450)
  rooms_revpar_mad       optional: rooms revenue / rooms available (= occupancy x ADR)
  rooms_available  optional: room-nights available in the month (rooms x nights open)

Daily figures are welcome too: use a "date" column (2026-10-31) instead of
"month", one row per night.

Checks when the file is loaded: occupancy between 0 and 100%, ADR between
100 and 100,000 MAD, Rooms RevPAR within 5% of occupancy x ADR, no month listed
twice, no month that is not finished yet, rooms available not above the
hotel's rooms x the days of the month. Each problem is reported with its row
number. Sending a month again replaces the earlier figure.

Example:
  month,occupancy_pct,adr_mad,rooms_revpar_mad,rooms_available
  2026-09,71.5,1500,1072.5,4500

FRANCAIS

A envoyer : une ligne par mois, pour des mois complets uniquement (par
exemple les 12 derniers mois). Vos chiffres sont confidentiels : Kodo les
utilise uniquement pour verifier et ameliorer son modele d'occupation. Ils
ne sont jamais montres aux autres clients, ni par nom ni autrement.

Colonnes (fichier : kodo_hotel_figures_fr.csv ou .xlsx) :
  mois                  le mois, au format 2026-10 (ou 10/2026)
  taux_occupation_pct   taux d'occupation du mois en % : chambres vendues / chambres disponibles (ex. 72,5)
  prix_moyen_mad        prix moyen par chambre vendue (ADR) en dirhams, hors taxes :
                        CA hebergement / chambres vendues (ex. 1450)
  rooms_revpar_mad            facultatif : CA hebergement / chambres disponibles (= taux x prix moyen)
  chambres_disponibles  facultatif : nuitees-chambres disponibles dans le mois (chambres x nuits ouvertes)

Les chiffres journaliers sont aussi bienvenus : une colonne "date"
(31/10/2026) a la place de "mois", une ligne par nuit.

Controles au chargement : taux entre 0 et 100 %, prix moyen entre 100 et
100 000 MAD, Rooms RevPAR a 5 % pres de taux x prix moyen, pas de mois en double,
pas de mois non termine, chambres disponibles pas au-dessus des chambres de
l'hotel x les jours du mois. Chaque probleme est signale avec son numero de
ligne. Un mois renvoye remplace le chiffre precedent.

Exemple :
  mois,taux_occupation_pct,prix_moyen_mad,rooms_revpar_mad,chambres_disponibles
  2026-09,"71,5",1500,"1072,5",4500
