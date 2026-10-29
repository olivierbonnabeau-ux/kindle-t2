@echo off
rem Lance le serveur Kindle T2 (à utiliser tel quel, ou via le Planificateur de tâches)
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist logs mkdir logs
:loop
echo [%date% %time%] demarrage serveur >> logs\server.log
python server.py >> logs\server.log 2>&1
echo [%date% %time%] serveur arrete, relance dans 10 s >> logs\server.log
rem ping plutot que timeout : timeout se bloque sur "Terminer le programme de commandes ?" apres un Ctrl+C
ping -n 11 127.0.0.1 > nul
goto loop
