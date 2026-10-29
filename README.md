# Kindle T2 — « quand partir » (Pont de Bezons → Porte de Versailles)

Écran e-ink pour Kindle jailbreaké : pour Cam et Oliv, dans combien de minutes
partir de l'appart pour attraper le prochain tram T2, plus les 4 prochains
départs et l'état du trafic. Données temps réel : API PRIM (Île-de-France Mobilités).

## 1. Installer (une fois, sur PC_Olivier)

```bash
cd "C:\Users\olivi\OneDrive\Claude\kindle-t2"
python -m pip install -r requirements.txt
```

Python 3.12 est déjà installé. Les dépendances : requests, Pillow, PyYAML, python-dotenv, Flask, tzdata.

## 2. Mettre la clé PRIM

1. Créer un compte gratuit sur https://prim.iledefrance-mobilites.fr
2. Mon compte → **Mes applications** → Créer une application (ex. « Kindle T2 »)
3. Dans l'application, souscrire aux API **Prochains passages (plateforme IDFM)** et **Messages info trafic**
4. Copier la clé affichée, puis :

```bash
copy .env.example .env
```

et remplacer `colle_ta_cle_ici` par la clé dans `.env` (jamais dans le code, le fichier est dans `.gitignore`).

## 3. Valider la clé et l'arrêt

```bash
python test_prim.py
```

Affiche le code HTTP, puis les prochains départs T2 → Porte de Versailles en clair
(`--raw` pour voir le JSON SIRI brut). Si 401/403 : clé invalide ou API non souscrite.
Les identifiants (quais `23445` / `25647`, ligne `C01390`) sont dans `config.yaml` ;
`python find_ids.py` les retrouve via l'open data si besoin.

## 4. Lancer le serveur

```bash
python server.py
```

ou double-clic sur `run.bat` (relance automatique si le serveur plante, log dans `logs\server.log`).

- `http://localhost:8080/kindle.png` → l'image 758×1024
- `http://localhost:8080/` → page HTML qui affiche l'image et se recharge seule
- `http://localhost:8080/health` → état (mode, données périmées ou non, erreur)

L'image n'est jamais régénérée plus d'une fois toutes les 30 s (`schedule.min_regen_s`),
l'API PRIM pas plus d'une fois toutes les 30 s (`prim.cache_s`). Si PRIM tombe,
la dernière réponse valide reste affichée avec « Données indisponibles ».

Plages horaires (`config.yaml` → `schedule`) : 6h–10h rafraîchissement conseillé 60 s,
reste de la journée 5 min, 23h–6h écran « nuit » (heure + lune, aucun appel API).
Le délai conseillé est renvoyé dans l'en-tête HTTP `X-Refresh-Seconds`.

## 5. Démarrage automatique

**Déjà en place (29/10/2026)** : un raccourci « Kindle T2 » dans le dossier Démarrage de la session
(`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Kindle T2.lnk`) lance `run.bat` en fenêtre
réduite à chaque ouverture de session, sans droits administrateur. Pour le retirer : supprimer le raccourci
(touche Windows + R, `shell:startup`). Pour l'arrêter sans le retirer : fermer la fenêtre « cmd » réduite
dans la barre des tâches.

**Variante Planificateur de tâches** (nécessite un PowerShell **administrateur**, sinon « Accès refusé ») :

