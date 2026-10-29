#!/bin/sh
# shellcheck disable=SC2034
# Réglages du tableau de bord "quand partir" (Pont de Bezons · T2), lus par dash.sh au démarrage.
# Modifiable par USB (D:\dashboard\local\env.sh) ; pris en compte au prochain "Démarrer".

# Image générée par le serveur hébergé sur Render (kindle-t2.onrender.com), indépendant de PC_Olivier.
# Secours local si besoin : http://192.168.1.6:8080/kindle.png (PC_Olivier allumé, NordVPN déconnecté).
DASH_URL="https://kindle-t2.onrender.com/kindle.png"

# Rythme de base : toutes les 10 min de 6h à 22h50, puis écran nuit jusqu'à 6h.
INTERVAL_MINUTES=10
ACTIVE_HOURS="6-22"
TIMEZONE="Europe/Paris"
REFRESH_SCHEDULE="*/10 6-22 * * *"

# Heures de pointe : toutes les minutes de 6h00 à 9h59 (combiné par le wrapper next-wakeup).
PEAK_SCHEDULE="* 6-9 * * *"

# Au-delà de ce délai (s) avant le prochain réveil, on affiche sleeping.png au lieu de rafraîchir.
SLEEP_SCREEN_INTERVAL=660

# Rafraîchissement complet (flash) une fois sur N, les autres sont partiels (sans flash).
FULL_DISPLAY_REFRESH_RATE=6
