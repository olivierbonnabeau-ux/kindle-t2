#!/bin/sh
# shellcheck disable=SC2034
# Réglages du tableau de bord "quand partir" (Pont de Bezons · T2), lus par dash.sh au démarrage.
# Modifiable par USB (D:\dashboard\local\env.sh) ; pris en compte au prochain "Démarrer".

# Image générée par le serveur hébergé sur Render (kindle-t2.onrender.com), indépendant de PC_Olivier.
# Secours local si besoin : http://192.168.1.6:8080/kindle.png (PC_Olivier allumé, NordVPN déconnecté).
DASH_URL="https://kindle-t2.onrender.com/kindle.png"

# Rythme de base : toutes les 10 min de 6h à 23h50.
INTERVAL_MINUTES=10
ACTIVE_HOURS="5-23"
TIMEZONE="Europe/Paris"
REFRESH_SCHEDULE="*/10 6-23 * * *"

# Horaires supplémentaires (cron 5 champs, séparés par ";") : le wrapper next-wakeup prend le réveil
# le plus proche parmi REFRESH_SCHEDULE et ceux-ci.
#   "30-59 5 * * *"       : toutes les minutes de 5h30 à 5h59 (premier T2 vers 5h30)
#   "* 6-9 * * *"         : toutes les minutes de 6h00 à 9h59
#   "*/10 0 * * *"        : toutes les 10 min de 0h00 à 0h50 (dernier T2 ~0h30 en semaine)
#   "*/10 1 * * SAT,SUN"  : idem de 1h00 à 1h50 les nuits de vendredi et samedi (dernier T2 ~1h30)
EXTRA_SCHEDULES="30-59 5 * * *;* 6-9 * * *;*/10 0 * * *;*/10 1 * * SAT,SUN"

# MODE CONTINU : si FIXED_INTERVAL_S est défini, les horaires ci-dessus sont ignorés et le Kindle
# recommence un cycle (téléchargement + affichage + pause) toutes les ~FIXED_INTERVAL_S + 10 s,
# sans jamais se mettre en veille. Avec 10 → un rafraîchissement toutes les ~20 s, jour et nuit
# (la nuit, c'est le serveur qui envoie l'écran "Bonne nuit" avec l'heure).
# Prévu pour un Kindle branché sur un chargeur : sur batterie, le Wi-Fi est coupé entre deux
# cycles et chaque reconnexion ajoute ~20 s. Mettre la ligne en commentaire pour revenir aux horaires.
FIXED_INTERVAL_S=10

# Au-delà de ce délai (s) avant le prochain réveil, on affiche sleeping.png au lieu de rafraîchir
# (horaires seulement : après 0h50, ou 1h50 le week-end, le prochain réveil est 5h30 → écran nuit).
SLEEP_SCREEN_INTERVAL=660

# Rafraîchissement complet (flash) une fois sur N, les autres sont partiels (sans flash).
# En mode continu 20 s, 15 → un flash toutes les ~5 min pour effacer les traces.
FULL_DISPLAY_REFRESH_RATE=15
