# Scan-m3u-file-on-actieve-links
m3u-scanner-gui.py

M3U Scanner - Handleiding
1: Deze tool controleert welke zenders in je M3U-afspeellijst werken en welke niet.
2: Installatie en vereisten

Zorg dat Python is geïnstalleerd op je computer
Installeer de benodigde module:

pip install requests

Gebruik

1: Start het programma:

python m3u-scanner-gui.py

2: Klik op "Selecteer Bestand" om je M3U-bestand te kiezen
3: Je kunt de timeout-waarde en het aantal gelijktijdige verbindingen aanpassen
4: Klik op "Start Scan" om te beginnen
5: De voortgang wordt getoond tijdens het scannen
6: Na afloop zie je in de tabbladen:
 
   * "Log": Algemene informatie over de scan
   * "Actieve Zenders": Lijst met werkende zenders
   * "Inactieve Zenders": Lijst met niet-werkende zenders en foutmeldingen

Resultaten
De resultaten worden automatisch opgeslagen in een map met de naam [bestandsnaam]_scan_results, die het volgende bevat:

active_channels.m3u: Lijst met werkende zenders
inactive_channels.m3u: Lijst met niet-werkende zenders
scan_report.txt: Gedetailleerd rapport met foutmeldingen

Je kunt deze bestanden direct in je mediaspeler gebruiken.