```powershell
$bat = "C:\Users\olivi\OneDrive\Claude\kindle-t2\run.bat"
schtasks /Create /TN "Kindle T2" /SC ONLOGON /RL LIMITED /F /TR "cmd /c `"$bat`""
```

Ou à la main : Planificateur de tâches → Créer une tâche → Déclencheur « À l'ouverture de session »,
Action « Démarrer un programme » = `run.bat`, Démarrer dans = le dossier du projet,
et dans Conditions décocher « Arrêter si l'ordinateur passe sur batterie ».
Pour un démarrage sans ouverture de session, remplacer `/SC ONLOGON` par `/SC ONSTART` et ajouter `/RU "olivi"` (demandera le mot de passe Windows).

Pour vérifier / arrêter : `schtasks /Run /TN "Kindle T2"`, `schtasks /End /TN "Kindle T2"`.

Trouver l'IP de PC_Olivier sur le Wi-Fi : `ipconfig` (ligne « Adresse IPv4 », ex. 192.168.1.42).
Pensez à autoriser le port 8080 dans le pare-feu Windows si le Kindle ne voit pas la page :

```powershell
netsh advfirewall firewall add rule name="Kindle T2" dir=in action=allow protocol=TCP localport=8080
```

## 6. Côté Kindle (Paperwhite 2, 5.12.2.2, jailbreak WinterBreak2 — fait le 29/10/2026)

Affichage par **kindle-dash**, fork Paperwhite [pusi77/kindle-dash-pw3](https://github.com/pusi77/kindle-dash-pw3)
(même plateforme Wario que le PW2). Installé dans `/mnt/us/dashboard` avec nos réglages depuis `kindle/` :

- `kindle/dashboard/local/env.sh` : URL de l'image, toutes les 10 min de 6h à 22h50, **toutes les minutes de 6h à 9h59**
  (`PEAK_SCHEDULE`, combiné par le wrapper `kindle/dashboard/next-wakeup`), écran nuit ensuite.
- `kindle/documents/*.sh` : scriptlets visibles comme des livres dans la bibliothèque.
- `kindle/copier_dashboard.ps1` : (ré)installe tout sur le Kindle branché en USB (release extraite dans `jailbreak/kindle-dash-pw3/`).

Utilisation :

- **« Tableau de bord T2 - Test »** : une seule récupération + affichage, l'interface Kindle reste. Log : `dashboard/logs/test.log`.
- **« Tableau de bord T2 - Démarrer »** : lance la boucle (interface Kindle coupée, veille profonde entre deux réveils). Log : `dashboard/logs/dash.log`, batterie : `dashboard/battery.log`.
- **Arrêter** : maintenir le bouton d'allumage ~40 s (redémarrage, rien ne se relance tout seul), ou créer un fichier `dashboard/STOP`.
- Brancher sur un **chargeur mural** (pas un PC : le mode USB coupe la boucle) : branché, le Kindle ne se met pas en veille et garde le Wi-Fi, idéal au mur.
- Le serveur doit être joignable sur `http://192.168.1.6:8080/kindle.png` : Python est autorisé dans le pare-feu (profil privé).
  Si NordVPN est connecté sur PC_Olivier, activer « Autoriser l'accès à distance sur le réseau local » (LAN discovery), sinon le Kindle ne la joint pas.
- Navigateur expérimental en dépannage : `http://192.168.1.6:8080/` (la page se recharge toute seule).

## Pictos

Mettre vos PNG dans `pictos/cam/` et `pictos/oliv/` (≈200×200 px, fond blanc ou transparent).
Un picto différent est choisi chaque jour. Si un nom de fichier contient un mot météo
(`pluie`, `soleil`, …) et que `render_screen(..., weather="pluie")` est appelé, il est préféré.
`make_placeholder_pictos.py` génère des silhouettes de secours (déjà fait).

## Fichiers

| Fichier | Rôle |
|---|---|
| `config.yaml` | ids arrêt/ligne, personnes (marche, marge), plages horaires, port |
| `prim_client.py` | appels PRIM (stop-monitoring + general-message), cache 30 s, repli sur dernière réponse |
| `logic.py` | calcul « partir dans X min » / « Maintenant ! » |
| `render.py` | image 758×1024 niveaux de gris (`python render.py` → `preview.png` avec données simulées) |
| `server.py` | Flask : `/kindle.png`, `/`, `/health` |
| `test_prim.py` | test de la clé et de l'arrêt |
| `find_ids.py` | recherche des ids dans l'open data IDFM |
| `run.bat` | lancement avec relance auto |
