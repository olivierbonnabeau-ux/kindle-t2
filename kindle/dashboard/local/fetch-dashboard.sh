#!/bin/sh
# Récupère l'image du tableau de bord dans "$1" (appelé par dash.sh).
# 1) essai avec le magasin de certificats du Kindle ;
# 2) repli avec le bundle Mozilla à jour embarqué (cacert.pem) : le magasin du Kindle 5.12
#    est ancien et peut ne pas connaître les racines récentes. La vérification TLS reste active.
# Délais larges : le serveur Render gratuit met jusqu'à ~1 min à se réveiller le matin.
OUT=$1
CA="$(dirname "$0")/../cacert.pem"
case "$DASH_URL" in
/*) exec cp "$DASH_URL" "$OUT" ;;
esac

fetch() {
  curl -sSf --max-time 75 --retry 4 --retry-delay 15 \
    -H "X-Kindle-Battery: $(gasgauge-info -s)" \
    "$@" -o "$OUT" "$DASH_URL"
}

fetch && exit 0
[ -f "$CA" ] && fetch --cacert "$CA"
