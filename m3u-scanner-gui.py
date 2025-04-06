#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import requests
import re
import os
import time
import threading
import concurrent.futures
from urllib.parse import urlparse

class M3UScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("M3U Scanner")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # Variabelen
        self.m3u_path = tk.StringVar()
        self.timeout = tk.IntVar(value=5)
        self.max_workers = tk.IntVar(value=10)
        self.is_scanning = False
        self.active_channels = []
        self.inactive_channels = []
        self.language = tk.StringVar(value="nl")  # Default language is Dutch

        # Translations
        self.translations = {
            "nl": {
                "title": "M3U Scanner",
                "file_frame": "M3U Bestand",
                "browse_file": "Selecteer Bestand",
                "options_frame": "Scanopties",
                "timeout": "Timeout (seconden):",
                "connections": "Gelijktijdige verbindingen:",
                "start_scan": "Start Scan",
                "stop_scan": "Stop Scan",
                "progress_label": "Gereed: 0/0 zenders",
                "log_tab": "Log",
                "active_tab": "Actieve Zenders (0)",
                "inactive_tab": "Inactieve Zenders (0)",
                "status_bar": "Gereed",
                "file_menu": "Bestand",
                "open_file": "Open M3U Bestand",
                "exit": "Afsluiten",
                "action_menu": "Acties",
                "save_results": "Resultaten Opslaan",
                "help_menu": "Help",
                "about": "Over",
                "language_menu": "Taal",
                "english": "Engels",
                "dutch": "Nederlands",
                "error_no_file": "Selecteer eerst een M3U-bestand",
                "log_selected_file": "Bestand geselecteerd: ",
                "log_start_scan": "Start scan van: ",
                "log_timeout": "Timeout: ",
                "log_max_connections": "Max verbindingen: ",
                "log_no_channels": "Geen zenders gevonden in de afspeellijst",
                "log_found_channels": "Gevonden: ",
                "log_scanning": "Scannen...",
                "log_scan_stopped": "Scan gestopt door gebruiker",
                "log_scan_completed": "SCAN VOLTOOID: ",
                "log_active_channels": "ACTIEVE ZENDERS: ",
                "log_inactive_channels": "INACTIEVE ZENDERS: ",
                "log_download_playlist": "Afspeellijst downloaden van URL: ",
                "log_load_playlist": "Afspeellijst laden van bestand: ",
                "log_invalid_format": "Waarschuwing: Bestand is mogelijk niet in geldig M3U-formaat",
                "log_error_downloading": "Fout bij downloaden afspeellijst: ",
                "log_error_reading": "Fout bij lezen afspeellijst: ",
                "log_error_scanning": "Fout tijdens scan: ",
                "log_results_saved": "Resultaten opgeslagen in:",
                "log_error_saving": "Fout bij opslaan resultaten: ",
                "about_text": "M3U Scanner v1.0\n\nEen tool om M3U-afspeellijsten te scannen en te controleren of de zenders actief zijn.\n\nGebruik:\n1. Selecteer een M3U-bestand\n2. Pas eventueel de scanopties aan\n3. Klik op 'Start Scan'\n4. Resultaten worden automatisch opgeslagen"
            },
            "en": {
                "title": "M3U Scanner",
                "file_frame": "M3U File",
                "browse_file": "Select File",
                "options_frame": "Scan Options",
                "timeout": "Timeout (seconds):",
                "connections": "Concurrent connections:",
                "start_scan": "Start Scan",
                "stop_scan": "Stop Scan",
                "progress_label": "Ready: 0/0 channels",
                "log_tab": "Log",
                "active_tab": "Active Channels (0)",
                "inactive_tab": "Inactive Channels (0)",
                "status_bar": "Ready",
                "file_menu": "File",
                "open_file": "Open M3U File",
                "exit": "Exit",
                "action_menu": "Actions",
                "save_results": "Save Results",
                "help_menu": "Help",
                "about": "About",
                "language_menu": "Language",
                "english": "English",
                "dutch": "Dutch",
                "error_no_file": "Please select an M3U file first",
                "log_selected_file": "File selected: ",
                "log_start_scan": "Starting scan of: ",
                "log_timeout": "Timeout: ",
                "log_max_connections": "Max connections: ",
                "log_no_channels": "No channels found in the playlist",
                "log_found_channels": "Found: ",
                "log_scanning": "Scanning...",
                "log_scan_stopped": "Scan stopped by user",
                "log_scan_completed": "SCAN COMPLETED: ",
                "log_active_channels": "ACTIVE CHANNELS: ",
                "log_inactive_channels": "INACTIVE CHANNELS: ",
                "log_download_playlist": "Downloading playlist from URL: ",
                "log_load_playlist": "Loading playlist from file: ",
                "log_invalid_format": "Warning: File may not be in valid M3U format",
                "log_error_downloading": "Error downloading playlist: ",
                "log_error_reading": "Error reading playlist: ",
                "log_error_scanning": "Error during scan: ",
                "log_results_saved": "Results saved in:",
                "log_error_saving": "Error saving results: ",
                "about_text": "M3U Scanner v1.0\n\nA tool to scan M3U playlists and check if the channels are active.\n\nUsage:\n1. Select an M3U file\n2. Adjust scan options if needed\n3. Click 'Start Scan'\n4. Results are saved automatically"
            }
        }

        # Main container
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Bestandsselectiegedeelte
        self.file_frame = ttk.LabelFrame(main_frame, text=self.translations[self.language.get()]["file_frame"], padding="10")
        self.file_frame.pack(fill=tk.X, pady=5)

        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.m3u_path, width=60)
        self.file_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.browse_button = ttk.Button(self.file_frame, text=self.translations[self.language.get()]["browse_file"], command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # Opties frame
        self.options_frame = ttk.LabelFrame(main_frame, text=self.translations[self.language.get()]["options_frame"], padding="10")
        self.options_frame.pack(fill=tk.X, pady=5)

        self.timeout_label = ttk.Label(self.options_frame, text=self.translations[self.language.get()]["timeout"])
        self.timeout_label.grid(row=0, column=0, padx=5, sticky=tk.W)

        self.timeout_spinbox = ttk.Spinbox(self.options_frame, from_=1, to=30, textvariable=self.timeout, width=5)
        self.timeout_spinbox.grid(row=0, column=1, padx=5, sticky=tk.W)

        self.connections_label = ttk.Label(self.options_frame, text=self.translations[self.language.get()]["connections"])
        self.connections_label.grid(row=0, column=2, padx=5, sticky=tk.W)

        self.connections_spinbox = ttk.Spinbox(self.options_frame, from_=1, to=50, textvariable=self.max_workers, width=5)
        self.connections_spinbox.grid(row=0, column=3, padx=5, sticky=tk.W)

        # Actieknoppen
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=5)

        self.scan_button = ttk.Button(action_frame, text=self.translations[self.language.get()]["start_scan"], command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(action_frame, text=self.translations[self.language.get()]["stop_scan"], command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Voortgangsbalk
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)

        self.progress_label = ttk.Label(progress_frame, text=self.translations[self.language.get()]["progress_label"])
        self.progress_label.pack(side=tk.TOP, anchor=tk.W, pady=2)

        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress_bar.pack(side=tk.TOP, fill=tk.X, pady=2)

        # Notebook met tabbladen voor de resultaten
        self.result_notebook = ttk.Notebook(main_frame)
        self.result_notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Log tabblad
        self.log_frame = ttk.Frame(self.result_notebook)
        self.result_notebook.add(self.log_frame, text=self.translations[self.language.get()]["log_tab"])

        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Actieve zenders tabblad
        self.active_frame = ttk.Frame(self.result_notebook)
        self.result_notebook.add(self.active_frame, text=self.translations[self.language.get()]["active_tab"])

        self.active_text = scrolledtext.ScrolledText(self.active_frame, wrap=tk.WORD)
        self.active_text.pack(fill=tk.BOTH, expand=True)

        # Inactieve zenders tabblad
        self.inactive_frame = ttk.Frame(self.result_notebook)
        self.result_notebook.add(self.inactive_frame, text=self.translations[self.language.get()]["inactive_tab"])

        self.inactive_text = scrolledtext.ScrolledText(self.inactive_frame, wrap=tk.WORD)
        self.inactive_text.pack(fill=tk.BOTH, expand=True)

        # Statusbalk
        self.status_bar = ttk.Label(root, text=self.translations[self.language.get()]["status_bar"], relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Voeg menu toe
        self.create_menu()

    def create_menu(self):
        """Maak menu aan"""
        menu_bar = tk.Menu(self.root)

        # Bestandsmenu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label=self.translations[self.language.get()]["open_file"], command=self.browse_file)
        file_menu.add_separator()
        file_menu.add_command(label=self.translations[self.language.get()]["exit"], command=self.root.quit)
        menu_bar.add_cascade(label=self.translations[self.language.get()]["file_menu"], menu=file_menu)

        # Actiemenu
        action_menu = tk.Menu(menu_bar, tearoff=0)
        action_menu.add_command(label=self.translations[self.language.get()]["start_scan"], command=self.start_scan)
        action_menu.add_command(label=self.translations[self.language.get()]["stop_scan"], command=self.stop_scan)
        action_menu.add_separator()
        action_menu.add_command(label=self.translations[self.language.get()]["save_results"], command=self.save_results)
        menu_bar.add_cascade(label=self.translations[self.language.get()]["action_menu"], menu=action_menu)

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label=self.translations[self.language.get()]["about"], command=self.show_about)
        menu_bar.add_cascade(label=self.translations[self.language.get()]["help_menu"], menu=help_menu)

        # Language menu
        language_menu = tk.Menu(menu_bar, tearoff=0)
        language_menu.add_radiobutton(label=self.translations[self.language.get()]["english"], variable=self.language, value="en", command=self.change_language)
        language_menu.add_radiobutton(label=self.translations[self.language.get()]["dutch"], variable=self.language, value="nl", command=self.change_language)
        menu_bar.add_cascade(label=self.translations[self.language.get()]["language_menu"], menu=language_menu)

        self.root.config(menu=menu_bar)

    def change_language(self):
        """Verander de taal van de UI"""
        self.root.title(self.translations[self.language.get()]["title"])
        self.file_frame.config(text=self.translations[self.language.get()]["file_frame"])
        self.browse_button.config(text=self.translations[self.language.get()]["browse_file"])
        self.options_frame.config(text=self.translations[self.language.get()]["options_frame"])
        self.timeout_label.config(text=self.translations[self.language.get()]["timeout"])
        self.connections_label.config(text=self.translations[self.language.get()]["connections"])
        self.scan_button.config(text=self.translations[self.language.get()]["start_scan"])
        self.stop_button.config(text=self.translations[self.language.get()]["stop_scan"])
        self.progress_label.config(text=self.translations[self.language.get()]["progress_label"])
        self.result_notebook.tab(0, text=self.translations[self.language.get()]["log_tab"])
        self.result_notebook.tab(1, text=self.translations[self.language.get()]["active_tab"])
        self.result_notebook.tab(2, text=self.translations[self.language.get()]["inactive_tab"])
        self.status_bar.config(text=self.translations[self.language.get()]["status_bar"])
        self.create_menu()

    def browse_file(self):
        """Open bestandskiezer om M3U-bestand te selecteren"""
        filepath = filedialog.askopenfilename(
            title=self.translations[self.language.get()]["open_file"],
            filetypes=[("M3U bestanden", "*.m3u"), ("Alle bestanden", "*.*")]
        )
        if filepath:
            self.m3u_path.set(filepath)
            self.log(self.translations[self.language.get()]["log_selected_file"] + filepath)

    def start_scan(self):
        """Start de scan in een aparte thread"""
        if not self.m3u_path.get():
            messagebox.showerror("Fout", self.translations[self.language.get()]["error_no_file"])
            return

        if self.is_scanning:
            return

        self.is_scanning = True
        self.active_channels = []
        self.inactive_channels = []

        # UI voorbereiden
        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar["value"] = 0
        self.progress_label.config(text=self.translations[self.language.get()]["progress_label"])
        self.clear_results()

        # Start de scan in een aparte thread
        self.scan_thread = threading.Thread(target=self.perform_scan)
        self.scan_thread.daemon = True
        self.scan_thread.start()

    def stop_scan(self):
        """Stop de scan"""
        if self.is_scanning:
            self.is_scanning = False
            self.log(self.translations[self.language.get()]["log_scan_stopped"])
            self.status_bar.config(text=self.translations[self.language.get()]["status_bar"])

    def perform_scan(self):
        """Voer de M3U-scan uit"""
        try:
            m3u_path = self.m3u_path.get()
            timeout = self.timeout.get()
            max_workers = self.max_workers.get()

            self.status_bar.config(text=self.translations[self.language.get()]["log_load_playlist"])
            self.log(self.translations[self.language.get()]["log_start_scan"] + m3u_path)
            self.log(self.translations[self.language.get()]["log_timeout"] + str(timeout) + " seconden, " + self.translations[self.language.get()]["log_max_connections"] + str(max_workers))

            # Laad afspeellijst
            channels = self.load_playlist(m3u_path)
            total_channels = len(channels)

            if total_channels == 0:
                self.log(self.translations[self.language.get()]["log_no_channels"])
                self.scan_completed()
                return

            self.log(self.translations[self.language.get()]["log_found_channels"] + str(total_channels) + " zenders. " + self.translations[self.language.get()]["log_scanning"])

            # Update voortgangsbalk instellen
            self.root.after(0, lambda: self.progress_label.config(text=f"Gereed: 0/{total_channels} zenders"))

            # Scan de zenders
            completed = 0
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
            future_to_channel = {executor.submit(self.check_channel, channel, timeout): channel for channel in channels}

            # Verzamel de resultaten
            for future in concurrent.futures.as_completed(future_to_channel):
                if not self.is_scanning:
                    executor.shutdown(wait=False)
                    self.log(self.translations[self.language.get()]["log_scan_stopped"])
                    self.scan_completed()
                    return

                channel, is_active, error_message = future.result()
                completed += 1

                if is_active:
                    self.active_channels.append(channel)
                    self.root.after(0, lambda ch=channel: self.add_to_active(ch))
                else:
                    self.inactive_channels.append(channel)
                    self.root.after(0, lambda ch=channel, err=error_message: self.add_to_inactive(ch, err))

                # Update voortgang
                progress = int((completed / total_channels) * 100)
                self.root.after(0, lambda p=progress, c=completed, t=total_channels: self.update_progress(p, c, t))

            # Scan voltooid
            self.log("\n" + "="*60)
            self.log(self.translations[self.language.get()]["log_scan_completed"] + str(len(self.active_channels) + len(self.inactive_channels)) + " zenders gecontroleerd")
            self.log(self.translations[self.language.get()]["log_active_channels"] + str(len(self.active_channels)))
            self.log(self.translations[self.language.get()]["log_inactive_channels"] + str(len(self.inactive_channels)))
            self.log("="*60)

            # Update tabbladen
            self.root.after(0, lambda a=len(self.active_channels), i=len(self.inactive_channels):
                self.update_tab_titles(a, i))

            # Automatisch opslaan van resultaten
            if self.active_channels or self.inactive_channels:
                self.save_results()

        except Exception as e:
            self.log(self.translations[self.language.get()]["log_error_scanning"] + str(e))
        finally:
            self.scan_completed()

    def scan_completed(self):
        """Herstel de UI naar de initiële status na scan"""
        self.is_scanning = False
        self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.status_bar.config(text=self.translations[self.language.get()]["status_bar"]))

    def update_progress(self, progress, completed, total):
        """Update voortgangsbalk en label"""
        self.progress_bar["value"] = progress
        self.progress_label.config(text=f"Gereed: {completed}/{total} zenders")
        self.status_bar.config(text=f"Scannen: {progress}% voltooid")

    def update_tab_titles(self, active_count, inactive_count):
        """Update titels van de tabbladen met aantallen"""
        self.result_notebook.tab(1, text=f"Actieve Zenders ({active_count})")
        self.result_notebook.tab(2, text=f"Inactieve Zenders ({inactive_count})")

    def load_playlist(self, m3u_path):
        """Laad en parse de M3U-afspeellijst van bestand of URL"""
        try:
            # Check if it's a URL or local file
            if m3u_path.startswith(('http://', 'https://')):
                self.log(self.translations[self.language.get()]["log_download_playlist"] + m3u_path)
                response = requests.get(m3u_path, timeout=self.timeout.get())
                response.raise_for_status()
                content = response.text
            else:
                self.log(self.translations[self.language.get()]["log_load_playlist"] + m3u_path)
                with open(m3u_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()

            return self.parse_m3u(content)

        except requests.exceptions.RequestException as e:
            self.log(self.translations[self.language.get()]["log_error_downloading"] + str(e))
            return []
        except IOError as e:
            self.log(self.translations[self.language.get()]["log_error_reading"] + str(e))
            return []

    def parse_m3u(self, content):
        """Parse M3U-inhoud en extraheer zenderinformatie"""
        channels = []
        lines = content.splitlines()

        if not lines or not lines[0].startswith('#EXTM3U'):
            self.log(self.translations[self.language.get()]["log_invalid_format"])

        channel = None

        for line in lines:
            line = line.strip()

            if not line:
                continue

            if line.startswith('#EXTINF:'):
                # Extract channel name
                name_match = re.search('tvg-name="([^"]*)"', line)

                if name_match:
                    channel_name = name_match.group(1)
                else:
                    # Try to extract from the end of the line
                    parts = line.split(',', 1)
                    channel_name = parts[1] if len(parts) > 1 else "Onbekend"

                # Clean up the name by removing quotes if present
                channel_name = channel_name.strip('"\'')

                channel = {"name": channel_name, "extinf": line}

            elif not line.startswith('#') and channel:
                # This is a URL
                channel["url"] = line
                channels.append(channel)
                channel = None

        return channels

    def check_channel(self, channel, timeout):
        """Controleer of een zender actief is door te proberen verbinding te maken"""
        url = channel["url"]
        name = channel["name"]

        try:
            # Voor HTTP/HTTPS URL's
            if url.startswith(('http://', 'https://')):
                # Probeer HEAD-request, als dat niet werkt, probeer een snelle GET-request
                try:
                    response = requests.head(url, timeout=timeout, allow_redirects=True)
                    is_active = 200 <= response.status_code < 400
                except requests.exceptions.RequestException:
                    # Probeer met een GET-request maar beperk de gedownloade bytes
                    response = requests.get(url, timeout=timeout, stream=True, allow_redirects=True)
                    is_active = 200 <= response.status_code < 400
                    response.close()  # Sluit de verbinding

            # Voor andere protocollen zoals RTMP, kunnen we alleen controleren of de URL-indeling geldig lijkt
            else:
                parsed = urlparse(url)
                is_active = bool(parsed.scheme and parsed.netloc)

            if is_active:
                return (channel, True, "")
            else:
                return (channel, False, f"Status code: {getattr(response, 'status_code', 'N/A')}")

        except requests.exceptions.RequestException as e:
            error_message = str(e)
            # Verkort de foutmelding voor leesbaarheid
            if len(error_message) > 100:
                error_message = error_message[:100] + "..."
            return (channel, False, error_message)

    def add_to_active(self, channel):
        """Voeg zender toe aan lijst met actieve zenders"""
        self.active_text.insert(tk.END, f"{channel['name']}\n")
        self.active_text.insert(tk.END, f"URL: {channel['url']}\n\n")
        self.active_text.see(tk.END)

    def add_to_inactive(self, channel, error):
        """Voeg zender toe aan lijst met inactieve zenders"""
        self.inactive_text.insert(tk.END, f"{channel['name']}\n")
        self.inactive_text.insert(tk.END, f"URL: {channel['url']}\n")
        self.inactive_text.insert(tk.END, f"Fout: {error}\n\n")
        self.inactive_text.see(tk.END)

    def log(self, message):
        """Voeg bericht toe aan log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def clear_results(self):
        """Wis resultaten"""
        self.log_text.delete(1.0, tk.END)
        self.active_text.delete(1.0, tk.END)
        self.inactive_text.delete(1.0, tk.END)

    def save_results(self):
        """Sla de scanresultaten op naar bestanden"""
        try:
            # Maak uitvoermap op basis van de invoerbestandsnaam
            m3u_path = self.m3u_path.get()
            input_name = os.path.basename(m3u_path).replace('.m3u', '')
            if input_name == m3u_path:  # In geval van een URL
                input_name = "playlist"

            output_dir = f"{input_name}_scan_results"
            os.makedirs(output_dir, exist_ok=True)

            # Sla actieve zenders op
            active_path = os.path.join(output_dir, "active_channels.m3u")
            with open(active_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for channel in self.active_channels:
                    f.write(f"{channel['extinf']}\n")
                    f.write(f"{channel['url']}\n")

            # Sla inactieve zenders op
            inactive_path = os.path.join(output_dir, "inactive_channels.m3u")
            with open(inactive_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for channel in self.inactive_channels:
                    f.write(f"{channel['extinf']}\n")
                    f.write(f"{channel['url']}\n")

            # Sla gedetailleerd rapport op
            report_path = os.path.join(output_dir, "scan_report.txt")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"M3U Scan Rapport voor: {m3u_path}\n")
                f.write(f"Datum: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Totaal zenders: {len(self.active_channels) + len(self.inactive_channels)}\n")
                f.write(f"Actieve zenders: {len(self.active_channels)}\n")
                f.write(f"Inactieve zenders: {len(self.inactive_channels)}\n\n")

                f.write("="*60 + "\n")
                f.write("INACTIEVE ZENDERS MET FOUTEN:\n")
                f.write("="*60 + "\n")
                for i, channel in enumerate(self.inactive_channels, 1):
                    f.write(f"{i}. {channel['name']}\n")
                    f.write(f"   URL: {channel['url']}\n")
                    f.write(f"   Fout: {channel.get('error', 'Onbekende fout')}\n\n")

            self.log("\n" + self.translations[self.language.get()]["log_results_saved"])
            self.log(f"- {active_path}")
            self.log(f"- {inactive_path}")
            self.log(f"- {report_path}")

        except IOError as e:
            self.log(self.translations[self.language.get()]["log_error_saving"] + str(e))
            messagebox.showerror("Fout", self.translations[self.language.get()]["log_error_saving"] + str(e))

    def show_about(self):
        """Toon informatie over de toepassing"""
        messagebox.showinfo(
            self.translations[self.language.get()]["about"],
            self.translations[self.language.get()]["about_text"]
        )

def main():
    root = tk.Tk()
    app = M3UScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

