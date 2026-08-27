from __future__ import annotations

LANGUAGES: dict[str, str] = {
    "en": "English",
    "pl": "Polski",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
}

_STRINGS: dict[str, dict[str, str]] = {

    "btn_add":      {"en": "Add",    "pl": "Dodaj",    "fr": "Ajouter", "de": 'Hinzufügen', "es": 'Añadir'},
    "btn_edit":     {"en": "Edit",   "pl": "Edytuj",   "fr": "Modifier", "de": 'Bearbeiten', "es": 'Editar'},
    "btn_toggle":   {"en": "On/Off", "pl": "Wł/Wył",   "fr": "Act/Dés", "de": 'An/Aus', "es": 'Act/Desact'},
    "btn_delete":   {"en": "Delete", "pl": "Usuń",     "fr": "Supprimer", "de": 'Löschen', "es": 'Eliminar'},
    "btn_save":     {"en": "Save",   "pl": "Zapisz",   "fr": "Enregistrer", "de": 'Speichern', "es": 'Guardar'},
    "btn_import":   {"en": "Import", "pl": "Importuj", "fr": "Importer", "de": 'Importieren', "es": 'Importar'},
    "btn_export":   {"en": "Export", "pl": "Eksportuj","fr": "Exporter", "de": 'Exportieren', "es": 'Exportar'},
    "btn_backups":  {"en": "Restore","pl": "Przywróć",    "fr": "Restaurer", "de": 'Wiederherstellen', "es": 'Restaurar'},

    "btn_repair":      {"en": "Repair",       "pl": "Napraw",          "fr": "Réparer", "de": 'Reparieren', "es": 'Reparar'},
    "btn_default":     {"en": "Default hosts",     "pl": "Domyślny hosts",       "fr": "Hosts par défaut", "de": 'Standard-Hosts', "es": 'Hosts predeterminado'},
    "btn_check_dom":   {"en": "Check domains",     "pl": "Sprawdź domeny",       "fr": "Vérifier domaines", "de": 'Domains prüfen', "es": 'Comprobar dominios'},
    "btn_malware":     {"en": "Scan malware",      "pl": "Szukaj malware",       "fr": "Scanner malware", "de": 'Malware scannen', "es": 'Escanear malware'},
    "btn_parental":    {"en": "Parental Protection  ",       "pl": "Ochrona rodzicielska",              "fr": "Protection parentale", "de": 'Kinderschutz  ', "es": 'Protección parental  '},
    "btn_privacy":     {"en": "Privacy  ",          "pl": "Prywatność",           "fr": "Confidentialité", "de": 'Datenschutz  ', "es": 'Privacidad  '},
    "btn_options":     {"en": "Options",           "pl": "Opcje",                "fr": "Options", "de": 'Optionen', "es": 'Opciones'},

    "opt_about":       {"en": "About",             "pl": "O programie",          "fr": "À propos", "de": 'Über', "es": 'Acerca de'},
    "opt_support":     {"en": "Support",           "pl": "Wsparcie",             "fr": "Soutenir", "de": 'Unterstützen', "es": 'Apoyar'},
    "opt_show_raw":    {"en": "Show Hosts",          "pl": "Pokaż Hosts",           "fr": "Afficher Hosts", "de": 'Hosts anzeigen', "es": 'Mostrar Hosts'},
    "opt_language":    {"en": "Language",          "pl": "Język",                "fr": "Langue", "de": 'Sprache', "es": 'Idioma'},
    "nav_menu_open":   {"en": "Open Navigation",  "pl": "Rozwiń pasek nawigacji", "fr": "Ouvrir la navigation", "de": 'Navigation öffnen', "es": 'Abrir navegación'},
    "nav_menu_close":  {"en": "Close Navigation", "pl": "Zwiń pasek nawigacji",   "fr": "Fermer la navigation", "de": 'Navigation schließen', "es": 'Cerrar navegación'},
    "opt_appearance":  {"en": "Appearance",       "pl": "Wygląd",               "fr": "Apparence", "de": 'Erscheinungsbild', "es": 'Apariencia'},

    "opt_pass_on":     {"en": "Password: ON",    "pl": "Hasło: WŁ",           "fr": "Passe: ACT", "de": 'Passwort: AN', "es": 'Contraseña: ACT'},
    "opt_pass_off":    {"en": "Password",   "pl": "Hasło",          "fr": "Mot de passe", "de": 'Passwort', "es": 'Contraseña'},

    "col_status":      {"en": "Status",      "pl": "Status",      "fr": "Statut", "de": 'Status', "es": 'Estado'},
    "col_ip":          {"en": "IP Address",  "pl": "Adres IP",    "fr": "Adresse IP", "de": 'IP-Adresse', "es": 'Dirección IP'},
    "col_hostname":    {"en": "Hostname",    "pl": "Nazwa hosta",    "fr": "Nom d'hôte", "de": 'Hostname', "es": 'Nombre de host'},
    "col_comment":     {"en": "Comment",     "pl": "Komentarz",   "fr": "Commentaire", "de": 'Kommentar', "es": 'Comentario'},
    "status_active":   {"en": "✔ active",   "pl": "✔ aktywny",  "fr": "✔ actif", "de": '✔ aktiv', "es": '✔ activo'},
    "status_disabled": {"en": "✘ disabled", "pl": "✘ wyłączony", "fr": "✘ désactivé", "de": '✘ deaktiviert', "es": '✘ desactivado'},

    "status_entries":   {"en": "Entries: {total}  |  Active: {active}  |  Disabled: {disabled}",
                         "pl": "Wpisów: {total}  |  Aktywnych: {active}  |  Wyłączonych: {disabled}",
                         "fr": "Entrées: {total}  |  Actives: {active}  |  Désactivées: {disabled}",
                         "de": 'Einträge: {total}  |  Aktiv: {active}  |  Deaktiviert: {disabled}',
                         "es": 'Entradas: {total}  |  Activas: {active}  |  Desactivadas: {disabled}',
                     },
    "status_backups":   {"en": "Backups: {n}", "pl": "Kopie: {n}", "fr": "Sauvegardes: {n}", "de": 'Sicherungen: {n}', "es": 'Copias de seguridad: {n}'},
    "status_filter":    {"en": "Filter: {shown} of {total} entries",
                         "pl": "Filtr: {shown} z {total} wpisów",
                         "fr": "Filtre: {shown} sur {total} entrées",
                         "de": 'Filter: {shown} von {total} Einträgen',
                         "es": 'Filtro: {shown} de {total} entradas',
                     },
    "status_saving":    {"en": "⏳ Windows DNS Client is verifying structure and updating cache... Please wait.",
                         "pl": "⏳ System Windows (Klient DNS) weryfikuje strukturę i aktualizuje pamięć podatną... Proszę czekać.",
                         "fr": "⏳ Le client DNS Windows vérifie la structure et met à jour le cache... Veuillez patienter.",
                         "de": '⏳ Der Windows-DNS-Client überprüft die Struktur und aktualisiert den Cache... Bitte warten.',
                         "es": '⏳ El cliente DNS de Windows está verificando la estructura y actualizando la caché... Por favor espera.',
                     },
    "hint_multiselect": {"en": "Shift+click / Ctrl+click — select multiple entries",
                         "pl": "Shift+klik / Ctrl+klik — zaznacz wiele wpisów",
                         "fr": "Maj+clic / Ctrl+clic — sélectionner plusieurs entrées",
                         "de": 'Umschalt+Klick / Strg+Klick — mehrere Einträge auswählen',
                         "es": 'Mayús+clic / Ctrl+clic — seleccionar varias entradas',
                     },
    "search_placeholder": {"en": "Search…", "pl": "Szukaj…", "fr": "Rechercher…", "de": 'Suchen…', "es": 'Buscar…'},

    "ctx_edit":     {"en": "Edit",         "pl": "Edytuj",        "fr": "Modifier", "de": 'Bearbeiten', "es": 'Editar'},
    "ctx_delete":   {"en": "Delete",       "pl": "Usuń",          "fr": "Supprimer", "de": 'Löschen', "es": 'Eliminar'},
    "ctx_toggle":   {"en": "Enable/Disable","pl": "Włącz/Wyłącz","fr": "Activer/Désactiver", "de": 'Aktivieren/Deaktivieren', "es": 'Activar/Desactivar'},
    "ctx_zero_ip":  {"en": "Change IP to 0.0.0.0","pl": "Zmień IP na 0.0.0.0","fr": "Changer IP en 0.0.0.0", "de": 'IP auf 0.0.0.0 ändern', "es": 'Cambiar IP a 0.0.0.0'},

    "dlg_unsaved_title":   {"en": "Unsaved changes",     "pl": "Niezapisane zmiany",     "fr": "Modifications non enregistrées", "de": 'Nicht gespeicherte Änderungen', "es": 'Cambios sin guardar'},
    "dlg_unsaved_msg":     {"en": "You have unsaved changes in the hosts file.\n\nExit without saving?",
                            "pl": "Masz niezapisane zmiany w pliku hosts.\n\nWyjść bez zapisywania?",
                            "fr": "Vous avez des modifications non enregistrées dans le fichier hosts.\n\nQuitter sans enregistrer?",
                            "de": 'Sie haben nicht gespeicherte Änderungen in der Hosts-Datei.\n\nOhne Speichern beenden?',
                            "es": 'Tienes cambios sin guardar en el archivo hosts.\n\n¿Salir sin guardar?',
                        },
    "dlg_no_selection":    {"en": "No selection",        "pl": "Brak zaznaczenia",       "fr": "Aucune sélection", "de": 'Keine Auswahl', "es": 'Sin selección'},
    "dlg_no_sel_msg":      {"en": "Select entries in the table to check.",
                            "pl": "Zaznacz wpisy w tabeli które chcesz sprawdzić.",
                            "fr": "Sélectionnez des entrées dans le tableau à vérifier.",
                            "de": 'Wählen Sie Einträge in der Tabelle zum Prüfen aus.',
                            "es": 'Selecciona entradas en la tabla para comprobar.',
                        },
    "dlg_about_title":     {"en": "About",               "pl": "O programie",            "fr": "À propos", "de": 'Über', "es": 'Acerca de'},

    "about_title":         {"en": "About",
                            "pl": "O programie",
                            "fr": "À propos",
                            "de": "Über",
                            "es": "Acerca de",
                        },
    "about_subtitle":      {"en": "HOTS — Handy OS Tools Suite",
                            "pl": "HOTS — Handy OS Tools Suite",
                            "fr": "HOTS — Handy OS Tools Suite",
                            "de": 'HOTS — Handy OS Tools Suite',
                            "es": 'HOTS — Handy OS Tools Suite',
                        },
    "about_version":       {"en": "version 2.1",
                            "pl": "wersja 2.1",
                            "fr": "version 2.1",
                            "de": 'Version 2.1',
                            "es": 'versión 2.1',
                        },
    "about_desc":          {"en": "HOTS Hosts is a modern hosts-file editor for Windows.\nManage entries safely, block trackers and unwanted content, lock the hosts file and block selected apps, enforce DNS-over-HTTPS blocking in browsers, and take fine-grained control over Windows telemetry — all from one dark or light interface.",
                            "pl": "HOTS Hosts to nowoczesny edytor pliku hosts dla Windows.\nBezpiecznie zarządzaj wpisami, blokuj trackery i niechciane treści, zablokuj plik hosts oraz wybrane aplikacje, wymuś blokadę DNS-over-HTTPS w przeglądarkach i miej pełną kontrolę nad telemetrią Windows — wszystko w jednym, ciemnym lub jasnym interfejsie.",
                            "fr": "HOTS Hosts est un éditeur de fichier hosts moderne pour Windows.\nGérez vos entrées en toute sécurité, bloquez les traqueurs et les contenus indésirables, verrouillez le fichier hosts et bloquez certaines applications, imposez le blocage du DNS-over-HTTPS dans les navigateurs, et gardez un contrôle fin sur la télémétrie Windows — le tout dans une interface sombre ou claire.",
                            "de": 'HOTS Hosts ist ein moderner Hosts-Datei-Editor für Windows.\nVerwalten Sie Einträge sicher, blockieren Sie Tracker und unerwünschte Inhalte, sperren Sie die Hosts-Datei und blockieren Sie ausgewählte Apps, erzwingen Sie die DNS-over-HTTPS-Blockierung in Browsern, und behalten Sie die volle Kontrolle über die Windows-Telemetrie — alles in einer dunklen oder hellen Oberfläche.',
                            "es": 'HOTS Hosts es un editor moderno del archivo hosts para Windows.\nGestiona entradas de forma segura, bloquea rastreadores y contenido no deseado, bloquea el archivo hosts y aplicaciones seleccionadas, fuerza el bloqueo de DNS-over-HTTPS en los navegadores, y controla con precisión la telemetría de Windows — todo desde una interfaz oscura o clara.',
                        },
    "about_feat_parental": {"en": "Parental control (15 categories)",
                            "pl": "Ochrona rodzicielska (15 kategorii)",
                            "fr": "Contrôle parental (15 catégories)",
                            "de": 'Kindersicherung (15 Kategorien)',
                            "es": 'Control parental (15 categorías)',
                        },
    "about_feat_diag":     {"en": "Fast, parallel DNS diagnostics",
                            "pl": "Szybka, równoległa diagnostyka DNS",
                            "fr": "Diagnostics DNS rapides et parallèles",
                            "de": 'Schnelle, parallele DNS-Diagnose',
                            "es": 'Diagnóstico DNS rápido y paralelo',
                        },
    "about_feat_backup":   {"en": "Backups with rotation",
                            "pl": "Kopie zapasowe z rotacją",
                            "fr": "Sauvegardes avec rotation",
                            "de": 'Sicherungen mit Rotation',
                            "es": 'Copias de seguridad con rotación',
                        },
    "about_feat_raw":      {"en": "Raw view & edit",
                            "pl": "Podgląd i edycja raw",
                            "fr": "Vue et édition brute",
                            "de": 'Rohansicht & Bearbeitung',
                            "es": 'Vista y edición en bruto',
                        },
    "about_feat_password": {"en": "Password lock",
                            "pl": "Blokada hasłem",
                            "fr": "Verrouillage par mot de passe",
                            "de": 'Passwortsperre',
                            "es": 'Bloqueo por contraseña',
                        },
    "about_feat_lang":     {"en": "Multilingual interface (PL/EN/FR/DE/ES)",
                            "pl": "Wielojęzyczny interfejs (PL/EN/FR/DE/ES)",
                            "fr": "Interface multilingue (PL/EN/FR/DE/ES)",
                            "de": 'Mehrsprachige Oberfläche (PL/EN/FR/DE/ES)',
                            "es": 'Interfaz multilingüe (PL/EN/FR/DE/ES)',
                        },
    "about_feat_antispy":  {"en": "Privacy protection (5 levels)",
                            "pl": "Ochrona prywatności (5 poziomów)",
                            "fr": "Protection de la confidentialité (5 niveaux)",
                            "de": 'Datenschutz (5 Stufen)',
                            "es": 'Protección de privacidad (5 niveles)',
                        },
    "about_feat_export":   {"en": "Import & export entries",
                            "pl": "Import i eksport wpisów",
                            "fr": "Import et export des entrées",
                            "de": 'Einträge importieren & exportieren',
                            "es": 'Importar y exportar entradas',
                        },
    "about_feat_theme":    {"en": "Dark/Light themes & accent colors",
                            "pl": "Motywy Dark/Light i kolory akcentu",
                            "fr": "Thèmes clair/sombre et couleurs d'accent",
                            "de": 'Dunkle/Helle Designs & Akzentfarben',
                            "es": 'Temas claro/oscuro y colores de acento',
                        },
    "about_feat_dns":      {"en": "Cloudflare Family DNS integration",
                            "pl": "Integracja z Cloudflare Family DNS",
                            "fr": "Intégration Cloudflare Family DNS",
                            "de": 'Cloudflare Family DNS-Integration',
                            "es": 'Integración con Cloudflare Family DNS',
                        },
    "about_feat_hostslock": {"en": "Hosts file lock",
                            "pl": "Blokada pliku hosts",
                            "fr": "Verrouillage du fichier hosts",
                            "de": 'Hosts-Datei sperren',
                            "es": 'Bloqueo del archivo hosts',
                        },
    "about_feat_appblock": {"en": "Application blocking",
                            "pl": "Blokowanie aplikacji",
                            "fr": "Blocage d'applications",
                            "de": 'App-Sperre',
                            "es": 'Bloqueo de aplicaciones',
                        },
    "about_feat_doh":      {"en": "DNS-over-HTTPS blocking in browsers",
                            "pl": "Blokada DNS-over-HTTPS w przeglądarkach",
                            "fr": "Blocage du DNS-over-HTTPS dans les navigateurs",
                            "de": 'DNS-over-HTTPS-Blockierung in Browsern',
                            "es": 'Bloqueo de DNS-over-HTTPS en navegadores',
                        },
    "about_feat_vpn":      {"en": "Popular VPN client blocking",
                            "pl": "Blokowanie popularnych klientów VPN",
                            "fr": "Blocage des clients VPN populaires",
                            "de": 'Blockierung gängiger VPN-Clients',
                            "es": 'Bloqueo de clientes VPN populares',
                        },
    "about_feat_customdomains": {"en": "Block your own domains",
                            "pl": "Blokada własnych domen",
                            "fr": "Bloquer vos propres domaines",
                            "de": 'Eigene Domains blockieren',
                            "es": 'Bloquear tus propios dominios',
                        },
    "about_feat_rstruilock": {"en": "System Restore tool lock",
                            "pl": "Blokada narzędzia Przywracanie systemu",
                            "fr": "Verrouillage de l'outil de restauration du système",
                            "de": 'Sperre des Systemwiederherstellungs-Tools',
                            "es": 'Bloqueo de la herramienta de restauración del sistema',
                        },
    "about_footer":        {"en": "© 2026 Darsono  •  All rights reserved",
                            "pl": "© 2026 Darsono  •  Wszelkie prawa zastrzeżone",
                            "fr": "© 2026 Darsono  •  Tous droits réservés",
                            "de": '© 2026 Darsono  •  Alle Rechte vorbehalten',
                            "es": '© 2026 Darsono  •  Todos los derechos reservados',
                        },
    "about_close":         {"en": "Close",
                            "pl": "Zamknij",
                            "fr": "Fermer",
                            "de": 'Schließen',
                            "es": 'Cerrar',
                        },
    "about_website_btn":   {"en": "hotstools.com",
                            "pl": "hotstools.com",
                            "fr": "hotstools.com",
                            "de": 'hotstools.com',
                            "es": 'hotstools.com',
                        },
    "about_check_update":  {"en": "Check for updates",
                            "pl": "Sprawdź aktualizacje",
                            "fr": "Vérifier les mises à jour",
                            "de": 'Nach Updates suchen',
                            "es": 'Buscar actualizaciones',
                        },
    "about_checking_update": {"en": "Checking…",
                            "pl": "Sprawdzanie…",
                            "fr": "Vérification…",
                            "de": 'Wird geprüft…',
                            "es": 'Comprobando…',
                        },
    "about_update_available_title": {"en": "Update available",
                            "pl": "Dostępna aktualizacja",
                            "fr": "Mise à jour disponible",
                            "de": 'Update verfügbar',
                            "es": 'Actualización disponible',
                        },
    "about_update_available_msg": {"en": "A newer version is available: {version}\n(you have {current}).\n\nOpen the GitHub page to download it?",
                            "pl": "Dostępna jest nowsza wersja: {version}\n(Twoja: {current}).\n\nOtworzyć stronę GitHub, aby ją pobrać?",
                            "fr": "Une nouvelle version est disponible : {version}\n(vous avez {current}).\n\nOuvrir la page GitHub pour la télécharger ?",
                            "de": 'Eine neuere Version ist verfügbar: {version}\n(Sie haben {current}).\n\nGitHub-Seite zum Herunterladen öffnen?',
                            "es": 'Hay una versión más reciente disponible: {version}\n(tienes {current}).\n\n¿Abrir la página de GitHub para descargarla?',
                        },
    "about_update_uptodate_title": {"en": "No updates",
                            "pl": "Brak aktualizacji",
                            "fr": "Aucune mise à jour",
                            "de": 'Keine Updates',
                            "es": 'Sin actualizaciones',
                        },
    "about_update_uptodate_msg": {"en": "You already have the latest version ({current}).",
                            "pl": "Masz już najnowszą wersję ({current}).",
                            "fr": "Vous avez déjà la dernière version ({current}).",
                            "de": 'Sie haben bereits die neueste Version ({current}).',
                            "es": 'Ya tienes la última versión ({current}).',
                        },
    "about_update_error_title": {"en": "Update check failed",
                            "pl": "Błąd sprawdzania aktualizacji",
                            "fr": "Échec de la vérification",
                            "de": 'Update-Prüfung fehlgeschlagen',
                            "es": 'Error al comprobar actualizaciones',
                        },
    "about_update_error_msg": {"en": "Could not check for updates.\n\n{error}",
                            "pl": "Nie udało się sprawdzić aktualizacji.\n\n{error}",
                            "fr": "Impossible de vérifier les mises à jour.\n\n{error}",
                            "de": 'Updates konnten nicht überprüft werden.\n\n{error}',
                            "es": 'No se pudieron comprobar las actualizaciones.\n\n{error}',
                        },
    "about_update_err_no_internet": {
                            "en": "No internet connection or a DNS problem. Check your network connection and try again.",
                            "pl": "Brak połączenia z internetem lub problem z DNS. Sprawdź połączenie sieciowe i spróbuj ponownie.",
                            "fr": "Pas de connexion internet ou problème DNS. Vérifiez votre connexion réseau et réessayez.",
                            "de": "Keine Internetverbindung oder ein DNS-Problem. Überprüfen Sie Ihre Netzwerkverbindung und versuchen Sie es erneut.",
                            "es": "Sin conexión a internet o un problema de DNS. Comprueba tu conexión de red e inténtalo de nuevo.",
                        },
    "about_update_err_firewall": {
                            "en": "The connection was blocked by a firewall or antivirus. Allow HOTS Hosts to access the internet and try again.",
                            "pl": "Połączenie zostało zablokowane przez zaporę sieciową (firewall) lub antywirusa. Zezwól programowi HOTS Hosts na dostęp do internetu i spróbuj ponownie.",
                            "fr": "La connexion a été bloquée par un pare-feu ou un antivirus. Autorisez HOTS Hosts à accéder à internet et réessayez.",
                            "de": "Die Verbindung wurde von einer Firewall oder einem Antivirenprogramm blockiert. Erlauben Sie HOTS Hosts den Internetzugriff und versuchen Sie es erneut.",
                            "es": "La conexión fue bloqueada por un firewall o antivirus. Permite que HOTS Hosts acceda a internet e inténtalo de nuevo.",
                        },
    "about_update_err_rate_limit": {
                            "en": "GitHub has temporarily limited the number of requests (API rate limit). Please try again in a few minutes.",
                            "pl": "GitHub tymczasowo ograniczył liczbę zapytań (limit API). Spróbuj ponownie za kilka minut.",
                            "fr": "GitHub a temporairement limité le nombre de requêtes (limite d'API). Réessayez dans quelques minutes.",
                            "de": "GitHub hat die Anzahl der Anfragen vorübergehend begrenzt (API-Limit). Bitte versuchen Sie es in einigen Minuten erneut.",
                            "es": "GitHub ha limitado temporalmente el número de solicitudes (límite de la API). Inténtalo de nuevo en unos minutos.",
                        },
    "about_update_err_not_found": {
                            "en": "No release information for this application could be found on GitHub.",
                            "pl": "Nie znaleziono informacji o wydaniach programu na GitHubie.",
                            "fr": "Aucune information de version n'a été trouvée sur GitHub.",
                            "de": "Auf GitHub konnten keine Versionsinformationen für dieses Programm gefunden werden.",
                            "es": "No se encontró información de versiones del programa en GitHub.",
                        },
    "about_update_err_timeout": {
                            "en": "The server took too long to respond. Check your internet connection and try again.",
                            "pl": "Przekroczono czas oczekiwania na odpowiedź serwera. Sprawdź połączenie z internetem i spróbuj ponownie.",
                            "fr": "Le serveur a mis trop de temps à répondre. Vérifiez votre connexion internet et réessayez.",
                            "de": "Der Server hat zu lange für eine Antwort gebraucht. Überprüfen Sie Ihre Internetverbindung und versuchen Sie es erneut.",
                            "es": "El servidor tardó demasiado en responder. Comprueba tu conexión a internet e inténtalo de nuevo.",
                        },
    "about_update_err_ssl": {
                            "en": "Could not establish a secure connection (SSL certificate error). Check your system date and time and try again.",
                            "pl": "Nie udało się nawiązać bezpiecznego połączenia (błąd certyfikatu SSL). Sprawdź datę i godzinę systemową i spróbuj ponownie.",
                            "fr": "Impossible d'établir une connexion sécurisée (erreur de certificat SSL). Vérifiez la date et l'heure de votre système et réessayez.",
                            "de": "Es konnte keine sichere Verbindung hergestellt werden (SSL-Zertifikatfehler). Überprüfen Sie Datum und Uhrzeit Ihres Systems und versuchen Sie es erneut.",
                            "es": "No se pudo establecer una conexión segura (error de certificado SSL). Comprueba la fecha y hora del sistema e inténtalo de nuevo.",
                        },
    "about_update_err_empty": {
                            "en": "The server returned an empty response. Please try again later.",
                            "pl": "Serwer zwrócił pustą odpowiedź. Spróbuj ponownie później.",
                            "fr": "Le serveur a renvoyé une réponse vide. Réessayez plus tard.",
                            "de": "Der Server hat eine leere Antwort zurückgegeben. Bitte versuchen Sie es später erneut.",
                            "es": "El servidor devolvió una respuesta vacía. Inténtalo de nuevo más tarde.",
                        },
    "about_update_err_generic": {
                            "en": "An unexpected error occurred: {detail}",
                            "pl": "Wystąpił nieoczekiwany błąd: {detail}",
                            "fr": "Une erreur inattendue s'est produite : {detail}",
                            "de": "Ein unerwarteter Fehler ist aufgetreten: {detail}",
                            "es": "Se produjo un error inesperado: {detail}",
                        },

    "save_success_title":  {"en": "Success",             "pl": "Sukces",                 "fr": "Succès", "de": 'Erfolg', "es": 'Éxito'},
    "save_success_msg":    {"en": "Hosts file saved successfully!\nBackup created automatically.",
                            "pl": "Plik hosts został pomyślnie zapisany!\nKopia zapasowa utworzona automatycznie.",
                            "fr": "Fichier hosts enregistré avec succès!\nSauvegarde créée automatiquement.",
                            "de": 'Hosts-Datei erfolgreich gespeichert!\nSicherung automatisch erstellt.',
                            "es": '¡Archivo hosts guardado correctamente!\nCopia de seguridad creada automáticamente.',
                        },
    "save_dns_ok":         {"en": "The Windows 'DNS Client' service successfully processed the structure and released the file handle.",
                            "pl": "Systemowa usługa 'Klient DNS' pomyślnie przetworzyła strukturę i zwolniła uchwyt pliku.",
                            "fr": "Le service Windows 'Client DNS' a traité la structure avec succès et libéré le descripteur de fichier.",
                            "de": 'Der Windows-Dienst „DNS-Client" hat die Struktur erfolgreich verarbeitet und das Datei-Handle freigegeben.',
                            "es": "El servicio 'Cliente DNS' de Windows procesó correctamente la estructura y liberó el identificador del archivo.",
                        },
    "save_dns_slow":       {"en": "Note: File saved, but the DNS service needs more time to fully process changes in the background.",
                            "pl": "Uwaga: Plik zapisany, ale usługa DNS potrzebuje więcej czasu na pełne przetworzenie zmian w tle.",
                            "fr": "Remarque: Fichier enregistré, mais le service DNS a besoin de plus de temps pour traiter les modifications en arrière-plan.",
                            "de": 'Hinweis: Datei gespeichert, aber der DNS-Dienst benötigt mehr Zeit, um die Änderungen im Hintergrund vollständig zu verarbeiten.',
                            "es": 'Nota: Archivo guardado, pero el servicio DNS necesita más tiempo para procesar completamente los cambios en segundo plano.',
                        },
    "save_err_title":      {"en": "Write error",         "pl": "Błąd zapisu",            "fr": "Erreur d'écriture", "de": 'Schreibfehler', "es": 'Error de escritura'},
    "save_perm_title":     {"en": "Access denied (DNS system lock)", "pl": "Odmowa dostępu (Lock systemowy DNS)", "fr": "Accès refusé (verrouillage DNS système)", "de": 'Zugriff verweigert (DNS-Systemsperre)', "es": 'Acceso denegado (bloqueo del sistema DNS)'},
    "save_perm_msg":       {
        "en": (
            "ERROR: File locked by Windows network service!\n\n"
            "The Windows 'DNS Client' (dnscache) service or your antivirus has imposed an Exclusive Lock on the hosts file.\n\n"
            "This happens when the system is still analyzing previous records in the background or the network loop has stalled.\n\n"
            "How to fix:\n"
            "1. Wait a moment for the DNS service to finish analysis and release the file.\n"
            "2. If the lock persists, restart your computer to reset the DNS service RAM."
        ),
        "pl": (
            "BŁĄD: Plik zablokowany przez usługę sieciową Windows!\n\n"
            "Systemowa usługa 'Klient DNS' (dnscache) lub Twój antywirus nałożyły wymuszony lock (Exclusive Lock) na plik hosts.\n\n"
            "Dzieje się tak, gdy system w tle wciąż analizuje poprzednie rekordy lub pętla sieciowa uległa zawieszeniu.\n\n"
            "Jak to rozwiązać?\n"
            "1. Odczekaj chwilę, aż usługa DNS zakończy analizę struktury i sama zwolni plik.\n"
            "2. Jeśli zablokowanie trwa stale, zrestartuj komputer w celu zresetowania pamięci RAM usługi DNS."
        ),
        "fr": (
            "ERREUR: Fichier verrouillé par le service réseau Windows!\n\n"
            "Le service Windows 'Client DNS' (dnscache) ou votre antivirus a imposé un verrou exclusif sur le fichier hosts.\n\n"
            "Cela se produit lorsque le système analyse encore des enregistrements précédents en arrière-plan ou que la boucle réseau est bloquée.\n\n"
            "Comment résoudre:\n"
            "1. Attendez que le service DNS termine l'analyse et libère le fichier.\n"
            "2. Si le verrou persiste, redémarrez l'ordinateur pour réinitialiser la RAM du service DNS."
        ),
    
        "de": 'FEHLER: Datei durch Windows-Netzwerkdienst gesperrt!\n\nDer Windows-Dienst „DNS-Client" (dnscache) oder Ihr Antivirenprogramm hat eine exklusive Sperre für die Hosts-Datei gesetzt.\n\nDies passiert, wenn das System im Hintergrund noch vorherige Einträge analysiert oder die Netzwerkschleife hängt.\n\nSo beheben Sie das Problem:\n1. Warten Sie einen Moment, bis der DNS-Dienst die Analyse beendet und die Datei freigibt.\n2. Wenn die Sperre bestehen bleibt, starten Sie den Computer neu, um den RAM des DNS-Dienstes zurückzusetzen.',
        "es": "ERROR: ¡Archivo bloqueado por el servicio de red de Windows!\n\nEl servicio 'Cliente DNS' (dnscache) de Windows o tu antivirus ha impuesto un bloqueo exclusivo sobre el archivo hosts.\n\nEsto ocurre cuando el sistema todavía está analizando registros anteriores en segundo plano o el bucle de red se ha detenido.\n\nCómo solucionarlo:\n1. Espera un momento a que el servicio DNS termine el análisis y libere el archivo.\n2. Si el bloqueo persiste, reinicia el equipo para reiniciar la memoria RAM del servicio DNS.",
    },

    "save_limit_title": {"en": "Save paused — performance limit",
                         "pl": "Zapis wstrzymany — limit wydajności",
                         "fr": "Enregistrement suspendu — limite de performance",
                         "de": 'Speichern pausiert — Leistungslimit',
                         "es": 'Guardado pausado — límite de rendimiento',
                     },
    "save_limit_msg":   {
        "en": (
            "Active entries detected: {n} — above the recommended limit of {max}.\n\n"
            "Very large hosts files can put a noticeable load on Windows' 'DNS Client' "
            "service, leading to system slowdowns and, in extreme cases, connectivity "
            "issues. To avoid that, HOTS Hosts has paused this save.\n\n"
            "What you can do:\n"
            "• Disable or delete some entries to get back under {max}\n"
            "• Or move filtering to a local DNS server (e.g. AdGuard Home or Acrylic "
            "DNS), which is built to handle much larger lists."
        ),
        "pl": (
            "Aktywne wpisy: {n} — powyżej zalecanego limitu {max}.\n\n"
            "Bardzo duże pliki hosts mogą znacząco obciążać usługę 'Klient DNS' w "
            "Windows, co prowadzi do zauważalnego spowolnienia systemu, a w skrajnych "
            "przypadkach do problemów z połączeniem internetowym. Żeby tego uniknąć, "
            "HOTS Hosts wstrzymał ten zapis.\n\n"
            "Co możesz zrobić:\n"
            "• Wyłącz lub usuń część wpisów, żeby zejść poniżej {max}\n"
            "• Albo przenieś filtrowanie na lokalny serwer DNS (np. AdGuard Home lub "
            "Acrylic DNS), który jest zaprojektowany do obsługi znacznie większych list."
        ),
        "fr": (
            "Entrées actives détectées : {n} — au-dessus de la limite recommandée de "
            "{max}.\n\n"
            "Des fichiers hosts très volumineux peuvent charger de manière notable le "
            "service Windows 'Client DNS', entraînant des ralentissements du système "
            "et, dans des cas extrêmes, des problèmes de connectivité. Pour éviter "
            "cela, HOTS Hosts a suspendu cet enregistrement.\n\n"
            "Ce que vous pouvez faire:\n"
            "• Désactivez ou supprimez certaines entrées pour repasser sous {max}\n"
            "• Ou déplacez le filtrage vers un serveur DNS local (ex. AdGuard Home ou "
            "Acrylic DNS), conçu pour gérer des listes bien plus grandes."
        ),
    
        "de": '{n} aktive Einträge erkannt — über dem empfohlenen Limit von {max}.\n\nSehr große Hosts-Dateien können den Windows-Dienst „DNS-Client" spürbar belasten, was zu Systemverlangsamungen und in Extremfällen zu Verbindungsproblemen führen kann. Um dies zu vermeiden, hat HOTS Hosts diesen Speichervorgang pausiert.\n\nWas Sie tun können:\n• Deaktivieren oder löschen Sie einige Einträge, um wieder unter {max} zu kommen\n• Oder verlagern Sie die Filterung auf einen lokalen DNS-Server (z. B. AdGuard Home oder Acrylic DNS), der für deutlich größere Listen ausgelegt ist.',
        "es": "Se detectaron {n} entradas activas — por encima del límite recomendado de {max}.\n\nLos archivos hosts muy grandes pueden sobrecargar de forma notable el servicio 'Cliente DNS' de Windows, provocando ralentizaciones del sistema y, en casos extremos, problemas de conectividad. Para evitarlo, HOTS Hosts ha pausado este guardado.\n\nQué puedes hacer:\n• Desactiva o elimina algunas entradas para volver a estar por debajo de {max}\n• O traslada el filtrado a un servidor DNS local (por ejemplo AdGuard Home o Acrylic DNS), diseñado para manejar listas mucho más grandes.",
    },

    "repair_no_changes_title": {"en": "No changes",    "pl": "Brak zmian",    "fr": "Aucun changement", "de": 'Keine Änderungen', "es": 'Sin cambios'},
    "repair_no_changes_msg":   {"en": "The hosts file required no syntax repairs.",
                                "pl": "Plik hosts nie wymagał żadnych napraw składniowych.",
                                "fr": "Le fichier hosts n'a nécessité aucune réparation syntaxique.",
                                "de": 'Die Hosts-Datei benötigte keine Syntaxreparaturen.',
                                "es": 'El archivo hosts no requirió ninguna reparación de sintaxis.',
                            },
    "repair_done_title":       {"en": "Repaired",      "pl": "Naprawiono",    "fr": "Réparé", "de": 'Repariert', "es": 'Reparado'},
    "repair_done_header":      {"en": "Hosts file cleaned. Save changes to apply.",
                                "pl": "Plik hosts został oczyszczony z błędów.\nZapisz zmiany, aby je utrwalić.",
                                "fr": "Fichier hosts nettoyé. Enregistrez les modifications pour les appliquer.",
                                "de": 'Hosts-Datei bereinigt. Speichern Sie die Änderungen, um sie anzuwenden.',
                                "es": 'Archivo hosts limpiado. Guarda los cambios para aplicarlos.',
                            },
    "repair_wildcards":        {"en": "• Wildcard entries fixed: {n}.",
                                "pl": "• Naprawionych wpisów z wildcard: {n}.",
                                "fr": "• Entrées avec wildcard corrigées : {n}.",
                                "de": '• Korrigierte Wildcard-Einträge: {n}.',
                                "es": '• Entradas con comodín corregidas: {n}.',
                            },
    "repair_dups":             {"en": "• Duplicate entries removed: {n}.",
                                "pl": "• Usuniętych duplikatów: {n}.",
                                "fr": "• Doublons supprimés : {n}.",
                                "de": '• Entfernte Duplikate: {n}.',
                                "es": '• Duplicados eliminados: {n}.',
                            },
    "repair_invalid":          {"en": "• Invalid entries removed: {n}.",
                                "pl": "• Usuniętych niepoprawnych wpisów: {n}.",
                                "fr": "• Entrées invalides supprimées : {n}.",
                                "de": '• Entfernte ungültige Einträge: {n}.',
                                "es": '• Entradas no válidas eliminadas: {n}.',
                            },
    "repair_normalized":       {"en": "• Hostnames normalized to lowercase: {n}.",
                                "pl": "• Znormalizowanych nazw hosta (małe litery): {n}.",
                                "fr": "• Noms d'hôte normalisés en minuscules : {n}.",
                                "de": '• Auf Kleinbuchstaben normalisierte Hostnamen: {n}.',
                                "es": '• Nombres de host normalizados a minúsculas: {n}.',
                            },

    "restore_ask_title": {"en": "Restore default hosts?",
                          "pl": "Przywrócić domyślny hosts?",
                          "fr": "Restaurer le hosts par défaut?",
                          "de": 'Standard-Hosts wiederherstellen?',
                          "es": '¿Restaurar hosts predeterminado?',
                      },
    "restore_ask_msg":   {"en": "The current hosts file will be replaced with Microsoft's default version.\nA backup will be created.",
                          "pl": "Obecny plik hosts zostanie zastąpiony domyślną wersją Microsoft.\nZostanie wykonana kopia zapasowa.",
                          "fr": "Le fichier hosts actuel sera remplacé par la version par défaut de Microsoft.\nUne sauvegarde sera créée.",
                          "de": 'Die aktuelle Hosts-Datei wird durch die Standardversion von Microsoft ersetzt.\nEs wird eine Sicherung erstellt.',
                          "es": 'El archivo hosts actual será reemplazado por la versión predeterminada de Microsoft.\nSe creará una copia de seguridad.',
                      },
    "restore_done_title":{"en": "Restored",   "pl": "Przywrócono",   "fr": "Restauré", "de": 'Wiederhergestellt', "es": 'Restaurado'},
    "restore_done_msg":  {"en": "Hosts file restored to Microsoft's default version.",
                          "pl": "Plik hosts został przywrócony do domyślnej wersji Microsoft.",
                          "fr": "Le fichier hosts a été restauré à la version par défaut de Microsoft.",
                          "de": 'Hosts-Datei auf die Standardversion von Microsoft zurückgesetzt.',
                          "es": 'Archivo hosts restaurado a la versión predeterminada de Microsoft.',
                      },

    "no_sel_title":      {"en": "No selection",    "pl": "Brak zaznaczenia",    "fr": "Aucune sélection", "de": 'Keine Auswahl', "es": 'Sin selección'},
    "no_sel_edit":       {"en": "Select an entry to edit.",
                          "pl": "Zaznacz wpis do edycji.",
                          "fr": "Sélectionnez une entrée à modifier.",
                          "de": 'Wählen Sie einen Eintrag zum Bearbeiten aus.',
                          "es": 'Selecciona una entrada para editar.',
                      },
    "no_sel_toggle":     {"en": "Select one or more entries.",
                          "pl": "Zaznacz wpis lub wpisy.",
                          "fr": "Sélectionnez une ou plusieurs entrées.",
                          "de": 'Wählen Sie einen oder mehrere Einträge aus.',
                          "es": 'Selecciona una o más entradas.',
                      },
    "no_sel_delete":     {"en": "Select one or more entries to delete.",
                          "pl": "Zaznacz wpis lub wpisy do usunięcia.",
                          "fr": "Sélectionnez une ou plusieurs entrées à supprimer.",
                          "de": 'Wählen Sie einen oder mehrere Einträge zum Löschen aus.',
                          "es": 'Selecciona una o más entradas para eliminar.',
                      },
    "no_sel_raw_delete": {"en": "Select text or a whole line in the editor to delete.",
                          "pl": "Zaznacz tekst lub całą linię w edytorze, którą chcesz usunąć.",
                          "fr": "Sélectionnez du texte ou une ligne entière dans l'éditeur à supprimer.",
                          "de": 'Wählen Sie Text oder eine ganze Zeile im Editor zum Löschen aus.',
                          "es": 'Selecciona texto o una línea completa en el editor para eliminar.',
                      },
    "no_sel_check":      {"en": "Select entries in the table to check.",
                          "pl": "Zaznacz wpisy w tabeli które chcesz sprawdzić.",
                          "fr": "Sélectionnez des entrées dans le tableau à vérifier.",
                          "de": 'Wählen Sie Einträge in der Tabelle zum Prüfen aus.',
                          "es": 'Selecciona entradas en la tabla para comprobar.',
                      },

    "del_confirm_title":   {"en": "Confirm",        "pl": "Potwierdzenie",      "fr": "Confirmation", "de": 'Bestätigen', "es": 'Confirmar'},
    "del_confirm_one":     {"en": "Delete entry:\n{ip}  {hostname}?",
                            "pl": "Usunąć wpis:\n{ip}  {hostname}?",
                            "fr": "Supprimer l'entrée:\n{ip}  {hostname}?",
                            "de": 'Eintrag löschen:\n{ip}  {hostname}?',
                            "es": '¿Eliminar entrada:\n{ip}  {hostname}?',
                        },
    "del_confirm_many":    {"en": "Delete {n} selected entries?\n\n{preview}{suffix}",
                            "pl": "Zaznaczone wpisy do usunięcia: {n}\n\n{preview}{suffix}\n\nUsunąć?",
                            "fr": "Supprimer {n} entrées sélectionnées?\n\n{preview}{suffix}",
                            "de": '{n} ausgewählte Einträge löschen?\n\n{preview}{suffix}',
                            "es": '¿Eliminar {n} entradas seleccionadas?\n\n{preview}{suffix}',
                        },
    "del_more":            {"en": "\n… and {n} more",
                            "pl": "\n… i {n} więcej",
                            "fr": "\n… et {n} de plus",
                            "de": '\n… und {n} weitere',
                            "es": '\n… y {n} más',
                        },

    "raw_view_title":      {"en": "Raw mode",   "pl": "Tryb surowy",   "fr": "Mode brut", "de": 'Rohmodus', "es": 'Modo bruto'},
    "raw_view_hint":       {"en": "You're editing the raw contents of the hosts file directly, like in Notepad. "
                                   "Remember to save your changes in the main HOTS window.",
                            "pl": "Edytujesz bezpośrednio surową zawartość pliku hosts, tak jak w Notatniku. "
                                   "Pamiętaj aby zapisać zmiany w głównym oknie HOTS.",
                            "fr": "Vous modifiez directement le contenu brut du fichier hosts, comme dans le Bloc-notes. "
                                   "N'oubliez pas d'enregistrer vos modifications dans la fenêtre principale HOTS.",
                            "de": 'Sie bearbeiten den rohen Inhalt der Hosts-Datei direkt, wie im Editor. Denken Sie daran, Ihre Änderungen im HOTS-Hauptfenster zu speichern.',
                            "es": 'Estás editando directamente el contenido en bruto del archivo hosts, como en el Bloc de notas. Recuerda guardar los cambios en la ventana principal de HOTS.',
                        },

    "parse_err_title":     {"en": "Parse error",    "pl": "Błąd parsowania",    "fr": "Erreur d'analyse", "de": 'Analysefehler', "es": 'Error de análisis'},
    "raw_commit_err_msg":  {"en": "Raw mode text could not be parsed, so those edits were discarded (last valid entries are kept): {error}",
                            "pl": "Nie udało się przetworzyć tekstu z trybu surowego, więc te zmiany zostały odrzucone (zachowano ostatnie poprawne wpisy): {error}",
                            "fr": "Le texte du mode brut n'a pas pu être analysé, ces modifications ont donc été annulées (les dernières entrées valides sont conservées) : {error}",
                            "de": 'Der Text im Rohmodus konnte nicht analysiert werden, daher wurden diese Änderungen verworfen (die letzten gültigen Einträge bleiben erhalten): {error}',
                            "es": 'No se pudo analizar el texto del modo bruto, por lo que esos cambios se descartaron (se conservan las últimas entradas válidas): {error}',
                        },


    "lang_title":        {"en": "Language",   "pl": "Język",         "fr": "Langue", "de": 'Sprache', "es": 'Idioma'},
    "lang_restart_msg":  {"en": "Language changed. Restart the application to apply.",
                          "pl": "Język zmieniony. Uruchom ponownie aplikację, aby zastosować.",
                          "fr": "Langue modifiée. Redémarrez l'application pour appliquer.",
                          "de": 'Sprache geändert. Starten Sie die Anwendung neu, um die Änderung zu übernehmen.',
                          "es": 'Idioma cambiado. Reinicia la aplicación para aplicarlo.',
                      },

    "app_title":         {"en": "Appearance",   "pl": "Wygląd",   "fr": "Apparence", "de": 'Erscheinungsbild', "es": 'Apariencia'},
    "app_theme_label":   {"en": "Theme",   "pl": "Motyw",   "fr": "Thème", "de": 'Design', "es": 'Tema'},
    "app_theme_dark":    {"en": "Dark",    "pl": "Ciemny",  "fr": "Sombre", "de": 'Dunkel', "es": 'Oscuro'},
    "app_theme_light":   {"en": "Light",   "pl": "Jasny",   "fr": "Clair", "de": 'Hell', "es": 'Claro'},
    "app_restart_msg":   {"en": "Appearance changed. Restart the application now to apply it?",
                          "pl": "Wygląd zmieniony. Uruchomić aplikację ponownie teraz, aby go zastosować?",
                          "fr": "Apparence modifiée. Redémarrer l'application maintenant pour l'appliquer ?",
                          "de": 'Erscheinungsbild geändert. Anwendung jetzt neu starten, um es anzuwenden?',
                          "es": 'Apariencia cambiada. ¿Reiniciar la aplicación ahora para aplicarla?',
                      },
    "btn_restart_now":   {"en": "Restart now",   "pl": "Uruchom ponownie",   "fr": "Redémarrer", "de": 'Jetzt neu starten', "es": 'Reiniciar ahora'},
    "btn_later":         {"en": "Later",         "pl": "Później",            "fr": "Plus tard", "de": 'Später', "es": 'Más tarde'},
    "app_restart_fail_msg": {"en": "Couldn't restart the application automatically. Please close and start it again manually.",
                             "pl": "Nie udało się automatycznie uruchomić aplikacji ponownie. Zamknij ją i uruchom ręcznie jeszcze raz.",
                             "fr": "Impossible de redémarrer automatiquement l'application. Fermez-la et relancez-la manuellement.",
                             "de": 'Die Anwendung konnte nicht automatisch neu gestartet werden. Bitte schließen Sie sie und starten Sie sie manuell erneut.',
                             "es": 'No se pudo reiniciar la aplicación automáticamente. Ciérrala e inícia\xadla manualmente de nuevo.',
                         },

    "acc_title":         {"en": "Accent Color",  "pl": "Kolor Akcentu",   "fr": "Couleur d'accent", "de": 'Akzentfarbe', "es": 'Color de acento'},
    "acc_desc":          {"en": "Choose the accent color used throughout the app.",
                          "pl": "Wybierz kolor akcentu używany w całej aplikacji.",
                          "fr": "Choisissez la couleur d'accent utilisée dans l'application.",
                          "de": 'Wählen Sie die in der gesamten App verwendete Akzentfarbe.',
                          "es": 'Elige el color de acento utilizado en toda la aplicación.',
                      },
    "acc_gold":          {"en": "Yellow", "pl": "Żółty",     "fr": "Jaune", "de": 'Gelb', "es": 'Amarillo'},
    "acc_red":           {"en": "Red",    "pl": "Czerwony",  "fr": "Rouge", "de": 'Rot', "es": 'Rojo'},
    "acc_green":         {"en": "Green",  "pl": "Zielony",   "fr": "Vert", "de": 'Grün', "es": 'Verde'},
    "acc_blue":          {"en": "Blue",   "pl": "Niebieski", "fr": "Bleu", "de": 'Blau', "es": 'Azul'},
    "acc_table_text_accent": {"en": "Use accent color for active entries in the table",
                          "pl": "Użyj koloru akcentu dla aktywnych wpisów w tabeli",
                          "fr": "Utiliser la couleur d'accent pour les entrées actives du tableau",
                          "de": 'Akzentfarbe für aktive Einträge in der Tabelle verwenden',
                          "es": 'Usar el color de acento para las entradas activas de la tabla',
                      },
    "acc_restart_msg":   {"en": "Accent color changed. Restart the application now to apply it?",
                          "pl": "Kolor akcentu zmieniony. Uruchomić aplikację ponownie teraz, aby go zastosować?",
                          "fr": "Couleur d'accent modifiée. Redémarrer l'application maintenant pour l'appliquer ?",
                          "de": 'Akzentfarbe geändert. Anwendung jetzt neu starten, um sie anzuwenden?',
                          "es": 'Color de acento cambiado. ¿Reiniciar la aplicación ahora para aplicarlo?',
                      },

    "bak_title":         {"en": "Backup Manager",               "pl": "Menedżer kopii zapasowych",        "fr": "Gestionnaire de sauvegardes", "de": 'Sicherungs-Manager', "es": 'Gestor de copias de seguridad'},
    "bak_header":        {"en": "Hosts file backups",           "pl": "Kopie zapasowe pliku hosts",       "fr": "Sauvegardes du fichier hosts", "de": 'Sicherungen der Hosts-Datei', "es": 'Copias de seguridad del archivo hosts'},
    "bak_subheader":     {"en": "Each save creates a new backup. You can restore any of them, or restore the default hosts.",
                          "pl": "Każdy zapis tworzy nową kopię. Możesz przywrócić dowolną lub przywrócić domyślny hosts.",
                          "fr": "Chaque enregistrement crée une nouvelle sauvegarde. Vous pouvez restaurer n'importe laquelle, ou restaurer le hosts par défaut.",
                          "de": 'Jeder Speichervorgang erstellt eine neue Sicherung. Sie können jede davon wiederherstellen oder den Standard-Hosts wiederherstellen.',
                          "es": 'Cada guardado crea una nueva copia de seguridad. Puedes restaurar cualquiera de ellas, o restaurar el hosts predeterminado.',
                      },
    "bak_btn_restore":   {"en": "Restore selected",             "pl": "Przywróć zaznaczoną",              "fr": "Restaurer la sélection", "de": 'Auswahl wiederherstellen', "es": 'Restaurar selección'},
    "bak_btn_delete":    {"en": "Delete selected",              "pl": "Usuń zaznaczone",                  "fr": "Supprimer la sélection", "de": 'Auswahl löschen', "es": 'Eliminar selección'},
    "bak_hint_multi":    {"en": "Shift+click or Ctrl+click — select multiple",
                          "pl": "Shift+klik lub Ctrl+klik — zaznacz wiele",
                          "fr": "Maj+clic ou Ctrl+clic — sélectionner plusieurs",
                          "de": 'Umschalt+Klick oder Strg+Klick — mehrere auswählen',
                          "es": 'Mayús+clic o Ctrl+clic — seleccionar varias',
                      },
    "bak_col_date":      {"en": "Date & Time",                  "pl": "Data i godzina",                   "fr": "Date et heure", "de": 'Datum & Uhrzeit', "es": 'Fecha y hora'},
    "bak_col_size":      {"en": "Size",                         "pl": "Rozmiar",                          "fr": "Taille", "de": 'Größe', "es": 'Tamaño'},
    "bak_col_file":      {"en": "File",                         "pl": "Plik",                             "fr": "Fichier", "de": 'Datei', "es": 'Archivo'},
    "bak_empty":         {"en": "No backups",                   "pl": "Brak kopii",                       "fr": "Aucune sauvegarde", "de": 'Keine Sicherungen', "es": 'Sin copias de seguridad'},
    "bak_no_sel_msg":    {"en": "Select at least one backup.",  "pl": "Zaznacz co najmniej jedną kopię.", "fr": "Sélectionnez au moins une sauvegarde.", "de": 'Wählen Sie mindestens eine Sicherung aus.', "es": 'Selecciona al menos una copia de seguridad.'},
    "bak_too_many_title":{"en": "Too many selected",            "pl": "Za dużo zaznaczonych",             "fr": "Trop d'éléments sélectionnés", "de": 'Zu viele ausgewählt', "es": 'Demasiadas seleccionadas'},
    "bak_too_many_msg":  {"en": "Only one backup can be restored at a time.\nSelect exactly one.",
                          "pl": "Przywróć można tylko jedną kopię na raz.\nZaznacz dokładnie jedną.",
                          "fr": "Une seule sauvegarde peut être restaurée à la fois.\nSélectionnez-en exactement une.",
                          "de": 'Es kann jeweils nur eine Sicherung wiederhergestellt werden.\nWählen Sie genau eine aus.',
                          "es": 'Solo se puede restaurar una copia de seguridad a la vez.\nSelecciona exactamente una.',
                      },
    "bak_restore_ask_title": {"en": "Restore backup",          "pl": "Przywróć kopię",                   "fr": "Restaurer la sauvegarde", "de": 'Sicherung wiederherstellen', "es": 'Restaurar copia de seguridad'},
    "bak_restore_ask_msg":   {"en": "Restore hosts file from:\n{name}\n\nThe current hosts file will be overwritten (a backup will be made).",
                              "pl": "Przywrócić plik hosts z:\n{name}\n\nObecny plik hosts zostanie nadpisany (kopia zostanie wykonana).",
                              "fr": "Restaurer le fichier hosts depuis:\n{name}\n\nLe fichier hosts actuel sera écrasé (une sauvegarde sera créée).",
                              "de": 'Hosts-Datei wiederherstellen aus:\n{name}\n\nDie aktuelle Hosts-Datei wird überschrieben (eine Sicherung wird erstellt).',
                              "es": 'Restaurar archivo hosts desde:\n{name}\n\nEl archivo hosts actual será sobrescrito (se creará una copia de seguridad).',
                          },
    "bak_restore_ok":    {"en": "Hosts file restored successfully.", "pl": "Plik hosts został przywrócony.", "fr": "Fichier hosts restauré avec succès.", "de": 'Hosts-Datei erfolgreich wiederhergestellt.', "es": 'Archivo hosts restaurado correctamente.'},
    "bak_del_ask_title": {"en": "Delete backups",               "pl": "Usuń kopie",                       "fr": "Supprimer les sauvegardes", "de": 'Sicherungen löschen', "es": 'Eliminar copias de seguridad'},
    "bak_del_err_title": {"en": "Delete error",                 "pl": "Błąd usuwania",                     "fr": "Erreur de suppression",     "de": 'Löschfehler',              "es": 'Error al eliminar'},
    "bak_del_ask_one":   {"en": "Permanently delete:\n{name}?", "pl": "Trwale usunąć:\n{name}?",          "fr": "Supprimer définitivement:\n{name}?", "de": 'Endgültig löschen:\n{name}?', "es": '¿Eliminar permanentemente:\n{name}?'},
    "bak_del_ask_many":  {"en": "Permanently delete {n} selected backups?\n\n{names}",
                          "pl": "Zaznaczone kopie do trwałego usunięcia: {n}\n\n{names}\n\nUsunąć?",
                          "fr": "Supprimer définitivement {n} sauvegardes sélectionnées?\n\n{names}",
                          "de": '{n} ausgewählte Sicherungen endgültig löschen?\n\n{names}',
                          "es": '¿Eliminar permanentemente {n} copias de seguridad seleccionadas?\n\n{names}',
                      },
    "bak_status_count":    {"en": "Backups found: {n}.",
                            "pl": "Znalezionych kopii zapasowych: {n}.",
                            "fr": "Sauvegardes trouvées : {n}.",
                            "de": 'Gefundene Sicherungen: {n}.',
                            "es": 'Copias de seguridad encontradas: {n}.',
                        },
    "bak_status_restored": {"en": "Restored backup: {name}",
                            "pl": "Przywrócono kopię: {name}",
                            "fr": "Sauvegarde restaurée : {name}",
                            "de": 'Sicherung wiederhergestellt: {name}',
                            "es": 'Copia de seguridad restaurada: {name}',
                        },
    "bak_status_deleted":  {"en": "Backups deleted: {n}.",
                            "pl": "Usuniętych kopii zapasowych: {n}.",
                            "fr": "Sauvegardes supprimées : {n}.",
                            "de": 'Gelöschte Sicherungen: {n}.',
                            "es": 'Copias de seguridad eliminadas: {n}.',
                        },
    "diff_title":        {"en": "Preview changes before saving", "pl": "Podgląd zmian przed zapisem",     "fr": "Aperçu des modifications avant enregistrement", "de": 'Änderungen vor dem Speichern anzeigen', "es": 'Vista previa de cambios antes de guardar'},
    "diff_file_current": {"en": "current hosts file",           "pl": "aktualny plik hosts",             "fr": "fichier hosts actuel", "de": 'aktuelle hosts-Datei', "es": 'archivo hosts actual'},
    "diff_file_new":     {"en": "new hosts file",               "pl": "nowy plik hosts",                "fr": "nouveau fichier hosts", "de": 'neue hosts-Datei', "es": 'nuevo archivo hosts'},
    "diff_legend":       {"en": "− removed line    + added line    @@ location of the change",
                           "pl": "− usunięta linia    + dodana linia    @@ miejsce zmiany",
                           "fr": "− ligne supprimée    + ligne ajoutée    @@ emplacement de la modification",
                           "de": '− entfernte Zeile    + hinzugefügte Zeile    @@ Position der Änderung',
                           "es": '− línea eliminada    + línea añadida    @@ ubicación del cambio'},
    "diff_header":       {"en": "Preview changes",               "pl": "Podgląd zmian",                   "fr": "Aperçu des modifications", "de": 'Änderungen anzeigen', "es": 'Vista previa de cambios'},
    "diff_added":        {"en": "  + added  ",                   "pl": "  + dodane  ",                    "fr": "  + ajoutées  ", "de": '  + hinzugefügt  ', "es": '  + añadidas  '},
    "diff_removed":      {"en": "  − removed  ",                 "pl": "  − usunięte  ",                  "fr": "  − supprimées  ", "de": '  − entfernt  ', "es": '  − eliminadas  '},
    "diff_no_changes":   {"en": "No changes",                    "pl": "Brak zmian",                      "fr": "Aucune modification", "de": 'Keine Änderungen', "es": 'Sin cambios'},
    "diff_stat":         {"en": "Added: {adds}   Removed: {dels}", "pl": "Dodane: {adds}   Usunięte: {dels}", "fr": "Ajoutées : {adds}   Supprimées : {dels}", "de": 'Hinzugefügt: {adds}   Entfernt: {dels}', "es": 'Añadidas: {adds}   Eliminadas: {dels}'},
    "diff_save_anyway":  {"en": "Save anyway",                   "pl": "Zapisz mimo to",                  "fr": "Enregistrer quand même", "de": 'Trotzdem speichern', "es": 'Guardar de todos modos'},
    "diff_save":         {"en": "Save",                          "pl": "Zapisz",                          "fr": "Enregistrer", "de": 'Speichern', "es": 'Guardar'},
    "diff_cancel":       {"en": "Cancel",                        "pl": "Anuluj",                          "fr": "Annuler", "de": 'Abbrechen', "es": 'Cancelar'},
    "diff_skip":         {"en": "Discard",                       "pl": "Pomiń",                            "fr": "Ignorer", "de": 'Verwerfen', "es": 'Descartar'},
    "diff_no_changes_body": {"en": "  (no changes — file is identical)\n",
                             "pl": "  (brak zmian — plik jest identyczny)\n",
                             "fr": "  (aucune modification — le fichier est identique)\n",
                             "de": '  (keine Änderungen — Datei ist identisch)\n',
                             "es": '  (sin cambios — el archivo es idéntico)\n',
                         },
    "diff_fromfile":     {"en": "hosts (current)",               "pl": "hosts (obecny)",                  "fr": "hosts (actuel)", "de": 'hosts (aktuell)', "es": 'hosts (actual)'},
    "diff_tofile":       {"en": "hosts (new)",                   "pl": "hosts (nowy)",                    "fr": "hosts (nouveau)", "de": 'hosts (neu)', "es": 'hosts (nuevo)'},
    "entry_title_add":   {"en": "Add entry",                     "pl": "Dodaj wpis",                      "fr": "Ajouter une entrée", "de": 'Eintrag hinzufügen', "es": 'Añadir entrada'},
    "entry_title_edit":  {"en": "Edit entry",                    "pl": "Edytuj wpis",                     "fr": "Modifier l'entrée", "de": 'Eintrag bearbeiten', "es": 'Editar entrada'},
    "entry_lbl_ip":      {"en": "IP Address:",                   "pl": "Adres IP:",                       "fr": "Adresse IP:", "de": 'IP-Adresse:', "es": 'Dirección IP:'},
    "entry_lbl_host":    {"en": "Hostname:",                     "pl": "Nazwa hosta:",                       "fr": "Nom d'hôte:", "de": 'Hostname:', "es": 'Nombre de host:'},
    "entry_lbl_comment": {"en": "Comment:",                      "pl": "Komentarz:",                      "fr": "Commentaire:", "de": 'Kommentar:', "es": 'Comentario:'},
    "entry_lbl_active":  {"en": "Active",                        "pl": "Aktywny",                         "fr": "Actif", "de": 'Aktiv', "es": 'Activo'},
    "entry_btn_save":    {"en": "Save",                          "pl": "Zapisz",                          "fr": "Enregistrer", "de": 'Speichern', "es": 'Guardar'},
    "entry_btn_cancel":  {"en": "Cancel",                        "pl": "Anuluj",                          "fr": "Annuler", "de": 'Abbrechen', "es": 'Cancelar'},
    "entry_hint_bulk":   {"en": "⚠ Multiple lines detected — click Save to add all at once.",
                          "pl": "⚠ Wykryto wiele linii — kliknij Zapisz, aby dodać wszystkie zbiorczo.",
                          "fr": "⚠ Plusieurs lignes détectées — cliquez sur Enregistrer pour tout ajouter.",
                          "de": '⚠ Mehrere Zeilen erkannt — klicken Sie auf Speichern, um alle auf einmal hinzuzufügen.',
                          "es": '⚠ Se detectaron varias líneas — haz clic en Guardar para añadirlas todas a la vez.',
                      },
    "entry_hint_sanitize":{"en": "⚠ Will be auto-corrected (protocol/slash removal) on save.",
                           "pl": "⚠ Zostanie auto-poprawiony (usunięcie protokołu/ukośników) przy zapisie.",
                           "fr": "⚠ Sera auto-corrigé (suppression protocole/slashes) à l'enregistrement.",
                           "de": '⚠ Wird beim Speichern automatisch korrigiert (Entfernen von Protokoll/Schrägstrichen).',
                           "es": '⚠ Se corregirá automáticamente (eliminación de protocolo/barras) al guardar.',
                       },
    "entry_hint_dup":    {"en": "✘ This hostname already points to {existing_ip}.",
                          "pl": "✘ Ta nazwa hosta jest już przypisana do {existing_ip}.",
                          "fr": "✘ Ce nom d'hôte pointe déjà vers {existing_ip}.",
                          "de": '✘ Dieser Hostname zeigt bereits auf {existing_ip}.',
                          "es": '✘ Este nombre de host ya apunta a {existing_ip}.',
                      },
    "entry_hint_bad_ip": {"en": "⚠ Invalid IP address format.",
                          "pl": "⚠ Nieprawidłowy format adresu IP.",
                          "fr": "⚠ Format d'adresse IP invalide.",
                          "de": '⚠ Ungültiges IP-Adressformat.',
                          "es": '⚠ Formato de dirección IP no válido.',
                      },
    "entry_err_title":   {"en": "Error",                         "pl": "Błąd",                            "fr": "Erreur", "de": 'Fehler', "es": 'Error'},
    "entry_err_bulk_fmt":{"en": "Could not parse format.\nExpected format per line: IP hostname",
                          "pl": "Nie udało się rozpoznać formatu.\nOczekiwany format każdej linii: IP hostname",
                          "fr": "Impossible d'analyser le format.\nFormat attendu par ligne: IP nom_d_hote",
                          "de": 'Format konnte nicht analysiert werden.\nErwartetes Format pro Zeile: IP Hostname',
                          "es": 'No se pudo analizar el formato.\nFormato esperado por línea: IP hostname',
                      },
    "entry_skip_title":  {"en": "All entries already exist",     "pl": "Wszystkie wpisy już istnieją",    "fr": "Toutes les entrées existent déjà", "de": 'Alle Einträge existieren bereits', "es": 'Todas las entradas ya existen'},
    "entry_skip_some":   {"en": "Some entries skipped",          "pl": "Część wpisów pominięta",          "fr": "Certaines entrées ignorées", "de": 'Einige Einträge übersprungen', "es": 'Algunas entradas omitidas'},
    "entry_skip_msg":    {"en": "Duplicates skipped: {n}\n{list}",
                          "pl": "Pominiętych duplikatów: {n}\n{list}",
                          "fr": "Doublons ignorés : {n}\n{list}",
                          "de": 'Übersprungene Duplikate: {n}\n{list}',
                          "es": 'Duplicados omitidos: {n}\n{list}',
                      },
    "entry_err_required":{"en": "IP and Hostname are required.", "pl": "IP i Hostname są wymagane.",      "fr": "L'IP et le nom d'hôte sont requis.", "de": 'IP und Hostname sind erforderlich.', "es": 'Se requieren IP y nombre de host.'},
    "entry_bad_ip_title":{"en": "Invalid IP",                    "pl": "Nieprawidłowy IP",                "fr": "IP invalide", "de": 'Ungültige IP', "es": 'IP no válida'},
    "entry_bad_ip_ask":  {"en": '"{ip}" does not look like a valid IPv4/IPv6 address.\n\nSave anyway?',
                          "pl": '"{ip}" nie wygląda jak poprawny adres IPv4/IPv6.\n\nZapisać mimo to?',
                          "fr": '"{ip}" ne ressemble pas à une adresse IPv4/IPv6 valide.\n\nEnregistrer quand même?',
                          "de": '„{ip}" sieht nicht wie eine gültige IPv4-/IPv6-Adresse aus.\n\nTrotzdem speichern?',
                          "es": '"{ip}" no parece una dirección IPv4/IPv6 válida.\n\n¿Guardar de todos modos?',
                      },
    "entry_dup_title":   {"en": "Hostname already used",           "pl": "Nazwa hosta już zajęta",            "fr": "Nom d'hôte déjà utilisé", "de": 'Hostname bereits verwendet', "es": 'Nombre de host ya usado'},
    "entry_dup_ask":     {"en": 'Hostname "{host}" already points to {existing_ip} in the hosts file.\n\nOnly the FIRST matching entry for a hostname is actually used - adding this one with a different IP ({ip}) will have no effect unless you disable or remove the existing one.\n\nAdd anyway?',
                          "pl": 'Nazwa "{host}" jest już przypisana do {existing_ip} w pliku hosts.\n\nDla danej nazwy hosta faktycznie działa tylko PIERWSZY pasujący wpis - dodanie tego z innym IP ({ip}) nic nie zmieni, dopóki nie wyłączysz lub nie usuniesz istniejącego.\n\nDodać mimo to?',
                          "fr": 'Le nom "{host}" pointe déjà vers {existing_ip} dans le fichier hosts.\n\nSeule la PREMIÈRE entrée correspondante pour un nom d\'hôte est réellement utilisée - ajouter celle-ci avec une IP différente ({ip}) n\'aura aucun effet tant que vous ne désactivez pas ou ne supprimez pas l\'entrée existante.\n\nAjouter quand même?',
                          "de": 'Der Hostname „{host}" zeigt bereits auf {existing_ip} in der Hosts-Datei.\n\nFür einen Hostnamen wird tatsächlich nur der ERSTE passende Eintrag verwendet - das Hinzufügen mit einer anderen IP ({ip}) hat keine Wirkung, solange Sie den vorhandenen Eintrag nicht deaktivieren oder entfernen.\n\nTrotzdem hinzufügen?',
                          "es": 'El nombre "{host}" ya apunta a {existing_ip} en el archivo hosts.\n\nSolo se usa realmente la PRIMERA entrada coincidente para un nombre de host - añadir esta con una IP distinta ({ip}) no tendrá efecto a menos que desactives o elimines la existente.\n\n¿Añadir de todos modos?',
                      },
    "diag_title_existence": {"en": "Domain existence check",     "pl": "Sprawdzanie istnienia domen",     "fr": "Vérification d'existence des domaines", "de": 'Domain-Existenzprüfung', "es": 'Comprobación de existencia de dominios'},
    "diag_title_malware":   {"en": "Suspicious entry detection", "pl": "Wykrywanie podejrzanych wpisów",  "fr": "Détection d'entrées suspectes", "de": 'Erkennung verdächtiger Einträge', "es": 'Detección de entradas sospechosas'},
    "diag_desc_existence":  {"en": "Checks entries via external DNS (8.8.8.8) — bypasses the hosts file.\nIf a domain does not exist on the internet — the block is unnecessary.",
                             "pl": "Sprawdza wpisy przez zewnętrzny DNS (8.8.8.8) — omija plik hosts.\nJeśli domena nie istnieje w internecie — blokada jest zbędna.",
                             "fr": "Vérifie les entrées via DNS externe (8.8.8.8) — contourne le fichier hosts.\nSi un domaine n'existe pas sur internet — le blocage est inutile.",
                             "de": 'Prüft Einträge über externes DNS (8.8.8.8) — umgeht die Hosts-Datei.\nWenn eine Domain im Internet nicht existiert — ist die Blockierung überflüssig.',
                             "es": 'Comprueba las entradas mediante DNS externo (8.8.8.8) — evita el archivo hosts.\nSi un dominio no existe en internet, el bloqueo es innecesario.',
                         },
    "diag_desc_malware":    {"en": "Analyzes entries for malware indicators.\nChecks: AV/Windows Update blocks, homoglyphs, suspicious IPs and more.",
                             "pl": "Analizuje wpisy pod kątem złośliwego oprogramowania.\nSprawdza: blokady AV/Windows Update, homoglify, podejrzane IP i inne.",
                             "fr": "Analyse les entrées pour des indicateurs de malware.\nVérifie: blocages AV/Windows Update, homoglyphes, IPs suspectes et plus.",
                             "de": 'Analysiert Einträge auf Malware-Indikatoren.\nPrüft: AV-/Windows-Update-Blockaden, Homoglyphen, verdächtige IPs und mehr.',
                             "es": 'Analiza las entradas en busca de indicadores de malware.\nComprueba: bloqueos de AV/Windows Update, homoglifos, IPs sospechosas y más.',
                         },
    "diag_scan_count":      {"en": "Selected to scan: {n}", "pl": "Zaznaczone wpisy do skanowania: {n}", "fr": "Sélectionné à analyser : {n}", "de": 'Zum Scannen ausgewählt: {n}', "es": 'Seleccionadas para escanear: {n}'},
    "diag_scan_count_all":  {"en": "Entries to scan: {n}", "pl": "Wpisy do skanowania: {n}", "fr": "Entrées à analyser : {n}", "de": 'Zu scannende Einträge: {n}', "es": 'Entradas para escanear: {n}'},
    "diag_btn_run":         {"en": "Run scan",                   "pl": "Uruchom skan",                    "fr": "Lancer le scan", "de": 'Scan starten', "es": 'Ejecutar escaneo'},
    "diag_btn_stop":        {"en": "Stop",                       "pl": "Zatrzymaj",                       "fr": "Arrêter", "de": 'Stopp', "es": 'Detener'},
    "diag_stopping":        {"en": "Stopping…",                  "pl": "Zatrzymuję…",                     "fr": "Arrêt en cours…", "de": 'Wird gestoppt…', "es": 'Deteniendo…'},
    "diag_click_to_start":  {"en": "Click Run scan to start.",   "pl": "Kliknij Uruchom skan aby rozpocząć.", "fr": "Cliquez sur Lancer le scan pour commencer.", "de": 'Klicken Sie auf „Scan starten", um zu beginnen.', "es": 'Haz clic en Ejecutar escaneo para empezar.'},
    "diag_col_result":      {"en": "Result",                     "pl": "Wynik",                           "fr": "Résultat", "de": 'Ergebnis', "es": 'Resultado'},
    "diag_col_hostname":    {"en": "Hostname",                   "pl": "Nazwa hosta",                        "fr": "Nom d'hôte", "de": 'Hostname', "es": 'Nombre de host'},
    "diag_col_ip":          {"en": "IP",                         "pl": "IP",                              "fr": "IP", "de": 'IP', "es": 'IP'},
    "diag_col_info":        {"en": "Info",                       "pl": "Informacja",                      "fr": "Information", "de": 'Info', "es": 'Información'},
    "diag_col_risk":        {"en": "Risk",                       "pl": "Ryzyko",                          "fr": "Risque", "de": 'Risiko', "es": 'Riesgo'},
    "diag_col_reason":      {"en": "Reason",                     "pl": "Powód",                           "fr": "Raison", "de": 'Grund', "es": 'Motivo'},
    "diag_btn_del_inactive":{"en": "Delete inactive",            "pl": "Usuń nieaktywne",                 "fr": "Supprimer les inactifs", "de": 'Inaktive löschen', "es": 'Eliminar inactivas'},
    "diag_btn_del_sel":     {"en": "Delete selected",            "pl": "Usuń zaznaczone",                 "fr": "Supprimer la sélection", "de": 'Auswahl löschen', "es": 'Eliminar seleccionadas'},
    "diag_btn_del_sel_hosts":{"en": "Delete selected from hosts","pl": "Usuń zaznaczone z hosts",         "fr": "Supprimer la sélection des hosts", "de": 'Auswahl aus Hosts löschen', "es": 'Eliminar seleccionadas de hosts'},
    "diag_hint_multi":      {"en": "Shift+click / Ctrl+click — select multiple",
                             "pl": "Shift+klik / Ctrl+klik — zaznacz wiele",
                             "fr": "Maj+clic / Ctrl+clic — sélectionner plusieurs",
                             "de": 'Umschalt+Klick / Strg+Klick — mehrere auswählen',
                             "es": 'Mayús+clic / Ctrl+clic — seleccionar varias',
                         },
    "diag_no_internet_title":{"en": "No internet connection",   "pl": "Brak połączenia z internetem",    "fr": "Pas de connexion internet", "de": 'Keine Internetverbindung', "es": 'Sin conexión a internet'},
    "diag_no_internet_msg": {"en": "No internet access was detected. Domain existence check requires a working connection — otherwise every entry would be reported as an error, even if the domains are actually fine.",
                             "pl": "Nie wykryto dostępu do internetu. Sprawdzenie istnienia domen wymaga działającego połączenia — w przeciwnym razie każdy wpis zostałby oznaczony jako błąd, mimo że domeny mogą być całkowicie w porządku.",
                             "fr": "Aucun accès à Internet détecté. La vérification de l'existence des domaines nécessite une connexion active — sinon chaque entrée serait signalée comme une erreur, même si les domaines sont en réalité corrects.",
                             "de": 'Es wurde kein Internetzugang erkannt. Die Domain-Existenzprüfung erfordert eine funktionierende Verbindung — andernfalls würde jeder Eintrag als Fehler gemeldet, selbst wenn die Domains eigentlich in Ordnung sind.',
                             "es": 'No se detectó acceso a internet. La comprobación de existencia de dominios requiere una conexión activa — de lo contrario, cada entrada se marcaría como error, aunque los dominios estén realmente bien.',
                         },
    "diag_no_inactive_title":{"en": "No entries",               "pl": "Brak wpisów",                     "fr": "Aucune entrée", "de": 'Keine Einträge', "es": 'Sin entradas'},
    "diag_no_inactive_msg": {"en": "No entries marked as non-existent were found.",
                             "pl": "Nie znaleziono wpisów oznaczonych jako nieistniejące.",
                             "fr": "Aucune entrée marquée comme inexistante n'a été trouvée.",
                             "de": 'Es wurden keine als nicht existent markierten Einträge gefunden.',
                             "es": 'No se encontraron entradas marcadas como inexistentes.',
                         },
    "diag_del_confirm_title":{"en": "Confirm deletion",          "pl": "Potwierdź usunięcie",             "fr": "Confirmer la suppression", "de": 'Löschung bestätigen', "es": 'Confirmar eliminación'},
    "diag_del_inactive_msg":{"en": "Unnecessary entries: {n}\n\n{preview}{suffix}\n\nDelete them?\n\nSave the file in the main window after closing this window.",
                             "pl": "Zbędne wpisy do usunięcia: {n}\n\n{preview}{suffix}\n\nUsunąć?\n\nZapisz plik w głównym oknie po zamknięciu tego okna.",
                             "fr": "Entrées inutiles : {n}\n\n{preview}{suffix}\n\nLes supprimer?\n\nEnregistrez le fichier dans la fenêtre principale après fermeture.",
                             "de": 'Unnötige Einträge: {n}\n\n{preview}{suffix}\n\nLöschen?\n\nSpeichern Sie die Datei nach dem Schließen dieses Fensters im Hauptfenster.',
                             "es": 'Entradas innecesarias: {n}\n\n{preview}{suffix}\n\n¿Eliminarlas?\n\nGuarda el archivo en la ventana principal después de cerrar esta ventana.',
                         },
    "diag_del_sel_msg":     {"en": "Entries to delete from the hosts file: {n}\n\n{preview}{suffix}\n\nDelete them?\n\nChanges will be visible in the main window.\nRemember to save the file after closing this window.",
                             "pl": "Wpisy do usunięcia z pliku hosts: {n}\n\n{preview}{suffix}\n\nUsunąć?\n\nZmiany będą widoczne w głównym oknie.\nPamiętaj aby zapisać plik po zamknięciu tego okna.",
                             "fr": "Entrées à supprimer du fichier hosts : {n}\n\n{preview}{suffix}\n\nLes supprimer?\n\nLes modifications seront visibles dans la fenêtre principale.\nPensez à enregistrer le fichier après fermeture.",
                             "de": 'Aus der Hosts-Datei zu löschende Einträge: {n}\n\n{preview}{suffix}\n\nLöschen?\n\nÄnderungen werden im Hauptfenster sichtbar.\nDenken Sie daran, die Datei nach dem Schließen dieses Fensters zu speichern.',
                             "es": 'Entradas a eliminar del archivo hosts: {n}\n\n{preview}{suffix}\n\n¿Eliminarlas?\n\nLos cambios serán visibles en la ventana principal.\nRecuerda guardar el archivo después de cerrar esta ventana.',
                         },
    "diag_more":            {"en": "\n... and {n} more",         "pl": "\n... i {n} więcej",              "fr": "\n... et {n} de plus", "de": '\n... und {n} weitere', "es": '\n... y {n} más'},
    "diag_no_sel_msg":      {"en": "Select entries you want to delete.",
                             "pl": "Zaznacz wpisy które chcesz usunąć.",
                             "fr": "Sélectionnez les entrées que vous souhaitez supprimer.",
                             "de": 'Wählen Sie die Einträge aus, die Sie löschen möchten.',
                             "es": 'Selecciona las entradas que deseas eliminar.',
                         },
    "diag_status_deleted_inactive": {"en": "Unnecessary entries deleted: {n}. Save the file in the main window.",
                                     "pl": "Usunięte zbędne wpisy: {n}. Zapisz plik w głównym oknie.",
                                     "fr": "Entrées inutiles supprimées : {n}. Enregistrez le fichier dans la fenêtre principale.",
                                     "de": 'Gelöschte unnötige Einträge: {n}. Speichern Sie die Datei im Hauptfenster.',
                                     "es": 'Entradas innecesarias eliminadas: {n}. Guarda el archivo en la ventana principal.',
                                 },
    "diag_status_deleted_sel":      {"en": "Entries deleted: {n}. Save the file in the main window.",
                                     "pl": "Usunięte wpisy: {n}. Zapisz plik w głównym oknie.",
                                     "fr": "Entrées supprimées : {n}. Enregistrez le fichier dans la fenêtre principale.",
                                     "de": 'Gelöschte Einträge: {n}. Speichern Sie die Datei im Hauptfenster.',
                                     "es": 'Entradas eliminadas: {n}. Guarda el archivo en la ventana principal.',
                                 },
    "diag_ctx_ignore_one":  {"en": "Ignore this entry",           "pl": "Zignoruj ten wpis",                "fr": "Ignorer cette entrée", "de": 'Diesen Eintrag ignorieren', "es": 'Ignorar esta entrada'},
    "diag_ctx_ignore_many": {"en": "Ignore selected ({n})",       "pl": "Zignoruj zaznaczone ({n})",        "fr": "Ignorer la sélection ({n})", "de": 'Auswahl ignorieren ({n})', "es": 'Ignorar seleccionadas ({n})'},
    "diag_status_ignored":  {"en": "Entries ignored: {n} — they won't appear in future scans.",
                             "pl": "Zignorowane wpisy: {n} — nie pojawią się w kolejnych skanach.",
                             "fr": "Entrées ignorées : {n} — elles n'apparaîtront plus dans les prochains scans.",
                             "de": 'Ignorierte Einträge: {n} — sie erscheinen in zukünftigen Scans nicht mehr.',
                             "es": 'Entradas ignoradas: {n} — no aparecerán en futuros escaneos.',
                         },
    "diag_scanning":        {"en": "Scanning: ",                 "pl": "Sprawdzam: ",                     "fr": "Analyse: ", "de": 'Scanne: ', "es": 'Escaneando: '},
    "diag_analyzing":       {"en": "Analyzing: ",                "pl": "Analizuję: ",                     "fr": "Analyse: ", "de": 'Analysiere: ', "es": 'Analizando: '},
    "diag_scan_done":       {"en": "Scan complete.",             "pl": "Skan zakończony.",                 "fr": "Scan terminé.", "de": 'Scan abgeschlossen.', "es": 'Escaneo completado.'},
    "diag_summary_exist":   {"en": "Done. Active: {found} | Unnecessary: {missing} | Timeout/error: {errors}.",
                             "pl": "Zakończono. Aktywne: {found} | Zbędne: {missing} | Timeout/błąd: {errors}.",
                             "fr": "Terminé. Actifs : {found} | Inutiles : {missing} | Timeout/erreur : {errors}.",
                             "de": 'Fertig. Aktiv: {found} | Unnötig: {missing} | Timeout/Fehler: {errors}.',
                             "es": 'Hecho. Activas: {found} | Innecesarias: {missing} | Tiempo de espera/error: {errors}.',
                         },
    "diag_summary_malware": {"en": "Done. Suspicious entries found: {issues} (out of {total} checked).",
                             "pl": "Zakończono. Podejrzane wpisy: {issues} (z {total} sprawdzonych).",
                             "fr": "Terminé. Entrées suspectes trouvées : {issues} (sur {total} vérifiées).",
                             "de": 'Fertig. Verdächtige Einträge gefunden: {issues} (von {total} geprüften).',
                             "es": 'Hecho. Entradas sospechosas encontradas: {issues} (de {total} comprobadas).',
                         },
    "diag_summary_stopped": {"en": "Stopped. Checked {done} of {total} entries.",
                             "pl": "Zatrzymano. Sprawdzono {done} z {total} wpisów.",
                             "fr": "Arrêté. Vérifié {done} sur {total} entrées.",
                             "de": 'Gestoppt. {done} von {total} Einträgen geprüft.',
                             "es": 'Detenido. Se comprobaron {done} de {total} entradas.',
                         },
    "diag_exist_ok":        {"en": "✔ exists",                   "pl": "✔ istnieje",                      "fr": "✔ existe", "de": '✔ existiert', "es": '✔ existe'},
    "diag_exist_ok_info":   {"en": "Domain active — block justified",  "pl": "Domena aktywna — blokada uzasadniona", "fr": "Domaine actif — blocage justifié", "de": 'Domain aktiv — Blockierung gerechtfertigt', "es": 'Dominio activo — bloqueo justificado'},
    "diag_exist_miss":      {"en": "✘ not found",                "pl": "✘ nie istnieje",                  "fr": "✘ introuvable", "de": '✘ nicht gefunden', "es": '✘ no encontrado'},
    "diag_exist_miss_info": {"en": "Not in DNS — entry unnecessary",   "pl": "Brak w DNS — wpis zbędny",        "fr": "Absent du DNS — entrée inutile", "de": 'Nicht im DNS — Eintrag unnötig', "es": 'No está en el DNS — entrada innecesaria'},
    "diag_exist_err":       {"en": "? timeout/error",            "pl": "? timeout/błąd",                  "fr": "? timeout/erreur", "de": '? Timeout/Fehler', "es": '? tiempo de espera/error'},
    "diag_exist_err_info":  {"en": "No response from DNS 8.8.8.8",    "pl": "Brak odpowiedzi z DNS 8.8.8.8",   "fr": "Pas de réponse du DNS 8.8.8.8", "de": 'Keine Antwort von DNS 8.8.8.8', "es": 'Sin respuesta del DNS 8.8.8.8'},
    "diag_clean":           {"en": "✔ Clean",                    "pl": "✔ Czysto",                         "fr": "✔ Propre", "de": '✔ Sauber', "es": '✔ Limpio'},
    "diag_clean_msg":       {"en": "No suspicious entries",      "pl": "Brak podejrzanych wpisów",        "fr": "Aucune entrée suspecte", "de": 'Keine verdächtigen Einträge', "es": 'Sin entradas sospechosas'},
    "diag_risk_high":       {"en": "\U0001f534 High",            "pl": "\U0001f534 Wysokie",               "fr": "\U0001f534 Élevé", "de": '🔴 Hoch', "es": '🔴 Alto'},
    "diag_risk_medium":     {"en": "\U0001f7e1 Medium",          "pl": "\U0001f7e1 Średnie",               "fr": "\U0001f7e1 Moyen", "de": '🟡 Mittel', "es": '🟡 Medio'},
    "diag_reason_sys_dom":  {"en": "Known system domain redirected to {ip}",
                             "pl": "Znana domena systemowa przekierowana na {ip}",
                             "fr": "Domaine système connu redirigé vers {ip}",
                             "de": 'Bekannte Systemdomain umgeleitet auf {ip}',
                             "es": 'Dominio del sistema conocido redirigido a {ip}',
                         },
    "diag_reason_update":   {"en": "System/AV update block: {host}",
                             "pl": "Blokada aktualizacji systemu/AV: {host}",
                             "fr": "Blocage mise à jour système/AV: {host}",
                             "de": 'System-/AV-Update-Blockierung: {host}',
                             "es": 'Bloqueo de actualización de sistema/AV: {host}',
                         },
    "diag_reason_public_ip":{"en": "Redirect to public IP: {ip}",
                             "pl": "Przekierowanie na publiczny IP: {ip}",
                             "fr": "Redirection vers IP public: {ip}",
                             "de": 'Umleitung zu öffentlicher IP: {ip}',
                             "es": 'Redirección a IP pública: {ip}',
                         },
    "diag_reason_many_dom": {"en": "Domains on same IP: {n} — suspicious",
                             "pl": "Domeny na tym IP: {n} — podejrzane",
                             "fr": "Domaines sur la même IP : {n} — suspect",
                             "de": 'Domains auf derselben IP: {n} — verdächtig',
                             "es": 'Dominios en la misma IP: {n} — sospechoso',
                         },
    "diag_reason_homoglyph":{"en": "Suspicious characters in hostname: {chars}",
                             "pl": "Podejrzane znaki w nazwie hosta: {chars}",
                             "fr": "Caractères suspects dans le nom d'hôte: {chars}",
                             "de": 'Verdächtige Zeichen im Hostname: {chars}',
                             "es": 'Caracteres sospechosos en el nombre de host: {chars}',
                         },
    "diag_reason_zero_width":{"en": "Hidden zero-width characters in hostname: {chars}",
                             "pl": "Ukryte znaki zero-width w nazwie hosta: {chars}",
                             "fr": "Caractères zero-width cachés dans le nom d'hôte: {chars}",
                             "de": 'Versteckte Zero-Width-Zeichen im Hostname: {chars}',
                             "es": 'Caracteres ocultos de ancho cero en el nombre de host: {chars}',
                         },
    "diag_reason_ip_host":  {"en": "Hostname is an IP address — unusual",
                             "pl": "Nazwa hosta jest adresem IP — nietypowe",
                             "fr": "Le nom d'hôte est une adresse IP — inhabituel",
                             "de": 'Hostname ist eine IP-Adresse — ungewöhnlich',
                             "es": 'El nombre de host es una dirección IP — inusual',
                         },
    "diag_reason_dga":      {"en": "High name entropy — possible DGA malware (entropy={entropy})",
                             "pl": "Wysoka entropia nazwy — możliwe DGA malware (entropia={entropy})",
                             "fr": "Entropie élevée — possible malware DGA (entropie={entropy})",
                             "de": 'Hohe Namensentropie — möglicherweise DGA-Malware (Entropie={entropy})',
                             "es": 'Alta entropía del nombre — posible malware DGA (entropía={entropy})',
                         },
    "diag_reason_typosquat":{"en": "Possible typosquatting — similar to: {similar_to}",
                             "pl": "Możliwy typosquatting — podobna do: {similar_to}",
                             "fr": "Possible typosquatting — similaire à: {similar_to}",
                             "de": 'Mögliches Typosquatting — ähnlich zu: {similar_to}',
                             "es": 'Posible typosquatting — similar a: {similar_to}',
                         },
    "diag_reason_bad_tld":  {"en": "Suspicious top-level domain: .{tld}",
                             "pl": "Podejrzana domena TLD: .{tld}",
                             "fr": "Domaine de premier niveau suspect: .{tld}",
                             "de": 'Verdächtige Top-Level-Domain: .{tld}',
                             "es": 'Dominio de nivel superior sospechoso: .{tld}',
                         },
    "diag_reason_punycode": {"en": "Punycode encoding (xn--) — possible IDN homograph attack",
                             "pl": "Kodowanie Punycode (xn--) — możliwy atak IDN homograph",
                             "fr": "Encodage Punycode (xn--) — possible attaque IDN homographe",
                             "de": 'Punycode-Kodierung (xn--) — möglicher IDN-Homograph-Angriff',
                             "es": 'Codificación Punycode (xn--) — posible ataque de homógrafos IDN',
                         },
    "diag_reason_deep_sub": {"en": "Excessive subdomain depth (levels: {n}) — possible DNS tunneling",
                             "pl": "Nadmierna głębokość subdomen (poziomów: {n}) — możliwy DNS tunneling",
                             "fr": "Profondeur de sous-domaine excessive (niveaux : {n}) — possible tunnel DNS",
                             "de": 'Übermäßige Subdomain-Tiefe (Ebenen: {n}) — mögliches DNS-Tunneling',
                             "es": 'Profundidad excesiva de subdominios (niveles: {n}) — posible DNS tunneling',
                         },
    "diag_reason_suspicious":{"en": "Suspicious pattern in domain name",
                              "pl": "Podejrzany wzorzec w nazwie domeny",
                              "fr": "Modèle suspect dans le nom de domaine",
                              "de": 'Verdächtiges Muster im Domainnamen',
                              "es": 'Patrón sospechoso en el nombre de dominio',
                          },
    "diag_reason_suspicious_phish": {"en": "Name looks like a phishing attempt impersonating {brand}",
                             "pl": "Nazwa wygląda na próbę podszycia się pod {brand}",
                             "fr": "Le nom ressemble à une tentative de phishing usurpant {brand}",
                             "de": 'Name sieht wie ein Phishing-Versuch aus, der {brand} imitiert',
                             "es": 'El nombre parece un intento de phishing suplantando a {brand}',
                         },
    "diag_reason_suspicious_digits": {"en": "Long sequence of digits in the name",
                             "pl": "Długi ciąg cyfr w nazwie",
                             "fr": "Longue séquence de chiffres dans le nom",
                             "de": 'Lange Ziffernfolge im Namen',
                             "es": 'Larga secuencia de dígitos en el nombre',
                         },
    "diag_reason_suspicious_label": {"en": "Very long, unreadable segment in the name",
                             "pl": "Bardzo długi, nieczytelny człon nazwy",
                             "fr": "Segment très long et illisible dans le nom",
                             "de": 'Sehr langes, unlesbares Segment im Namen',
                             "es": 'Segmento muy largo e ilegible en el nombre',
                         },
    "diag_reason_suspicious_iplike": {"en": "Name starts like an IP address",
                             "pl": "Nazwa zaczyna się jak adres IP",
                             "fr": "Le nom commence comme une adresse IP",
                             "de": 'Name beginnt wie eine IP-Adresse',
                             "es": 'El nombre empieza como una dirección IP',
                         },
    "par_limitations_tooltip": {
        "en": (
            "Hosts-based blocking has known limitations:\n\n"
            "• DNS-over-HTTPS (DoH) — Chrome, Firefox and Edge may use\n"
            "  their own encrypted DNS, bypassing the hosts file entirely.\n"
            "  Turn on DoH blocking for browsers below in this tab, so it\n"
            "  can't be disabled from inside the browser itself.\n\n"
            "• Large platforms (TikTok, YouTube…) use hundreds of\n"
            "  subdomains. Blocklists are updated with each HOTS release,\n"
            "  but gaps may exist at any given time."
        ),
        "pl": (
            "Blokowanie przez plik hosts ma znane ograniczenia:\n\n"
            "• DNS-over-HTTPS (DoH) — Chrome, Firefox i Edge mogą używać\n"
            "  własnego szyfrowanego DNS, całkowicie omijając plik hosts.\n"
            "  Włącz blokadę DoH dla przeglądarek niżej w tej zakładce —\n"
            "  wtedy nie da się jej wyłączyć z poziomu samej przeglądarki.\n\n"
            "• Duże platformy (TikTok, YouTube…) używają setek subdomen.\n"
            "  Listy blokad są aktualizowane z każdą wersją HOTS,\n"
            "  ale luki mogą istnieć w dowolnym momencie."
        ),
        "fr": (
            "Le blocage par fichier hosts a des limitations connues:\n\n"
            "• DNS-over-HTTPS (DoH) — Chrome, Firefox et Edge peuvent utiliser\n"
            "  leur propre DNS chiffré, contournant entièrement le fichier hosts.\n"
            "  Activez le blocage DoH pour les navigateurs plus bas dans cet\n"
            "  onglet, afin qu'il ne puisse pas être désactivé depuis le navigateur.\n\n"
            "• Les grandes plateformes (TikTok, YouTube…) utilisent des centaines\n"
            "  de sous-domaines. Les listes sont mises à jour à chaque version de HOTS,\n"
            "  mais des lacunes peuvent exister à tout moment."
        ),
    
        "de": 'Die Blockierung über die Hosts-Datei hat bekannte Einschränkungen:\n\n• DNS-over-HTTPS (DoH) — Chrome, Firefox und Edge verwenden\n  möglicherweise ihr eigenes verschlüsseltes DNS und umgehen\n  die Hosts-Datei vollständig. Aktivieren Sie weiter unten in diesem\n  Tab die DoH-Blockierung für Browser, damit sie nicht aus dem\n  Browser heraus deaktiviert werden kann.\n\n• Große Plattformen (TikTok, YouTube…) verwenden Hunderte\n  von Subdomains. Die Blocklisten werden mit jedem HOTS-Release\n  aktualisiert, aber es können jederzeit Lücken bestehen.',
        "es": "El bloqueo mediante hosts tiene limitaciones conocidas:\n\n• DNS-over-HTTPS (DoH) — Chrome, Firefox y Edge pueden usar\n  su propio DNS cifrado, evitando por completo el archivo hosts.\n  Activa el bloqueo de DoH para los navegadores más abajo en esta\n  pestaña, para que no se pueda desactivar desde el propio navegador.\n\n• Las grandes plataformas (TikTok, YouTube…) usan cientos de\n  subdominios. Las listas de bloqueo se actualizan con cada versión\n  de HOTS, pero puede haber huecos en cualquier momento.",
    },
    "par_title":            {"en": "🛡️ Parental Protection",              "pl": "🛡️ Ochrona rodzicielska",                        "fr": "🛡️ Protection parentale", "de": '🛡️ Kinderschutz', "es": '🛡️ Protección parental'},
    "par_header":           {"en": "🛡️  Parental Protection",             "pl": "🛡️  Ochrona rodzicielska",                       "fr": "🛡️  Protection parentale", "de": '🛡️  Kinderschutz', "es": '🛡️  Protección parental'},
    "par_subheader":        {"en": "Control access and protect your system settings.",
                             "pl": "Kontroluj dostęp i chroń ustawienia systemu.",
                             "fr": "Contrôlez l'accès et protégez les paramètres système.",
                             "de": 'Kontrolliere den Zugriff und schütze die Systemeinstellungen.',
                             "es": 'Controla el acceso y protege la configuración del sistema.',
                         },
    "par_categories_title": {"en": "Popular services block", "pl": "Blokada popularnych serwisów",   "fr": "Blocage de services populaires", "de": 'Blockierung beliebter Dienste', "es": 'Bloqueo de servicios populares'},
    "par_categories_tooltip": {
        "en": "Blocks selected services and platforms (e.g. social media, adult content, games, "
              "torrents, dating apps and random video chat) via hosts file entries.",
        "pl": "Blokuje wybrane serwisy i platformy (np. media społecznościowe, treści dla dorosłych, "
              "gry, torrenty, aplikacje randkowe i losowe czaty wideo) poprzez wpisy w pliku hosts.",
        "fr": "Bloque les services et plateformes sélectionnés (réseaux sociaux, contenu adulte, jeux, "
              "torrents, applications de rencontre et chats vidéo aléatoires) via des entrées du fichier hosts.",
        "de": "Blockiert ausgewählte Dienste und Plattformen (z. B. soziale Medien, Erwachseneninhalte, "
              "Spiele, Torrents, Dating-Apps und Zufalls-Videochats) über Einträge in der Hosts-Datei.",
        "es": "Bloquea servicios y plataformas seleccionados (redes sociales, contenido para adultos, "
              "juegos, torrents, apps de citas y videochats aleatorios) mediante entradas en el archivo hosts.",
    },
    "par_categories_count": {"en": "{n} of {total} active",    "pl": "{n} z {total} aktywnych",       "fr": "{n} sur {total} actives", "de": '{n} von {total} aktiv', "es": '{n} de {total} activas'},
    "par_categories_expand":   {"en": "Expand",  "pl": "Rozwiń", "fr": "Développer", "de": 'Erweitern', "es": 'Expandir'},
    "priv_levels_group_title": {"en": "Privacy protection mode", "pl": "Tryb ochrony prywatności", "fr": "Mode de protection de la vie privée", "de": 'Datenschutzmodus', "es": 'Modo de protección de la privacidad'},
    "priv_levels_group_tooltip": {
        "en": "Four escalating protection levels disable Windows tasks and services responsible "
              "for telemetry. This is a different mechanism than blocking telemetry domains in "
              "the hosts file — it works at the system level, not the network level.",
        "pl": "Cztery rosnące poziomy ochrony wyłączają w systemie zadania i usługi Windows "
              "odpowiedzialne za telemetrię. To inny mechanizm niż blokada domen w pliku hosts — "
              "działa na poziomie samego systemu, nie sieci.",
        "fr": "Quatre niveaux de protection croissants désactivent les tâches et services Windows "
              "responsables de la télémétrie. C'est un mécanisme différent du blocage des "
              "domaines de télémétrie dans le fichier hosts — il agit au niveau du système, pas "
              "du réseau.",
        "de": "Vier ansteigende Schutzstufen deaktivieren die für die Telemetrie zuständigen "
              "Windows-Aufgaben und -Dienste. Das ist ein anderer Mechanismus als das Blockieren "
              "von Telemetrie-Domains in der Hosts-Datei — er wirkt auf Systemebene, nicht auf "
              "Netzwerkebene.",
        "es": "Cuatro niveles de protección crecientes desactivan las tareas y servicios de "
              "Windows responsables de la telemetría. Es un mecanismo distinto al bloqueo de "
              "dominios de telemetría en el archivo hosts — actúa a nivel del sistema, no de la "
              "red.",
    },
    "priv_levels_group_desc": {
        "en": "Four ready-made telemetry and tracking blocking presets.",
        "pl": "Cztery gotowe zestawy blokad telemetrii i śledzenia.",
        "fr": "Quatre préréglages prêts à l'emploi de blocage de la télémétrie et du pistage.",
        "de": 'Vier fertige Presets zum Blockieren von Telemetrie und Tracking.',
        "es": 'Cuatro conjuntos predefinidos de bloqueo de telemetría y seguimiento.',
    },
    "par_categories_collapse": {"en": "Collapse", "pl": "Zwiń",  "fr": "Réduire", "de": 'Einklappen', "es": 'Contraer'},
    "priv_title":           {"en": "🕵️ Privacy",                 "pl": "🕵️ Prywatność",                     "fr": "🕵️ Confidentialité", "de": '🕵️ Datenschutz', "es": '🕵️ Privacidad'},
    "priv_subheader":       {"en": "Control Windows telemetry protection and block telemetry domains at the system level (hosts file).",
                             "pl": "Zarządzaj ochroną przed telemetrią Windows oraz blokuj domeny telemetryczne na poziomie systemu (plik hosts).",
                             "fr": "Gérez la protection contre la télémétrie Windows et bloquez les domaines de télémétrie au niveau système (fichier hosts).",
                             "de": 'Verwalten Sie den Schutz vor Windows-Telemetrie und blockieren Sie Telemetrie-Domains auf Systemebene (Hosts-Datei).',
                             "es": 'Controla la protección contra la telemetría de Windows y bloquea dominios de telemetría a nivel del sistema (archivo hosts).',
                         },
    "priv_watchdog_checking": {"en": "Checking protection status…", "pl": "Sprawdzanie stanu ochrony…",        "fr": "Vérification de l'état de la protection…", "de": 'Schutzstatus wird geprüft…', "es": 'Comprobando el estado de la protección…'},
    "toolbar_watchdog_scanning": {"en": "Scanning…", "pl": "Skanowanie…", "fr": "Analyse…", "de": 'Scan läuft…', "es": 'Escaneando…'},
    "priv_op_working":       {"en": "Applying changes…",           "pl": "Wprowadzanie zmian…",                "fr": "Application des modifications…", "de": 'Änderungen werden angewendet…', "es": 'Aplicando cambios…'},
    "par_btn_close":        {"en": "Close",                       "pl": "Zamknij",                          "fr": "Fermer", "de": 'Schließen', "es": 'Cerrar'},
    "priv_restore_banner_title": {"en": "Before making changes", "pl": "Zanim wprowadzisz zmiany", "fr": "Avant de faire des changements", "de": 'Bevor Sie Änderungen vornehmen', "es": 'Antes de hacer cambios'},
    "priv_restore_banner_desc": {
        "en": "It's a good idea to create a Windows System Restore point first.",
        "pl": "Warto najpierw utworzyć punkt przywracania systemu Windows.",
        "fr": "Il est conseillé de créer d'abord un point de restauration Windows.",
    
        "de": 'Es ist ratsam, zuerst einen Windows-Systemwiederherstellungspunkt zu erstellen.',
        "es": 'Es una buena idea crear primero un punto de restauración del sistema Windows.',
    },
    "priv_restore_btn_create": {"en": "Create", "pl": "Utwórz", "fr": "Créer", "de": 'Erstellen', "es": 'Crear'},
    "priv_restore_btn_working": {"en": "Creating…", "pl": "Tworzenie…", "fr": "Création…", "de": 'Wird erstellt…', "es": 'Creando…'},
    "priv_restore_msg_created": {"en": "✔ Restore point created.", "pl": "✔ Punkt przywracania utworzony.", "fr": "✔ Point de restauration créé.", "de": '✔ Wiederherstellungspunkt erstellt.', "es": '✔ Punto de restauración creado.'},
    "priv_restore_msg_throttled": {
        "en": (
            "⚠ Windows already created a restore point recently and by default allows only "
            "one every 24 hours. You can still create one manually at any time from Windows' "
            "own System Protection window (System Properties → System Protection → Create)."
        ),
        "pl": (
            "⚠ Windows utworzył już niedawno punkt przywracania i domyślnie pozwala na jeden "
            "co 24 godziny. Możesz jednak w dowolnej chwili utworzyć go ręcznie z natywnego okna "
            "Windows (Właściwości systemu → Ochrona systemu → Utwórz)."
        ),
        "fr": (
            "⚠ Windows a déjà créé un point de restauration récemment et n'en autorise par défaut "
            "qu'un seul toutes les 24 heures. Vous pouvez toutefois en créer un manuellement à tout "
            "moment depuis la fenêtre native de Windows (Propriétés système → Protection du système → Créer)."
        ),
    
        "de": '⚠ Windows hat kürzlich bereits einen Wiederherstellungspunkt erstellt und lässt standardmäßig nur einen alle 24 Stunden zu. Sie können jederzeit manuell einen über das native Windows-Fenster für Systemschutz erstellen (Systemeigenschaften → Systemschutz → Erstellen).',
        "es": '⚠ Windows ya creó un punto de restauración recientemente y, de forma predeterminada, solo permite uno cada 24 horas. Aun así, puedes crear uno manualmente en cualquier momento desde la propia ventana de Protección del sistema de Windows (Propiedades del sistema → Protección del sistema → Crear).',
    },
    "priv_restore_msg_no_admin": {"en": "Administrator rights are required.", "pl": "Wymagane są uprawnienia administratora.", "fr": "Des droits administrateur sont requis.", "de": 'Administratorrechte sind erforderlich.', "es": 'Se requieren derechos de administrador.'},
    "priv_restore_remove_limit_hint": {
        "en": "Or remove this limit.",
        "pl": "Lub usuń to ograniczenie.",
        "fr": "Ou supprimez cette limite.",
    
        "de": 'Oder entfernen Sie dieses Limit.',
        "es": 'O elimina este límite.',
    },
    "priv_restore_remove_limit_link": {"en": "Remove", "pl": "Usuń", "fr": "Supprimer", "de": 'Entfernen', "es": 'Eliminar'},
    "priv_restore_remove_limit_working": {"en": "Removing…", "pl": "Usuwanie…", "fr": "Suppression…", "de": 'Wird entfernt…', "es": 'Eliminando…'},
    "priv_restore_remove_limit_tooltip": {
        "en": "Sets the Windows restore-point time limit (registry) to 0, so a new restore point can be created immediately instead of waiting up to 24 hours. This is a permanent system-wide change.",
        "pl": "Ustawia systemowy limit czasu między punktami przywracania (rejestr) na 0, dzięki czemu kolejny punkt można utworzyć od razu zamiast czekać do 24h. To trwała zmiana na poziomie systemu.",
        "fr": "Définit à 0 la limite de temps entre les points de restauration (registre), permettant d'en créer un nouveau immédiatement au lieu d'attendre jusqu'à 24h. Ceci est un changement système permanent.",
    
        "de": 'Setzt das Zeitlimit für Windows-Wiederherstellungspunkte (Registry) auf 0, sodass sofort ein neuer Wiederherstellungspunkt erstellt werden kann, anstatt bis zu 24 Stunden zu warten. Dies ist eine dauerhafte systemweite Änderung.',
        "es": 'Establece el límite de tiempo entre puntos de restauración de Windows (registro) en 0, de modo que se pueda crear un nuevo punto de restauración de inmediato en lugar de esperar hasta 24 horas. Este es un cambio permanente a nivel de todo el sistema.',
    },
    "priv_restore_limit_removed": {
        "en": "✔ Limit removed — you can create a restore point now.",
        "pl": "✔ Ograniczenie usunięte — możesz teraz utworzyć punkt przywracania.",
        "fr": "✔ Limite supprimée — vous pouvez maintenant créer un point de restauration.",
    
        "de": '✔ Limit entfernt — Sie können jetzt einen Wiederherstellungspunkt erstellen.',
        "es": '✔ Límite eliminado — ya puedes crear un punto de restauración.',
    },
    "priv_restore_limit_remove_error": {
        "en": "Couldn't remove the limit: {details}",
        "pl": "Nie udało się usunąć ograniczenia: {details}",
        "fr": "Impossible de supprimer la limite : {details}",
    
        "de": 'Das Limit konnte nicht entfernt werden: {details}',
        "es": 'No se pudo eliminar el límite: {details}',
    },

    "priv_rstrui_lock_title": {
        "en": "Block System Restore tool",
        "pl": "Zablokuj narzędzie Przywracanie systemu",
        "fr": "Bloquer l'outil de restauration du système",
        "de": 'Systemwiederherstellungs-Tool blockieren',
        "es": 'Bloquear la herramienta de restauración del sistema',
    },
    "priv_rstrui_lock_desc": {
        "en": "Prevents the Windows System Restore wizard from starting.",
        "pl": "Uniemożliwia uruchomienie kreatora Przywracania systemu Windows.",
        "fr": "Empêche le démarrage de l'assistant de restauration du système Windows.",
        "de": 'Verhindert, dass der Windows-Systemwiederherstellungsassistent startet.',
        "es": 'Impide que se inicie el asistente de restauración del sistema de Windows.',
    },
    "priv_rstrui_lock_tooltip": {
        "en": (
            "Blocks only the System Restore window — restore points are still created "
            "automatically, and you can still make one yourself (the \"Create restore point\" "
            "button above still works even while blocked).\n\n"
            "This closes a way to bypass parental controls: without this block, an unauthorized "
            "person could open System Restore and revert the whole system to before the blocks "
            "were set up."
        ),
        "pl": (
            "Blokuje tylko okno „Przywracanie systemu” — punkty przywracania nadal są tworzone "
            "automatycznie i nadal możesz je tworzyć ręcznie (przycisk „Utwórz punkt przywracania” "
            "powyżej działa mimo włączonej blokady).\n\n"
            "Dzięki temu zamykasz sposób na obejście ochrony rodzicielskiej — bez tej blokady "
            "osoba nieupoważniona mogłaby użyć Przywracania systemu, żeby cofnąć cały system do "
            "stanu sprzed wprowadzenia blokad."
        ),
        "fr": (
            "Bloque uniquement la fenêtre « Restauration du système » — les points de "
            "restauration continuent d'être créés automatiquement, et vous pouvez toujours en "
            "créer un vous-même (le bouton « Créer un point de restauration » ci-dessus "
            "fonctionne toujours).\n\n"
            "Cela ferme un moyen de contourner le contrôle parental : sans ce blocage, une "
            "personne non autorisée pourrait restaurer tout le système à son état antérieur aux "
            "blocages."
        ),
        "de": (
            "Blockiert nur das Fenster „Systemwiederherstellung“ — Wiederherstellungspunkte "
            "werden weiterhin automatisch erstellt, und Sie können auch selbst einen erstellen "
            "(die Schaltfläche „Wiederherstellungspunkt erstellen“ oben funktioniert weiterhin).\n\n"
            "Das schließt eine Möglichkeit, die Kindersicherung zu umgehen: ohne diese Blockierung "
            "könnte eine unbefugte Person das System auf den Zustand vor den Blockierungen "
            "zurücksetzen."
        ),
        "es": (
            "Bloquea solo la ventana de «Restauración del sistema» — los puntos de restauración "
            "se siguen creando automáticamente, y tú también puedes crear uno (el botón «Crear "
            "punto de restauración» de arriba sigue funcionando).\n\n"
            "Esto cierra una forma de eludir el control parental: sin este bloqueo, una persona "
            "no autorizada podría restaurar todo el sistema a un estado anterior a los bloqueos."
        ),
    },
    "priv_rstrui_lock_status_locked": {"en": "Blocked", "pl": "Zablokowane", "fr": "Bloqué", "de": 'Blockiert', "es": 'Bloqueado'},
    "priv_rstrui_lock_status_unlocked": {"en": "Not blocked", "pl": "Niezablokowane", "fr": "Non bloqué", "de": 'Nicht blockiert', "es": 'No bloqueado'},
    "priv_rstrui_lock_btn_enable": {"en": "Block", "pl": "Zablokuj", "fr": "Bloquer", "de": 'Blockieren', "es": 'Bloquear'},
    "priv_rstrui_lock_btn_disable": {"en": "Unblock", "pl": "Odblokuj", "fr": "Débloquer", "de": 'Freigeben', "es": 'Desbloquear'},
    "priv_rstrui_lock_on_ok": {"en": "System Restore tool is now blocked.", "pl": "Narzędzie Przywracanie systemu jest teraz zablokowane.", "fr": "L'outil de restauration du système est maintenant bloqué.", "de": 'Das Systemwiederherstellungs-Tool ist jetzt blockiert.', "es": 'La herramienta de restauración del sistema está bloqueada.'},
    "priv_rstrui_lock_off_ok": {"en": "System Restore tool is unblocked.", "pl": "Narzędzie Przywracanie systemu jest odblokowane.", "fr": "L'outil de restauration du système est débloqué.", "de": 'Das Systemwiederherstellungs-Tool ist freigegeben.', "es": 'La herramienta de restauración del sistema está desbloqueada.'},
    "priv_rstrui_lock_on_fail": {"en": "Couldn't block the System Restore tool.", "pl": "Nie udało się zablokować narzędzia Przywracanie systemu.", "fr": "Impossible de bloquer l'outil de restauration du système.", "de": 'Das Systemwiederherstellungs-Tool konnte nicht blockiert werden.', "es": 'No se pudo bloquear la herramienta de restauración del sistema.'},
    "priv_rstrui_lock_off_fail": {"en": "Couldn't unblock the System Restore tool.", "pl": "Nie udało się odblokować narzędzia Przywracanie systemu.", "fr": "Impossible de débloquer l'outil de restauration du système.", "de": 'Das Systemwiederherstellungs-Tool konnte nicht freigegeben werden.', "es": 'No se pudo desbloquear la herramienta de restauración del sistema.'},
    "priv_rstrui_lock_err_no_admin": {"en": "Administrator rights are required.", "pl": "Wymagane są uprawnienia administratora.", "fr": "Des droits administrateur sont requis.", "de": 'Administratorrechte sind erforderlich.', "es": 'Se requieren derechos de administrador.'},

    "hosts_lock_title": {"en": "Hosts file lock", "pl": "Blokada pliku hosts", "fr": "Verrouillage du fichier hosts", "de": 'Hosts-Datei sperren', "es": 'Bloqueo del archivo hosts'},
    "hosts_lock_desc": {
        "en": "Blocks standard programs from modifying or deleting the hosts file.",
        "pl": "Blokuje standardowym programom możliwość modyfikacji lub usunięcia pliku hosts.",
        "fr": "Empêche les programmes standards de modifier ou supprimer le fichier hosts.",
        "de": 'Verhindert, dass Standardprogramme die Hosts-Datei ändern oder löschen.',
        "es": 'Impide que los programas estándar modifiquen o eliminen el archivo hosts.',
    },
    "hosts_lock_tooltip": {
        "en": "Locking significantly raises protection against malware and prevents changes to hosts file entries. Unlock it if a trusted program requires it.",
        "pl": "Blokada znacząco podnosi ochronę przed malware oraz uniemożliwia zmianę wpisów w pliku hosts. Odblokuj, jeśli wymaga tego jakiś zaufany program.",
        "fr": "Le verrouillage renforce considérablement la protection contre les malwares et empêche toute modification des entrées du fichier hosts. Déverrouillez-le si un programme de confiance l'exige.",
        "de": 'Die Sperre erhöht den Schutz vor Malware erheblich und verhindert Änderungen an den Einträgen der Hosts-Datei. Entsperren Sie sie, wenn ein vertrauenswürdiges Programm dies erfordert.',
        "es": 'El bloqueo aumenta considerablemente la protección frente a malware e impide cambios en las entradas del archivo hosts. Desbloquéalo si algún programa de confianza lo requiere.',
    },
    "hosts_lock_status_locked": {"en": "Status: locked", "pl": "Status: zablokowany", "fr": "État : verrouillé", "de": 'Status: gesperrt', "es": 'Estado: bloqueado'},
    "hosts_lock_status_unlocked": {"en": "Status: not locked", "pl": "Status: niezablokowany", "fr": "État : non verrouillé", "de": 'Status: nicht gesperrt', "es": 'Estado: no bloqueado'},
    "hosts_lock_btn_enable": {"en": "Lock", "pl": "Zablokuj", "fr": "Verrouiller", "de": 'Sperren', "es": 'Bloquear'},
    "hosts_lock_btn_disable": {"en": "Unlock", "pl": "Odblokuj", "fr": "Déverrouiller", "de": 'Entsperren', "es": 'Desbloquear'},
    "hosts_lock_on_ok": {"en": "Hosts file is now locked.", "pl": "Plik hosts został zablokowany.", "fr": "Le fichier hosts est maintenant verrouillé.", "de": 'Die Hosts-Datei ist jetzt gesperrt.', "es": 'El archivo hosts ahora está bloqueado.'},
    "hosts_lock_off_ok": {"en": "Hosts file is now unlocked.", "pl": "Plik hosts został odblokowany.", "fr": "Le fichier hosts est maintenant déverrouillé.", "de": 'Die Hosts-Datei ist jetzt entsperrt.', "es": 'El archivo hosts ahora está desbloqueado.'},
    "hosts_lock_on_fail": {"en": "Failed to lock the hosts file.", "pl": "Nie udało się zablokować pliku hosts.", "fr": "Échec du verrouillage du fichier hosts.", "de": 'Sperren der Hosts-Datei fehlgeschlagen.', "es": 'No se pudo bloquear el archivo hosts.'},
    "hosts_lock_off_fail": {"en": "Failed to unlock the hosts file.", "pl": "Nie udało się odblokować pliku hosts.", "fr": "Échec du déverrouillage du fichier hosts.", "de": 'Entsperren der Hosts-Datei fehlgeschlagen.', "es": 'No se pudo desbloquear el archivo hosts.'},
    "hosts_lock_drift_regressed": {
        "en": "⚠ The lock was removed outside the app.",
        "pl": "⚠ Blokada została zdjęta poza aplikacją.",
        "fr": "⚠ Le verrou a été supprimé en dehors de l'application.",
        "de": '⚠ Die Sperre wurde außerhalb der App entfernt.',
        "es": '⚠ El bloqueo se eliminó fuera de la aplicación.',
    },
    "hosts_lock_drift_restored": {
        "en": "Lock detected on disk — status synced.",
        "pl": "Wykryto blokadę na dysku — status zsynchronizowany.",
        "fr": "Verrou détecté sur le disque — état synchronisé.",
        "de": 'Sperre auf der Festplatte erkannt — Status synchronisiert.',
        "es": 'Bloqueo detectado en el disco — estado sincronizado.',
    },
    "hosts_lock_watchdog_title": {
        "en": "Hosts file protection changed",
        "pl": "Zmiana ochrony pliku hosts",
        "fr": "Protection du fichier hosts modifiée",
        "de": "Schutz der Hosts-Datei geändert",
        "es": "La protección del archivo hosts ha cambiado",
    },
    "appblock_title": {
        "en": "App blocking", "pl": "Blokada aplikacji",
        "fr": "Blocage d'applications", "de": "App-Sperre",
        "es": "Bloqueo de aplicaciones",
    },
    "appblock_desc": {
        "en": "Blocks selected applications from launching (e.g. games, VPN clients).",
        "pl": "Blokuje uruchomienie wybranych aplikacji (np. gry, klienty VPN).",
        "fr": "Bloque le lancement des applications sélectionnées (jeux, clients VPN...).",
        "de": "Blockiert den Start ausgewählter Anwendungen (z. B. Spiele, VPN-Clients).",
        "es": "Bloquea el inicio de las aplicaciones seleccionadas (juegos, clientes VPN...).",
    },
    "appblock_tooltip": {
        "en": (
            "Blocking combines two Windows mechanisms: it prevents the program or game from "
            "launching by file name (IFEO) and protects the file itself from being renamed, "
            "deleted or overwritten (ACL).\n\n"
            "Block known VPN apps — blocks the most common VPN apps with one click, to reduce "
            "the risk of bypassing the app's other protections."
        ),
        "pl": (
            "Blokada łączy dwa mechanizmy Windows: uniemożliwia uruchomienie programu lub gry "
            "(IFEO) oraz chroni sam plik przed zmianą nazwy, usunięciem czy nadpisaniem (ACL).\n\n"
            "Zablokuj popularne VPN — jednym kliknięciem blokuje najczęściej używane aplikacje "
            "VPN, w celu zmniejszenia ryzyka obejścia zabezpieczeń oferowanych w programie."
        ),
        "fr": (
            "Le blocage combine deux mécanismes Windows : il empêche le lancement du programme "
            "ou du jeu par nom de fichier (IFEO) et protège le fichier lui-même contre le "
            "renommage, la suppression ou l'écrasement (ACL).\n\n"
            "Bloquer les VPN connus — bloque en un clic les applications VPN les plus courantes, "
            "pour réduire le risque de contournement des autres protections du programme."
        ),
        "de": (
            "Die Sperre kombiniert zwei Windows-Mechanismen: Sie verhindert den Start des "
            "Programms oder Spiels anhand des Dateinamens (IFEO) und schützt die Datei selbst "
            "vor Umbenennung, Löschung oder Überschreibung (ACL).\n\n"
            "Bekannte VPN-Apps sperren — blockiert mit einem Klick die gängigsten VPN-Apps, um "
            "das Risiko einer Umgehung der übrigen Schutzfunktionen zu verringern."
        ),
        "es": (
            "El bloqueo combina dos mecanismos de Windows: impide que el programa o juego se "
            "inicie por nombre de archivo (IFEO) y protege el propio archivo frente a cambios de "
            "nombre, eliminación o sobrescritura (ACL).\n\n"
            "Bloquear VPN conocidas — bloquea con un clic las aplicaciones VPN más habituales, "
            "para reducir el riesgo de saltarse el resto de las protecciones del programa."
        ),
    },
    "appblock_search_loading": {
        "en": "Loading program list…", "pl": "Ładowanie listy programów…",
        "fr": "Chargement de la liste des programmes…", "de": "Programmliste wird geladen…",
        "es": "Cargando lista de programas…",
    },
    "appblock_search_placeholder": {
        "en": "Search installed program…", "pl": "Szukaj zainstalowanego programu…",
        "fr": "Rechercher un programme installé…", "de": "Installiertes Programm suchen…",
        "es": "Buscar programa instalado…",
    },
    "appblock_search_hint": {
        "en": "Results come from the list of programs installed via Windows (Control Panel / Settings). "
              "Portable .exe files without an installer won't show up here — use \"Browse\" for those instead.",
        "pl": "Wyniki pochodzą z listy programów zainstalowanych przez Windows (Panel sterowania / Ustawienia). "
              "Programy przenośne (.exe bez instalatora) się tu nie pojawią — dla nich użyj „Przeglądaj”.",
        "fr": "Les résultats proviennent de la liste des programmes installés via Windows (Panneau de configuration / "
              "Paramètres). Les .exe portables sans installateur n'apparaissent pas ici — utilisez « Parcourir » pour ceux-ci.",
        "de": "Die Ergebnisse stammen aus der Liste der über Windows installierten Programme (Systemsteuerung/"
              "Einstellungen). Portable .exe-Dateien ohne Installer erscheinen hier nicht — verwenden Sie dafür „Durchsuchen“.",
        "es": "Los resultados provienen de la lista de programas instalados mediante Windows (Panel de control/"
              "Configuración). Los .exe portátiles sin instalador no aparecerán aquí; para esos use «Examinar».",
    },
    "appblock_btn_block_vpn": {
        "en": "Block known VPN apps", "pl": "Zablokuj popularne VPN",
        "fr": "Bloquer les VPN connus", "de": "Bekannte VPN-Apps sperren",
        "es": "Bloquear VPN conocidas",
    },
    "appblock_btn_unblock_vpn": {
        "en": "Unblock known VPN apps", "pl": "Odblokuj popularne VPN",
        "fr": "Débloquer les VPN connus", "de": "Bekannte VPN-Apps entsperren",
        "es": "Desbloquear VPN conocidas",
    },
    "appblock_btn_browse": {
        "en": "Browse & lock file...", "pl": "Przeglądaj i zablokuj plik...",
        "fr": "Parcourir et verrouiller...", "de": "Durchsuchen & Datei sperren...",
        "es": "Examinar y bloquear archivo...",
    },
    "appblock_btn_force_unlock": {
        "en": "Unlock a specific file...", "pl": "Odblokuj wskazany plik...",
        "fr": "Débloquer un fichier...", "de": "Datei entsperren...",
        "es": "Desbloquear un archivo...",
    },
    "appblock_tooltip_force_unlock": {
        "en": "Emergency full unlock of the selected file — useful if the configuration "
              "file was deleted from disk and the app stayed blocked anyway.",
        "pl": "Awaryjne, pełne odblokowanie wskazanego pliku — przydatne, gdy plik "
              "konfiguracyjny został skasowany z dysku, a aplikacja mimo to pozostała "
              "zablokowana.",
        "fr": "Déblocage complet et d'urgence du fichier sélectionné — utile si le fichier "
              "de configuration a été supprimé du disque et que l'appli est restée bloquée "
              "malgré tout.",
        "de": "Vollständige Notfall-Entsperrung der ausgewählten Datei — nützlich, wenn die "
              "Konfigurationsdatei von der Festplatte gelöscht wurde und die App trotzdem "
              "gesperrt blieb.",
        "es": "Desbloqueo completo de emergencia del archivo seleccionado — útil si el "
              "archivo de configuración fue eliminado del disco y la app siguió bloqueada "
              "de todos modos.",
    },
    "appblock_force_unlock_ok": {
        "en": "File fully unlocked: {path}", "pl": "Plik został całkowicie odblokowany: {path}",
        "fr": "Fichier entièrement débloqué : {path}", "de": "Datei vollständig entsperrt: {path}",
        "es": "Archivo completamente desbloqueado: {path}",
    },
    "appblock_row_toggle_off_tooltip": {
        "en": "Blocking is active — click to pause it (the app stays on the list).",
        "pl": "Blokada jest aktywna — kliknij, aby ją wyłączyć (wpis zostanie na liście).",
        "fr": "Le blocage est actif — cliquez pour le désactiver (l'appli reste dans la liste).",
        "de": "Sperre ist aktiv — zum Pausieren klicken (App bleibt in der Liste).",
        "es": "El bloqueo está activo — haz clic para pausarlo (la app permanece en la lista).",
    },
    "appblock_row_toggle_on_tooltip": {
        "en": "Blocking is paused — click to turn it back on.",
        "pl": "Blokada jest wyłączona — kliknij, aby ją ponownie włączyć.",
        "fr": "Le blocage est en pause — cliquez pour le réactiver.",
        "de": "Sperre ist pausiert — zum erneuten Aktivieren klicken.",
        "es": "El bloqueo está pausado — haz clic para reactivarlo.",
    },
    "appblock_row_remove_tooltip": {
        "en": "Remove from the list (permanently clears the block).",
        "pl": "Usuń z listy (na stałe zdejmuje blokadę).",
        "fr": "Retirer de la liste (supprime le blocage définitivement).",
        "de": "Aus der Liste entfernen (Sperre wird dauerhaft aufgehoben).",
        "es": "Eliminar de la lista (quita el bloqueo de forma permanente).",
    },
    "appblock_section_custom": {
        "en": "Manually blocked", "pl": "Zablokowane ręcznie",
        "fr": "Bloquées manuellement", "de": "Manuell gesperrt",
        "es": "Bloqueadas manualmente",
    },
    "appblock_section_vpn": {
        "en": "Blocked VPN apps", "pl": "Zablokowane VPN",
        "fr": "Applications VPN bloquées", "de": "Gesperrte VPN-Apps",
        "es": "Aplicaciones VPN bloqueadas",
    },
    "appblock_empty": {
        "en": "No applications blocked yet.", "pl": "Brak zablokowanych aplikacji.",
        "fr": "Aucune application bloquée.", "de": "Keine Anwendungen gesperrt.",
        "es": "No hay aplicaciones bloqueadas.",
    },
    "appblock_err_no_admin": {
        "en": "Administrator rights are required to block or unblock applications.",
        "pl": "Blokowanie/odblokowywanie aplikacji wymaga uprawnień administratora.",
        "fr": "Des droits administrateur sont requis pour bloquer/débloquer des applications.",
        "de": "Zum Sperren/Entsperren von Anwendungen sind Administratorrechte erforderlich.",
        "es": "Se requieren derechos de administrador para bloquear o desbloquear aplicaciones.",
    },
    "appblock_err_generic": {
        "en": "The operation failed. Please try again.",
        "pl": "Operacja się nie powiodła. Spróbuj ponownie.",
        "fr": "L'opération a échoué. Veuillez réessayer.",
        "de": "Der Vorgang ist fehlgeschlagen. Bitte erneut versuchen.",
        "es": "La operación falló. Inténtalo de nuevo.",
    },
    "appblock_err_protected": {
        "en": "This is a core Windows system file — Windows Defender actively "
              "protects it from this kind of change, so it can't be blocked this way. "
              "This feature is meant for third-party apps (games, VPN clients, etc.), not system tools.",
        "pl": "To kluczowy plik systemowy Windows — Windows Defender aktywnie chroni go "
              "przed tego typu zmianą, więc nie da się go tak zablokować. Ta funkcja jest "
              "przeznaczona do blokowania aplikacji zewnętrznych (gier, klientów VPN itp.), nie narzędzi systemowych.",
        "fr": "Il s'agit d'un fichier système Windows essentiel — Windows Defender le protège "
              "activement contre ce type de modification. Cette fonction vise les applications "
              "tierces (jeux, clients VPN...), pas les outils système.",
        "de": "Dies ist eine wichtige Windows-Systemdatei — Windows Defender schützt sie aktiv "
              "vor dieser Art von Änderung. Diese Funktion ist für Drittanbieter-Apps (Spiele, "
              "VPN-Clients usw.) gedacht, nicht für Systemwerkzeuge.",
        "es": "Este es un archivo esencial del sistema Windows — Windows Defender lo protege "
              "activamente de este tipo de cambio. Esta función está pensada para aplicaciones "
              "de terceros (juegos, clientes VPN, etc.), no para herramientas del sistema.",
    },
    "appblock_err_self": {
        "en": "You can't block HOTS Hosts itself — since blocking works by "
              "file name, that would prevent the program from starting again "
              "the next time you (or it) try to launch it.",
        "pl": "Nie można zablokować samego programu HOTS Hosts — blokada działa "
              "po nazwie pliku, więc uniemożliwiłaby ponowne uruchomienie "
              "programu przy następnej próbie.",
        "fr": "Impossible de bloquer HOTS Hosts lui-même — le blocage agissant "
              "par nom de fichier, cela empêcherait le programme de redémarrer "
              "la prochaine fois.",
        "de": "HOTS Hosts kann sich nicht selbst sperren — da die Sperre über "
              "den Dateinamen erfolgt, würde dies den nächsten Start des "
              "Programms verhindern.",
        "es": "No puedes bloquear HOTS Hosts a sí mismo — como el bloqueo actúa "
              "por nombre de archivo, esto impediría que el programa vuelva a "
              "iniciarse la próxima vez.",
    },
    "appblock_vpn_bundle_ok": {
        "en": "Known VPN applications blocked: {n}.",
        "pl": "Zablokowanych popularnych aplikacji VPN: {n}.",
        "fr": "Applications VPN connues bloquées : {n}.",
        "de": "Gesperrte bekannte VPN-Anwendungen: {n}.",
        "es": "Aplicaciones VPN conocidas bloqueadas: {n}.",
    },
    "appblock_vpn_bundle_removed_ok": {
        "en": "Known VPN applications unblocked: {n}.",
        "pl": "Odblokowanych popularnych aplikacji VPN: {n}.",
        "fr": "Applications VPN connues débloquées : {n}.",
        "de": "Entsperrte bekannte VPN-Anwendungen: {n}.",
        "es": "Aplicaciones VPN conocidas desbloqueadas: {n}.",
    },
    "appblock_vpn_bundle_partial": {
        "en": "Failed for: {failed}", "pl": "Nie powiodło się dla: {failed}",
        "fr": "Échec pour : {failed}", "de": "Fehlgeschlagen für: {failed}",
        "es": "Fallo en: {failed}",
    },
    "appblock_watchdog_title": {
        "en": "Blocked app protection changed",
        "pl": "Zmiana ochrony zablokowanej aplikacji",
        "fr": "Protection d'application bloquée modifiée",
        "de": "Schutz für gesperrte App geändert",
        "es": "La protección de la app bloqueada ha cambiado",
    },
    "appblock_drift_regressed": {
        "en": "One or more blocked apps were unblocked outside HOTS Hosts: {apps}",
        "pl": "Co najmniej jedna zablokowana aplikacja została odblokowana poza HOTS Hosts: {apps}",
        "fr": "Une ou plusieurs applications bloquées ont été débloquées en dehors de HOTS Hosts : {apps}",
        "de": "Eine oder mehrere gesperrte Apps wurden außerhalb von HOTS Hosts entsperrt: {apps}",
        "es": "Una o más aplicaciones bloqueadas se desbloquearon fuera de HOTS Hosts: {apps}",
    },
    "doh_title": {
        "en": "DoH blocking in browsers",
        "pl": "Blokada DoH w przeglądarkach",
        "fr": "Blocage DoH dans les navigateurs",
        "de": "DoH-Blockierung in Browsern",
        "es": "Bloqueo de DoH en navegadores",
    },
    "doh_desc": {
        "en": "Disables DNS-over-HTTPS in installed browsers.",
        "pl": "Wyłącza DNS-over-HTTPS w zainstalowanych przeglądarkach.",
        "fr": "Désactive le DNS-over-HTTPS dans les navigateurs installés.",
        "de": "Deaktiviert DNS-over-HTTPS in installierten Browsern.",
        "es": "Desactiva DNS-over-HTTPS en los navegadores instalados.",
    },
    "doh_tooltip": {
        "en": "Blocks DNS-over-HTTPS in browsers so they can't bypass the hosts file. "
              "Restart the browser after blocking.",
        "pl": "Blokuje DNS-over-HTTPS w przeglądarkach, żeby nie omijały pliku hosts. "
              "Po zablokowaniu zrestartuj przeglądarkę.",
        "fr": "Bloque le DNS-over-HTTPS dans les navigateurs pour qu'ils ne contournent pas "
              "le fichier hosts. Redémarrez le navigateur après le blocage.",
        "de": "Blockiert DNS-over-HTTPS in Browsern, damit sie die Hosts-Datei nicht umgehen. "
              "Starten Sie den Browser nach der Blockierung neu.",
        "es": "Bloquea DNS-over-HTTPS en los navegadores para que no eludan el archivo hosts. "
              "Reinicia el navegador después de bloquear.",
    },
    "doh_row_status_blocked": {
        "en": "Blocked", "pl": "Zablokowane", "fr": "Bloqué", "de": "Blockiert", "es": "Bloqueado",
    },
    "doh_row_status_unblocked": {
        "en": "Not blocked", "pl": "Niezablokowane", "fr": "Non bloqué", "de": "Nicht blockiert", "es": "No bloqueado",
    },
    "doh_row_status_not_installed": {
        "en": "Not installed", "pl": "Niezainstalowana", "fr": "Non installé", "de": "Nicht installiert", "es": "No instalado",
    },
    "doh_row_toggle_off_tooltip": {
        "en": "DoH blocking is active — click to turn it off.",
        "pl": "Blokada DoH jest aktywna — kliknij, aby ją wyłączyć.",
        "fr": "Le blocage DoH est actif — cliquez pour le désactiver.",
        "de": "DoH-Blockierung ist aktiv — zum Deaktivieren klicken.",
        "es": "El bloqueo de DoH está activo — haz clic para desactivarlo.",
    },
    "doh_row_toggle_on_tooltip": {
        "en": "DoH blocking is off — click to turn it on.",
        "pl": "Blokada DoH jest wyłączona — kliknij, aby ją włączyć.",
        "fr": "Le blocage DoH est désactivé — cliquez pour l'activer.",
        "de": "DoH-Blockierung ist deaktiviert — zum Aktivieren klicken.",
        "es": "El bloqueo de DoH está desactivado — haz clic para activarlo.",
    },
    "doh_row_toggle_not_installed_tooltip": {
        "en": "Browser not detected on this computer.",
        "pl": "Przeglądarka nie została wykryta na tym komputerze.",
        "fr": "Navigateur non détecté sur cet ordinateur.",
        "de": "Browser auf diesem Computer nicht gefunden.",
        "es": "No se detectó el navegador en este equipo.",
    },
    "doh_err_no_admin": {
        "en": "Administrator rights are required to change browser DoH policy.",
        "pl": "Zmiana zasady DoH w przeglądarce wymaga uprawnień administratora.",
        "fr": "Des droits administrateur sont requis pour modifier la stratégie DoH du navigateur.",
        "de": "Zum Ändern der Browser-DoH-Richtlinie sind Administratorrechte erforderlich.",
        "es": "Se requieren derechos de administrador para cambiar la política de DoH del navegador.",
    },
    "doh_err_generic": {
        "en": "The operation failed. Please try again.",
        "pl": "Operacja się nie powiodła. Spróbuj ponownie.",
        "fr": "L'opération a échoué. Veuillez réessayer.",
        "de": "Der Vorgang ist fehlgeschlagen. Bitte erneut versuchen.",
        "es": "La operación falló. Inténtalo de nuevo.",
    },
    "doh_watchdog_title": {
        "en": "DoH blocking protection changed",
        "pl": "Zmiana ochrony blokady DoH",
        "fr": "Protection du blocage DoH modifiée",
        "de": "Schutz für DoH-Blockierung geändert",
        "es": "La protección del bloqueo de DoH ha cambiado",
    },
    "doh_drift_regressed": {
        "en": "DoH blocking was turned off outside HOTS Hosts in: {browsers}",
        "pl": "Blokada DoH została wyłączona poza HOTS Hosts w: {browsers}",
        "fr": "Le blocage DoH a été désactivé en dehors de HOTS Hosts dans : {browsers}",
        "de": "Die DoH-Blockierung wurde außerhalb von HOTS Hosts deaktiviert in: {browsers}",
        "es": "El bloqueo de DoH se desactivó fuera de HOTS Hosts en: {browsers}",
    },

    "hosts_lock_err_no_file": {"en": "The hosts file does not exist.", "pl": "Plik hosts nie istnieje.", "fr": "Le fichier hosts n'existe pas.", "de": 'Die Hosts-Datei existiert nicht.', "es": 'El archivo hosts no existe.'},
    "hosts_lock_blocks_write": {
        "en": "The hosts file is locked. Unlock it on the Parental Protection page before editing.",
        "pl": "Plik hosts jest zablokowany. Odblokuj go na stronie Ochrona rodzicielska przed edycją.",
        "fr": "Le fichier hosts est verrouillé. Déverrouillez-le dans Protection parentale avant modification.",
        "de": 'Die Hosts-Datei ist gesperrt. Entsperren Sie sie auf der Seite Kinderschutz vor der Bearbeitung.',
        "es": 'El archivo hosts está bloqueado. Desbloquéalo en la página Protección parental antes de editar.',
    },

    "priv_nav_locked_tooltip": {
        "en": "Navigation is locked while a Privacy operation is in progress.",
        "pl": "Nawigacja jest zablokowana na czas trwania operacji w zakładce Prywatność.",
        "fr": "La navigation est verrouillée pendant qu'une opération de confidentialité est en cours.",
    
        "de": 'Die Navigation ist gesperrt, während ein Datenschutzvorgang läuft.',
        "es": 'La navegación está bloqueada mientras hay una operación de privacidad en curso.',
    },
    "priv_restore_msg_error": {"en": "Couldn't create a restore point: {details}", "pl": "Nie udało się utworzyć punktu przywracania: {details}", "fr": "Impossible de créer un point de restauration : {details}", "de": 'Wiederherstellungspunkt konnte nicht erstellt werden: {details}', "es": 'No se pudo crear un punto de restauración: {details}'},
    "priv_restore_point_description": {
        "en": "HOTS Hosts - before Privacy changes",
        "pl": "HOTS Hosts - przed zmianami w Prywatności",
        "fr": "HOTS Hosts - avant modifications de confidentialité",
    
        "de": 'HOTS Hosts - vor Datenschutzänderungen',
        "es": 'HOTS Hosts - antes de cambios de privacidad',
    },
    "par_blocklists_path":  {"en": "Block lists: {path}",         "pl": "Pliki blokad: {path}",             "fr": "Listes de blocage: {path}", "de": 'Blocklisten: {path}', "es": 'Listas de bloqueo: {path}'},
    "par_file_ok":          {"en": "✔  {file}",                   "pl": "✔  {file}",                        "fr": "✔  {file}", "de": '✔  {file}', "es": '✔  {file}'},
    "par_file_missing":     {"en": "✘  Missing file: {file}",     "pl": "✘  Brak pliku: {file}",            "fr": "✘  Fichier manquant: {file}", "de": '✘  Fehlende Datei: {file}', "es": '✘  Archivo faltante: {file}'},
    "par_btn_disable":      {"en": "Disable",                     "pl": "Wyłącz",                           "fr": "Désactiver", "de": 'Deaktivieren', "es": 'Desactivar'},
    "par_btn_enable":       {"en": "Enable",                      "pl": "Włącz",                            "fr": "Activer", "de": 'Aktivieren', "es": 'Activar'},
    "par_btn_no_file":      {"en": "No file",                     "pl": "Brak pliku",                       "fr": "Fichier absent", "de": 'Keine Datei', "es": 'Sin archivo'},
    "par_err_no_file_title":{"en": "Missing block list",          "pl": "Brak pliku blokad",                "fr": "Liste de blocage manquante", "de": 'Blockliste fehlt', "es": 'Falta la lista de bloqueo'},
    "par_err_no_file_msg":  {"en": "File not found:\n{path}\n\nCreate the file {file} in the blocklists/ folder.",
                             "pl": "Nie znaleziono pliku:\n{path}\n\nUtwórz plik {file} w folderze blocklists/.",
                             "fr": "Fichier introuvable:\n{path}\n\nCréez le fichier {file} dans le dossier blocklists/.",
                             "de": 'Datei nicht gefunden:\n{path}\n\nErstellen Sie die Datei {file} im Ordner blocklists/.',
                             "es": 'Archivo no encontrado:\n{path}\n\nCrea el archivo {file} en la carpeta blocklists/.',
                         },
    "par_err_no_custom_file_msg": {"en": "The custom domain list is empty.\n\nClick \"Edit\", add domains and save - the file will be created automatically next to the hosts file.",
                             "pl": "Lista własnych domen jest pusta.\n\nKliknij „Edytuj”, dodaj domeny i zapisz - plik zostanie utworzony automatycznie obok pliku hosts.",
                             "fr": "La liste de domaines personnalisés est vide.\n\nCliquez sur « Modifier », ajoutez des domaines et enregistrez - le fichier sera créé automatiquement à côté du fichier hosts.",
                             "de": 'Die Liste eigener Domains ist leer.\n\nKlicken Sie auf „Bearbeiten“, fügen Sie Domains hinzu und speichern Sie - die Datei wird automatisch neben der hosts-Datei erstellt.',
                             "es": 'La lista de dominios personalizados está vacía.\n\nHaz clic en «Editar», añade dominios y guarda - el archivo se creará automáticamente junto al archivo hosts.',
                         },
    "par_dirty_warn_title": {"en": "Unsaved changes in the table",
                             "pl": "Niezapisane zmiany w tabeli",
                             "fr": "Modifications non enregistrées",
                             "de": 'Nicht gespeicherte Änderungen in der Tabelle',
                             "es": 'Cambios sin guardar en la tabla',
                         },
    "par_dirty_warn_msg":   {
        "en": (
            "You have unsaved changes in the main table. This action writes "
            "directly to the hosts file on disk and then reloads the table "
            "from disk — your unsaved changes (anything not yet saved with "
            "'Save') will be discarded, not written to the file.\n\n"
            "Continue and discard them, or go back and save first?"
        ),
        "pl": (
            "Masz niezapisane zmiany w głównej tabeli. Ta operacja zapisuje "
            "bezpośrednio do pliku hosts na dysku, a potem przeładowuje "
            "tabelę z dysku — Twoje niezapisane zmiany (wszystko, czego "
            "jeszcze nie zapisałeś/aś przyciskiem 'Zapisz') zostaną "
            "odrzucone, a nie zapisane do pliku.\n\n"
            "Kontynuować i je odrzucić, czy wrócić i najpierw zapisać?"
        ),
        "fr": (
            "Vous avez des modifications non enregistrées dans le tableau "
            "principal. Cette action écrit directement dans le fichier "
            "hosts sur le disque, puis recharge le tableau depuis le "
            "disque — vos modifications non enregistrées seront "
            "abandonnées, pas écrites dans le fichier.\n\n"
            "Continuer et les abandonner, ou revenir en arrière et "
            "enregistrer d'abord?"
        ),
    
        "de": 'Sie haben nicht gespeicherte Änderungen in der Haupttabelle. Diese Aktion schreibt direkt in die Hosts-Datei auf der Festplatte und lädt die Tabelle dann von der Festplatte neu — Ihre nicht gespeicherten Änderungen (alles, was noch nicht mit „Speichern" gespeichert wurde) werden verworfen, nicht in die Datei geschrieben.\n\nFortfahren und sie verwerfen, oder zurückgehen und zuerst speichern?',
        "es": "Tienes cambios sin guardar en la tabla principal. Esta acción escribe directamente en el archivo hosts del disco y luego recarga la tabla desde el disco — tus cambios sin guardar (todo lo que aún no se haya guardado con 'Guardar') se descartarán, no se escribirán en el archivo.\n\n¿Continuar y descartarlos, o volver atrás y guardar primero?",
    },
    "par_err_hosts_title":  {"en": "Error",                       "pl": "Błąd",                             "fr": "Erreur", "de": 'Fehler', "es": 'Error'},
    "par_err_hosts_msg":    {"en": "Could not modify the hosts file.\nCheck administrator permissions.",
                             "pl": "Nie udało się zmodyfikować pliku hosts.\nSprawdź uprawnienia administratora.",
                             "fr": "Impossible de modifier le fichier hosts.\nVérifiez les permissions administrateur.",
                             "de": 'Die Hosts-Datei konnte nicht geändert werden.\nÜberprüfen Sie die Administratorrechte.',
                             "es": 'No se pudo modificar el archivo hosts.\nComprueba los permisos de administrador.',
                         },
    "hosts_busy_msg":       {"en": "The hosts file is temporarily busy — Windows is still processing previous changes (DNS Client service).\nWait about a minute and try again. This is not a permissions problem.",
                             "pl": "Plik hosts jest chwilowo zajęty — Windows wciąż przetwarza poprzednie zmiany (usługa DNS Client).\nOdczekaj około minuty i spróbuj ponownie. To nie jest problem z uprawnieniami.",
                             "fr": "Le fichier hosts est temporairement occupé — Windows traite encore les changements précédents (service Client DNS).\nAttendez environ une minute puis réessayez. Ce n'est pas un problème de permissions.",
                             "de": 'Die Hosts-Datei ist vorübergehend belegt — Windows verarbeitet noch vorherige Änderungen (DNS-Client-Dienst).\nWarten Sie etwa eine Minute und versuchen Sie es erneut. Dies ist kein Berechtigungsproblem.',
                             "es": 'El archivo hosts está temporalmente ocupado — Windows aún está procesando cambios anteriores (servicio de cliente DNS).\nEspera aproximadamente un minuto y vuelve a intentarlo. No es un problema de permisos.',
                         },
    "par_success_title":    {"en": "Success",                     "pl": "Sukces",                           "fr": "Succès", "de": 'Erfolg', "es": 'Éxito'},
    "par_success_on":       {"en": "{label} has been activated!",  "pl": "{label} została aktywowana!",      "fr": "{label} a été activé!", "de": '{label} wurde aktiviert!', "es": '¡{label} ha sido activada!'},
    "par_success_off":      {"en": "{label} has been deactivated!", "pl": "{label} została dezaktywowana!",  "fr": "{label} a été désactivé!", "de": '{label} wurde deaktiviert!', "es": '¡{label} ha sido desactivada!'},
    "par_cat_adult":        {"en": "Block adult content sites",    "pl": "Blokada stron dla dorosłych",      "fr": "Bloquer sites pour adultes", "de": 'Inhalte für Erwachsene blockieren', "es": 'Bloquear sitios de contenido para adultos'},
    "par_cat_twitter":      {"en": "Block Twitter / X",           "pl": "Blokada Twitter / X",              "fr": "Bloquer Twitter / X", "de": 'Twitter / X blockieren', "es": 'Bloquear Twitter / X'},
    "par_cat_instagram":    {"en": "Block Instagram",             "pl": "Blokada Instagram",                "fr": "Bloquer Instagram", "de": 'Instagram blockieren', "es": 'Bloquear Instagram'},
    "par_cat_youtube":      {"en": "Block YouTube",               "pl": "Blokada YouTube",                  "fr": "Bloquer YouTube", "de": 'YouTube blockieren', "es": 'Bloquear YouTube'},
    "par_cat_facebook":     {"en": "Block Facebook",              "pl": "Blokada Facebook",                 "fr": "Bloquer Facebook", "de": 'Facebook blockieren', "es": 'Bloquear Facebook'},
    "par_cat_whatsapp":     {"en": "Block WhatsApp",              "pl": "Blokada WhatsApp",                 "fr": "Bloquer WhatsApp", "de": 'WhatsApp blockieren', "es": 'Bloquear WhatsApp'},
    "par_cat_tiktok":       {"en": "Block TikTok",                "pl": "Blokada TikTok",                   "fr": "Bloquer TikTok", "de": 'TikTok blockieren', "es": 'Bloquear TikTok'},
    "par_cat_twitch":       {"en": "Block Twitch",                "pl": "Blokada Twitch",                   "fr": "Bloquer Twitch", "de": 'Twitch blockieren', "es": 'Bloquear Twitch'},
    "par_cat_snapchat":     {"en": "Block Snapchat",              "pl": "Blokada Snapchat",                 "fr": "Bloquer Snapchat", "de": 'Snapchat blockieren', "es": 'Bloquear Snapchat'},
    "par_cat_dating":       {"en": "Block dating sites",          "pl": "Blokada serwisów randkowych",      "fr": "Bloquer sites de rencontre", "de": 'Dating-Seiten blockieren', "es": 'Bloquear sitios de citas'},
    "par_cat_random_chat":  {"en": "Block random video chat",     "pl": "Blokada losowego czatu wideo",     "fr": "Bloquer le chat vidéo aléatoire", "de": 'Zufälligen Video-Chat blockieren', "es": 'Bloquear chat de vídeo aleatorio'},
    "par_btn_working":       {"en": "Working…",                   "pl": "Przetwarzanie…",                   "fr": "Traitement…", "de": 'Wird verarbeitet…', "es": 'Procesando…'},
    "par_antispy_err_title": {"en": "Privacy Protection Error",
                             "pl": "Błąd ochrony prywatności",
                             "fr": "Erreur de protection de la confidentialité",
                             "de": 'Fehler beim Datenschutz',
                             "es": 'Error de protección de privacidad',
                         },
    "par_antispy_err_msg":  {"en": "Could not apply the selected protection level (services / registry / firewall / scheduled tasks).\nMake sure HOTS is running as Administrator.",
                             "pl": "Nie udało się zastosować wybranego poziomu ochrony (usługi / rejestr / zapora / zadania).\nUpewnij się, że HOTS jest uruchomiony jako Administrator.",
                             "fr": "Impossible d'appliquer le niveau de protection sélectionné (services / registre / pare-feu / tâches).\nAssurez-vous que HOTS est exécuté en tant qu'administrateur.",
                             "de": 'Die ausgewählte Schutzstufe konnte nicht angewendet werden (Dienste / Registry / Firewall / geplante Aufgaben).\nStellen Sie sicher, dass HOTS als Administrator ausgeführt wird.',
                             "es": 'No se pudo aplicar el nivel de protección seleccionado (servicios / registro / firewall / tareas programadas).\nAsegúrate de que HOTS se ejecute como administrador.',
                         },
    "par_cat_antispy":      {"en": "Windows AntiSpy",             "pl": "Windows AntiSpy",                  "fr": "Windows AntiSpy", "de": 'Windows AntiSpy', "es": 'Windows AntiSpy'},

    "par_antispy_basic_btn":    {"en": "Basic",        "pl": "Podstawowy",     "fr": "Basique", "de": 'Basis', "es": 'Básico'},
    "par_antispy_medium_btn":   {"en": "Medium",       "pl": "Średni",        "fr": "Moyen", "de": 'Mittel', "es": 'Medio'},
    "par_antispy_advanced_btn": {"en": "Advanced",     "pl": "Zaawansowany",   "fr": "Avancé", "de": 'Erweitert', "es": 'Avanzado'},
    "par_antispy_extra_btn":    {"en": "Privacy+",     "pl": "Prywatność+",    "fr": "Confidentialité+", "de": 'Datenschutz+', "es": 'Privacidad+'},
    "par_antispy_basic_label":    {"en": "Basic privacy protection",    "pl": "Podstawowa ochrona prywatności",    "fr": "Protection de la confidentialité basique", "de": 'Grundlegender Datenschutz', "es": 'Protección de privacidad básica'},
    "par_antispy_medium_label":   {"en": "Medium privacy protection",   "pl": "Średnia ochrona prywatności",       "fr": "Protection de la confidentialité moyenne", "de": 'Mittlerer Datenschutz', "es": 'Protección de privacidad media'},
    "par_antispy_advanced_label": {"en": "Advanced privacy protection", "pl": "Zaawansowana ochrona prywatności",  "fr": "Protection de la confidentialité avancée", "de": 'Erweiterter Datenschutz', "es": 'Protección de privacidad avanzada'},
    "par_antispy_extra_label":    {"en": "Privacy+ protection (location & personalization)", "pl": "Ochrona Prywatność+ (lokalizacja i personalizacja)", "fr": "Protection Confidentialité+ (localisation et personnalisation)", "de": 'Datenschutz+ (Standort & Personalisierung)', "es": 'Protección Privacidad+ (ubicación y personalización)'},
    "par_antispy_basic_tooltip":  {
        "en": (
            "Enable:\n"
            "Disables telemetry services (DiagTrack, dmwappushservice).\n"
            "Adds registry policies: AllowTelemetry = 0, AllowExperimentation = 0, "
            "DisableWindowsConsumerFeatures = 1, "
            "DisableTailoredExperiencesWithDiagnosticData = 1, DODownloadMode = 0, "
            "DisableAIDataAnalysis = 1 (blocks Windows Recall), "
            "DoNotShowFeedbackNotifications = 1, CEIPEnable = 0.\n"
            "Turns off Advertising ID, Bing web search in Start Menu search, "
            "and search box suggestions (per-user settings).\n\n"
            "Disable:\n"
            "Restores the exact state of these services and the registry "
            "that existed immediately before this level was activated."
        ),
        "pl": (
            "Włączenie:\n"
            "Wyłącza usługi telemetrii (DiagTrack, dmwappushservice).\n"
            "Dodaje wpisy w rejestrze: AllowTelemetry = 0, AllowExperimentation = 0, "
            "DisableWindowsConsumerFeatures = 1, "
            "DisableTailoredExperiencesWithDiagnosticData = 1, DODownloadMode = 0, "
            "DisableAIDataAnalysis = 1 (blokuje Windows Recall), "
            "DoNotShowFeedbackNotifications = 1, CEIPEnable = 0.\n"
            "Wyłącza identyfikator reklamowy, wyszukiwanie w sieci przez Bing "
            "w menu Start oraz sugestie w polu wyszukiwania (ustawienia per-użytkownik).\n\n"
            "Wyłączenie:\n"
            "Przywraca dokładny stan tych usług i rejestru sprzed aktywacji tego poziomu."
        ),
        "fr": (
            "Activation :\n"
            "Désactive les services de télémétrie (DiagTrack, dmwappushservice).\n"
            "Ajoute des stratégies de registre : AllowTelemetry = 0, "
            "AllowExperimentation = 0, DisableWindowsConsumerFeatures = 1, "
            "DisableTailoredExperiencesWithDiagnosticData = 1, DODownloadMode = 0, "
            "DisableAIDataAnalysis = 1 (bloque Windows Recall), "
            "DoNotShowFeedbackNotifications = 1, CEIPEnable = 0.\n"
            "Désactive l'ID publicitaire, la recherche web Bing dans le menu "
            "Démarrer et les suggestions de recherche (paramètres par utilisateur).\n\n"
            "Désactivation :\n"
            "Restaure l'état exact de ces services et du registre "
            "tel qu'il était avant l'activation de ce niveau."
        ),
    
        "de": 'Aktivierung:\nDeaktiviert Telemetriedienste (DiagTrack, dmwappushservice).\nFügt Registry-Richtlinien hinzu: AllowTelemetry = 0, AllowExperimentation = 0, DisableWindowsConsumerFeatures = 1, DisableTailoredExperiencesWithDiagnosticData = 1, DODownloadMode = 0, DisableAIDataAnalysis = 1 (blockiert Windows Recall), DoNotShowFeedbackNotifications = 1, CEIPEnable = 0.\nDeaktiviert die Werbe-ID, die Bing-Websuche im Startmenü und Suchvorschläge (benutzerbezogene Einstellungen).\n\nDeaktivierung:\nStellt den genauen Zustand dieser Dienste und der Registry wieder her, der unmittelbar vor der Aktivierung dieser Stufe bestand.',
        "es": 'Activación:\nDesactiva los servicios de telemetría (DiagTrack, dmwappushservice).\nAñade políticas de registro: AllowTelemetry = 0, AllowExperimentation = 0, DisableWindowsConsumerFeatures = 1, DisableTailoredExperiencesWithDiagnosticData = 1, DODownloadMode = 0, DisableAIDataAnalysis = 1 (bloquea Windows Recall), DoNotShowFeedbackNotifications = 1, CEIPEnable = 0.\nDesactiva el ID de publicidad, la búsqueda web de Bing en el menú Inicio y las sugerencias del cuadro de búsqueda (ajustes por usuario).\n\nDesactivación:\nRestaura el estado exacto de estos servicios y del registro que existía inmediatamente antes de activar este nivel.',
    },
    "par_antispy_medium_tooltip": {
        "en": (
            "Enable:\n"
            "Adds outbound block rules in Windows Firewall "
            "(CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\n"
            "Disables 9 telemetry-related Task Scheduler tasks "
            "(Compatibility Appraiser, ProgramDataUpdater, Consolidator, "
            "UsbCeip, QueueReporting, KernelCeipTask, "
            "DiskDiagnosticDataCollector, Siuf\\DmClient, "
            "Siuf\\DmClientOnScenarioDownload).\n\n"
            "Disable:\n"
            "Removes the firewall rules and re-enables any of those tasks "
            "that were enabled before this level was activated."
        ),
        "pl": (
            "Włączenie:\n"
            "Dodaje reguły blokady wychodzącej w Windows Firewall "
            "(CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\n"
            "Wyłącza 9 zadań telemetrycznych w Harmonogramie zadań "
            "(Compatibility Appraiser, ProgramDataUpdater, Consolidator, "
            "UsbCeip, QueueReporting, KernelCeipTask, "
            "DiskDiagnosticDataCollector, Siuf\\DmClient, "
            "Siuf\\DmClientOnScenarioDownload).\n\n"
            "Wyłączenie:\n"
            "Usuwa reguły zapory i przywraca te zadania, które były "
            "włączone przed aktywacją tego poziomu."
        ),
        "fr": (
            "Activation :\n"
            "Ajoute des règles de blocage sortant dans le Pare-feu Windows "
            "(CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\n"
            "Désactive 9 tâches liées à la télémétrie dans le Planificateur "
            "de tâches (Compatibility Appraiser, ProgramDataUpdater, "
            "Consolidator, UsbCeip, QueueReporting, KernelCeipTask, "
            "DiskDiagnosticDataCollector, Siuf\\DmClient, "
            "Siuf\\DmClientOnScenarioDownload).\n\n"
            "Désactivation :\n"
            "Supprime les règles du pare-feu et réactive les tâches qui "
            "étaient activées avant l'activation de ce niveau."
        ),
    
        "de": 'Aktivierung:\nFügt ausgehende Blockierungsregeln in der Windows-Firewall hinzu (CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\nDeaktiviert 9 telemetriebezogene Aufgaben im Aufgabenplaner (Compatibility Appraiser, ProgramDataUpdater, Consolidator, UsbCeip, QueueReporting, KernelCeipTask, DiskDiagnosticDataCollector, Siuf\\DmClient, Siuf\\DmClientOnScenarioDownload).\n\nDeaktivierung:\nEntfernt die Firewall-Regeln und aktiviert die Aufgaben erneut, die vor der Aktivierung dieser Stufe aktiviert waren.',
        "es": 'Activación:\nAñade reglas de bloqueo de salida en el Firewall de Windows (CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\nDesactiva 9 tareas relacionadas con la telemetría en el Programador de tareas (Compatibility Appraiser, ProgramDataUpdater, Consolidator, UsbCeip, QueueReporting, KernelCeipTask, DiskDiagnosticDataCollector, Siuf\\DmClient, Siuf\\DmClientOnScenarioDownload).\n\nDesactivación:\nElimina las reglas del firewall y vuelve a activar las tareas que estaban activadas antes de activar este nivel.',
    },
    "par_antispy_advanced_tooltip": {
        "en": (
            "Enable:\n"
            "Disables WerSvc (Windows Error Reporting service) and "
            "PcaSvc (Program Compatibility Assistant).\n"
            "Adds registry policies: EnableActivityFeed = 0, "
            "PublishUserActivities = 0, UploadUserActivities = 0.\n\n"
            "Note — real functional impact:\n"
            "Disabling WerSvc means crash/BSOD reports are no longer collected. "
            "Disabling PcaSvc means Windows will no longer warn you about "
            "compatibility problems when running older software. "
            "Disabling the Activity Feed settings means your activity history "
            "(Timeline) and 'continue on another device' will stop working.\n\n"
            "Disable:\n"
            "Restores the exact state of these services and registry "
            "settings that existed immediately before this level was activated."
        ),
        "pl": (
            "Włączenie:\n"
            "Wyłącza usługi WerSvc (Zgłaszanie błędów systemu Windows) "
            "i PcaSvc (Asystent zgodności programów).\n"
            "Dodaje wpisy w rejestrze: EnableActivityFeed = 0, "
            "PublishUserActivities = 0, UploadUserActivities = 0.\n\n"
            "Uwaga — realny skutek funkcjonalny:\n"
            "Wyłączenie WerSvc oznacza, że raporty awarii/BSOD nie będą "
            "już zbierane. Wyłączenie PcaSvc oznacza, że Windows przestanie "
            "ostrzegać o problemach ze zgodnością przy uruchamianiu starszego "
            "oprogramowania. Wyłączenie ustawień Osi czasu oznacza utratę "
            "historii aktywności i funkcji 'kontynuuj na innym urządzeniu'.\n\n"
            "Wyłączenie:\n"
            "Przywraca dokładny stan tych usług i ustawień rejestru sprzed "
            "aktywacji tego poziomu."
        ),
        "fr": (
            "Activation :\n"
            "Désactive WerSvc (service de rapport d'erreurs Windows) et "
            "PcaSvc (Assistant de compatibilité des programmes).\n"
            "Ajoute des stratégies de registre : EnableActivityFeed = 0, "
            "PublishUserActivities = 0, UploadUserActivities = 0.\n\n"
            "Remarque — impact fonctionnel réel :\n"
            "Désactiver WerSvc signifie que les rapports de plantage/BSOD ne "
            "seront plus collectés. Désactiver PcaSvc signifie que Windows ne "
            "vous avertira plus des problèmes de compatibilité lors de "
            "l'exécution d'anciens logiciels. Désactiver les paramètres de la "
            "Chronologie entraîne la perte de l'historique d'activité et de la "
            "fonction « continuer sur un autre appareil ».\n\n"
            "Désactivation :\n"
            "Restaure l'état exact de ces services et paramètres de registre "
            "tel qu'il était avant l'activation de ce niveau."
        ),
    
        "de": 'Aktivierung:\nDeaktiviert WerSvc (Windows-Fehlerberichterstattung) und PcaSvc (Programmkompatibilitäts-Assistent).\nFügt Registry-Richtlinien hinzu: EnableActivityFeed = 0, PublishUserActivities = 0, UploadUserActivities = 0.\n\nHinweis — tatsächliche Auswirkung:\nDas Deaktivieren von WerSvc bedeutet, dass Absturz-/BSOD-Berichte nicht mehr gesammelt werden. Das Deaktivieren von PcaSvc bedeutet, dass Windows Sie nicht mehr vor Kompatibilitätsproblemen bei älterer Software warnt. Das Deaktivieren der Aktivitätsverlauf-Einstellungen bedeutet, dass Ihr Aktivitätsverlauf (Zeitleiste) und „Auf einem anderen Gerät fortsetzen" nicht mehr funktionieren.\n\nDeaktivierung:\nStellt den genauen Zustand dieser Dienste und Registry-Einstellungen wieder her, der unmittelbar vor der Aktivierung dieser Stufe bestand.',
        "es": "Activación:\nDesactiva WerSvc (servicio de informes de errores de Windows) y PcaSvc (Asistente de compatibilidad de programas).\nAñade políticas de registro: EnableActivityFeed = 0, PublishUserActivities = 0, UploadUserActivities = 0.\n\nNota — impacto funcional real:\nDesactivar WerSvc significa que ya no se recopilarán informes de errores/BSOD. Desactivar PcaSvc significa que Windows dejará de advertirte sobre problemas de compatibilidad al ejecutar software antiguo. Desactivar los ajustes del Historial de actividades significa que tu historial de actividad (Cronología) y la función 'continuar en otro dispositivo' dejarán de funcionar.\n\nDesactivación:\nRestaura el estado exacto de estos servicios y ajustes de registro que existía inmediatamente antes de activar este nivel.",
    },
    "par_antispy_extra_tooltip": {
        "en": (
            "Enable:\n"
            "Disables the lfsvc (Geolocation) service and blocks location "
            "access via registry policy (DisableLocation = 1).\n"
            "Adds registry policies: RestrictImplicitTextCollection = 1, "
            "RestrictImplicitInkCollection = 1, AcceptedPrivacyPolicy = 0 "
            "(stops Windows collecting samples of your typing/handwriting "
            "for personalization), AllowCrossDeviceClipboard = 0 (blocks "
            "Cloud Clipboard syncing to your other devices), "
            "AllowFindMyDevice = 0 (stops this device's location being "
            "registered in Microsoft's cloud in the background).\n\n"
            "Note — real functional impact:\n"
            "Apps relying on automatic location (weather, maps) will stop "
            "working correctly. Text/handwriting suggestions and "
            "autocorrect will become less accurate. Clipboard content will "
            "no longer sync between your devices. You won't be able to "
            "locate this device via account.microsoft.com if it's lost "
            "or stolen.\n\n"
            "Disable:\n"
            "Restores the exact state of this service and these registry "
            "settings that existed immediately before this level was activated."
        ),
        "pl": (
            "Włączenie:\n"
            "Wyłącza usługę lfsvc (lokalizacja geograficzna) i blokuje "
            "dostęp do lokalizacji polityką rejestru (DisableLocation = 1).\n"
            "Dodaje wpisy w rejestrze: RestrictImplicitTextCollection = 1, "
            "RestrictImplicitInkCollection = 1, AcceptedPrivacyPolicy = 0 "
            "(zatrzymuje zbieranie przez Windows próbek pisania/pisma "
            "odręcznego do personalizacji), AllowCrossDeviceClipboard = 0 "
            "(blokuje synchronizację schowka z innymi urządzeniami), "
            "AllowFindMyDevice = 0 (zatrzymuje rejestrowanie lokalizacji "
            "tego komputera w chmurze Microsoft w tle).\n\n"
            "Uwaga — realny skutek funkcjonalny:\n"
            "Aplikacje korzystające z automatycznej lokalizacji (pogoda, "
            "mapy) przestaną działać poprawnie. Sugestie tekstu/pisma "
            "odręcznego i autokorekta będą mniej trafne. Zawartość schowka "
            "przestanie się synchronizować między Twoimi urządzeniami. "
            "Nie będzie można zlokalizować tego komputera przez "
            "account.microsoft.com w razie zgubienia lub kradzieży.\n\n"
            "Wyłączenie:\n"
            "Przywraca dokładny stan tej usługi i tych ustawień rejestru "
            "sprzed aktywacji tego poziomu."
        ),
        "fr": (
            "Activation :\n"
            "Désactive le service lfsvc (géolocalisation) et bloque l'accès "
            "à la localisation via une stratégie de registre "
            "(DisableLocation = 1).\n"
            "Ajoute des stratégies de registre : "
            "RestrictImplicitTextCollection = 1, "
            "RestrictImplicitInkCollection = 1, AcceptedPrivacyPolicy = 0 "
            "(empêche Windows de collecter des échantillons de votre saisie/"
            "écriture pour la personnalisation), "
            "AllowCrossDeviceClipboard = 0 (bloque la synchronisation du "
            "presse-papiers avec vos autres appareils), "
            "AllowFindMyDevice = 0 (empêche l'enregistrement en arrière-plan "
            "de la position de cet appareil dans le cloud Microsoft).\n\n"
            "Remarque — impact fonctionnel réel :\n"
            "Les applications utilisant la localisation automatique (météo, "
            "cartes) cesseront de fonctionner correctement. Les suggestions "
            "de texte/écriture et l'autocorrection seront moins précises. "
            "Le contenu du presse-papiers ne se synchronisera plus entre "
            "vos appareils. Vous ne pourrez plus localiser cet appareil via "
            "account.microsoft.com en cas de perte ou de vol.\n\n"
            "Désactivation :\n"
            "Restaure l'état exact de ce service et de ces paramètres de "
            "registre tel qu'il était avant l'activation de ce niveau."
        ),
    
        "de": 'Aktivierung:\nDeaktiviert den Dienst lfsvc (Geolokalisierung) und blockiert den Standortzugriff per Registry-Richtlinie (DisableLocation = 1).\nFügt Registry-Richtlinien hinzu: RestrictImplicitTextCollection = 1, RestrictImplicitInkCollection = 1, AcceptedPrivacyPolicy = 0 (verhindert, dass Windows Proben Ihrer Eingaben/Handschrift zur Personalisierung sammelt), AllowCrossDeviceClipboard = 0 (blockiert die Synchronisierung der Zwischenablage mit Ihren anderen Geräten), AllowFindMyDevice = 0 (verhindert, dass der Standort dieses Geräts im Hintergrund in der Microsoft-Cloud registriert wird).\n\nHinweis — tatsächliche Auswirkung:\nApps, die auf automatische Standorterkennung angewiesen sind (Wetter, Karten), funktionieren nicht mehr korrekt. Text-/Handschriftvorschläge und Autokorrektur werden ungenauer. Zwischenablage-Inhalte werden nicht mehr zwischen Ihren Geräten synchronisiert. Sie können dieses Gerät bei Verlust oder Diebstahl nicht mehr über account.microsoft.com orten.\n\nDeaktivierung:\nStellt den genauen Zustand dieses Dienstes und dieser Registry-Einstellungen wieder her, der unmittelbar vor der Aktivierung dieser Stufe bestand.',
        "es": "Activación:\nDesactiva el servicio lfsvc (geolocalización) y bloquea el acceso a la ubicación mediante política de registro (DisableLocation = 1).\nAñade políticas de registro: RestrictImplicitTextCollection = 1, RestrictImplicitInkCollection = 1, AcceptedPrivacyPolicy = 0 (impide que Windows recopile muestras de tu escritura para la personalización), AllowCrossDeviceClipboard = 0 (bloquea la sincronización del portapapeles con tus otros dispositivos), AllowFindMyDevice = 0 (impide que la ubicación de este equipo se registre en segundo plano en la nube de Microsoft).\n\nNota — impacto funcional real:\nLas aplicaciones que dependen de la ubicación automática (clima, mapas) dejarán de funcionar correctamente. Las sugerencias de texto/escritura y el autocorrector serán menos precisos. El contenido del portapapeles dejará de sincronizarse entre tus dispositivos. No podrás localizar este equipo desde account.microsoft.com si se pierde o es robado.\n\nDesactivación:\nRestaura el estado exacto de este servicio y estos ajustes de registro que existía inmediatamente antes de activar este nivel.",
    },
    "priv_advanced_services_label": {"en": "Diagnostic services", "pl": "Usługi diagnostyczne", "fr": "Services de diagnostic", "de": 'Diagnosedienste', "es": 'Servicios de diagnóstico'},
    "priv_advanced_services_tooltip": {
        "en": "Enable: disables WerSvc and PcaSvc.\nDisable: restores their exact previous startup type.",
        "pl": "Włączenie: wyłącza usługi WerSvc i PcaSvc.\nWyłączenie: przywraca ich dokładny poprzedni typ uruchamiania.",
        "fr": "Activation : désactive WerSvc et PcaSvc.\nDésactivation : restaure leur type de démarrage précédent.",
    
        "de": 'Aktivieren: deaktiviert WerSvc und PcaSvc.\nDeaktivieren: stellt deren genauen vorherigen Starttyp wieder her.',
        "es": 'Activar: desactiva WerSvc y PcaSvc.\nDesactivar: restaura su tipo de inicio anterior exacto.',
    },
    "priv_advanced_privacy_label": {"en": "Privacy settings (per tweak)", "pl": "Ustawienia prywatności (osobno)", "fr": "Paramètres de confidentialité (séparés)", "de": 'Datenschutzeinstellungen (einzeln)', "es": 'Ajustes de privacidad (individuales)'},
    "priv_item_basic_reg": {"en": "Diagnostic reporting level (AllowTelemetry = 0)", "pl": "Poziom raportowania diagnostycznego (AllowTelemetry = 0)", "fr": "Niveau de rapport de diagnostic (AllowTelemetry = 0)", "de": 'Diagnoseberichtsstufe (AllowTelemetry = 0)', "es": 'Nivel de informes de diagnóstico (AllowTelemetry = 0)'},
    "priv_item_basic_diagtrack": {"en": "Telemetry collection service (DiagTrack)", "pl": "Usługa zbierania telemetrii (DiagTrack)", "fr": "Service de collecte de télémétrie (DiagTrack)", "de": 'Telemetrie-Erfassungsdienst (DiagTrack)', "es": 'Servicio de recopilación de telemetría (DiagTrack)'},
    "priv_item_basic_dmwap": {"en": "Telemetry via push notifications (dmwappushservice)", "pl": "Telemetria przez powiadomienia push (dmwappushservice)", "fr": "Télémétrie via notifications push (dmwappushservice)", "de": 'Telemetrie über Push-Benachrichtigungen (dmwappushservice)', "es": 'Telemetría vía notificaciones push (dmwappushservice)'},
    "priv_item_basic_experimentation": {"en": "Participation in Microsoft experiments (AllowExperimentation = 0)", "pl": "Udział w eksperymentach Microsoft (AllowExperimentation = 0)", "fr": "Participation aux expérimentations Microsoft (AllowExperimentation = 0)", "de": 'Teilnahme an Microsoft-Experimenten (AllowExperimentation = 0)', "es": 'Participación en experimentos de Microsoft (AllowExperimentation = 0)'},
    "priv_item_basic_consumerfeatures": {"en": "Promoted apps in Start Menu (DisableWindowsConsumerFeatures = 1)", "pl": "Reklamowe aplikacje w Menu Start (DisableWindowsConsumerFeatures = 1)", "fr": "Applications promotionnelles dans le menu Démarrer (DisableWindowsConsumerFeatures = 1)", "de": 'Werbe-Apps im Startmenü (DisableWindowsConsumerFeatures = 1)', "es": 'Aplicaciones promocionadas en el menú Inicio (DisableWindowsConsumerFeatures = 1)'},
    "priv_item_basic_tailored": {"en": "Personalized ads and tips (DisableTailoredExperiencesWithDiagnosticData = 1)", "pl": "Spersonalizowane reklamy i podpowiedzi (DisableTailoredExperiencesWithDiagnosticData = 1)", "fr": "Publicités et conseils personnalisés (DisableTailoredExperiencesWithDiagnosticData = 1)", "de": 'Personalisierte Werbung und Tipps (DisableTailoredExperiencesWithDiagnosticData = 1)', "es": 'Anuncios y sugerencias personalizados (DisableTailoredExperiencesWithDiagnosticData = 1)'},
    "priv_item_basic_deliveryopt": {"en": "Update sharing over the network (DODownloadMode = 0)", "pl": "Współdzielenie aktualizacji w sieci (DODownloadMode = 0)", "fr": "Partage des mises à jour sur le réseau (DODownloadMode = 0)", "de": 'Freigabe von Updates im Netzwerk (DODownloadMode = 0)', "es": 'Uso compartido de actualizaciones en red (DODownloadMode = 0)'},
    "priv_item_basic_recall": {"en": "Windows Recall (DisableAIDataAnalysis = 1)", "pl": "Windows Recall (DisableAIDataAnalysis = 1)", "fr": "Windows Recall (DisableAIDataAnalysis = 1)", "de": 'Windows Recall (DisableAIDataAnalysis = 1)', "es": 'Windows Recall (DisableAIDataAnalysis = 1)'},
    "priv_item_basic_feedback": {"en": "Windows feedback requests (DoNotShowFeedbackNotifications = 1)", "pl": "Prośby o opinię o Windows (DoNotShowFeedbackNotifications = 1)", "fr": "Demandes de commentaires Windows (DoNotShowFeedbackNotifications = 1)", "de": 'Windows-Feedback-Anfragen (DoNotShowFeedbackNotifications = 1)', "es": 'Solicitudes de comentarios de Windows (DoNotShowFeedbackNotifications = 1)'},
    "priv_item_basic_ceip": {"en": "Customer Experience Improvement Program (CEIPEnable = 0)", "pl": "Program ulepszania jakości oprogramowania (CEIPEnable = 0)", "fr": "Programme d'amélioration de l'expérience (CEIPEnable = 0)", "de": 'Programm zur Verbesserung der Benutzerfreundlichkeit (CEIPEnable = 0)', "es": 'Programa de mejora de la experiencia del cliente (CEIPEnable = 0)'},
    "priv_item_medium_compattel": {"en": "Hardware/software compatibility data collection (CompatTelRunner.exe)", "pl": "Zbieranie danych o zgodności sprzętu (CompatTelRunner.exe)", "fr": "Collecte de données de compatibilité (CompatTelRunner.exe)", "de": 'Erfassung von Kompatibilitätsdaten (CompatTelRunner.exe)', "es": 'Recopilación de datos de compatibilidad (CompatTelRunner.exe)'},
    "priv_item_medium_devicecensus": {"en": "Device data census (devicecensus.exe)", "pl": "Spis danych o urządzeniu (devicecensus.exe)", "fr": "Recensement des données de l'appareil (devicecensus.exe)", "de": 'Gerätedaten-Erfassung (devicecensus.exe)', "es": 'Censo de datos del dispositivo (devicecensus.exe)'},
    "priv_item_medium_werfault": {"en": "Application crash reports (WerFault.exe)", "pl": "Raporty o awariach aplikacji (WerFault.exe)", "fr": "Rapports de plantage des applications (WerFault.exe)", "de": 'Absturzberichte von Anwendungen (WerFault.exe)', "es": 'Informes de fallos de aplicaciones (WerFault.exe)'},
    "priv_item_medium_appraiser": {"en": "Windows upgrade compatibility check (Compatibility Appraiser)", "pl": "Sprawdzanie zgodności z nową wersją Windows (Compatibility Appraiser)", "fr": "Vérification de compatibilité de mise à niveau (Compatibility Appraiser)", "de": 'Kompatibilitätsprüfung für Windows-Upgrade (Compatibility Appraiser)', "es": 'Comprobación de compatibilidad de actualización (Compatibility Appraiser)'},
    "priv_item_medium_programdata": {"en": "Installed programs data collection (ProgramDataUpdater)", "pl": "Zbieranie danych o zainstalowanych programach (ProgramDataUpdater)", "fr": "Collecte de données sur les programmes installés (ProgramDataUpdater)", "de": 'Erfassung installierter Programme (ProgramDataUpdater)', "es": 'Recopilación de datos de programas instalados (ProgramDataUpdater)'},
    "priv_item_medium_consolidator": {"en": "Telemetry data upload (Consolidator)", "pl": "Wysyłanie danych telemetrycznych (Consolidator)", "fr": "Envoi des données de télémétrie (Consolidator)", "de": 'Übermittlung von Telemetriedaten (Consolidator)', "es": 'Envío de datos de telemetría (Consolidator)'},
    "priv_item_medium_usbceip": {"en": "USB device data collection (UsbCeip)", "pl": "Zbieranie danych o urządzeniach USB (UsbCeip)", "fr": "Collecte de données sur les périphériques USB (UsbCeip)", "de": 'Erfassung von USB-Gerätedaten (UsbCeip)', "es": 'Recopilación de datos de dispositivos USB (UsbCeip)'},
    "priv_item_medium_queuereporting": {"en": "System error report queuing (QueueReporting)", "pl": "Kolejkowanie raportów błędów systemu (QueueReporting)", "fr": "Mise en file d'attente des rapports d'erreurs (QueueReporting)", "de": 'Warteschlange für Systemfehlerberichte (QueueReporting)', "es": 'Cola de informes de errores del sistema (QueueReporting)'},
    "priv_item_medium_kernelceip": {"en": "Kernel-level diagnostics (KernelCeipTask)", "pl": "Diagnostyka jądra systemu (KernelCeipTask)", "fr": "Diagnostics au niveau du noyau (KernelCeipTask)", "de": 'Diagnose auf Kernel-Ebene (KernelCeipTask)', "es": 'Diagnóstico a nivel de kernel (KernelCeipTask)'},
    "priv_item_medium_diskdiagnostic": {"en": "Disk health diagnostics (DiskDiagnosticDataCollector)", "pl": "Diagnostyka stanu dysku (DiskDiagnosticDataCollector)", "fr": "Diagnostic de l'état du disque (DiskDiagnosticDataCollector)", "de": 'Datenträgerdiagnose (DiskDiagnosticDataCollector)', "es": 'Diagnóstico del estado del disco (DiskDiagnosticDataCollector)'},
    "priv_item_medium_siuf_dmclient": {"en": "Feedback requests and diagnostic data (DmClient)", "pl": "Prośby o opinię i dane diagnostyczne (DmClient)", "fr": "Demandes de commentaires et données de diagnostic (DmClient)", "de": 'Feedback-Anfragen und Diagnosedaten (DmClient)', "es": 'Solicitudes de comentarios y datos de diagnóstico (DmClient)'},
    "priv_item_medium_siuf_dmclientonscenario": {"en": "Post-update feedback requests (DmClientOnScenarioDownload)", "pl": "Prośby o opinię po aktualizacjach (DmClientOnScenarioDownload)", "fr": "Demandes de commentaires après mise à jour (DmClientOnScenarioDownload)", "de": 'Feedback-Anfragen nach Updates (DmClientOnScenarioDownload)', "es": 'Solicitudes de comentarios tras actualizaciones (DmClientOnScenarioDownload)'},
    "priv_item_advanced_wersvc": {"en": "Crash/BSOD report collection (WerSvc)", "pl": "Zbieranie raportów o awariach/BSOD (WerSvc)", "fr": "Collecte des rapports de plantage/BSOD (WerSvc)", "de": 'Erfassung von Absturz-/BSOD-Berichten (WerSvc)', "es": 'Recopilación de informes de fallos/BSOD (WerSvc)'},
    "priv_item_advanced_pcasvc": {"en": "Program Compatibility Assistant (PcaSvc)", "pl": "Asystent zgodności programów (PcaSvc)", "fr": "Assistant de compatibilité des programmes (PcaSvc)", "de": 'Programmkompatibilitäts-Assistent (PcaSvc)', "es": 'Asistente de compatibilidad de programas (PcaSvc)'},
    "priv_item_advanced_activityfeed": {"en": "Timeline (EnableActivityFeed = 0)", "pl": "Oś czasu (EnableActivityFeed = 0)", "fr": "Chronologie (EnableActivityFeed = 0)", "de": 'Zeitleiste (EnableActivityFeed = 0)', "es": 'Cronología (EnableActivityFeed = 0)'},
    "priv_item_advanced_publishactivities": {"en": "Recording your activity (PublishUserActivities = 0)", "pl": "Zapisywanie Twojej aktywności (PublishUserActivities = 0)", "fr": "Enregistrement de votre activité (PublishUserActivities = 0)", "de": 'Aufzeichnung Ihrer Aktivität (PublishUserActivities = 0)', "es": 'Registro de tu actividad (PublishUserActivities = 0)'},
    "priv_item_advanced_uploadactivities": {"en": "Uploading activity to the cloud (UploadUserActivities = 0)", "pl": "Wysyłanie aktywności do chmury (UploadUserActivities = 0)", "fr": "Envoi de l'activité vers le cloud (UploadUserActivities = 0)", "de": 'Hochladen der Aktivität in die Cloud (UploadUserActivities = 0)', "es": 'Envío de actividad a la nube (UploadUserActivities = 0)'},
    "priv_item_extra_lfsvc": {"en": "Windows location service (lfsvc)", "pl": "Usługa lokalizacji Windows (lfsvc)", "fr": "Service de localisation Windows (lfsvc)", "de": 'Windows-Standortdienst (lfsvc)', "es": 'Servicio de ubicación de Windows (lfsvc)'},
    "priv_item_extra_disablelocation": {"en": "Additional location lock (DisableLocation = 1)", "pl": "Dodatkowa blokada lokalizacji (DisableLocation = 1)", "fr": "Verrouillage supplémentaire de la localisation (DisableLocation = 1)", "de": 'Zusätzliche Standortsperre (DisableLocation = 1)', "es": 'Bloqueo adicional de ubicación (DisableLocation = 1)'},
    "priv_item_extra_text_collection": {"en": "Typing sample collection (RestrictImplicitTextCollection = 1)", "pl": "Zbieranie próbek tekstu (RestrictImplicitTextCollection = 1)", "fr": "Collecte d'échantillons de frappe (RestrictImplicitTextCollection = 1)", "de": 'Erfassung von Tippbeispielen (RestrictImplicitTextCollection = 1)', "es": 'Recopilación de muestras de escritura (RestrictImplicitTextCollection = 1)'},
    "priv_item_extra_ink_collection": {"en": "Handwriting sample collection (RestrictImplicitInkCollection = 1)", "pl": "Zbieranie próbek pisma odręcznego (RestrictImplicitInkCollection = 1)", "fr": "Collecte d'échantillons d'écriture manuscrite (RestrictImplicitInkCollection = 1)", "de": 'Erfassung von Handschriftproben (RestrictImplicitInkCollection = 1)', "es": 'Recopilación de muestras de escritura manuscrita (RestrictImplicitInkCollection = 1)'},
    "priv_item_extra_personalization_policy": {"en": "Handwriting personalization consent (AcceptedPrivacyPolicy = 0)", "pl": "Zgoda na personalizację pisma (AcceptedPrivacyPolicy = 0)", "fr": "Consentement à la personnalisation de l'écriture (AcceptedPrivacyPolicy = 0)", "de": 'Zustimmung zur Handschriftpersonalisierung (AcceptedPrivacyPolicy = 0)', "es": 'Consentimiento de personalización de escritura (AcceptedPrivacyPolicy = 0)'},
    "priv_item_extra_cross_device_clipboard": {"en": "Cross-device clipboard sync (AllowCrossDeviceClipboard = 0)", "pl": "Synchronizacja schowka między urządzeniami (AllowCrossDeviceClipboard = 0)", "fr": "Synchronisation du presse-papiers entre appareils (AllowCrossDeviceClipboard = 0)", "de": 'Geräteübergreifende Zwischenablage-Synchronisierung (AllowCrossDeviceClipboard = 0)', "es": 'Sincronización del portapapeles entre dispositivos (AllowCrossDeviceClipboard = 0)'},
    "priv_item_extra_findmydevice": {"en": "Device location reporting (AllowFindMyDevice = 0)", "pl": "Raportowanie lokalizacji urządzenia (AllowFindMyDevice = 0)", "fr": "Signalement de la position de l'appareil (AllowFindMyDevice = 0)", "de": 'Standortmeldung des Geräts (AllowFindMyDevice = 0)', "es": 'Informe de ubicación del dispositivo (AllowFindMyDevice = 0)'},
    "priv_desc_basic_reg_telemetry": {"en": "Stops sending diagnostic data about your PC to Microsoft.", "pl": "Wyłącza wysyłanie do Microsoftu danych diagnostycznych o Twoim komputerze.", "fr": "Arrête l'envoi de données de diagnostic sur votre PC à Microsoft.", "de": 'Beendet das Senden von Diagnosedaten über Ihren PC an Microsoft.', "es": 'Detiene el envío de datos de diagnóstico sobre tu PC a Microsoft.'},
    "priv_desc_basic_svc_diagtrack": {"en": "Stops the background service that collects telemetry data.", "pl": "Zatrzymuje usługę zbierającą w tle dane telemetryczne.", "fr": "Arrête le service qui collecte les données de télémétrie en arrière-plan.", "de": 'Stoppt den Hintergrunddienst, der Telemetriedaten sammelt.', "es": 'Detiene el servicio en segundo plano que recopila datos de telemetría.'},
    "priv_desc_basic_svc_dmwap": {"en": "Stops the service that pushes telemetry data via notifications.", "pl": "Zatrzymuje usługę wysyłającą dane telemetryczne przez powiadomienia push.", "fr": "Arrête le service qui envoie des données de télémétrie via les notifications.", "de": 'Stoppt den Dienst, der Telemetriedaten über Benachrichtigungen sendet.', "es": 'Detiene el servicio que envía datos de telemetría mediante notificaciones.'},
    "priv_desc_basic_reg_experimentation": {"en": "Blocks your PC from taking part in Microsoft's A/B tests and experiments.", "pl": "Blokuje udział komputera w testach A/B i eksperymentach Microsoftu.", "fr": "Empêche votre PC de participer aux tests A/B et expériences de Microsoft.", "de": 'Verhindert, dass Ihr PC an A/B-Tests und Experimenten von Microsoft teilnimmt.', "es": 'Impide que tu PC participe en las pruebas A/B y experimentos de Microsoft.'},
    "priv_desc_basic_reg_consumerfeatures": {"en": "Stops Windows from auto-installing suggested/advertised apps in the Start Menu.", "pl": "Blokuje automatyczne instalowanie reklamowych aplikacji w Menu Start.", "fr": "Empêche Windows d'installer automatiquement des applications suggérées/publicitaires.", "de": 'Verhindert, dass Windows automatisch vorgeschlagene/beworbene Apps im Startmenü installiert.', "es": 'Impide que Windows instale automáticamente aplicaciones sugeridas/publicitarias en el menú Inicio.'},
    "priv_desc_basic_reg_tailored": {"en": "Blocks personalized tips and ads built from data collected about you.", "pl": "Blokuje spersonalizowane podpowiedzi i reklamy budowane na podstawie zebranych o Tobie danych.", "fr": "Bloque les astuces et publicités personnalisées basées sur vos données.", "de": 'Blockiert personalisierte Tipps und Werbung, die aus über Sie gesammelten Daten erstellt werden.', "es": 'Bloquea sugerencias y anuncios personalizados creados a partir de datos recopilados sobre ti.'},
    "priv_desc_basic_reg_deliveryopt": {"en": "Stops Windows Update from sharing update files with other PCs over the internet.", "pl": "Wyłącza wysyłanie/pobieranie aktualizacji Windows do i od innych komputerów w sieci.", "fr": "Empêche le partage des fichiers de mise à jour avec d'autres PC sur internet.", "de": 'Verhindert, dass Windows Update Aktualisierungsdateien über das Internet mit anderen PCs teilt.', "es": 'Impide que Windows Update comparta archivos de actualización con otros PCs a través de internet.'},
    "priv_desc_basic_reg_recall": {"en": "Blocks Windows Recall — the feature that keeps taking screenshots for AI analysis.", "pl": "Blokuje funkcję Windows Recall — ciągłe robienie zrzutów ekranu do analizy przez AI.", "fr": "Bloque Windows Recall — la prise continue de captures d'écran pour analyse par IA.", "de": 'Blockiert Windows Recall — die Funktion, die ständig Screenshots für die KI-Analyse erstellt.', "es": 'Bloquea Windows Recall — la función que toma capturas de pantalla continuamente para el análisis de IA.'},
    "priv_desc_basic_reg_feedback": {"en": "Turns off the pop-ups asking you to rate and give feedback on Windows.", "pl": "Wyłącza wyskakujące prośby o ocenę i opinię o systemie Windows.", "fr": "Désactive les fenêtres demandant d'évaluer et de donner votre avis sur Windows.", "de": 'Deaktiviert die Popups, die Sie um eine Bewertung und Feedback zu Windows bitten.', "es": 'Desactiva las ventanas emergentes que piden calificar y dar comentarios sobre Windows.'},
    "priv_desc_basic_reg_ceip": {"en": "Blocks participation in Microsoft's Customer Experience Improvement Program.", "pl": "Blokuje udział w Programie ulepszania jakości oprogramowania Microsoft.", "fr": "Bloque la participation au programme d'amélioration de l'expérience client Microsoft.", "de": 'Blockiert die Teilnahme am Microsoft-Programm zur Verbesserung der Benutzerfreundlichkeit.', "es": 'Bloquea la participación en el Programa de mejora de la experiencia del cliente de Microsoft.'},
    "priv_desc_advertising_id": {"en": "Turns off the unique ad ID used to show you personalized ads.", "pl": "Wyłącza unikalny identyfikator reklamowy używany do spersonalizowanych reklam.", "fr": "Désactive l'identifiant publicitaire unique utilisé pour les publicités personnalisées.", "de": 'Deaktiviert die eindeutige Werbe-ID, die für personalisierte Werbung verwendet wird.', "es": 'Desactiva el ID de publicidad único utilizado para mostrarte anuncios personalizados.'},
    "priv_desc_bing_search": {"en": "Stops web (Bing) results from appearing in Start Menu search.", "pl": "Wyłącza pokazywanie wyników wyszukiwania z internetu (Bing) w Menu Start.", "fr": "Empêche les résultats web (Bing) d'apparaître dans la recherche du menu Démarrer.", "de": 'Verhindert, dass Web-Ergebnisse (Bing) in der Startmenü-Suche erscheinen.', "es": 'Impide que los resultados web (Bing) aparezcan en la búsqueda del menú Inicio.'},
    "priv_desc_search_suggestions": {"en": "Turns off web suggestions in the taskbar search box.", "pl": "Wyłącza podpowiedzi z internetu w polu wyszukiwania na pasku zadań.", "fr": "Désactive les suggestions web dans la barre de recherche de la barre des tâches.", "de": 'Deaktiviert Websuchvorschläge im Suchfeld der Taskleiste.', "es": 'Desactiva las sugerencias web en el cuadro de búsqueda de la barra de tareas.'},
    "priv_desc_medium_fw_compattel": {"en": "Firewall-blocks the process that collects hardware/software compatibility data.", "pl": "Blokuje w zaporze proces zbierający dane o zgodności sprzętu i oprogramowania.", "fr": "Bloque dans le pare-feu le processus qui collecte les données de compatibilité.", "de": 'Blockiert per Firewall den Prozess, der Hardware-/Software-Kompatibilitätsdaten sammelt.', "es": 'Bloquea mediante firewall el proceso que recopila datos de compatibilidad de hardware/software.'},
    "priv_desc_medium_fw_devicecensus": {"en": "Firewall-blocks the process that sends a full inventory of your device to Microsoft.", "pl": "Blokuje w zaporze proces wysyłający spis danych o Twoim urządzeniu do Microsoft.", "fr": "Bloque dans le pare-feu le processus qui envoie l'inventaire de votre appareil.", "de": 'Blockiert per Firewall den Prozess, der ein vollständiges Geräteinventar an Microsoft sendet.', "es": 'Bloquea mediante firewall el proceso que envía un inventario completo de tu dispositivo a Microsoft.'},
    "priv_desc_medium_fw_werfault": {"en": "Firewall-blocks the upload of application crash reports to Microsoft.", "pl": "Blokuje w zaporze wysyłanie raportów o awariach aplikacji do Microsoft.", "fr": "Bloque dans le pare-feu l'envoi des rapports de plantage d'applications.", "de": 'Blockiert per Firewall das Hochladen von Absturzberichten an Microsoft.', "es": 'Bloquea mediante firewall el envío de informes de fallos de aplicaciones a Microsoft.'},
    "priv_desc_medium_task_appraiser": {"en": "Disables the scheduled task that checks if your PC/apps are ready for a newer Windows version.", "pl": "Wyłącza zadanie sprawdzające zgodność Twojego sprzętu i programów z nowszą wersją Windows.", "fr": "Désactive la tâche qui vérifie la compatibilité avec une version plus récente de Windows.", "de": 'Deaktiviert die geplante Aufgabe, die prüft, ob Ihr PC/Ihre Apps für eine neuere Windows-Version bereit sind.', "es": 'Desactiva la tarea programada que comprueba si tu PC/aplicaciones están listas para una versión más reciente de Windows.'},
    "priv_desc_medium_task_programdata": {"en": "Disables the scheduled task that collects data about your installed programs.", "pl": "Wyłącza zadanie zbierające dane o zainstalowanych na komputerze programach.", "fr": "Désactive la tâche qui collecte des données sur vos programmes installés.", "de": 'Deaktiviert die geplante Aufgabe, die Daten über Ihre installierten Programme sammelt.', "es": 'Desactiva la tarea programada que recopila datos sobre tus programas instalados.'},
    "priv_desc_medium_task_consolidator": {"en": "Disables the task that uploads the telemetry data gathered by CEIP.", "pl": "Wyłącza zadanie wysyłające zebrane dane telemetryczne w ramach programu CEIP.", "fr": "Désactive la tâche qui envoie les données de télémétrie collectées par le CEIP.", "de": 'Deaktiviert die Aufgabe, die die von CEIP gesammelten Telemetriedaten hochlädt.', "es": 'Desactiva la tarea que envía los datos de telemetría recopilados por el CEIP.'},
    "priv_desc_medium_task_usbceip": {"en": "Disables the scheduled task that collects data about USB devices you plug in.", "pl": "Wyłącza zadanie zbierające dane o podłączanych do komputera urządzeniach USB.", "fr": "Désactive la tâche qui collecte des données sur les périphériques USB branchés.", "de": 'Deaktiviert die geplante Aufgabe, die Daten über angeschlossene USB-Geräte sammelt.', "es": 'Desactiva la tarea programada que recopila datos sobre los dispositivos USB que conectas.'},
    "priv_desc_medium_task_queuereporting": {"en": "Disables the scheduled task that queues and sends system error reports.", "pl": "Wyłącza zadanie kolejkujące i wysyłające raporty o błędach systemu.", "fr": "Désactive la tâche qui met en file d'attente et envoie les rapports d'erreurs système.", "de": 'Deaktiviert die geplante Aufgabe, die Systemfehlerberichte in die Warteschlange stellt und sendet.', "es": 'Desactiva la tarea programada que pone en cola y envía informes de errores del sistema.'},
    "priv_desc_medium_task_kernelceip": {"en": "Disables the scheduled task that collects kernel-level diagnostic data for Microsoft's Customer Experience Improvement Program.", "pl": "Wyłącza zadanie zbierające dane diagnostyczne na poziomie jądra dla Programu ulepszania jakości.", "fr": "Désactive la tâche qui collecte des données de diagnostic au niveau du noyau pour le programme d'amélioration.", "de": 'Deaktiviert die geplante Aufgabe, die Diagnosedaten auf Kernel-Ebene für das Programm zur Verbesserung der Benutzerfreundlichkeit sammelt.', "es": 'Desactiva la tarea programada que recopila datos de diagnóstico a nivel de kernel para el Programa de mejora de la experiencia del cliente.'},
    "priv_desc_medium_task_diskdiagnostic": {"en": "Disables the scheduled task that collects diagnostic data about your disk's health and reports it to Microsoft.", "pl": "Wyłącza zadanie zbierające dane diagnostyczne o stanie dysku i wysyłające je do Microsoftu.", "fr": "Désactive la tâche qui collecte des données de diagnostic sur l'état du disque et les envoie à Microsoft.", "de": 'Deaktiviert die geplante Aufgabe, die Diagnosedaten zum Zustand Ihrer Festplatte sammelt und an Microsoft meldet.', "es": 'Desactiva la tarea programada que recopila datos de diagnóstico sobre el estado del disco y los envía a Microsoft.'},
    "priv_desc_medium_task_siuf_dmclient": {"en": "Disables the scheduled task behind Windows feedback prompts and diagnostic data uploads.", "pl": "Wyłącza zadanie odpowiadające za prośby o opinię w Windows i wysyłanie danych diagnostycznych.", "fr": "Désactive la tâche à l'origine des demandes d'avis Windows et de l'envoi de données de diagnostic.", "de": 'Deaktiviert die geplante Aufgabe hinter den Windows-Feedback-Aufforderungen und dem Hochladen von Diagnosedaten.', "es": 'Desactiva la tarea programada responsable de las solicitudes de opinión de Windows y el envío de datos de diagnóstico.'},
    "priv_desc_medium_task_siuf_dmclientonscenario": {"en": "Disables the companion task that triggers feedback prompts after specific system scenarios (e.g. after an update).", "pl": "Wyłącza powiązane zadanie wywołujące prośby o opinię po określonych zdarzeniach systemowych (np. po aktualizacji).", "fr": "Désactive la tâche associée qui déclenche des demandes d'avis après certains scénarios système (par ex. après une mise à jour).", "de": 'Deaktiviert die zugehörige Aufgabe, die nach bestimmten Systemereignissen (z. B. nach einem Update) Feedback-Aufforderungen auslöst.', "es": 'Desactiva la tarea asociada que activa solicitudes de opinión tras determinados eventos del sistema (p. ej., tras una actualización).'},
    "priv_desc_advanced_svc_wersvc": {"en": "Stops the crash-reporting service — you'll lose crash/BSOD report collection.", "pl": "Zatrzymuje usługę zbierania raportów o awariach — stracisz zbieranie raportów awarii/BSOD.", "fr": "Arrête le service de rapport de plantage — vous perdrez la collecte des rapports BSOD.", "de": 'Stoppt den Absturzberichtsdienst — Sie verlieren die Sammlung von Absturz-/BSOD-Berichten.', "es": 'Detiene el servicio de informes de fallos — perderás la recopilación de informes de fallos/BSOD.'},
    "priv_desc_advanced_svc_pcasvc": {"en": "Stops the Program Compatibility Assistant — you'll lose warnings about incompatible older software.", "pl": "Zatrzymuje Asystenta zgodności programów — stracisz ostrzeżenia o niekompatybilności starszego oprogramowania.", "fr": "Arrête l'Assistant de compatibilité — vous perdrez les avertissements de compatibilité.", "de": 'Stoppt den Programmkompatibilitäts-Assistenten — Sie verlieren Warnungen zu inkompatibler älterer Software.', "es": 'Detiene el Asistente de compatibilidad de programas — perderás las advertencias sobre software antiguo incompatible.'},
    "priv_desc_advanced_reg_activityfeed": {"en": "Turns off Timeline — the history of files and apps you've opened.", "pl": "Wyłącza funkcję Osi czasu — historię otwieranych plików i aplikacji.", "fr": "Désactive la Chronologie — l'historique des fichiers et applications ouverts.", "de": 'Deaktiviert die Zeitleiste — den Verlauf geöffneter Dateien und Apps.', "es": 'Desactiva la Cronología — el historial de archivos y aplicaciones que has abierto.'},
    "priv_desc_advanced_reg_publishactivities": {"en": "Stops Windows from recording your activity (opened files/apps) at all.", "pl": "Blokuje zapisywanie Twojej aktywności (otwierane pliki/aplikacje) w systemie.", "fr": "Empêche Windows d'enregistrer votre activité (fichiers/applications ouverts).", "de": 'Verhindert, dass Windows Ihre Aktivität (geöffnete Dateien/Apps) überhaupt aufzeichnet.', "es": 'Impide que Windows registre tu actividad (archivos/aplicaciones abiertos) por completo.'},
    "priv_desc_advanced_reg_uploadactivities": {"en": "Stops your activity history from being uploaded to Microsoft's cloud — you'll lose 'continue on another device'.", "pl": "Blokuje wysyłanie Twojej aktywności do chmury Microsoft — stracisz funkcję 'kontynuuj na innym urządzeniu'.", "fr": "Empêche l'envoi de votre historique d'activité vers le cloud — vous perdrez « continuer sur un autre appareil ».", "de": 'Verhindert, dass Ihr Aktivitätsverlauf in die Microsoft-Cloud hochgeladen wird — Sie verlieren „Auf einem anderen Gerät fortsetzen".', "es": "Impide que tu historial de actividad se suba a la nube de Microsoft — perderás 'continuar en otro dispositivo'."},
    "priv_desc_extra_svc_lfsvc": {"en": "Stops the Windows Geolocation Service — Weather, Maps and other apps will stop detecting your location.", "pl": "Zatrzymuje usługę lokalizacji Windows — pogoda, mapy i inne aplikacje przestaną widzieć Twoją lokalizację.", "fr": "Arrête le service de géolocalisation Windows — Météo, Cartes et autres apps ne détecteront plus votre position.", "de": 'Stoppt den Windows-Geolokalisierungsdienst — Wetter, Karten und andere Apps erkennen Ihren Standort nicht mehr.', "es": 'Detiene el servicio de geolocalización de Windows — Tiempo, Mapas y otras apps dejarán de detectar tu ubicación.'},
    "priv_desc_extra_reg_disablelocation": {"en": "Backup safeguard — blocks location even if the service gets turned back on.", "pl": "Dodatkowe zabezpieczenie — blokuje lokalizację, nawet gdyby usługa się włączyła.", "fr": "Verrou de secours — bloque la position même si le service redémarre.", "de": 'Zusätzliche Absicherung — blockiert den Standort selbst bei neu gestartetem Dienst.', "es": 'Bloqueo de respaldo — funciona aunque el servicio se reactive por sí solo.'},
    "priv_desc_extra_reg_text_collection": {"en": "Stops Windows from collecting samples of what you type to improve text suggestions.", "pl": "Zatrzymuje zbieranie przez Windows próbek tego, co piszesz, do ulepszania sugestii tekstu.", "fr": "Empêche Windows de collecter des échantillons de ce que vous tapez pour améliorer les suggestions de texte.", "de": 'Verhindert, dass Windows Proben Ihrer Eingaben sammelt, um Textvorschläge zu verbessern.', "es": 'Impide que Windows recopile muestras de lo que escribes para mejorar las sugerencias de texto.'},
    "priv_desc_extra_reg_ink_collection": {"en": "Stops Windows from collecting samples of your handwriting input to improve handwriting recognition.", "pl": "Zatrzymuje zbieranie przez Windows próbek pisma odręcznego do ulepszania jego rozpoznawania.", "fr": "Empêche Windows de collecter des échantillons de votre écriture manuscrite pour améliorer la reconnaissance.", "de": 'Verhindert, dass Windows Proben Ihrer Handschrift sammelt, um die Handschrifterkennung zu verbessern.', "es": 'Impide que Windows recopile muestras de tu escritura a mano para mejorar su reconocimiento.'},
    "priv_desc_extra_reg_personalization_policy": {"en": "Revokes consent for handwriting/typing personalization, disabling it at the source.", "pl": "Cofa zgodę na personalizację pisma/pisania, wyłączając ją u źródła.", "fr": "Révoque le consentement à la personnalisation de l'écriture, la désactivant à la source.", "de": 'Widerruft die Zustimmung zur Personalisierung von Handschrift/Eingabe und deaktiviert sie damit an der Quelle.', "es": 'Revoca el consentimiento para la personalización de escritura, desactivándola en el origen.'},
    "priv_desc_extra_reg_cross_device_clipboard": {"en": "Blocks Cloud Clipboard from syncing copied content (text, links, images) to your other devices via Microsoft's cloud.", "pl": "Blokuje synchronizację schowka (skopiowany tekst, linki, obrazy) z innymi Twoimi urządzeniami przez chmurę Microsoft.", "fr": "Empêche le presse-papiers cloud de synchroniser le contenu copié (texte, liens, images) vers vos autres appareils via le cloud Microsoft.", "de": 'Verhindert, dass die Cloud-Zwischenablage kopierte Inhalte (Text, Links, Bilder) über die Microsoft-Cloud mit Ihren anderen Geräten synchronisiert.', "es": 'Bloquea que el portapapeles en la nube sincronice el contenido copiado (texto, enlaces, imágenes) con tus otros dispositivos a través de la nube de Microsoft.'},
    "priv_desc_extra_reg_findmydevice": {"en": "Stops this device reporting its location to Microsoft's cloud — after this, 'Find My Device' will no longer know where this computer is.", "pl": "Wyłącza raportowanie lokalizacji do chmury Microsoft — po tej zmianie funkcja 'Znajdź moje urządzenie' przestanie wiedzieć, gdzie jest ten komputer.", "fr": "Empêche cet appareil d'envoyer sa position au cloud Microsoft — la fonction « Localiser mon appareil » ne saura plus où il se trouve.", "de": 'Verhindert, dass dieses Gerät seinen Standort an die Microsoft-Cloud meldet — „Mein Gerät suchen" weiß danach nicht mehr, wo es sich befindet.', "es": "Impide que este equipo reporte su ubicación a la nube de Microsoft — 'Encontrar mi dispositivo' ya no sabrá dónde está."},
    "priv_gear_tooltip": {"en": "Show individual items", "pl": "Pokaż pojedyncze elementy", "fr": "Afficher les éléments individuels", "de": 'Einzelne Elemente anzeigen', "es": 'Mostrar elementos individuales'},
    "priv_level_status": {"en": "{active} of {total} active", "pl": "{active} z {total} aktywnych", "fr": "{active} sur {total} actifs", "de": '{active} von {total} aktiv', "es": '{active} de {total} activas'},
    "priv_level_status_drift": {"en": "⚠ Settings changed by the system: {n} — click to review", "pl": "⚠ Ustawienia zmienione przez system: {n} — kliknij, by sprawdzić", "fr": "⚠ Paramètres modifiés par le système : {n} — cliquez pour vérifier", "de": '⚠ Vom System geänderte Einstellungen: {n} — klicken Sie zum Überprüfen', "es": '⚠ Ajustes cambiados por el sistema: {n} — haz clic para revisar'},
    "priv_item_drift_tooltip": {"en": "This setting was reset by Windows (e.g. a major update). It's still checked here — click 'Apply' to enforce it again.", "pl": "To ustawienie zostało zresetowane przez Windows (np. przy dużej aktualizacji). Nadal jest tu zaznaczone — kliknij 'Zastosuj', żeby wymusić je ponownie.", "fr": "Ce paramètre a été réinitialisé par Windows (ex. mise à jour majeure). Il reste coché ici — cliquez sur « Appliquer » pour le forcer à nouveau.", "de": 'Diese Einstellung wurde von Windows zurückgesetzt (z. B. bei einem großen Update). Sie ist hier weiterhin aktiviert — klicken Sie auf „Anwenden", um sie erneut durchzusetzen.', "es": "Esta opción fue restablecida por Windows (por ejemplo, en una actualización importante). Sigue marcada aquí — haz clic en 'Aplicar' para forzarla de nuevo."},
    "priv_item_missing_suffix": {"en": "(unavailable)", "pl": "(niedostępne)", "fr": "(indisponible)", "de": '(nicht verfügbar)', "es": '(no disponible)'},
    "priv_item_missing_tooltip": {"en": "This feature doesn't exist on this edition/version of Windows — there's nothing here for HOTS to protect, so it can't be enabled.", "pl": "Ta funkcja nie istnieje w tej edycji/wersji Windows — nie ma tu nic, co HOTS mógłby chronić, więc nie da się jej włączyć.", "fr": "Cette fonctionnalité n'existe pas dans cette édition/version de Windows — il n'y a rien ici à protéger, elle ne peut donc pas être activée.", "de": 'Diese Funktion existiert in dieser Edition/Version von Windows nicht — es gibt hier nichts, das HOTS schützen könnte, daher kann sie nicht aktiviert werden.', "es": 'Esta función no existe en esta edición/versión de Windows — no hay nada aquí que HOTS pueda proteger, por lo que no se puede activar.'},
    "priv_toggle_active_tooltip": {"en": "Blocking active", "pl": "Blokada aktywna", "fr": "Blocage actif", "de": 'Sperre aktiv', "es": 'Bloqueo activo'},
    "priv_toggle_inactive_tooltip": {"en": "Blocking inactive", "pl": "Blokada nieaktywna", "fr": "Blocage inactif", "de": 'Sperre inaktiv', "es": 'Bloqueo inactivo'},
    "priv_checklist_apply_btn": {"en": "Apply selection", "pl": "Zastosuj zmiany", "fr": "Appliquer la sélection", "de": 'Auswahl anwenden', "es": 'Aplicar selección'},
    "priv_checklist_hint": {"en": "Select the items you want to protect and click “Apply changes”. Unchecked items will not be protected.",
                             "pl": "Zaznacz elementy, które chcesz chronić i kliknij „Zastosuj zmiany”. Odznaczone pozycje nie będą chronione.",
                             "fr": "Sélectionnez les éléments que vous souhaitez protéger et cliquez sur « Appliquer les modifications ». Les éléments décochés ne seront pas protégés.",
                             "de": 'Wählen Sie die Elemente aus, die Sie schützen möchten, und klicken Sie auf „Änderungen anwenden". Nicht ausgewählte Elemente werden nicht geschützt.',
                             "es": 'Selecciona los elementos que deseas proteger y haz clic en «Aplicar cambios». Los elementos no marcados no estarán protegidos.',
                         },
    "priv_tweak_advertising_id": {"en": "Advertising ID (Enabled = 0)", "pl": "Identyfikator reklamowy (Enabled = 0)", "fr": "ID publicitaire (Enabled = 0)", "de": 'Werbe-ID (Enabled = 0)', "es": 'ID de publicidad (Enabled = 0)'},
    "priv_tweak_advertising_id_tooltip": {
        "en": "Turns off the per-user Advertising ID used by apps to personalize ads.",
        "pl": "Wyłącza identyfikator reklamowy (per-użytkownik), używany przez aplikacje do personalizacji reklam.",
        "fr": "Désactive l'ID publicitaire par utilisateur utilisé pour personnaliser les publicités.",
    
        "de": 'Deaktiviert die benutzerbezogene Werbe-ID, die von Apps zur Personalisierung von Werbung verwendet wird.',
        "es": 'Desactiva el ID de publicidad por usuario que las aplicaciones utilizan para personalizar anuncios.',
    },
    "priv_tweak_bing_search": {"en": "Bing search in Start Menu (BingSearchEnabled = 0)", "pl": "Wyniki wyszukiwania Bing w Menu Start (BingSearchEnabled = 0)", "fr": "Recherche Bing dans le menu Démarrer (BingSearchEnabled = 0)", "de": 'Bing-Suche im Startmenü (BingSearchEnabled = 0)', "es": 'Búsqueda de Bing en el menú Inicio (BingSearchEnabled = 0)'},
    "priv_tweak_bing_search_tooltip": {
        "en": "Stops Start Menu search from sending your queries to Bing over the web.",
        "pl": "Zatrzymuje wysyłanie zapytań z wyszukiwania w menu Start do Bing przez internet.",
        "fr": "Empêche la recherche du menu Démarrer d'envoyer vos requêtes à Bing.",
    
        "de": 'Verhindert, dass die Startmenü-Suche Ihre Anfragen über das Web an Bing sendet.',
        "es": 'Impide que la búsqueda del menú Inicio envíe tus consultas a Bing a través de internet.',
    },
    "priv_tweak_search_suggestions": {"en": "Search box internet suggestions (DisableSearchBoxSuggestions = 1)", "pl": "Podpowiedzi z internetu w wyszukiwarce (DisableSearchBoxSuggestions = 1)", "fr": "Suggestions internet dans la recherche (DisableSearchBoxSuggestions = 1)", "de": 'Internetvorschläge im Suchfeld (DisableSearchBoxSuggestions = 1)', "es": 'Sugerencias de internet en el buscador (DisableSearchBoxSuggestions = 1)'},
    "priv_tweak_search_suggestions_tooltip": {
        "en": "Disables suggestions shown while typing in the taskbar search box.",
        "pl": "Wyłącza podpowiedzi pokazywane podczas pisania w polu wyszukiwania na pasku zadań.",
        "fr": "Désactive les suggestions affichées lors de la saisie dans la barre de recherche.",
    
        "de": 'Deaktiviert Vorschläge, die beim Tippen im Suchfeld der Taskleiste angezeigt werden.',
        "es": 'Desactiva las sugerencias que aparecen al escribir en el cuadro de búsqueda de la barra de tareas.',
    },
    "par_cat_pinterest":    {"en": "Block Pinterest",             "pl": "Blokada Pinterest",                "fr": "Bloquer Pinterest", "de": 'Pinterest blockieren', "es": 'Bloquear Pinterest'},
    "par_cat_reddit":       {"en": "Block Reddit",                "pl": "Blokada Reddit",                   "fr": "Bloquer Reddit", "de": 'Reddit blockieren', "es": 'Bloquear Reddit'},
    "par_cat_games":        {"en": "Block Games",                 "pl": "Blokada Gier",                     "fr": "Bloquer les jeux", "de": 'Spiele blockieren', "es": 'Bloquear juegos'},
    "par_cat_torrent":      {"en": "Block Torrent",               "pl": "Blokada Torrent",                   "fr": "Bloquer Torrent", "de": 'Torrent blockieren', "es": 'Bloquear Torrent'},
    "par_cat_antispy_domains": {"en": "Block telemetry domains",
                             "pl": "Blokada domen telemetrycznych",
                             "fr": "Bloquer les domaines de télémétrie",
                             "de": 'Telemetrie-Domains blockieren',
                             "es": 'Bloquear dominios de telemetría',
                         },
    "priv_telemetry_domains_tooltip": {
        "en": "Blocks Windows telemetry at the hosts file level, so connection attempts to the "
              "listed telemetry domains fail.",
        "pl": "Blokuje telemetrię Windows na poziomie pliku hosts, dzięki czemu próby połączenia "
              "z wymienionymi domenami telemetrycznymi kończą się niepowodzeniem.",
        "fr": "Bloque la télémétrie Windows au niveau du fichier hosts, ce qui fait échouer les "
              "tentatives de connexion aux domaines de télémétrie listés.",
        "de": "Blockiert die Windows-Telemetrie auf Ebene der Hosts-Datei, sodass "
              "Verbindungsversuche zu den aufgeführten Telemetrie-Domains fehlschlagen.",
        "es": "Bloquea la telemetría de Windows a nivel del archivo hosts, lo que hace fallar los "
              "intentos de conexión a los dominios de telemetría indicados.",
    },

    "par_comment_prefix": {"en": "Blocked", "pl": "Zablokowano", "fr": "Bloqué", "de": 'Blockiert', "es": 'Bloqueado'},
    "par_comment_name_adult":     {"en": "Adult Content", "pl": "Treści dla dorosłych", "fr": "Contenu adulte", "de": 'Inhalte für Erwachsene', "es": 'Contenido para adultos'},
    "par_comment_name_twitter":   {"en": "Twitter",       "pl": "Twitter",              "fr": "Twitter", "de": 'Twitter', "es": 'Twitter'},
    "par_comment_name_instagram": {"en": "Instagram",     "pl": "Instagram",            "fr": "Instagram", "de": 'Instagram', "es": 'Instagram'},
    "par_comment_name_youtube":   {"en": "YouTube",       "pl": "YouTube",              "fr": "YouTube", "de": 'YouTube', "es": 'YouTube'},
    "par_comment_name_facebook":  {"en": "Facebook",      "pl": "Facebook",             "fr": "Facebook", "de": 'Facebook', "es": 'Facebook'},
    "par_comment_name_whatsapp":  {"en": "WhatsApp",      "pl": "WhatsApp",             "fr": "WhatsApp", "de": 'WhatsApp', "es": 'WhatsApp'},
    "par_comment_name_tiktok":    {"en": "TikTok",        "pl": "TikTok",               "fr": "TikTok", "de": 'TikTok', "es": 'TikTok'},
    "par_comment_name_twitch":    {"en": "Twitch",        "pl": "Twitch",               "fr": "Twitch", "de": 'Twitch', "es": 'Twitch'},
    "par_comment_name_snapchat":  {"en": "Snapchat",      "pl": "Snapchat",             "fr": "Snapchat", "de": 'Snapchat', "es": 'Snapchat'},
    "par_comment_name_pinterest": {"en": "Pinterest",     "pl": "Pinterest",            "fr": "Pinterest", "de": 'Pinterest', "es": 'Pinterest'},
    "par_comment_name_reddit":    {"en": "Reddit",        "pl": "Reddit",               "fr": "Reddit", "de": 'Reddit', "es": 'Reddit'},
    "par_comment_name_games":     {"en": "Games",         "pl": "Gry",                  "fr": "Jeux", "de": 'Spiele', "es": 'Juegos'},
    "par_comment_name_torrent":   {"en": "Torrent",       "pl": "Torrent",              "fr": "Torrent", "de": 'Torrent', "es": 'Torrent'},
    "par_comment_name_dating":       {"en": "Dating Sites",     "pl": "Serwisy randkowe",       "fr": "Sites de rencontre", "de": 'Dating-Seiten', "es": 'Sitios de citas'},
    "par_comment_name_random_chat":  {"en": "Random Video Chat", "pl": "Losowy czat wideo",      "fr": "Chat vidéo aléatoire", "de": 'Zufälliger Video-Chat', "es": 'Chat de vídeo aleatorio'},
    "par_comment_name_telemetry": {"en": "Telemetry Domains", "pl": "Domeny telemetryczne", "fr": "Domaines de télémétrie", "de": 'Telemetrie-Domains', "es": 'Dominios de telemetría'},
    "par_comment_name_custom_domains": {"en": "Custom Domains", "pl": "Własne domeny", "fr": "Domaines personnalisés", "de": 'Eigene Domains', "es": 'Dominios personalizados'},

    "par_cat_custom": {"en": "Block your own domains", "pl": "Blokada własnych domen", "fr": "Bloquer vos propres domaines", "de": 'Eigene Domains blockieren', "es": 'Bloquear tus propios dominios'},
    "par_custom_domains_tooltip": {
        "en": "Lets you block websites yourself at the hosts file level. Type in the domain "
              "names you want to block (e.g. example.com).\n\n"
              "The list of blocked domains is stored in a safe location, so you'll be able to "
              "use it again after restoring the hosts file or uninstalling the program.",
        "pl": "Pozwala samodzielnie zablokować strony internetowe na poziomie pliku hosts. "
              "Wpisz nazwy domen, które chcesz zablokować (np. przykład.pl).\n\n"
              "Lista zablokowanych domen znajduje się w bezpiecznym miejscu, więc po "
              "przywróceniu pliku hosts lub odinstalowaniu programu będziesz mógł z niej "
              "ponownie skorzystać.",
        "fr": "Vous permet de bloquer vous-même des sites web au niveau du fichier hosts. "
              "Saisissez les noms de domaine à bloquer (par ex. exemple.fr).\n\n"
              "La liste des domaines bloqués est stockée dans un emplacement sûr, vous pourrez "
              "donc la réutiliser après une restauration du fichier hosts ou une "
              "désinstallation du programme.",
        "de": "Ermöglicht es Ihnen, Websites selbst auf Ebene der Hosts-Datei zu sperren. "
              "Geben Sie die zu blockierenden Domainnamen ein (z. B. beispiel.de).\n\n"
              "Die Liste der blockierten Domains wird an einem sicheren Ort gespeichert, "
              "sodass Sie sie nach dem Wiederherstellen der Hosts-Datei oder dem "
              "Deinstallieren des Programms erneut nutzen können.",
        "es": "Te permite bloquear tú mismo sitios web a nivel del archivo hosts. Escribe los "
              "nombres de dominio que quieras bloquear (p. ej. ejemplo.es).\n\n"
              "La lista de dominios bloqueados se guarda en un lugar seguro, así que podrás "
              "volver a usarla después de restaurar el archivo hosts o desinstalar el "
              "programa.",
    },
    "par_custom_count": {"en": "{n} domain(s) on the list", "pl": "Domen na liście: {n}", "fr": "{n} domaine(s) dans la liste", "de": '{n} Domain(s) in der Liste', "es": '{n} dominio(s) en la lista'},
    "par_custom_empty": {"en": "List is empty - add domains", "pl": "Lista jest pusta - dodaj domeny", "fr": "La liste est vide - ajoutez des domaines", "de": 'Liste ist leer - Domains hinzufügen', "es": 'La lista está vacía - añade dominios'},
    "par_custom_empty_btn": {"en": "Empty list", "pl": "Pusta lista", "fr": "Liste vide", "de": 'Liste leer', "es": 'Lista vacía'},
    "par_custom_edit_btn": {"en": "Edit", "pl": "Edytuj", "fr": "Modifier", "de": 'Bearbeiten', "es": 'Editar'},

    "par_custom_dialog_title": {"en": "Your domains", "pl": "Twoje domeny", "fr": "Vos domaines", "de": 'Ihre Domains', "es": 'Tus dominios'},
    "par_custom_dialog_hint": {
        "en": "One domain per line (e.g. example.com). Wildcards (*) are not supported by the Windows hosts file.",
        "pl": "Jedna domena w linii (np. przyklad.pl). Windows hosts nie obsługuje symboli wieloznacznych (*).",
        "fr": "Un domaine par ligne (ex. exemple.com). Le fichier hosts de Windows ne prend pas en charge les jokers (*).",
        "de": 'Eine Domain pro Zeile (z. B. beispiel.de). Platzhalter (*) werden von der Windows-hosts-Datei nicht unterstützt.',
        "es": 'Un dominio por línea (p. ej. ejemplo.com). El archivo hosts de Windows no admite comodines (*).',
    },
    "par_custom_placeholder": {
        "en": "example.com\nanother-site.org",
        "pl": "przyklad.pl\ninny-serwis.pl",
        "fr": "exemple.com\nautre-site.org",
        "de": 'beispiel.de\nanderer-seite.org',
        "es": 'ejemplo.com\notro-sitio.org',
    },
    "par_custom_err_title": {"en": "Invalid domains", "pl": "Nieprawidłowe domeny", "fr": "Domaines invalides", "de": 'Ungültige Domains', "es": 'Dominios no válidos'},
    "par_custom_err_msg": {
        "en": "The following lines are not valid domains and were not saved:\n{list}",
        "pl": "Poniższe linie nie są prawidłowymi domenami i nie zostały zapisane:\n{list}",
        "fr": "Les lignes suivantes ne sont pas des domaines valides et n'ont pas été enregistrées :\n{list}",
        "de": 'Die folgenden Zeilen sind keine gültigen Domains und wurden nicht gespeichert:\n{list}',
        "es": 'Las siguientes líneas no son dominios válidos y no se guardaron:\n{list}',
    },
    "par_custom_saved_title": {"en": "Saved", "pl": "Zapisano", "fr": "Enregistré", "de": 'Gespeichert', "es": 'Guardado'},
    "par_custom_saved_msg": {"en": "{n} domain(s) saved.", "pl": "Zapisano domen: {n}.", "fr": "{n} domaine(s) enregistré(s).", "de": '{n} Domain(s) gespeichert.', "es": '{n} dominio(s) guardado(s).'},
    "antispy_watchdog_title": {"en": "Privacy protection changed",
                             "pl": "Ochrona prywatności została zmieniona",
                             "fr": "La protection de la confidentialité a changé",
                             "de": 'Datenschutz geändert',
                             "es": 'La protección de privacidad ha cambiado',
                         },
    "antispy_watchdog_msg": {"en": "Windows appears to have reset part of your privacy protection ({modules}), for example during an update. Reapply it?",
                             "pl": "Wygląda na to, że Windows (np. przy aktualizacji) przywrócił część ochrony prywatności ({modules}). Zastosować ją ponownie?",
                             "fr": "Windows semble avoir réinitialisé une partie de votre protection de la confidentialité ({modules}), par exemple lors d'une mise à jour. La réappliquer ?",
                             "de": 'Windows hat anscheinend einen Teil Ihres Datenschutzes zurückgesetzt ({modules}), zum Beispiel während eines Updates. Erneut anwenden?',
                             "es": 'Parece que Windows ha restablecido parte de tu protección de privacidad ({modules}), por ejemplo durante una actualización. ¿Volver a aplicarla?',
                         },
    "antispy_watchdog_reapply_btn": {"en": "Reapply", "pl": "Zastosuj ponownie", "fr": "Réappliquer", "de": 'Erneut anwenden', "es": 'Volver a aplicar'},
    "antispy_watchdog_reapply_success": {
        "en": "Privacy protection has been restored.",
        "pl": "Ochrona prywatności została przywrócona.",
        "fr": "La protection de la confidentialité a été restaurée.",
    
        "de": 'Der Datenschutz wurde wiederhergestellt.',
        "es": 'La protección de privacidad ha sido restaurada.',
    },
    "antispy_watchdog_restored_title": {
        "en": "Privacy protection restored",
        "pl": "Ochrona prywatności przywrócona",
        "fr": "Protection de la confidentialité restaurée",
    
        "de": 'Datenschutz wiederhergestellt',
        "es": 'Protección de privacidad restaurada',
    },
    "antispy_watchdog_restored_msg": {
        "en": "Part of your privacy protection ({modules}) was turned back on outside the app.",
        "pl": "Część ochrony prywatności ({modules}) została włączona poza aplikacją.",
        "fr": "Une partie de votre protection de la confidentialité ({modules}) a été réactivée en dehors de l'application.",
    
        "de": 'Ein Teil Ihres Datenschutzes ({modules}) wurde außerhalb der App wieder aktiviert.',
        "es": 'Parte de tu protección de privacidad ({modules}) se volvió a activar fuera de la aplicación.',
    },

    "antispy_err_unknown_item": {"en": "Unknown item: {id}", "pl": "Nieznany element: {id}", "fr": "Élément inconnu : {id}", "de": 'Unbekanntes Element: {id}', "es": 'Elemento desconocido: {id}'},
    "antispy_err_no_admin": {"en": "Administrator rights are required.", "pl": "Brak uprawnień administratora.", "fr": "Des droits administrateur sont requis.", "de": 'Administratorrechte sind erforderlich.', "es": 'Se requieren derechos de administrador.'},
    "antispy_warn_service_missing": {
        "en": "Service '{service}' doesn't exist on this Windows edition — skipped.",
        "pl": "Usługa '{service}' nie istnieje w tej edycji Windows — pominięto.",
        "fr": "Le service « {service} » n'existe pas dans cette édition de Windows — ignoré.",
    
        "de": 'Der Dienst „{service}" existiert in dieser Windows-Edition nicht — übersprungen.',
        "es": "El servicio '{service}' no existe en esta edición de Windows — omitido.",
    },
    "antispy_warn_service_disable_failed": {
        "en": "Couldn't fully disable service {service}",
        "pl": "Nie udało się w pełni wyłączyć usługi {service}",
        "fr": "Impossible de désactiver complètement le service {service}",
    
        "de": 'Der Dienst {service} konnte nicht vollständig deaktiviert werden',
        "es": 'No se pudo desactivar completamente el servicio {service}',
    },
    "antispy_warn_exe_missing": {
        "en": "File '{exe}' doesn't exist on this Windows edition — firewall rule skipped.",
        "pl": "Plik '{exe}' nie istnieje w tej edycji Windows — reguła zapory pominięta.",
        "fr": "Le fichier « {exe} » n'existe pas dans cette édition de Windows — règle de pare-feu ignorée.",
    
        "de": 'Die Datei „{exe}" existiert in dieser Windows-Edition nicht — Firewall-Regel übersprungen.',
        "es": "El archivo '{exe}' no existe en esta edición de Windows — regla de firewall omitida.",
    },
    "antispy_err_firewall_add_failed": {
        "en": "Couldn't add firewall rule: {rule}",
        "pl": "Nie udało się dodać reguły zapory: {rule}",
        "fr": "Impossible d'ajouter la règle de pare-feu : {rule}",
    
        "de": 'Firewall-Regel konnte nicht hinzugefügt werden: {rule}',
        "es": 'No se pudo añadir la regla de firewall: {rule}',
    },
    "antispy_err_ps_missing_task": {
        "en": "No PowerShell interpreter available — can't check task '{task}'.",
        "pl": "Brak interpretera PowerShell — nie można sprawdzić zadania '{task}'.",
        "fr": "Aucun interpréteur PowerShell disponible — impossible de vérifier la tâche « {task} ».",
    
        "de": 'Kein PowerShell-Interpreter verfügbar — Aufgabe „{task}" kann nicht geprüft werden.',
        "es": "No hay ningún intérprete de PowerShell disponible — no se puede comprobar la tarea '{task}'.",
    },
    "antispy_warn_task_missing": {
        "en": "Task '{task}' doesn't exist on this Windows edition — skipped.",
        "pl": "Zadanie '{task}' nie istnieje w tej edycji Windows — pominięto.",
        "fr": "La tâche « {task} » n'existe pas dans cette édition de Windows — ignorée.",
    
        "de": 'Die Aufgabe „{task}" existiert in dieser Windows-Edition nicht — übersprungen.',
        "es": "La tarea '{task}' no existe en esta edición de Windows — omitida.",
    },
    "antispy_warn_task_disable_failed": {
        "en": "Couldn't disable task: {task}",
        "pl": "Nie udało się wyłączyć zadania: {task}",
        "fr": "Impossible de désactiver la tâche : {task}",
    
        "de": 'Aufgabe konnte nicht deaktiviert werden: {task}',
        "es": 'No se pudo desactivar la tarea: {task}',
    },
    "antispy_warn_service_restore_failed": {
        "en": "Couldn't fully restore service {service}",
        "pl": "Nie udało się w pełni przywrócić usługi {service}",
        "fr": "Impossible de restaurer complètement le service {service}",
    
        "de": 'Der Dienst {service} konnte nicht vollständig wiederhergestellt werden',
        "es": 'No se pudo restaurar completamente el servicio {service}',
    },
    "antispy_warn_task_restore_failed": {
        "en": "Couldn't restore task: {task}",
        "pl": "Nie udało się przywrócić zadania: {task}",
        "fr": "Impossible de restaurer la tâche : {task}",
    
        "de": 'Aufgabe konnte nicht wiederhergestellt werden: {task}',
        "es": 'No se pudo restaurar la tarea: {task}',
    },
    "antispy_err_ps_missing_tasks_batch": {
        "en": "No PowerShell interpreter available (neither powershell.exe nor pwsh.exe) — can't check the state of scheduled tasks.",
        "pl": "Brak dostępnego interpretera PowerShell (ani powershell.exe, ani pwsh.exe) — nie można sprawdzić stanu zadań harmonogramu.",
        "fr": "Aucun interpréteur PowerShell disponible (ni powershell.exe, ni pwsh.exe) — impossible de vérifier l'état des tâches planifiées.",
    
        "de": 'Kein PowerShell-Interpreter verfügbar (weder powershell.exe noch pwsh.exe) — der Status geplanter Aufgaben kann nicht geprüft werden.',
        "es": 'No hay ningún intérprete de PowerShell disponible (ni powershell.exe ni pwsh.exe) — no se puede comprobar el estado de las tareas programadas.',
    },
    "antispy_err_ps_spawn_failed_tasks": {
        "en": "Couldn't start PowerShell — can't check the state of scheduled tasks.",
        "pl": "Nie udało się uruchomić PowerShell — nie można sprawdzić stanu zadań harmonogramu.",
        "fr": "Impossible de démarrer PowerShell — impossible de vérifier l'état des tâches planifiées.",
    
        "de": 'PowerShell konnte nicht gestartet werden — der Status geplanter Aufgaben kann nicht geprüft werden.',
        "es": 'No se pudo iniciar PowerShell — no se puede comprobar el estado de las tareas programadas.',
    },
    "antispy_err_ps_missing_task_check": {
        "en": "No PowerShell interpreter available (neither powershell.exe nor pwsh.exe) — can't check the state of task '{task}'.",
        "pl": "Brak dostępnego interpretera PowerShell (ani powershell.exe, ani pwsh.exe) — nie można sprawdzić stanu zadania '{task}'.",
        "fr": "Aucun interpréteur PowerShell disponible (ni powershell.exe, ni pwsh.exe) — impossible de vérifier l'état de la tâche « {task} ».",
    
        "de": 'Kein PowerShell-Interpreter verfügbar (weder powershell.exe noch pwsh.exe) — der Status der Aufgabe „{task}" kann nicht geprüft werden.',
        "es": "No hay ningún intérprete de PowerShell disponible (ni powershell.exe ni pwsh.exe) — no se puede comprobar el estado de la tarea '{task}'.",
    },
    "antispy_err_ps_missing_task_set": {
        "en": "No PowerShell interpreter available — can't change the state of task '{task}'.",
        "pl": "Brak interpretera PowerShell — nie można zmienić stanu zadania '{task}'.",
        "fr": "Aucun interpréteur PowerShell disponible — impossible de modifier l'état de la tâche « {task} ».",
    
        "de": 'Kein PowerShell-Interpreter verfügbar — der Status der Aufgabe „{task}" kann nicht geändert werden.',
        "es": "No hay ningún intérprete de PowerShell disponible — no se puede cambiar el estado de la tarea '{task}'.",
    },
    "antispy_warn_task_set_exception": {
        "en": "{verb} '{task}': {error}",
        "pl": "{verb} '{task}': {error}",
        "fr": "{verb} « {task} » : {error}",
    
        "de": '{verb} „{task}": {error}',
        "es": "{verb} '{task}': {error}",
    },
    "antispy_warn_sc_config_failed": {
        "en": "sc config {service}: code {code} ({stderr})",
        "pl": "sc config {service}: kod {code} ({stderr})",
        "fr": "sc config {service} : code {code} ({stderr})",
    
        "de": 'sc config {service}: Code {code} ({stderr})',
        "es": 'sc config {service}: código {code} ({stderr})',
    },
    "antispy_warn_net_stop_failed": {
        "en": "net stop {service}: code {code} ({stderr})",
        "pl": "net stop {service}: kod {code} ({stderr})",
        "fr": "net stop {service} : code {code} ({stderr})",
    
        "de": 'net stop {service}: Code {code} ({stderr})',
        "es": 'net stop {service}: código {code} ({stderr})',
    },
    "antispy_warn_net_start_failed": {
        "en": "net start {service}: code {code} ({stderr})",
        "pl": "net start {service}: kod {code} ({stderr})",
        "fr": "net start {service} : code {code} ({stderr})",
    
        "de": 'net start {service}: Code {code} ({stderr})',
        "es": 'net start {service}: código {code} ({stderr})',
    },
    "antispy_warn_firewall_rule_failed": {
        "en": "firewall rule {rule}: code {code} ({stderr})",
        "pl": "firewall rule {rule}: kod {code} ({stderr})",
        "fr": "firewall rule {rule} : code {code} ({stderr})",
    
        "de": 'firewall rule {rule}: Code {code} ({stderr})',
        "es": 'firewall rule {rule}: código {code} ({stderr})',
    },
    "priv_restore_detail_no_powershell": {
        "en": "No PowerShell interpreter available (neither powershell.exe nor pwsh.exe).",
        "pl": "Brak dostępnego interpretera PowerShell (ani powershell.exe, ani pwsh.exe).",
        "fr": "Aucun interpréteur PowerShell disponible (ni powershell.exe, ni pwsh.exe).",
    
        "de": 'Kein PowerShell-Interpreter verfügbar (weder powershell.exe noch pwsh.exe).',
        "es": 'No hay ningún intérprete de PowerShell disponible (ni powershell.exe ni pwsh.exe).',
    },
    "priv_restore_detail_timeout": {
        "en": "Timed out (120 s).",
        "pl": "Przekroczono czas oczekiwania (120 s).",
        "fr": "Délai dépassé (120 s).",
    
        "de": 'Zeitüberschreitung (120 s).',
        "es": 'Tiempo de espera agotado (120 s).',
    },
    "priv_restore_detail_unknown_error": {
        "en": "Unknown PowerShell error.",
        "pl": "Nieznany błąd PowerShell.",
        "fr": "Erreur PowerShell inconnue.",
    
        "de": 'Unbekannter PowerShell-Fehler.',
        "es": 'Error desconocido de PowerShell.',
    },
    "pwd_set_title":        {"en": "🔒  Password — HOTS Hosts lock",  "pl": "🔒  Hasło — blokada HOTS Hosts", "fr": "🔒  Mot de passe — verrou HOTS Hosts", "de": '🔒  Passwort — HOTS-Hosts-Sperre', "es": '🔒  Contraseña — bloqueo de HOTS Hosts'},
    "pwd_prompt_title":     {"en": "🔒  HOTS Hosts — password verification",  "pl": "🔒  HOTS Hosts — weryfikacja hasła",      "fr": "🔒  HOTS Hosts — vérification du mot de passe", "de": '🔒  HOTS Hosts — Passwortüberprüfung', "es": '🔒  HOTS Hosts — verificación de contraseña'},
    "pwd_info_on":          {"en": "Password is currently ENABLED.\nYou can change it or disable it completely.",
                             "pl": "Hasło jest aktualnie WŁĄCZONE.\nMożesz je zmienić lub całkowicie wyłączyć.",
                             "fr": "Le mot de passe est actuellement ACTIVÉ.\nVous pouvez le modifier ou le désactiver complètement.",
                             "de": 'Das Passwort ist derzeit AKTIVIERT.\nSie können es ändern oder vollständig deaktivieren.',
                             "es": 'La contraseña está actualmente ACTIVADA.\nPuedes cambiarla o desactivarla por completo.',
                         },
    "pwd_info_off":         {"en": "Password is currently DISABLED.\nEnter a password to protect the program from being launched.",
                             "pl": "Hasło jest aktualnie WYŁĄCZONE.\nWprowadź hasło, aby chronić program przed uruchomieniem.",
                             "fr": "Le mot de passe est actuellement DÉSACTIVÉ.\nEntrez un mot de passe pour protéger le programme.",
                             "de": 'Das Passwort ist derzeit DEAKTIVIERT.\nGeben Sie ein Passwort ein, um den Programmstart zu schützen.',
                             "es": 'La contraseña está actualmente DESACTIVADA.\nIntroduce una contraseña para proteger el inicio del programa.',
                         },
    "pwd_lbl_current":      {"en": "Current password:",           "pl": "Aktualne hasło:",                  "fr": "Mot de passe actuel:", "de": 'Aktuelles Passwort:', "es": 'Contraseña actual:'},
    "pwd_lbl_new":          {"en": "New password:",               "pl": "Nowe hasło:",                      "fr": "Nouveau mot de passe:", "de": 'Neues Passwort:', "es": 'Nueva contraseña:'},
    "pwd_lbl_repeat":       {"en": "Repeat new password:",        "pl": "Powtórz nowe hasło:",              "fr": "Répéter le nouveau mot de passe:", "de": 'Neues Passwort wiederholen:', "es": 'Repetir nueva contraseña:'},
    "pwd_btn_set":          {"en": "Set password",                "pl": "Ustaw hasło",                      "fr": "Définir le mot de passe", "de": 'Passwort festlegen', "es": 'Establecer contraseña'},
    "pwd_btn_remove":       {"en": "Remove password",             "pl": "Usuń hasło",                       "fr": "Supprimer le mot de passe", "de": 'Passwort entfernen', "es": 'Eliminar contraseña'},
    "pwd_btn_cancel":       {"en": "Cancel",                      "pl": "Anuluj",                           "fr": "Annuler", "de": 'Abbrechen', "es": 'Cancelar'},
    "pwd_btn_confirm":      {"en": "Confirm",                     "pl": "Zatwierdź",                        "fr": "Confirmer", "de": 'Bestätigen', "es": 'Confirmar'},
    "pwd_err_no_current":   {"en": "Enter the current password.", "pl": "Podaj aktualne hasło.",            "fr": "Entrez le mot de passe actuel.", "de": 'Geben Sie das aktuelle Passwort ein.', "es": 'Introduce la contraseña actual.'},
    "pwd_err_wrong":        {"en": "Current password is incorrect.", "pl": "Aktualne hasło jest nieprawidłowe.", "fr": "Le mot de passe actuel est incorrect.", "de": 'Das aktuelle Passwort ist falsch.', "es": 'La contraseña actual es incorrecta.'},
    "pwd_err_empty":        {"en": "New password cannot be empty.", "pl": "Nowe hasło nie może być puste.", "fr": "Le nouveau mot de passe ne peut pas être vide.", "de": 'Das neue Passwort darf nicht leer sein.', "es": 'La nueva contraseña no puede estar vacía.'},
    "pwd_err_too_short":    {"en": "Password must be at least 4 characters.", "pl": "Hasło musi mieć co najmniej 4 znaki.", "fr": "Le mot de passe doit contenir au moins 4 caractères.", "de": 'Das Passwort muss mindestens 4 Zeichen lang sein.', "es": 'La contraseña debe tener al menos 4 caracteres.'},
    "pwd_err_mismatch":     {"en": "Passwords do not match.",     "pl": "Hasła nie są identyczne.",         "fr": "Les mots de passe ne correspondent pas.", "de": 'Die Passwörter stimmen nicht überein.', "es": 'Las contraseñas no coinciden.'},
    "pwd_err_no_for_remove":{"en": "Enter the current password to remove it.", "pl": "Podaj aktualne hasło aby je usunąć.", "fr": "Entrez le mot de passe actuel pour le supprimer.", "de": 'Geben Sie das aktuelle Passwort ein, um es zu entfernen.', "es": 'Introduce la contraseña actual para eliminarla.'},
    "pwd_set_ok_title":     {"en": "Password set",                "pl": "Hasło ustawione",                  "fr": "Mot de passe défini", "de": 'Passwort festgelegt', "es": 'Contraseña establecida'},
    "pwd_set_ok_msg":       {"en": "Password set successfully.\nFrom the next launch, HOTS will require a password.",
                             "pl": "Hasło zostało pomyślnie ustawione.\nOd następnego uruchomienia HOTS będzie wymagał hasła.",
                             "fr": "Mot de passe défini avec succès.\nDès le prochain lancement, HOTS demandera un mot de passe.",
                             "de": 'Passwort erfolgreich festgelegt.\nAb dem nächsten Start wird HOTS ein Passwort verlangen.',
                             "es": 'Contraseña establecida correctamente.\nA partir del próximo inicio, HOTS requerirá una contraseña.',
                         },
    "pwd_remove_ok_title":  {"en": "Password removed",            "pl": "Hasło usunięte",                   "fr": "Mot de passe supprimé", "de": 'Passwort entfernt', "es": 'Contraseña eliminada'},
    "pwd_remove_ok_msg":    {"en": "Password removed.\nThe program will no longer require a password on launch.",
                             "pl": "Hasło zostało usunięte.\nProgram nie będzie już wymagał hasła przy uruchomieniu.",
                             "fr": "Mot de passe supprimé.\nLe programme ne demandera plus de mot de passe au lancement.",
                             "de": 'Passwort entfernt.\nDas Programm verlangt beim Start kein Passwort mehr.',
                             "es": 'Contraseña eliminada.\nEl programa ya no requerirá una contraseña al iniciarse.',
                         },
    "pwd_prompt_intro":     {"en": "HOTS Hosts is password-protected.\nEnter the password to continue.",
                             "pl": "Program HOTS Hosts jest chroniony hasłem.\nPodaj hasło, aby kontynuować.",
                             "fr": "Le programme HOTS Hosts est protégé par mot de passe.\nEntrez le mot de passe pour continuer.",
                             "de": 'HOTS Hosts ist passwortgeschützt.\nGeben Sie das Passwort ein, um fortzufahren.',
                             "es": 'HOTS Hosts está protegido con contraseña.\nIntroduce la contraseña para continuar.',
                         },
    "pwd_lbl_password":     {"en": "Password:",                   "pl": "Hasło:",                           "fr": "Mot de passe:", "de": 'Passwort:', "es": 'Contraseña:'},
    "pwd_err_empty_field":  {"en": "Enter password.",             "pl": "Podaj hasło.",                     "fr": "Entrez le mot de passe.", "de": 'Passwort eingeben.', "es": 'Introduce la contraseña.'},
    "pwd_err_wrong_retry":  {"en": "Incorrect password. Try again.", "pl": "Nieprawidłowe hasło. Spróbuj ponownie.", "fr": "Mot de passe incorrect. Réessayez.", "de": 'Falsches Passwort. Versuchen Sie es erneut.', "es": 'Contraseña incorrecta. Inténtalo de nuevo.'},
    "sup_title":            {"en": "Support the HOTS project",  "pl": "Wesprzyj projekt HOTS",        "fr": "Soutenir le projet HOTS", "de": 'Das HOTS-Projekt unterstützen', "es": 'Apoyar el proyecto HOTS'},
    "sup_subtitle":         {"en": "Windows Hosts File Editor",    "pl": "Windows Hosts File Editor",       "fr": "Windows Hosts File Editor", "de": 'Windows Hosts File Editor', "es": 'Windows Hosts File Editor'},
    "sup_greeting":         {"en": "Hi! I'm Darsono.",             "pl": "Cześć! Jestem Darsono.",          "fr": "Salut! Je suis Darsono.", "de": 'Hallo! Ich bin Darsono.', "es": '¡Hola! Soy Darsono.'},
    "sup_body":             {"en": "HOTS is a project created in my free time, completely free of charge.\nIf you enjoy it and it makes your work easier — or maybe you're just\nhaving a good day — you can support its further development.\nI'll be truly grateful for any amount, even a small one.",
                             "pl": "HOTS to projekt tworzony w wolnym czasie, całkowicie za darmo.\nJeśli program podoba Ci się i ułatwia pracę — a może po prostu\nmasz dziś dobry dzień — możesz wesprzeć jego dalszy rozwój.\nBędę naprawdę wdzięczny za każdą, nawet drobną kwotę.",
                             "fr": "HOTS est un projet créé pendant mon temps libre, entièrement gratuit.\nSi le programme vous plaît et facilite votre travail — ou peut-être\nque vous passez simplement une bonne journée — vous pouvez soutenir\nson développement. Je serai vraiment reconnaissant pour tout montant.",
                             "de": 'HOTS ist ein Projekt, das ich in meiner Freizeit erstellt habe, völlig kostenlos.\nWenn es Ihnen gefällt und Ihre Arbeit erleichtert — oder Sie vielleicht\neinfach einen guten Tag haben — können Sie die weitere Entwicklung unterstützen.\nIch bin für jeden Betrag, auch einen kleinen, wirklich dankbar.',
                             "es": 'HOTS es un proyecto creado en mi tiempo libre, completamente gratuito.\nSi te gusta y te facilita el trabajo — o quizás simplemente\nestás teniendo un buen día — puedes apoyar su desarrollo futuro.\nEstaré verdaderamente agradecido por cualquier cantidad, incluso pequeña.',
                         },
    "sup_paypal_sub":       {"en": "One-time payment · No registration", "pl": "Płatność jednorazowa · Bez rejestracji", "fr": "Paiement unique · Sans inscription", "de": 'Einmalige Zahlung · Keine Registrierung', "es": 'Pago único · Sin registro'},
    "sup_btn_support":      {"en": "Support",                      "pl": "Wesprzyj",                         "fr": "Soutenir", "de": 'Unterstützen', "es": 'Apoyar'},
    "sup_alt_contact":      {"en": "You can also contact me directly:",  "pl": "Możesz też napisać do mnie bezpośrednio:", "fr": "Vous pouvez aussi me contacter directement:", "de": 'Sie können mich auch direkt kontaktieren:', "es": 'También puedes contactarme directamente:'},
    "sup_footer":           {"en": "Thank you for using HOTS! — Darsono", "pl": "Dziękuję za używanie HOTS! — Darsono", "fr": "Merci d'utiliser HOTS! — Darsono", "de": 'Danke, dass Sie HOTS verwenden! — Darsono', "es": '¡Gracias por usar HOTS! — Darsono'},
    "sup_btn_close":        {"en": "Close",                        "pl": "Zamknij",                          "fr": "Fermer", "de": 'Schließen', "es": 'Cerrar'},
    "sup_err_browser":      {"en": "Could not open the browser.\n\nGo manually to:\n{url}",
                             "pl": "Nie udało się otworzyć przeglądarki.\n\nWejdź ręcznie na:\n{url}",
                             "fr": "Impossible d'ouvrir le navigateur.\n\nAccédez manuellement à:\n{url}",
                             "de": 'Der Browser konnte nicht geöffnet werden.\n\nGehen Sie manuell zu:\n{url}',
                             "es": 'No se pudo abrir el navegador.\n\nVe manualmente a:\n{url}',
                         },
    "sup_copied_title":     {"en": "Copied",                       "pl": "Skopiowano",                       "fr": "Copié", "de": 'Kopiert', "es": 'Copiado'},
    "sup_copied_msg":       {"en": "Email address copied to clipboard!", "pl": "Adres email skopiowany do schowka!", "fr": "Adresse e-mail copiée dans le presse-papiers!", "de": 'E-Mail-Adresse in die Zwischenablage kopiert!', "es": '¡Dirección de correo copiada al portapapeles!'},
    "btn_yes":            {"en": "  Yes  ",   "pl": "  Tak  ",   "fr": "  Oui  ", "de": '  Ja  ', "es": '  Sí  '},
    "btn_no":             {"en": "  No  ",    "pl": "  Nie  ",   "fr": "  Non  ", "de": '  Nein  ', "es": '  No  '},
    "btn_ok":             {"en": "  OK  ",    "pl": "  OK  ",    "fr": "  OK  ", "de": '  OK  ', "es": '  OK  '},
    "ctx_cut":            {"en": "Cut",       "pl": "Wytnij",    "fr": "Couper", "de": 'Ausschneiden', "es": 'Cortar'},
    "ctx_copy":           {"en": "Copy",      "pl": "Kopiuj",    "fr": "Copier", "de": 'Kopieren', "es": 'Copiar'},
    "ctx_paste":          {"en": "Paste",     "pl": "Wklej",     "fr": "Coller", "de": 'Einfügen', "es": 'Pegar'},
    "ctx_select_all":     {"en": "Select all","pl": "Zaznacz wszystko","fr": "Tout sélectionner", "de": 'Alles auswählen', "es": 'Seleccionar todo'},
    "import_dialog_title":   {"en": "Select hosts file to import", "pl": "Wybierz plik hosts do importu", "fr": "Sélectionner le fichier hosts à importer", "de": 'Hosts-Datei zum Importieren auswählen', "es": 'Seleccionar archivo hosts para importar'},
    "import_filetypes_hosts":{"en": "Hosts / text files", "pl": "Pliki hosts / tekstowe", "fr": "Fichiers hosts / texte", "de": 'Hosts-/Textdateien', "es": 'Archivos hosts / texto'},
    "import_filetypes_all":  {"en": "All files", "pl": "Wszystkie pliki", "fr": "Tous les fichiers", "de": 'Alle Dateien', "es": 'Todos los archivos'},
    "import_empty_title":    {"en": "Import", "pl": "Import", "fr": "Import", "de": 'Import', "es": 'Importar'},
    "import_empty_msg":      {"en": "The selected file contains no valid hosts entries.", "pl": "Wybrany plik nie zawiera prawidłowych wpisów hosts.", "fr": "Le fichier sélectionné ne contient aucune entrée hosts valide.", "de": 'Die ausgewählte Datei enthält keine gültigen Hosts-Einträge.', "es": 'El archivo seleccionado no contiene entradas hosts válidas.'},
    "import_confirm_title":  {"en": "Confirm import", "pl": "Potwierdź import", "fr": "Confirmer l'import", "de": 'Import bestätigen', "es": 'Confirmar importación'},
    "import_confirm_msg":    {"en": "Entries found in the selected file: {n}\n\nImport into the program?\n(Duplicates or formatting errors can be fixed later with 'Repair file').", "pl": "Wpisy znalezione w wybranym pliku: {n}\n\nZaimportować do programu?\n(Ewentualne duplikaty lub błędy formatowania uporządkujesz później funkcją 'Napraw plik').", "fr": "Entrées trouvées dans le fichier sélectionné : {n}\n\nImporter dans le programme?\n(Les doublons ou erreurs de formatage peuvent être corrigés avec 'Réparer fichier').", "de": 'In der ausgewählten Datei gefundene Einträge: {n}\n\nIn das Programm importieren?\n(Duplikate oder Formatierungsfehler können später mit „Datei reparieren" behoben werden).', "es": "Entradas encontradas en el archivo seleccionado: {n}\n\n¿Importar al programa?\n(Los duplicados o errores de formato se pueden corregir después con 'Reparar archivo')."},
    "import_limit_ask_title": {"en": "Import will exceed the safe limit",
                               "pl": "Import przekroczy bezpieczny limit",
                               "fr": "L'import dépassera la limite sécurisée",
                               "de": 'Der Import überschreitet das sichere Limit',
                               "es": 'La importación superará el límite seguro',
                           },
    "add_limit_ask_title":    {"en": "This will exceed the safe limit",
                               "pl": "To przekroczy bezpieczny limit",
                               "fr": "Cela dépassera la limite sécurisée",
                               "de": 'Dies überschreitet das sichere Limit',
                               "es": 'Esto superará el límite seguro',
                           },
    "add_limit_ask_msg":      {
        "en": (
            "Entries to add: {n}. Active entries after that: {total} "
            "in total — above the safe limit of {max}.\n\n"
            "You'll still be able to add them, but HOTS will refuse to save the file "
            "until you disable/delete enough entries to get back under {max} "
            "(see 'Protection & Privacy' — Windows performance limit).\n\n"
            "Add anyway?"
        ),
        "pl": (
            "Wpisy do dodania: {n}. Aktywne wpisy po dodaniu: {total} "
            "łącznie — powyżej bezpiecznego limitu {max}.\n\n"
            "Dodanie się wykona, ale HOTS odmówi zapisu pliku, dopóki nie wyłączysz/"
            "usuniesz wystarczająco wpisów, żeby wrócić poniżej {max} (patrz limit "
            "wydajności Windows przy zapisie).\n\n"
            "Dodać mimo to?"
        ),
        "fr": (
            "Entrées à ajouter : {n}. Entrées actives après ajout : {total} "
            "au total — au-dessus de la limite sécurisée de {max}.\n\n"
            "L'ajout s'effectuera, mais HOTS refusera d'enregistrer le fichier tant que "
            "vous n'aurez pas désactivé/supprimé assez d'entrées pour repasser sous "
            "{max}.\n\n"
            "Ajouter quand même?"
        ),
    
        "de": 'Hinzuzufügende Einträge: {n}. Aktive Einträge danach: {total} insgesamt — über dem sicheren Limit von {max}.\n\nSie können sie trotzdem hinzufügen, aber HOTS wird das Speichern der Datei verweigern, bis Sie genügend Einträge deaktivieren/löschen, um wieder unter {max} zu kommen (siehe „Schutz & Datenschutz" — Windows-Leistungslimit).\n\nTrotzdem hinzufügen?',
        "es": "Entradas a añadir: {n}. Entradas activas después: {total} en total — por encima del límite seguro de {max}.\n\nAún podrás añadirlas, pero HOTS se negará a guardar el archivo hasta que desactives/elimines suficientes entradas para volver a estar por debajo de {max} (consulta 'Protección y privacidad' — límite de rendimiento de Windows).\n\n¿Añadir de todos modos?",
    },
    "import_limit_ask_msg":   {
        "en": (
            "Entries in this file: {n}. Active entries after importing: {total} "
            "in total — above the safe limit of {max}.\n\n"
            "You'll be able to import them and review the list, but HOTS will refuse "
            "to save the file until you disable/delete enough entries to get back "
            "under {max} (see 'Protection & Privacy' — Windows performance limit).\n\n"
            "Import anyway?"
        ),
        "pl": (
            "Wpisy w tym pliku: {n}. Aktywne wpisy po imporcie: {total} "
            "łącznie — powyżej bezpiecznego limitu {max}.\n\n"
            "Import się wykona i będziesz mógł/mogła przejrzeć listę, ale HOTS odmówi "
            "zapisu pliku, dopóki nie wyłączysz/usuniesz wystarczająco wpisów, żeby "
            "wrócić poniżej {max} (patrz limit wydajności Windows przy zapisie).\n\n"
            "Zaimportować mimo to?"
        ),
        "fr": (
            "Entrées dans ce fichier : {n}. Entrées actives après import : {total} "
            "au total — au-dessus de la limite sécurisée de {max}.\n\n"
            "L'import s'effectuera et vous pourrez consulter la liste, mais HOTS "
            "refusera d'enregistrer le fichier tant que vous n'aurez pas désactivé/"
            "supprimé assez d'entrées pour repasser sous {max}.\n\n"
            "Importer quand même?"
        ),
    
        "de": 'Einträge in dieser Datei: {n}. Aktive Einträge nach dem Import: {total} insgesamt — über dem sicheren Limit von {max}.\n\nSie können sie importieren und die Liste überprüfen, aber HOTS wird das Speichern der Datei verweigern, bis Sie genügend Einträge deaktivieren/löschen, um wieder unter {max} zu kommen (siehe „Schutz & Datenschutz" — Windows-Leistungslimit).\n\nTrotzdem importieren?',
        "es": "Entradas en este archivo: {n}. Entradas activas después de importar: {total} en total — por encima del límite seguro de {max}.\n\nPodrás importarlas y revisar la lista, pero HOTS se negará a guardar el archivo hasta que desactives/elimines suficientes entradas para volver a estar por debajo de {max} (consulta 'Protección y privacidad' — límite de rendimiento de Windows).\n\n¿Importar de todos modos?",
    },
    "import_header_comment": {"en": "# Imported from: {path}  [{ts}]", "pl": "# Zaimportowano z: {path}  [{ts}]", "fr": "# Importé depuis: {path}  [{ts}]", "de": '# Importiert aus: {path}  [{ts}]', "es": '# Importado desde: {path}  [{ts}]'},
    "export_dialog_title":   {"en": "Export hosts entries", "pl": "Eksportuj wpisy hosts", "fr": "Exporter les entrées hosts", "de": 'Hosts-Einträge exportieren', "es": 'Exportar entradas hosts'},
    "export_scope_label":    {"en": "Export scope",                    "pl": "Zakres eksportu",                       "fr": "Portée de l'export", "de": 'Exportbereich', "es": 'Ámbito de exportación'},
    "export_scope_all":      {"en": "All entries ({n})",               "pl": "Wszystkie wpisy ({n})",                 "fr": "Toutes les entrées ({n})", "de": 'Alle Einträge ({n})', "es": 'Todas las entradas ({n})'},
    "export_scope_sel":      {"en": "Selected entries ({n})",          "pl": "Zaznaczone wpisy ({n})",               "fr": "Entrées sélectionnées ({n})", "de": 'Ausgewählte Einträge ({n})', "es": 'Entradas seleccionadas ({n})'},
    "export_scope_sel_none": {"en": "Selected entries (none selected)","pl": "Zaznaczone wpisy (brak zaznaczenia)",  "fr": "Entrées sélectionnées (aucune)", "de": 'Ausgewählte Einträge (keine Auswahl)', "es": 'Entradas seleccionadas (ninguna seleccionada)'},
    "export_comments_label": {"en": "Comments",                        "pl": "Komentarze",                           "fr": "Commentaires", "de": 'Kommentare', "es": 'Comentarios'},
    "export_comments_include":{"en":"Include comments in export",      "pl": "Dołącz komentarze do eksportu",        "fr": "Inclure les commentaires dans l'export", "de": 'Kommentare in den Export einbeziehen', "es": 'Incluir comentarios en la exportación'},
    "btn_cancel":            {"en": "Cancel",                          "pl": "Anuluj",                               "fr": "Annuler", "de": 'Abbrechen', "es": 'Cancelar'},
    "export_filetypes_txt":  {"en": "Hosts text file", "pl": "Plik tekstowy hosts", "fr": "Fichier texte hosts", "de": 'Hosts-Textdatei', "es": 'Archivo de texto hosts'},
    "export_filetypes_csv":  {"en": "CSV file (IP, Hostname, Comment)", "pl": "Plik CSV (IP, Hostname, Komentarz)", "fr": "Fichier CSV (IP, Nom d'hote, Commentaire)", "de": 'CSV-Datei (IP, Hostname, Kommentar)', "es": 'Archivo CSV (IP, Hostname, Comentario)'},
    "export_filetypes_all":  {"en": "All files", "pl": "Wszystkie pliki", "fr": "Tous les fichiers", "de": 'Alle Dateien', "es": 'Todos los archivos'},
    "export_csv_headers":    {"en": "Status,IP,Hostname,Comment", "pl": "Status,IP,Hostname,Komentarz", "fr": "Statut,IP,Nom d'hote,Commentaire", "de": 'Status,IP,Hostname,Kommentar', "es": 'Estado,IP,Hostname,Comentario'},
    "export_ok_csv_title":   {"en": "Export", "pl": "Eksport", "fr": "Export", "de": 'Export', "es": 'Exportar'},
    "export_ok_csv_msg":     {"en": "Successfully exported to CSV:\n{path}", "pl": "Pomyślnie wyeksportowano tabelę do pliku CSV:\n{path}", "fr": "Exporté avec succès en CSV:\n{path}", "de": 'Erfolgreich als CSV exportiert:\n{path}', "es": 'Exportado correctamente a CSV:\n{path}'},
    "export_ok_txt_title":   {"en": "Export", "pl": "Eksport", "fr": "Export", "de": 'Export', "es": 'Exportar'},
    "export_ok_txt_msg":     {"en": "Exported hosts file (entries: {n}):\n{path}", "pl": "Wyeksportowano plik hosts (wpisów: {n}):\n{path}", "fr": "Fichier hosts exporté (entrées : {n}):\n{path}", "de": 'Hosts-Datei exportiert (Einträge: {n}):\n{path}', "es": 'Archivo hosts exportado (entradas: {n}):\n{path}'},
    "export_err_title":      {"en": "Export error", "pl": "Błąd eksportu", "fr": "Erreur d'export", "de": 'Exportfehler', "es": 'Error de exportación'},
    "save_backup_err":       {"en": "Failed to create hosts file backup: {ex}", "pl": "Nie udało się utworzyć kopii zapasowej pliku hosts: {ex}", "fr": "Échec de la création de la sauvegarde : {ex}", "de": 'Sicherung der Hosts-Datei konnte nicht erstellt werden: {ex}', "es": 'No se pudo crear la copia de seguridad del archivo hosts: {ex}'},
    "save_perm_err":         {"en": "Access denied to write hosts file. Run the program as Administrator.", "pl": "Brak uprawnień do zapisu pliku hosts. Uruchom program jako Administrator.", "fr": "Accès refusé pour écrire le fichier hosts. Lancez le programme en tant qu'administrateur.", "de": 'Zugriff zum Schreiben der Hosts-Datei verweigert. Führen Sie das Programm als Administrator aus.', "es": 'Acceso denegado para escribir el archivo hosts. Ejecuta el programa como Administrador.'},
    "save_write_err":        {"en": "Error writing file: {ex}", "pl": "Błąd podczas zapisu pliku: {ex}", "fr": "Erreur lors de l'écriture du fichier : {ex}", "de": 'Fehler beim Schreiben der Datei: {ex}', "es": 'Error al escribir el archivo: {ex}'},
    "parental_comment":      {"en": "Parental Control", "pl": "Ochrona Rodzicielska", "fr": "Controle parental", "de": 'Kindersicherung', "es": 'Control parental'},
    "parental_err":          {"en": "Parental control error: {ex}", "pl": "Błąd ochrony rodzicielskiej: {ex}", "fr": "Erreur de controle parental: {ex}", "de": 'Fehler bei der Kindersicherung: {ex}', "es": 'Error de control parental: {ex}'},

    "par_cf_title":      {"en": "Cloudflare DNS Block",
                          "pl": "Blokada Cloudflare DNS",
                          "fr": "Blocage Cloudflare DNS",
                          "de": 'Cloudflare-DNS-Blockierung',
                          "es": 'Bloqueo DNS de Cloudflare',
                      },

    "par_cf_desc":       {"en": "Cloudflare Family (1.1.1.3) — DNS filter",
                          "pl": "Cloudflare Family (1.1.1.3) — filtr DNS",
                          "fr": "Cloudflare Family (1.1.1.3) — filtre DNS",
                          "de": 'Cloudflare Family (1.1.1.3) — DNS-Filter',
                          "es": 'Cloudflare Family (1.1.1.3) — filtro DNS',
                      },

    "par_cf_btn_enable": {"en": "Enable",   "pl": "Włącz",    "fr": "Activer", "de": 'Aktivieren', "es": 'Activar'},
    "par_cf_btn_disable":{"en": "Disable",  "pl": "Wyłącz",   "fr": "Désactiver", "de": 'Deaktivieren', "es": 'Desactivar'},

    "par_cf_tooltip": {
        "en": (
            "Cloudflare Family DNS (1.1.1.3 / 1.0.0.3) blocks adult content "
            "and known malware/phishing domains at the network level — it "
            "works for every program and browser on this computer, not "
            "just hosts-file entries.\n\n"
            "Enabling it changes the DNS servers on the active network "
            "interfaces. The hosts-based 'Block adult content sites' filter is then "
            "disabled, since this protection already covers more ground.\n\n"
            "Disabling it restores the DNS settings that were in place on "
            "this computer before the change was made."
        ),
        "pl": (
            "Cloudflare Family DNS (1.1.1.3 / 1.0.0.3) blokuje treści dla "
            "dorosłych oraz znane domeny malware/phishingowe na poziomie "
            "sieci — działa dla wszystkich programów i przeglądarek na tym "
            "komputerze, nie tylko dla wpisów w pliku hosts.\n\n"
            "Włączenie zmienia serwery DNS na aktywnych kartach sieciowych. "
            "Filtr 'Blokada stron dla dorosłych' oparty na hosts zostaje wtedy "
            "wyłączony, ponieważ ta ochrona zapewnia już szerszy zasięg.\n\n"
            "Wyłączenie przywraca ustawienia DNS, jakie obowiązywały na tym "
            "komputerze przed wprowadzeniem zmiany."
        ),
        "fr": (
            "Cloudflare Family DNS (1.1.1.3 / 1.0.0.3) bloque les contenus "
            "adultes et les domaines connus de malware/phishing au niveau "
            "réseau — il fonctionne pour tous les programmes et navigateurs "
            "sur cet ordinateur, pas seulement pour les entrées du fichier "
            "hosts.\n\n"
            "Son activation modifie les serveurs DNS sur les interfaces "
            "réseau actives. Le filtre 'Bloquer sites pour adultes' basé sur hosts "
            "est alors désactivé, car cette protection offre déjà une "
            "couverture plus large.\n\n"
            "Sa désactivation restaure les paramètres DNS qui étaient en "
            "place sur cet ordinateur avant la modification."
        ),
    
        "de": 'Cloudflare Family DNS (1.1.1.3 / 1.0.0.3) blockiert Inhalte für Erwachsene sowie bekannte Malware-/Phishing-Domains auf Netzwerkebene — es funktioniert für alle Programme und Browser auf diesem Computer, nicht nur für Einträge in der Hosts-Datei.\n\nDie Aktivierung ändert die DNS-Server auf den aktiven Netzwerkschnittstellen. Der Hosts-basierte Filter „Inhalte für Erwachsene blockieren" wird dann deaktiviert, da dieser Schutz bereits einen größeren Bereich abdeckt.\n\nDie Deaktivierung stellt die DNS-Einstellungen wieder her, die vor der Änderung auf diesem Computer galten.',
        "es": "Cloudflare Family DNS (1.1.1.3 / 1.0.0.3) bloquea el contenido para adultos y los dominios conocidos de malware/phishing a nivel de red — funciona para todos los programas y navegadores de este equipo, no solo para las entradas del archivo hosts.\n\nAl activarlo se cambian los servidores DNS en las interfaces de red activas. El filtro basado en hosts 'Bloquear sitios para adultos' se desactiva entonces, ya que esta protección ya cubre un ámbito más amplio.\n\nAl desactivarlo se restauran los ajustes DNS que existían en este equipo antes de realizar el cambio.",
    },

    "par_cf_on_ok": {
        "en": "Cloudflare DNS Protection has been enabled.",
        "pl": "Ochrona Cloudflare DNS została włączona.",
        "fr": "La protection Cloudflare DNS a été activée.",
    
        "de": 'Der Cloudflare-DNS-Schutz wurde aktiviert.',
        "es": 'La protección DNS de Cloudflare ha sido activada.',
    },

    "par_cf_off_ok": {
        "en": "Original DNS servers have been restored.\nCloudflare Family protection is now disabled.",
        "pl": "Oryginalne serwery DNS zostały przywrócone.\nOchrona Cloudflare Family jest teraz wyłączona.",
        "fr": "Les serveurs DNS d'origine ont été restaurés.\nLa protection Cloudflare Family est maintenant désactivée.",
    
        "de": 'Die ursprünglichen DNS-Server wurden wiederhergestellt.\nDer Cloudflare-Family-Schutz ist jetzt deaktiviert.',
        "es": 'Se han restaurado los servidores DNS originales.\nLa protección de Cloudflare Family está ahora desactivada.',
    },

    "par_cf_on_fail": {
        "en": "Failed to change DNS servers.\nMake sure the program is running as Administrator.",
        "pl": "Nie udało się zmienić serwerów DNS.\nUpewnij się, że program działa jako Administrator.",
        "fr": "Impossible de modifier les serveurs DNS.\nAssurez-vous que le programme s'exécute en tant qu'Administrateur.",
    
        "de": 'DNS-Server konnten nicht geändert werden.\nStellen Sie sicher, dass das Programm als Administrator ausgeführt wird.',
        "es": 'No se pudieron cambiar los servidores DNS.\nAsegúrate de que el programa se ejecute como Administrador.',
    },

    "par_cf_off_fail": {
        "en": "Failed to restore original DNS servers.\nYou can restore them manually in network adapter settings.",
        "pl": "Nie udało się przywrócić oryginalnych serwerów DNS.\nMożesz je przywrócić ręcznie w ustawieniach karty sieciowej.",
        "fr": "Impossible de restaurer les serveurs DNS d'origine.\nVous pouvez les restaurer manuellement dans les paramètres de la carte réseau.",
    
        "de": 'Die ursprünglichen DNS-Server konnten nicht wiederhergestellt werden.\nSie können sie manuell in den Netzwerkadaptereinstellungen wiederherstellen.',
        "es": 'No se pudieron restaurar los servidores DNS originales.\nPuedes restaurarlos manualmente en la configuración del adaptador de red.',
    },

    "par_cf_partial_fail": {
        "en": "⚠ Error on interfaces: {ifaces}",
        "pl": "⚠ Błąd na interfejsach: {ifaces}",
        "fr": "⚠ Erreur sur les interfaces: {ifaces}",
    
        "de": '⚠ Fehler bei Schnittstellen: {ifaces}',
        "es": '⚠ Error en las interfaces: {ifaces}',
    },

    "support_thank_you": {
        "en": "Thank you for being here \U0001F49B",
        "pl": "Dziękuję, że tu jesteś \U0001F49B",
        "fr": "Merci d'être ici \U0001F49B",
    
        "de": 'Danke, dass Sie hier sind 💛',
        "es": 'Gracias por estar aquí 💛',
    },
    "support_comet_msg": {
        "en": "\u2728 You found the comet! Thanks for being here \u2728",
        "pl": "\u2728 Znalazłeś kometę! Dzięki, że tu jesteś \u2728",
        "fr": "\u2728 Vous avez trouvé la comète ! Merci d'être ici \u2728",
    
        "de": '✨ Sie haben den Kometen gefunden! Danke, dass Sie hier sind ✨',
        "es": '✨ ¡Encontraste el cometa! Gracias por estar aquí ✨',
    },
}

_current_lang: str = "en"


def current_lang() -> str:
    return _current_lang


def set_lang(code: str) -> None:
    global _current_lang
    if code in LANGUAGES:
        _current_lang = code


def _pl_backup_word(n: int) -> str:
    n = abs(n)
    if n == 1:
        return "kopię zapasową"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return "kopie zapasowe"
    return "kopii zapasowych"


def T(key: str, **kwargs) -> str:
    entry = _STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(_current_lang) or entry.get("en") or key
    result = text.format(**kwargs) if kwargs else text
    if _current_lang == "pl" and "n" in kwargs and "kopii zapasowych" in result:
        result = result.replace("kopii zapasowych", _pl_backup_word(kwargs["n"]))
    return result
