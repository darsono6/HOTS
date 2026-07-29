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
    "btn_backups":  {"en": "Backups","pl": "Kopie",    "fr": "Sauvegardes", "de": 'Sicherungen', "es": 'Copias de seguridad'},

    "btn_repair":      {"en": "Repair file",       "pl": "Napraw plik",          "fr": "Réparer fichier", "de": 'Datei reparieren', "es": 'Reparar archivo'},
    "btn_default":     {"en": "Default hosts",     "pl": "Domyślny hosts",       "fr": "Hosts par défaut", "de": 'Standard-Hosts', "es": 'Hosts predeterminado'},
    "btn_check_dom":   {"en": "Check domains",     "pl": "Sprawdź domeny",       "fr": "Vérifier domaines", "de": 'Domains prüfen', "es": 'Comprobar dominios'},
    "btn_malware":     {"en": "Scan malware",      "pl": "Szukaj malware",       "fr": "Scanner malware", "de": 'Malware scannen', "es": 'Escanear malware'},
    "btn_parental":    {"en": "Protection  ",       "pl": "Ochrona",              "fr": "Protection", "de": 'Schutz  ', "es": 'Protección  '},
    "btn_privacy":     {"en": "Privacy  ",          "pl": "Prywatność",           "fr": "Confidentialité", "de": 'Datenschutz  ', "es": 'Privacidad  '},
    "btn_options":     {"en": "Options",           "pl": "Opcje",                "fr": "Options", "de": 'Optionen', "es": 'Opciones'},

    "opt_about":       {"en": "About",             "pl": "O programie",          "fr": "À propos", "de": 'Über', "es": 'Acerca de'},
    "opt_support":     {"en": "Support",           "pl": "Wsparcie",             "fr": "Soutenir", "de": 'Unterstützen', "es": 'Apoyar'},
    "opt_show_raw":    {"en": "Show Raw",          "pl": "Pokaż Host",           "fr": "Afficher brut", "de": 'Rohdaten anzeigen', "es": 'Mostrar bruto'},
    "opt_language":    {"en": "Language",          "pl": "Język",                "fr": "Langue", "de": 'Sprache', "es": 'Idioma'},
    "opt_appearance":  {"en": "Appearance",       "pl": "Wygląd",               "fr": "Apparence", "de": 'Erscheinungsbild', "es": 'Apariencia'},

    "opt_pass_on":     {"en": "Password: ON",    "pl": "Hasło: WŁ",           "fr": "Passe: ACT", "de": 'Passwort: AN', "es": 'Contraseña: ACT'},
    "opt_pass_off":    {"en": "Password",   "pl": "Hasło",          "fr": "Mot de passe", "de": 'Passwort', "es": 'Contraseña'},

    "col_status":      {"en": "Status",      "pl": "Status",      "fr": "Statut", "de": 'Status', "es": 'Estado'},
    "col_ip":          {"en": "IP Address",  "pl": "Adres IP",    "fr": "Adresse IP", "de": 'IP-Adresse', "es": 'Dirección IP'},
    "col_hostname":    {"en": "Hostname",    "pl": "Hostname",    "fr": "Nom d'hôte", "de": 'Hostname', "es": 'Nombre de host'},
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

    "about_subtitle":      {"en": "HOTS — Handy OS Tools Suite",
                            "pl": "HOTS — Handy OS Tools Suite",
                            "fr": "HOTS — Handy OS Tools Suite",
                            "de": 'HOTS — Handy OS Tools Suite',
                            "es": 'HOTS — Handy OS Tools Suite',
                        },
    "about_version":       {"en": "version 2.0",
                            "pl": "wersja 2.0",
                            "fr": "version 2.0",
                            "de": 'Version 2.0',
                            "es": 'versión 2.0',
                        },
    "about_desc":          {"en": "HOTS Hosts is a modern hosts-file editor for Windows, built with PySide6 and Fluent Design.\nManage entries safely, block trackers and unwanted content, and take fine-grained control over Windows telemetry — all from one dark or light interface.",
                            "pl": "HOTS Hosts to nowoczesny edytor pliku hosts dla Windows, zbudowany w PySide6 i Fluent Design.\nBezpiecznie zarządzaj wpisami, blokuj trackery i niechciane treści oraz miej pełną kontrolę nad telemetrią Windows — wszystko w jednym, ciemnym lub jasnym interfejsie.",
                            "fr": "HOTS Hosts est un éditeur de fichier hosts moderne pour Windows, conçu avec PySide6 et Fluent Design.\nGérez vos entrées en toute sécurité, bloquez les traqueurs et les contenus indésirables, et gardez un contrôle fin sur la télémétrie Windows — le tout dans une interface sombre ou claire.",
                            "de": 'HOTS Hosts ist ein moderner Hosts-Datei-Editor für Windows, entwickelt mit PySide6 und Fluent Design.\nVerwalten Sie Einträge sicher, blockieren Sie Tracker und unerwünschte Inhalte und behalten Sie die volle Kontrolle über die Windows-Telemetrie — alles in einer dunklen oder hellen Oberfläche.',
                            "es": 'HOTS Hosts es un editor moderno del archivo hosts para Windows, creado con PySide6 y Fluent Design.\nGestiona entradas de forma segura, bloquea rastreadores y contenido no deseado, y controla con precisión la telemetría de Windows — todo desde una interfaz oscura o clara.',
                        },
    "about_feat_parental": {"en": "Parental control (14 categories)",
                            "pl": "Ochrona rodzicielska (14 kategorii)",
                            "fr": "Contrôle parental (14 catégories)",
                            "de": 'Kindersicherung (14 Kategorien)',
                            "es": 'Control parental (14 categorías)',
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
    "about_feat_antispy":  {"en": "Privacy protection (3 levels)",
                            "pl": "Ochrona prywatności (3 poziomy)",
                            "fr": "Protection de la confidentialité (3 niveaux)",
                            "de": 'Datenschutz (3 Stufen)',
                            "es": 'Protección de privacidad (3 niveles)',
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
            "2. Run the program as Administrator.\n"
            "3. Apply a registry modification (MaxCacheTtl = 1) so Windows releases locks immediately.\n"
            "4. If the lock persists, restart your computer to reset the DNS service RAM."
        ),
        "pl": (
            "BŁĄD: Plik zablokowany przez usługę sieciową Windows!\n\n"
            "Systemowa usługa 'Klient DNS' (dnscache) lub Twój antywirus nałożyły wymuszony lock (Exclusive Lock) na plik hosts.\n\n"
            "Dzieje się tak, gdy system w tle wciąż analizuje poprzednie rekordy lub pętla sieciowa uległa zawieszeniu.\n\n"
            "Jak to rozwiązać?\n"
            "1. Odczekaj chwilę, aż usługa DNS zakończy analizę struktury i sama zwolni plik.\n"
            "2. Uruchom program jako Administrator.\n"
            "3. Zastosuj modyfikację rejestru (MaxCacheTtl = 1), aby Windows natychmiast puszczał blokady.\n"
            "4. Jeśli zablokowanie trwa stale, zrestartuj komputer w celu zresetowania pamięci RAM usługi DNS."
        ),
        "fr": (
            "ERREUR: Fichier verrouillé par le service réseau Windows!\n\n"
            "Le service Windows 'Client DNS' (dnscache) ou votre antivirus a imposé un verrou exclusif sur le fichier hosts.\n\n"
            "Cela se produit lorsque le système analyse encore des enregistrements précédents en arrière-plan ou que la boucle réseau est bloquée.\n\n"
            "Comment résoudre:\n"
            "1. Attendez que le service DNS termine l'analyse et libère le fichier.\n"
            "2. Exécutez le programme en tant qu'Administrateur.\n"
            "3. Appliquez une modification du registre (MaxCacheTtl = 1) pour que Windows libère les verrous immédiatement.\n"
            "4. Si le verrou persiste, redémarrez l'ordinateur pour réinitialiser la RAM du service DNS."
        ),
    
        "de": 'FEHLER: Datei durch Windows-Netzwerkdienst gesperrt!\n\nDer Windows-Dienst „DNS-Client" (dnscache) oder Ihr Antivirenprogramm hat eine exklusive Sperre für die Hosts-Datei gesetzt.\n\nDies passiert, wenn das System im Hintergrund noch vorherige Einträge analysiert oder die Netzwerkschleife hängt.\n\nSo beheben Sie das Problem:\n1. Warten Sie einen Moment, bis der DNS-Dienst die Analyse beendet und die Datei freigibt.\n2. Führen Sie das Programm als Administrator aus.\n3. Nehmen Sie eine Registry-Änderung vor (MaxCacheTtl = 1), damit Windows Sperren sofort freigibt.\n4. Wenn die Sperre bestehen bleibt, starten Sie den Computer neu, um den RAM des DNS-Dienstes zurückzusetzen.',
        "es": "ERROR: ¡Archivo bloqueado por el servicio de red de Windows!\n\nEl servicio 'Cliente DNS' (dnscache) de Windows o tu antivirus ha impuesto un bloqueo exclusivo sobre el archivo hosts.\n\nEsto ocurre cuando el sistema todavía está analizando registros anteriores en segundo plano o el bucle de red se ha detenido.\n\nCómo solucionarlo:\n1. Espera un momento a que el servicio DNS termine el análisis y libere el archivo.\n2. Ejecuta el programa como Administrador.\n3. Aplica una modificación del registro (MaxCacheTtl = 1) para que Windows libere los bloqueos inmediatamente.\n4. Si el bloqueo persiste, reinicia el equipo para reiniciar la memoria RAM del servicio DNS.",
    },

    "save_limit_title": {"en": "Save paused — performance limit",
                         "pl": "Zapis wstrzymany — limit wydajności",
                         "fr": "Enregistrement suspendu — limite de performance",
                         "de": 'Speichern pausiert — Leistungslimit',
                         "es": 'Guardado pausado — límite de rendimiento',
                     },
    "save_limit_msg":   {
        "en": (
            "Detected {n} active entries — above the recommended limit of {max}.\n\n"
            "Very large hosts files can put a noticeable load on Windows' 'DNS Client' "
            "service, leading to system slowdowns and, in extreme cases, connectivity "
            "issues. To avoid that, HOTS Hosts has paused this save.\n\n"
            "What you can do:\n"
            "• Disable or delete some entries to get back under {max}\n"
            "• Or move filtering to a local DNS server (e.g. AdGuard Home or Acrylic "
            "DNS), which is built to handle much larger lists."
        ),
        "pl": (
            "Wykryto {n} aktywnych wpisów — powyżej zalecanego limitu {max}.\n\n"
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
            "Détecté {n} entrées actives — au-dessus de la limite recommandée de "
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
    "repair_wildcards":        {"en": "• Fixed {n} wildcard entry/entries.",
                                "pl": "• Naprawiono {n} wpis(ów) z wildcard.",
                                "fr": "• Corrigé {n} entrée(s) avec wildcard.",
                                "de": '• {n} Wildcard-Eintrag/Einträge korrigiert.',
                                "es": '• Se corrigieron {n} entrada(s) con comodín.',
                            },
    "repair_dups":             {"en": "• Removed {n} duplicate entry/entries.",
                                "pl": "• Usunięto {n} zduplikowanych wpisów.",
                                "fr": "• Supprimé {n} entrée(s) en double.",
                                "de": '• {n} doppelte(r) Eintrag/Einträge entfernt.',
                                "es": '• Se eliminaron {n} entrada(s) duplicada(s).',
                            },
    "repair_invalid":          {"en": "• Removed {n} invalid entry/entries.",
                                "pl": "• Usunięto {n} niepoprawnych wpisów.",
                                "fr": "• Supprimé {n} entrée(s) invalide(s).",
                                "de": '• {n} ungültige(r) Eintrag/Einträge entfernt.',
                                "es": '• Se eliminaron {n} entrada(s) no válida(s).',
                            },
    "repair_normalized":       {"en": "• Normalized {n} hostname(s) to lowercase.",
                                "pl": "• Znormalizowano {n} hostname(ów) do małych liter.",
                                "fr": "• Normalisé {n} nom(s) d'hôte en minuscules.",
                                "de": '• {n} Hostname(s) in Kleinbuchstaben normalisiert.',
                                "es": '• Se normalizaron {n} nombre(s) de host a minúsculas.',
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
                            "pl": "Usunąć {n} zaznaczone wpisy?\n\n{preview}{suffix}",
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
    "acc_restart_msg":   {"en": "Accent color changed. Restart the application now to apply it?",
                          "pl": "Kolor akcentu zmieniony. Uruchomić aplikację ponownie teraz, aby go zastosować?",
                          "fr": "Couleur d'accent modifiée. Redémarrer l'application maintenant pour l'appliquer ?",
                          "de": 'Akzentfarbe geändert. Anwendung jetzt neu starten, um sie anzuwenden?',
                          "es": 'Color de acento cambiado. ¿Reiniciar la aplicación ahora para aplicarlo?',
                      },

    "bak_title":         {"en": "Backup Manager",               "pl": "Menedżer kopii zapasowych",        "fr": "Gestionnaire de sauvegardes", "de": 'Sicherungs-Manager', "es": 'Gestor de copias de seguridad'},
    "bak_header":        {"en": "Hosts file backups",           "pl": "Kopie zapasowe pliku hosts",       "fr": "Sauvegardes du fichier hosts", "de": 'Sicherungen der Hosts-Datei', "es": 'Copias de seguridad del archivo hosts'},
    "bak_subheader":     {"en": "Each save creates a new backup. You can restore any of them.",
                          "pl": "Każdy zapis tworzy nową kopię. Możesz przywrócić dowolną.",
                          "fr": "Chaque enregistrement crée une nouvelle sauvegarde. Vous pouvez restaurer n'importe laquelle.",
                          "de": 'Jeder Speichervorgang erstellt eine neue Sicherung. Sie können jede davon wiederherstellen.',
                          "es": 'Cada guardado crea una nueva copia de seguridad. Puedes restaurar cualquiera de ellas.',
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
                          "pl": "Trwale usunąć {n} zaznaczone kopie?\n\n{names}",
                          "fr": "Supprimer définitivement {n} sauvegardes sélectionnées?\n\n{names}",
                          "de": '{n} ausgewählte Sicherungen endgültig löschen?\n\n{names}',
                          "es": '¿Eliminar permanentemente {n} copias de seguridad seleccionadas?\n\n{names}',
                      },
    "bak_status_count":    {"en": "Found {n} backup(s).",
                            "pl": "Znaleziono {n} kopii zapasowych.",
                            "fr": "{n} sauvegarde(s) trouvée(s).",
                            "de": '{n} Sicherung(en) gefunden.',
                            "es": 'Se encontraron {n} copia(s) de seguridad.',
                        },
    "bak_status_restored": {"en": "Restored backup: {name}",
                            "pl": "Przywrócono kopię: {name}",
                            "fr": "Sauvegarde restaurée : {name}",
                            "de": 'Sicherung wiederhergestellt: {name}',
                            "es": 'Copia de seguridad restaurada: {name}',
                        },
    "bak_status_deleted":  {"en": "Deleted {n} backup(s).",
                            "pl": "Usunięto {n} kopii zapasowych.",
                            "fr": "{n} sauvegarde(s) supprimée(s).",
                            "de": '{n} Sicherung(en) gelöscht.',
                            "es": 'Se eliminaron {n} copia(s) de seguridad.',
                        },
    "diff_title":        {"en": "Preview changes before saving", "pl": "Podgląd zmian przed zapisem",     "fr": "Aperçu des modifications avant enregistrement", "de": 'Änderungen vor dem Speichern anzeigen', "es": 'Vista previa de cambios antes de guardar'},
    "diff_header":       {"en": "Preview changes",               "pl": "Podgląd zmian",                   "fr": "Aperçu des modifications", "de": 'Änderungen anzeigen', "es": 'Vista previa de cambios'},
    "diff_added":        {"en": "  + added  ",                   "pl": "  + dodane  ",                    "fr": "  + ajoutées  ", "de": '  + hinzugefügt  ', "es": '  + añadidas  '},
    "diff_removed":      {"en": "  − removed  ",                 "pl": "  − usunięte  ",                  "fr": "  − supprimées  ", "de": '  − entfernt  ', "es": '  − eliminadas  '},
    "diff_no_changes":   {"en": "No changes",                    "pl": "Brak zmian",                      "fr": "Aucune modification", "de": 'Keine Änderungen', "es": 'Sin cambios'},
    "diff_stat":         {"en": "+{adds} added   \u2212{dels} removed", "pl": "+{adds} dodanych   \u2212{dels} usuniętych", "fr": "+{adds} ajoutées   \u2212{dels} supprimées", "de": '+{adds} hinzugefügt   −{dels} entfernt', "es": '+{adds} añadidas   −{dels} eliminadas'},
    "diff_save_anyway":  {"en": "Save anyway",                   "pl": "Zapisz mimo to",                  "fr": "Enregistrer quand même", "de": 'Trotzdem speichern', "es": 'Guardar de todos modos'},
    "diff_save":         {"en": "Save",                          "pl": "Zapisz",                          "fr": "Enregistrer", "de": 'Speichern', "es": 'Guardar'},
    "diff_cancel":       {"en": "Cancel",                        "pl": "Anuluj",                          "fr": "Annuler", "de": 'Abbrechen', "es": 'Cancelar'},
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
    "entry_lbl_host":    {"en": "Hostname:",                     "pl": "Hostname:",                       "fr": "Nom d'hôte:", "de": 'Hostname:', "es": 'Nombre de host:'},
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
    "entry_hint_dup":    {"en": "✘ This entry already exists in the hosts file.",
                          "pl": "✘ Taki wpis już istnieje w pliku hosts.",
                          "fr": "✘ Cette entrée existe déjà dans le fichier hosts.",
                          "de": '✘ Dieser Eintrag existiert bereits in der Hosts-Datei.',
                          "es": '✘ Esta entrada ya existe en el archivo hosts.',
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
    "entry_skip_msg":    {"en": "Skipped {n} duplicate(s):\n{list}",
                          "pl": "Pominięto {n} duplikat(ów):\n{list}",
                          "fr": "Ignoré {n} doublon(s):\n{list}",
                          "de": '{n} Duplikat(e) übersprungen:\n{list}',
                          "es": 'Se omitieron {n} duplicado(s):\n{list}',
                      },
    "entry_err_required":{"en": "IP and Hostname are required.", "pl": "IP i Hostname są wymagane.",      "fr": "L'IP et le nom d'hôte sont requis.", "de": 'IP und Hostname sind erforderlich.', "es": 'Se requieren IP y nombre de host.'},
    "entry_bad_ip_title":{"en": "Invalid IP",                    "pl": "Nieprawidłowy IP",                "fr": "IP invalide", "de": 'Ungültige IP', "es": 'IP no válida'},
    "entry_bad_ip_ask":  {"en": '"{ip}" does not look like a valid IPv4/IPv6 address.\n\nSave anyway?',
                          "pl": '"{ip}" nie wygląda jak poprawny adres IPv4/IPv6.\n\nZapisać mimo to?',
                          "fr": '"{ip}" ne ressemble pas à une adresse IPv4/IPv6 valide.\n\nEnregistrer quand même?',
                          "de": '„{ip}" sieht nicht wie eine gültige IPv4-/IPv6-Adresse aus.\n\nTrotzdem speichern?',
                          "es": '"{ip}" no parece una dirección IPv4/IPv6 válida.\n\n¿Guardar de todos modos?',
                      },
    "entry_dup_title":   {"en": "Duplicate",                     "pl": "Duplikat",                        "fr": "Doublon", "de": 'Duplikat', "es": 'Duplicado'},
    "entry_dup_ask":     {"en": 'Entry "{host}" already exists in the hosts file.\n\nAdd anyway?',
                          "pl": 'Wpis "{host}" już istnieje w pliku hosts.\n\nDodać mimo to?',
                          "fr": 'L\'entrée "{host}" existe déjà dans le fichier hosts.\n\nAjouter quand même?',
                          "de": 'Der Eintrag „{host}" existiert bereits in der Hosts-Datei.\n\nTrotzdem hinzufügen?',
                          "es": 'La entrada "{host}" ya existe en el archivo hosts.\n\n¿Añadir de todos modos?',
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
    "diag_btn_run":         {"en": "Run scan",                   "pl": "Uruchom skan",                    "fr": "Lancer le scan", "de": 'Scan starten', "es": 'Ejecutar escaneo'},
    "diag_btn_stop":        {"en": "Stop",                       "pl": "Zatrzymaj",                       "fr": "Arrêter", "de": 'Stopp', "es": 'Detener'},
    "diag_stopping":        {"en": "Stopping…",                  "pl": "Zatrzymuję…",                     "fr": "Arrêt en cours…", "de": 'Wird gestoppt…', "es": 'Deteniendo…'},
    "diag_click_to_start":  {"en": "Click Run scan to start.",   "pl": "Kliknij Uruchom skan aby rozpocząć.", "fr": "Cliquez sur Lancer le scan pour commencer.", "de": 'Klicken Sie auf „Scan starten", um zu beginnen.', "es": 'Haz clic en Ejecutar escaneo para empezar.'},
    "diag_col_result":      {"en": "Result",                     "pl": "Wynik",                           "fr": "Résultat", "de": 'Ergebnis', "es": 'Resultado'},
    "diag_col_hostname":    {"en": "Hostname",                   "pl": "Hostname",                        "fr": "Nom d'hôte", "de": 'Hostname', "es": 'Nombre de host'},
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
    "diag_del_inactive_msg":{"en": "Delete {n} unnecessary entries?\n\n{preview}{suffix}\n\nSave the file in the main window after closing this window.",
                             "pl": "Usunąć {n} zbędnych wpisów?\n\n{preview}{suffix}\n\nZapisz plik w głównym oknie po zamknięciu tego okna.",
                             "fr": "Supprimer {n} entrées inutiles?\n\n{preview}{suffix}\n\nEnregistrez le fichier dans la fenêtre principale après fermeture.",
                             "de": '{n} unnötige Einträge löschen?\n\n{preview}{suffix}\n\nSpeichern Sie die Datei nach dem Schließen dieses Fensters im Hauptfenster.',
                             "es": '¿Eliminar {n} entradas innecesarias?\n\n{preview}{suffix}\n\nGuarda el archivo en la ventana principal después de cerrar esta ventana.',
                         },
    "diag_del_sel_msg":     {"en": "Delete {n} entries from the hosts file?\n\n{preview}{suffix}\n\nChanges will be visible in the main window.\nRemember to save the file after closing this window.",
                             "pl": "Usunąć {n} wpisów z pliku hosts?\n\n{preview}{suffix}\n\nZmiany będą widoczne w głównym oknie.\nPamiętaj aby zapisać plik po zamknięciu tego okna.",
                             "fr": "Supprimer {n} entrées du fichier hosts?\n\n{preview}{suffix}\n\nLes modifications seront visibles dans la fenêtre principale.\nPensez à enregistrer le fichier après fermeture.",
                             "de": '{n} Einträge aus der Hosts-Datei löschen?\n\n{preview}{suffix}\n\nÄnderungen werden im Hauptfenster sichtbar.\nDenken Sie daran, die Datei nach dem Schließen dieses Fensters zu speichern.',
                             "es": '¿Eliminar {n} entradas del archivo hosts?\n\n{preview}{suffix}\n\nLos cambios serán visibles en la ventana principal.\nRecuerda guardar el archivo después de cerrar esta ventana.',
                         },
    "diag_more":            {"en": "\n... and {n} more",         "pl": "\n... i {n} więcej",              "fr": "\n... et {n} de plus", "de": '\n... und {n} weitere', "es": '\n... y {n} más'},
    "diag_no_sel_msg":      {"en": "Select entries you want to delete.",
                             "pl": "Zaznacz wpisy które chcesz usunąć.",
                             "fr": "Sélectionnez les entrées que vous souhaitez supprimer.",
                             "de": 'Wählen Sie die Einträge aus, die Sie löschen möchten.',
                             "es": 'Selecciona las entradas que deseas eliminar.',
                         },
    "diag_status_deleted_inactive": {"en": "Deleted {n} unnecessary entries. Save the file in the main window.",
                                     "pl": "Usunięto {n} zbędnych wpisów. Zapisz plik w głównym oknie.",
                                     "fr": "Supprimé {n} entrées inutiles. Enregistrez le fichier dans la fenêtre principale.",
                                     "de": '{n} unnötige Einträge gelöscht. Speichern Sie die Datei im Hauptfenster.',
                                     "es": 'Se eliminaron {n} entradas innecesarias. Guarda el archivo en la ventana principal.',
                                 },
    "diag_status_deleted_sel":      {"en": "Deleted {n} entries. Save the file in the main window.",
                                     "pl": "Usunięto {n} wpisów. Zapisz plik w głównym oknie.",
                                     "fr": "Supprimé {n} entrées. Enregistrez le fichier dans la fenêtre principale.",
                                     "de": '{n} Einträge gelöscht. Speichern Sie die Datei im Hauptfenster.',
                                     "es": 'Se eliminaron {n} entradas. Guarda el archivo en la ventana principal.',
                                 },
    "diag_ctx_ignore_one":  {"en": "Ignore this entry",           "pl": "Zignoruj ten wpis",                "fr": "Ignorer cette entrée", "de": 'Diesen Eintrag ignorieren', "es": 'Ignorar esta entrada'},
    "diag_ctx_ignore_many": {"en": "Ignore selected ({n})",       "pl": "Zignoruj zaznaczone ({n})",        "fr": "Ignorer la sélection ({n})", "de": 'Auswahl ignorieren ({n})', "es": 'Ignorar seleccionadas ({n})'},
    "diag_status_ignored":  {"en": "Ignored {n} entries — they won't appear in future scans.",
                             "pl": "Zignorowano {n} wpisów — nie pojawią się w kolejnych skanach.",
                             "fr": "{n} entrées ignorées — elles n'apparaîtront plus dans les prochains scans.",
                             "de": '{n} Einträge ignoriert — sie erscheinen in zukünftigen Scans nicht mehr.',
                             "es": 'Se ignoraron {n} entradas — no aparecerán en futuros escaneos.',
                         },
    "diag_scanning":        {"en": "Scanning: ",                 "pl": "Sprawdzam: ",                     "fr": "Analyse: ", "de": 'Scanne: ', "es": 'Escaneando: '},
    "diag_analyzing":       {"en": "Analyzing: ",                "pl": "Analizuję: ",                     "fr": "Analyse: ", "de": 'Analysiere: ', "es": 'Analizando: '},
    "diag_scan_done":       {"en": "Scan complete.",             "pl": "Skan zakończony.",                 "fr": "Scan terminé.", "de": 'Scan abgeschlossen.', "es": 'Escaneo completado.'},
    "diag_summary_exist":   {"en": "Done: {found} active, {missing} unnecessary, {errors} timeout/error.",
                             "pl": "Zakończono: {found} aktywnych, {missing} zbędnych, {errors} timeout/błąd.",
                             "fr": "Terminé: {found} actifs, {missing} inutiles, {errors} timeout/erreur.",
                             "de": 'Fertig: {found} aktiv, {missing} unnötig, {errors} Timeout/Fehler.',
                             "es": 'Hecho: {found} activas, {missing} innecesarias, {errors} tiempo de espera/error.',
                         },
    "diag_summary_malware": {"en": "Done. Found {issues} suspicious entries out of {total} checked.",
                             "pl": "Zakończono. Znaleziono {issues} podejrzanych wpisów z {total} sprawdzonych.",
                             "fr": "Terminé. Trouvé {issues} entrées suspectes sur {total} vérifiées.",
                             "de": 'Fertig. {issues} verdächtige Einträge von {total} geprüften gefunden.',
                             "es": 'Hecho. Se encontraron {issues} entradas sospechosas de {total} comprobadas.',
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
    "diag_reason_many_dom": {"en": "{n} domains on the same IP — suspicious",
                             "pl": "{n} domen na ten sam IP — podejrzane",
                             "fr": "{n} domaines sur le même IP — suspect",
                             "de": '{n} Domains auf derselben IP — verdächtig',
                             "es": '{n} dominios en la misma IP — sospechoso',
                         },
    "diag_reason_homoglyph":{"en": "Suspicious characters in hostname: {chars}",
                             "pl": "Podejrzane znaki w hostname: {chars}",
                             "fr": "Caractères suspects dans le nom d'hôte: {chars}",
                             "de": 'Verdächtige Zeichen im Hostname: {chars}',
                             "es": 'Caracteres sospechosos en el nombre de host: {chars}',
                         },
    "diag_reason_zero_width":{"en": "Hidden zero-width characters in hostname: {chars}",
                             "pl": "Ukryte znaki zero-width w hostname: {chars}",
                             "fr": "Caractères zero-width cachés dans le nom d'hôte: {chars}",
                             "de": 'Versteckte Zero-Width-Zeichen im Hostname: {chars}',
                             "es": 'Caracteres ocultos de ancho cero en el nombre de host: {chars}',
                         },
    "diag_reason_ip_host":  {"en": "Hostname is an IP address — unusual",
                             "pl": "Hostname jest adresem IP — nietypowe",
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
    "diag_reason_deep_sub": {"en": "Excessive subdomain depth ({n} levels) — possible DNS tunneling",
                             "pl": "Nadmierna głębokość subdomen ({n} poziomów) — możliwy DNS tunneling",
                             "fr": "Profondeur de sous-domaine excessive ({n} niveaux) — possible tunnel DNS",
                             "de": 'Übermäßige Subdomain-Tiefe ({n} Ebenen) — mögliches DNS-Tunneling',
                             "es": 'Profundidad excesiva de subdominios ({n} niveles) — posible DNS tunneling',
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
            "  Disable 'Secure DNS' in each browser's settings.\n\n"
            "• Large platforms (TikTok, YouTube…) use hundreds of\n"
            "  subdomains. Blocklists are updated with each HOTS release,\n"
            "  but gaps may exist at any given time.\n\n"
            "• Mobile devices and VPNs are not covered — the hosts file\n"
            "  only applies to this Windows PC."
        ),
        "pl": (
            "Blokowanie przez plik hosts ma znane ograniczenia:\n\n"
            "• DNS-over-HTTPS (DoH) — Chrome, Firefox i Edge mogą używać\n"
            "  własnego szyfrowanego DNS, całkowicie omijając plik hosts.\n"
            "  Wyłącz 'Bezpieczny DNS' w ustawieniach każdej przeglądarki.\n\n"
            "• Duże platformy (TikTok, YouTube…) używają setek subdomen.\n"
            "  Listy blokad są aktualizowane z każdą wersją HOTS,\n"
            "  ale luki mogą istnieć w dowolnym momencie.\n\n"
            "• Urządzenia mobilne i VPN nie są objęte ochroną —\n"
            "  plik hosts działa tylko na tym komputerze z Windows."
        ),
        "fr": (
            "Le blocage par fichier hosts a des limitations connues:\n\n"
            "• DNS-over-HTTPS (DoH) — Chrome, Firefox et Edge peuvent utiliser\n"
            "  leur propre DNS chiffré, contournant entièrement le fichier hosts.\n"
            "  Désactivez le 'DNS sécurisé' dans les paramètres de chaque navigateur.\n\n"
            "• Les grandes plateformes (TikTok, YouTube…) utilisent des centaines\n"
            "  de sous-domaines. Les listes sont mises à jour à chaque version de HOTS,\n"
            "  mais des lacunes peuvent exister à tout moment.\n\n"
            "• Les appareils mobiles et les VPN ne sont pas couverts —\n"
            "  le fichier hosts ne s'applique qu'à ce PC Windows."
        ),
    
        "de": 'Die Blockierung über die Hosts-Datei hat bekannte Einschränkungen:\n\n• DNS-over-HTTPS (DoH) — Chrome, Firefox und Edge verwenden\n  möglicherweise ihr eigenes verschlüsseltes DNS und umgehen\n  die Hosts-Datei vollständig. Deaktivieren Sie „Sicheres DNS"\n  in den Einstellungen jedes Browsers.\n\n• Große Plattformen (TikTok, YouTube…) verwenden Hunderte\n  von Subdomains. Die Blocklisten werden mit jedem HOTS-Release\n  aktualisiert, aber es können jederzeit Lücken bestehen.\n\n• Mobilgeräte und VPNs werden nicht abgedeckt — die Hosts-Datei\n  gilt nur für diesen Windows-PC.',
        "es": "El bloqueo mediante hosts tiene limitaciones conocidas:\n\n• DNS-over-HTTPS (DoH) — Chrome, Firefox y Edge pueden usar\n  su propio DNS cifrado, evitando por completo el archivo hosts.\n  Desactiva el 'DNS seguro' en la configuración de cada navegador.\n\n• Las grandes plataformas (TikTok, YouTube…) usan cientos de\n  subdominios. Las listas de bloqueo se actualizan con cada versión\n  de HOTS, pero puede haber huecos en cualquier momento.\n\n• Los dispositivos móviles y las VPN no están cubiertos — el archivo\n  hosts solo se aplica a este PC con Windows.",
    },
    "par_title":            {"en": "🛡️ Protection",              "pl": "🛡️ Ochrona",                        "fr": "🛡️ Protection", "de": '🛡️ Schutz', "es": '🛡️ Protección'},
    "par_header":           {"en": "🛡️  Protection",             "pl": "🛡️  Ochrona",                       "fr": "🛡️  Protection", "de": '🛡️  Schutz', "es": '🛡️  Protección'},
    "par_subheader":        {"en": "Block selected services at the system level (hosts file).",
                             "pl": "Blokuj wybrane serwisy na poziomie systemu (plik hosts).",
                             "fr": "Bloquez les services sélectionnés au niveau système (fichier hosts).",
                             "de": 'Blockieren Sie ausgewählte Dienste auf Systemebene (Hosts-Datei).',
                             "es": 'Bloquea los servicios seleccionados a nivel del sistema (archivo hosts).',
                         },
    "priv_title":           {"en": "🕵️ Privacy",                 "pl": "🕵️ Prywatność",                     "fr": "🕵️ Confidentialité", "de": '🕵️ Datenschutz', "es": '🕵️ Privacidad'},
    "priv_subheader":       {"en": "Control Windows telemetry protection and block telemetry domains at the system level (hosts file).",
                             "pl": "Zarządzaj ochroną przed telemetrią Windows oraz blokuj domeny telemetryczne na poziomie systemu (plik hosts).",
                             "fr": "Gérez la protection contre la télémétrie Windows et bloquez les domaines de télémétrie au niveau système (fichier hosts).",
                             "de": 'Verwalten Sie den Schutz vor Windows-Telemetrie und blockieren Sie Telemetrie-Domains auf Systemebene (Hosts-Datei).',
                             "es": 'Controla la protección contra la telemetría de Windows y bloquea dominios de telemetría a nivel del sistema (archivo hosts).',
                         },
    "priv_watchdog_checking": {"en": "Checking protection status…", "pl": "Sprawdzanie stanu ochrony…",        "fr": "Vérification de l'état de la protection…", "de": 'Schutzstatus wird geprüft…', "es": 'Comprobando el estado de la protección…'},
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
    "priv_restore_btn_create": {"en": "Create restore point", "pl": "Utwórz punkt przywracania", "fr": "Créer un point de restauration", "de": 'Wiederherstellungspunkt erstellen', "es": 'Crear punto de restauración'},
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
    "par_antispy_section_desc": {
        "en": "Three independent protection levels against Windows telemetry. They use separate system resources, so you can enable any combination.",
        "pl": "Trzy niezależne poziomy ochrony przed telemetrią Windows. Korzystają z rozłącznych zasobów systemowych, więc możesz włączyć dowolną ich kombinację.",
        "fr": "Trois niveaux de protection indépendants contre la télémétrie Windows. Ils utilisent des ressources système distinctes, vous pouvez donc activer n'importe quelle combinaison.",
    
        "de": 'Drei unabhängige Schutzstufen gegen Windows-Telemetrie. Sie nutzen getrennte Systemressourcen, sodass Sie jede beliebige Kombination aktivieren können.',
        "es": 'Tres niveles de protección independientes contra la telemetría de Windows. Utilizan recursos del sistema separados, por lo que puedes activar cualquier combinación.',
    },
    "par_antispy_basic_btn":    {"en": "Basic",        "pl": "Podstawowa",     "fr": "Basique", "de": 'Basis', "es": 'Básica'},
    "par_antispy_medium_btn":   {"en": "Medium",       "pl": "Średnia",        "fr": "Moyenne", "de": 'Mittel', "es": 'Media'},
    "par_antispy_advanced_btn": {"en": "Advanced",     "pl": "Zaawansowana",   "fr": "Avancée", "de": 'Erweitert', "es": 'Avanzada'},
    "par_antispy_basic_label":    {"en": "Basic privacy protection",    "pl": "Podstawowa ochrona prywatności",    "fr": "Protection de la confidentialité basique", "de": 'Grundlegender Datenschutz', "es": 'Protección de privacidad básica'},
    "par_antispy_medium_label":   {"en": "Medium privacy protection",   "pl": "Średnia ochrona prywatności",       "fr": "Protection de la confidentialité moyenne", "de": 'Mittlerer Datenschutz', "es": 'Protección de privacidad media'},
    "par_antispy_advanced_label": {"en": "Advanced privacy protection", "pl": "Zaawansowana ochrona prywatności",  "fr": "Protection de la confidentialité avancée", "de": 'Erweiterter Datenschutz', "es": 'Protección de privacidad avanzada'},
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
            "Disables 5 telemetry-related Task Scheduler tasks "
            "(Compatibility Appraiser, ProgramDataUpdater, Consolidator, "
            "UsbCeip, QueueReporting).\n\n"
            "Disable:\n"
            "Removes the firewall rules and re-enables any of those tasks "
            "that were enabled before this level was activated."
        ),
        "pl": (
            "Włączenie:\n"
            "Dodaje reguły blokady wychodzącej w Windows Firewall "
            "(CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\n"
            "Wyłącza 5 zadań telemetrycznych w Harmonogramie zadań "
            "(Compatibility Appraiser, ProgramDataUpdater, Consolidator, "
            "UsbCeip, QueueReporting).\n\n"
            "Wyłączenie:\n"
            "Usuwa reguły zapory i przywraca te zadania, które były "
            "włączone przed aktywacją tego poziomu."
        ),
        "fr": (
            "Activation :\n"
            "Ajoute des règles de blocage sortant dans le Pare-feu Windows "
            "(CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\n"
            "Désactive 5 tâches liées à la télémétrie dans le Planificateur "
            "de tâches (Compatibility Appraiser, ProgramDataUpdater, "
            "Consolidator, UsbCeip, QueueReporting).\n\n"
            "Désactivation :\n"
            "Supprime les règles du pare-feu et réactive les tâches qui "
            "étaient activées avant l'activation de ce niveau."
        ),
    
        "de": 'Aktivierung:\nFügt ausgehende Blockierungsregeln in der Windows-Firewall hinzu (CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\nDeaktiviert 5 telemetriebezogene Aufgaben im Aufgabenplaner (Compatibility Appraiser, ProgramDataUpdater, Consolidator, UsbCeip, QueueReporting).\n\nDeaktivierung:\nEntfernt die Firewall-Regeln und aktiviert die Aufgaben erneut, die vor der Aktivierung dieser Stufe aktiviert waren.',
        "es": 'Activación:\nAñade reglas de bloqueo de salida en el Firewall de Windows (CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\nDesactiva 5 tareas relacionadas con la telemetría en el Programador de tareas (Compatibility Appraiser, ProgramDataUpdater, Consolidator, UsbCeip, QueueReporting).\n\nDesactivación:\nElimina las reglas del firewall y vuelve a activar las tareas que estaban activadas antes de activar este nivel.',
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
    "priv_advanced_services_label": {"en": "Diagnostic services", "pl": "Usługi diagnostyczne", "fr": "Services de diagnostic", "de": 'Diagnosedienste', "es": 'Servicios de diagnóstico'},
    "priv_advanced_services_tooltip": {
        "en": "Enable: disables WerSvc and PcaSvc.\nDisable: restores their exact previous startup type.",
        "pl": "Włączenie: wyłącza usługi WerSvc i PcaSvc.\nWyłączenie: przywraca ich dokładny poprzedni typ uruchamiania.",
        "fr": "Activation : désactive WerSvc et PcaSvc.\nDésactivation : restaure leur type de démarrage précédent.",
    
        "de": 'Aktivieren: deaktiviert WerSvc und PcaSvc.\nDeaktivieren: stellt deren genauen vorherigen Starttyp wieder her.',
        "es": 'Activar: desactiva WerSvc y PcaSvc.\nDesactivar: restaura su tipo de inicio anterior exacto.',
    },
    "priv_advanced_privacy_label": {"en": "Privacy settings (per tweak)", "pl": "Ustawienia prywatności (osobno)", "fr": "Paramètres de confidentialité (séparés)", "de": 'Datenschutzeinstellungen (einzeln)', "es": 'Ajustes de privacidad (individuales)'},
    "priv_item_basic_reg": {"en": "Registry policy: AllowTelemetry = 0", "pl": "Polityka rejestru: AllowTelemetry = 0", "fr": "Stratégie de registre : AllowTelemetry = 0", "de": 'Registry-Richtlinie: AllowTelemetry = 0', "es": 'Política de registro: AllowTelemetry = 0'},
    "priv_item_basic_diagtrack": {"en": "Service: DiagTrack", "pl": "Usługa: DiagTrack", "fr": "Service : DiagTrack", "de": 'Dienst: DiagTrack', "es": 'Servicio: DiagTrack'},
    "priv_item_basic_dmwap": {"en": "Service: dmwappushservice", "pl": "Usługa: dmwappushservice", "fr": "Service : dmwappushservice", "de": 'Dienst: dmwappushservice', "es": 'Servicio: dmwappushservice'},
    "priv_item_basic_experimentation": {"en": "Registry policy: AllowExperimentation = 0", "pl": "Polityka rejestru: AllowExperimentation = 0", "fr": "Stratégie de registre : AllowExperimentation = 0", "de": 'Registry-Richtlinie: AllowExperimentation = 0', "es": 'Política de registro: AllowExperimentation = 0'},
    "priv_item_basic_consumerfeatures": {"en": "Registry policy: DisableWindowsConsumerFeatures = 1", "pl": "Polityka rejestru: DisableWindowsConsumerFeatures = 1", "fr": "Stratégie de registre : DisableWindowsConsumerFeatures = 1", "de": 'Registry-Richtlinie: DisableWindowsConsumerFeatures = 1', "es": 'Política de registro: DisableWindowsConsumerFeatures = 1'},
    "priv_item_basic_tailored": {"en": "Registry policy: DisableTailoredExperiencesWithDiagnosticData = 1", "pl": "Polityka rejestru: DisableTailoredExperiencesWithDiagnosticData = 1", "fr": "Stratégie de registre : DisableTailoredExperiencesWithDiagnosticData = 1", "de": 'Registry-Richtlinie: DisableTailoredExperiencesWithDiagnosticData = 1', "es": 'Política de registro: DisableTailoredExperiencesWithDiagnosticData = 1'},
    "priv_item_basic_deliveryopt": {"en": "Registry policy: DODownloadMode = 0 (no P2P update sharing)", "pl": "Polityka rejestru: DODownloadMode = 0 (bez P2P przy aktualizacjach)", "fr": "Stratégie de registre : DODownloadMode = 0 (pas de partage P2P)", "de": 'Registry-Richtlinie: DODownloadMode = 0 (kein P2P-Update-Sharing)', "es": 'Política de registro: DODownloadMode = 0 (sin compartición P2P de actualizaciones)'},
    "priv_item_basic_recall": {"en": "Registry policy: DisableAIDataAnalysis = 1 (blocks Windows Recall)", "pl": "Polityka rejestru: DisableAIDataAnalysis = 1 (blokuje Windows Recall)", "fr": "Stratégie de registre : DisableAIDataAnalysis = 1 (bloque Windows Recall)", "de": 'Registry-Richtlinie: DisableAIDataAnalysis = 1 (blockiert Windows Recall)', "es": 'Política de registro: DisableAIDataAnalysis = 1 (bloquea Windows Recall)'},
    "priv_item_basic_feedback": {"en": "Registry policy: DoNotShowFeedbackNotifications = 1", "pl": "Polityka rejestru: DoNotShowFeedbackNotifications = 1", "fr": "Stratégie de registre : DoNotShowFeedbackNotifications = 1", "de": 'Registry-Richtlinie: DoNotShowFeedbackNotifications = 1', "es": 'Política de registro: DoNotShowFeedbackNotifications = 1'},
    "priv_item_basic_ceip": {"en": "Registry policy: CEIPEnable = 0 (Customer Experience Improvement Program)", "pl": "Polityka rejestru: CEIPEnable = 0 (Program ulepszania jakości)", "fr": "Stratégie de registre : CEIPEnable = 0 (Programme d'amélioration)", "de": 'Registry-Richtlinie: CEIPEnable = 0 (Programm zur Verbesserung der Benutzerfreundlichkeit)', "es": 'Política de registro: CEIPEnable = 0 (Programa de mejora de la experiencia del cliente)'},
    "priv_item_medium_compattel": {"en": "Firewall rule: CompatTelRunner.exe", "pl": "Reguła zapory: CompatTelRunner.exe", "fr": "Règle pare-feu : CompatTelRunner.exe", "de": 'Firewall-Regel: CompatTelRunner.exe', "es": 'Regla de firewall: CompatTelRunner.exe'},
    "priv_item_medium_devicecensus": {"en": "Firewall rule: devicecensus.exe", "pl": "Reguła zapory: devicecensus.exe", "fr": "Règle pare-feu : devicecensus.exe", "de": 'Firewall-Regel: devicecensus.exe', "es": 'Regla de firewall: devicecensus.exe'},
    "priv_item_medium_werfault": {"en": "Firewall rule: WerFault.exe", "pl": "Reguła zapory: WerFault.exe", "fr": "Règle pare-feu : WerFault.exe", "de": 'Firewall-Regel: WerFault.exe', "es": 'Regla de firewall: WerFault.exe'},
    "priv_item_medium_appraiser": {"en": "Task: Compatibility Appraiser", "pl": "Zadanie: Compatibility Appraiser", "fr": "Tâche : Compatibility Appraiser", "de": 'Aufgabe: Compatibility Appraiser', "es": 'Tarea: Compatibility Appraiser'},
    "priv_item_medium_programdata": {"en": "Task: ProgramDataUpdater", "pl": "Zadanie: ProgramDataUpdater", "fr": "Tâche : ProgramDataUpdater", "de": 'Aufgabe: ProgramDataUpdater', "es": 'Tarea: ProgramDataUpdater'},
    "priv_item_medium_consolidator": {"en": "Task: Consolidator", "pl": "Zadanie: Consolidator", "fr": "Tâche : Consolidator", "de": 'Aufgabe: Consolidator', "es": 'Tarea: Consolidator'},
    "priv_item_medium_usbceip": {"en": "Task: UsbCeip", "pl": "Zadanie: UsbCeip", "fr": "Tâche : UsbCeip", "de": 'Aufgabe: UsbCeip', "es": 'Tarea: UsbCeip'},
    "priv_item_medium_queuereporting": {"en": "Task: QueueReporting", "pl": "Zadanie: QueueReporting", "fr": "Tâche : QueueReporting", "de": 'Aufgabe: QueueReporting', "es": 'Tarea: QueueReporting'},
    "priv_item_advanced_wersvc": {"en": "Service: WerSvc", "pl": "Usługa: WerSvc", "fr": "Service : WerSvc", "de": 'Dienst: WerSvc', "es": 'Servicio: WerSvc'},
    "priv_item_advanced_pcasvc": {"en": "Service: PcaSvc", "pl": "Usługa: PcaSvc", "fr": "Service : PcaSvc", "de": 'Dienst: PcaSvc', "es": 'Servicio: PcaSvc'},
    "priv_item_advanced_activityfeed": {"en": "Registry policy: EnableActivityFeed = 0 (Timeline)", "pl": "Polityka rejestru: EnableActivityFeed = 0 (Oś czasu)", "fr": "Stratégie de registre : EnableActivityFeed = 0 (Chronologie)", "de": 'Registry-Richtlinie: EnableActivityFeed = 0 (Zeitleiste)', "es": 'Política de registro: EnableActivityFeed = 0 (Cronología)'},
    "priv_item_advanced_publishactivities": {"en": "Registry policy: PublishUserActivities = 0", "pl": "Polityka rejestru: PublishUserActivities = 0", "fr": "Stratégie de registre : PublishUserActivities = 0", "de": 'Registry-Richtlinie: PublishUserActivities = 0', "es": 'Política de registro: PublishUserActivities = 0'},
    "priv_item_advanced_uploadactivities": {"en": "Registry policy: UploadUserActivities = 0 (cross-device continuity)", "pl": "Polityka rejestru: UploadUserActivities = 0 (kontynuacja na innym urządzeniu)", "fr": "Stratégie de registre : UploadUserActivities = 0 (continuité entre appareils)", "de": 'Registry-Richtlinie: UploadUserActivities = 0 (geräteübergreifende Kontinuität)', "es": 'Política de registro: UploadUserActivities = 0 (continuidad entre dispositivos)'},
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
    "priv_desc_advanced_svc_wersvc": {"en": "Stops the crash-reporting service — you'll lose crash/BSOD report collection.", "pl": "Zatrzymuje usługę zbierania raportów o awariach — stracisz zbieranie raportów awarii/BSOD.", "fr": "Arrête le service de rapport de plantage — vous perdrez la collecte des rapports BSOD.", "de": 'Stoppt den Absturzberichtsdienst — Sie verlieren die Sammlung von Absturz-/BSOD-Berichten.', "es": 'Detiene el servicio de informes de fallos — perderás la recopilación de informes de fallos/BSOD.'},
    "priv_desc_advanced_svc_pcasvc": {"en": "Stops the Program Compatibility Assistant — you'll lose warnings about incompatible older software.", "pl": "Zatrzymuje Asystenta zgodności programów — stracisz ostrzeżenia o niekompatybilności starszego oprogramowania.", "fr": "Arrête l'Assistant de compatibilité — vous perdrez les avertissements de compatibilité.", "de": 'Stoppt den Programmkompatibilitäts-Assistenten — Sie verlieren Warnungen zu inkompatibler älterer Software.', "es": 'Detiene el Asistente de compatibilidad de programas — perderás las advertencias sobre software antiguo incompatible.'},
    "priv_desc_advanced_reg_activityfeed": {"en": "Turns off Timeline — the history of files and apps you've opened.", "pl": "Wyłącza funkcję Osi czasu — historię otwieranych plików i aplikacji.", "fr": "Désactive la Chronologie — l'historique des fichiers et applications ouverts.", "de": 'Deaktiviert die Zeitleiste — den Verlauf geöffneter Dateien und Apps.', "es": 'Desactiva la Cronología — el historial de archivos y aplicaciones que has abierto.'},
    "priv_desc_advanced_reg_publishactivities": {"en": "Stops Windows from recording your activity (opened files/apps) at all.", "pl": "Blokuje zapisywanie Twojej aktywności (otwierane pliki/aplikacje) w systemie.", "fr": "Empêche Windows d'enregistrer votre activité (fichiers/applications ouverts).", "de": 'Verhindert, dass Windows Ihre Aktivität (geöffnete Dateien/Apps) überhaupt aufzeichnet.', "es": 'Impide que Windows registre tu actividad (archivos/aplicaciones abiertos) por completo.'},
    "priv_desc_advanced_reg_uploadactivities": {"en": "Stops your activity history from being uploaded to Microsoft's cloud — you'll lose 'continue on another device'.", "pl": "Blokuje wysyłanie Twojej aktywności do chmury Microsoft — stracisz funkcję 'kontynuuj na innym urządzeniu'.", "fr": "Empêche l'envoi de votre historique d'activité vers le cloud — vous perdrez « continuer sur un autre appareil ».", "de": 'Verhindert, dass Ihr Aktivitätsverlauf in die Microsoft-Cloud hochgeladen wird — Sie verlieren „Auf einem anderen Gerät fortsetzen".', "es": "Impide que tu historial de actividad se suba a la nube de Microsoft — perderás 'continuar en otro dispositivo'."},
    "priv_gear_tooltip": {"en": "Show individual items", "pl": "Pokaż pojedyncze elementy", "fr": "Afficher les éléments individuels", "de": 'Einzelne Elemente anzeigen', "es": 'Mostrar elementos individuales'},
    "priv_level_status": {"en": "{active} of {total} active", "pl": "{active} z {total} aktywnych", "fr": "{active} sur {total} actifs", "de": '{active} von {total} aktiv', "es": '{active} de {total} activas'},
    "priv_level_status_drift": {"en": "⚠ {n} changed by the system — click to review", "pl": "⚠ {n} zmienione przez system — kliknij, by sprawdzić", "fr": "⚠ {n} modifié(s) par le système — cliquez pour vérifier", "de": '⚠ {n} vom System geändert — klicken Sie zum Überprüfen', "es": '⚠ {n} cambiado(s) por el sistema — haz clic para revisar'},
    "priv_item_drift_tooltip": {"en": "This setting was reset by Windows (e.g. a major update). It's still checked here — click 'Apply' to enforce it again.", "pl": "To ustawienie zostało zresetowane przez Windows (np. przy dużej aktualizacji). Nadal jest tu zaznaczone — kliknij 'Zastosuj', żeby wymusić je ponownie.", "fr": "Ce paramètre a été réinitialisé par Windows (ex. mise à jour majeure). Il reste coché ici — cliquez sur « Appliquer » pour le forcer à nouveau.", "de": 'Diese Einstellung wurde von Windows zurückgesetzt (z. B. bei einem großen Update). Sie ist hier weiterhin aktiviert — klicken Sie auf „Anwenden", um sie erneut durchzusetzen.', "es": "Esta opción fue restablecida por Windows (por ejemplo, en una actualización importante). Sigue marcada aquí — haz clic en 'Aplicar' para forzarla de nuevo."},
    "priv_item_missing_suffix": {"en": "(unavailable)", "pl": "(niedostępne)", "fr": "(indisponible)", "de": '(nicht verfügbar)', "es": '(no disponible)'},
    "priv_item_missing_tooltip": {"en": "This feature doesn't exist on this edition/version of Windows — there's nothing here for HOTS to protect, so it can't be enabled.", "pl": "Ta funkcja nie istnieje w tej edycji/wersji Windows — nie ma tu nic, co HOTS mógłby chronić, więc nie da się jej włączyć.", "fr": "Cette fonctionnalité n'existe pas dans cette édition/version de Windows — il n'y a rien ici à protéger, elle ne peut donc pas être activée.", "de": 'Diese Funktion existiert in dieser Edition/Version von Windows nicht — es gibt hier nichts, das HOTS schützen könnte, daher kann sie nicht aktiviert werden.', "es": 'Esta función no existe en esta edición/versión de Windows — no hay nada aquí que HOTS pueda proteger, por lo que no se puede activar.'},
    "priv_checklist_apply_btn": {"en": "Apply selection", "pl": "Zastosuj zmiany", "fr": "Appliquer la sélection", "de": 'Auswahl anwenden', "es": 'Aplicar selección'},
    "priv_checklist_hint": {"en": "Select the items you want to protect and click “Apply changes”. Unchecked items will not be protected.",
                             "pl": "Zaznacz elementy, które chcesz chronić i kliknij „Zastosuj zmiany”. Odznaczone pozycje nie będą chronione.",
                             "fr": "Sélectionnez les éléments que vous souhaitez protéger et cliquez sur « Appliquer les modifications ». Les éléments décochés ne seront pas protégés.",
                             "de": 'Wählen Sie die Elemente aus, die Sie schützen möchten, und klicken Sie auf „Änderungen anwenden". Nicht ausgewählte Elemente werden nicht geschützt.',
                             "es": 'Selecciona los elementos que deseas proteger y haz clic en «Aplicar cambios». Los elementos no marcados no estarán protegidos.',
                         },
    "priv_tweak_advertising_id": {"en": "Advertising ID", "pl": "Identyfikator reklamowy", "fr": "ID publicitaire", "de": 'Werbe-ID', "es": 'ID de publicidad'},
    "priv_tweak_advertising_id_tooltip": {
        "en": "Turns off the per-user Advertising ID used by apps to personalize ads.",
        "pl": "Wyłącza identyfikator reklamowy (per-użytkownik), używany przez aplikacje do personalizacji reklam.",
        "fr": "Désactive l'ID publicitaire par utilisateur utilisé pour personnaliser les publicités.",
    
        "de": 'Deaktiviert die benutzerbezogene Werbe-ID, die von Apps zur Personalisierung von Werbung verwendet wird.',
        "es": 'Desactiva el ID de publicidad por usuario que las aplicaciones utilizan para personalizar anuncios.',
    },
    "priv_tweak_bing_search": {"en": "Bing search in Start Menu", "pl": "Wyszukiwanie Bing w menu Start", "fr": "Recherche Bing dans le menu Démarrer", "de": 'Bing-Suche im Startmenü', "es": 'Búsqueda de Bing en el menú Inicio'},
    "priv_tweak_bing_search_tooltip": {
        "en": "Stops Start Menu search from sending your queries to Bing over the web.",
        "pl": "Zatrzymuje wysyłanie zapytań z wyszukiwania w menu Start do Bing przez internet.",
        "fr": "Empêche la recherche du menu Démarrer d'envoyer vos requêtes à Bing.",
    
        "de": 'Verhindert, dass die Startmenü-Suche Ihre Anfragen über das Web an Bing sendet.',
        "es": 'Impide que la búsqueda del menú Inicio envíe tus consultas a Bing a través de internet.',
    },
    "priv_tweak_search_suggestions": {"en": "Search box suggestions", "pl": "Sugestie w polu wyszukiwania", "fr": "Suggestions de recherche", "de": 'Vorschläge im Suchfeld', "es": 'Sugerencias del cuadro de búsqueda'},
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
    "par_cat_antispy_domains": {"en": "Block telemetry domains (hosts)",
                             "pl": "Blokada domen telemetrycznych (hosts)",
                             "fr": "Bloquer les domaines de télémétrie (hosts)",
                             "de": 'Telemetrie-Domains blockieren (hosts)',
                             "es": 'Bloquear dominios de telemetría (hosts)',
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
    "par_comment_name_telemetry": {"en": "Telemetry Domains", "pl": "Domeny telemetryczne", "fr": "Domaines de télémétrie", "de": 'Telemetrie-Domains', "es": 'Dominios de telemetría'},
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
    "import_confirm_msg":    {"en": "Found {n} entries in the selected file.\n\nDo you want to import them?\n(Duplicates or formatting errors can be fixed later with 'Repair file').", "pl": "Znaleziono {n} wpisów w wybranym pliku.\n\nCzy chcesz je zaimportować do programu?\n(Ewentualne duplikaty lub błędy formatowania uporządkujesz później funkcją 'Napraw plik').", "fr": "Trouvé {n} entrées dans le fichier sélectionné.\n\nVoulez-vous les importer?\n(Les doublons ou erreurs de formatage peuvent être corrigés avec 'Réparer fichier').", "de": '{n} Einträge in der ausgewählten Datei gefunden.\n\nMöchten Sie sie importieren?\n(Duplikate oder Formatierungsfehler können später mit „Datei reparieren" behoben werden).', "es": "Se encontraron {n} entradas en el archivo seleccionado.\n\n¿Deseas importarlas?\n(Los duplicados o errores de formato se pueden corregir después con 'Reparar archivo')."},
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
            "You're about to add {n} entr(y/ies). After that, you would have {total} "
            "active entries in total — above the safe limit of {max}.\n\n"
            "You'll still be able to add them, but HOTS will refuse to save the file "
            "until you disable/delete enough entries to get back under {max} "
            "(see 'Protection & Privacy' — Windows performance limit).\n\n"
            "Add anyway?"
        ),
        "pl": (
            "Zamierzasz dodać {n} wpis(ów). Po tym miałbyś łącznie {total} aktywnych "
            "wpisów — powyżej bezpiecznego limitu {max}.\n\n"
            "Dodanie się wykona, ale HOTS odmówi zapisu pliku, dopóki nie wyłączysz/"
            "usuniesz wystarczająco wpisów, żeby wrócić poniżej {max} (patrz limit "
            "wydajności Windows przy zapisie).\n\n"
            "Dodać mimo to?"
        ),
        "fr": (
            "Vous êtes sur le point d'ajouter {n} entrée(s). Vous auriez alors {total} "
            "entrées actives au total — au-dessus de la limite sécurisée de {max}.\n\n"
            "L'ajout s'effectuera, mais HOTS refusera d'enregistrer le fichier tant que "
            "vous n'aurez pas désactivé/supprimé assez d'entrées pour repasser sous "
            "{max}.\n\n"
            "Ajouter quand même?"
        ),
    
        "de": 'Sie sind dabei, {n} Eintrag/Einträge hinzuzufügen. Danach hätten Sie insgesamt {total} aktive Einträge — über dem sicheren Limit von {max}.\n\nSie können sie trotzdem hinzufügen, aber HOTS wird das Speichern der Datei verweigern, bis Sie genügend Einträge deaktivieren/löschen, um wieder unter {max} zu kommen (siehe „Schutz & Datenschutz" — Windows-Leistungslimit).\n\nTrotzdem hinzufügen?',
        "es": "Estás a punto de añadir {n} entrada(s). Después de eso, tendrías {total} entradas activas en total — por encima del límite seguro de {max}.\n\nAún podrás añadirlas, pero HOTS se negará a guardar el archivo hasta que desactives/elimines suficientes entradas para volver a estar por debajo de {max} (consulta 'Protección y privacidad' — límite de rendimiento de Windows).\n\n¿Añadir de todos modos?",
    },
    "import_limit_ask_msg":   {
        "en": (
            "This file contains {n} entries. After importing, you would have {total} "
            "active entries in total — above the safe limit of {max}.\n\n"
            "You'll be able to import them and review the list, but HOTS will refuse "
            "to save the file until you disable/delete enough entries to get back "
            "under {max} (see 'Protection & Privacy' — Windows performance limit).\n\n"
            "Import anyway?"
        ),
        "pl": (
            "Ten plik zawiera {n} wpisów. Po imporcie miałbyś łącznie {total} aktywnych "
            "wpisów — powyżej bezpiecznego limitu {max}.\n\n"
            "Import się wykona i będziesz mógł/mogła przejrzeć listę, ale HOTS odmówi "
            "zapisu pliku, dopóki nie wyłączysz/usuniesz wystarczająco wpisów, żeby "
            "wrócić poniżej {max} (patrz limit wydajności Windows przy zapisie).\n\n"
            "Zaimportować mimo to?"
        ),
        "fr": (
            "Ce fichier contient {n} entrées. Après l'import, vous auriez {total} "
            "entrées actives au total — au-dessus de la limite sécurisée de {max}.\n\n"
            "L'import s'effectuera et vous pourrez consulter la liste, mais HOTS "
            "refusera d'enregistrer le fichier tant que vous n'aurez pas désactivé/"
            "supprimé assez d'entrées pour repasser sous {max}.\n\n"
            "Importer quand même?"
        ),
    
        "de": 'Diese Datei enthält {n} Einträge. Nach dem Import hätten Sie insgesamt {total} aktive Einträge — über dem sicheren Limit von {max}.\n\nSie können sie importieren und die Liste überprüfen, aber HOTS wird das Speichern der Datei verweigern, bis Sie genügend Einträge deaktivieren/löschen, um wieder unter {max} zu kommen (siehe „Schutz & Datenschutz" — Windows-Leistungslimit).\n\nTrotzdem importieren?',
        "es": "Este archivo contiene {n} entradas. Después de importar, tendrías {total} entradas activas en total — por encima del límite seguro de {max}.\n\nPodrás importarlas y revisar la lista, pero HOTS se negará a guardar el archivo hasta que desactives/elimines suficientes entradas para volver a estar por debajo de {max} (consulta 'Protección y privacidad' — límite de rendimiento de Windows).\n\n¿Importar de todos modos?",
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
    "export_ok_txt_msg":     {"en": "Exported hosts file ({n} entries):\n{path}", "pl": "Wyeksportowano plik hosts ({n} wpisów):\n{path}", "fr": "Fichier hosts exporté ({n} entrées):\n{path}", "de": 'Hosts-Datei exportiert ({n} Einträge):\n{path}', "es": 'Archivo hosts exportado ({n} entradas):\n{path}'},
    "export_err_title":      {"en": "Export error", "pl": "Błąd eksportu", "fr": "Erreur d'export", "de": 'Exportfehler', "es": 'Error de exportación'},
    "save_backup_err":       {"en": "Failed to create hosts file backup: {ex}", "pl": "Nie udało się utworzyć kopii zapasowej pliku hosts: {ex}", "fr": "Echec de la creation de la sauvegarde: {ex}", "de": 'Sicherung der Hosts-Datei konnte nicht erstellt werden: {ex}', "es": 'No se pudo crear la copia de seguridad del archivo hosts: {ex}'},
    "save_perm_err":         {"en": "Access denied to write hosts file. Run the program as Administrator.", "pl": "Brak uprawnień do zapisu pliku hosts. Uruchom program jako Administrator.", "fr": "Acces refuse pour ecrire le fichier hosts. Lancez le programme en tant qu'Administrateur.", "de": 'Zugriff zum Schreiben der Hosts-Datei verweigert. Führen Sie das Programm als Administrator aus.', "es": 'Acceso denegado para escribir el archivo hosts. Ejecuta el programa como Administrador.'},
    "save_write_err":        {"en": "Error writing file: {ex}", "pl": "Błąd podczas zapisu pliku: {ex}", "fr": "Erreur lors de l'ecriture du fichier: {ex}", "de": 'Fehler beim Schreiben der Datei: {ex}', "es": 'Error al escribir el archivo: {ex}'},
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
        "en": "✅ Cloudflare DNS Protection has been enabled.",
        "pl": "✅ Ochrona Cloudflare DNS została włączona.",
        "fr": "✅ La protection Cloudflare DNS a été activée.",
    
        "de": '✅ Der Cloudflare-DNS-Schutz wurde aktiviert.',
        "es": '✅ La protección DNS de Cloudflare ha sido activada.',
    },

    "par_cf_off_ok": {
        "en": "✅ Original DNS servers have been restored.\nCloudflare Family protection is now disabled.",
        "pl": "✅ Oryginalne serwery DNS zostały przywrócone.\nOchrona Cloudflare Family jest teraz wyłączona.",
        "fr": "✅ Les serveurs DNS d'origine ont été restaurés.\nLa protection Cloudflare Family est maintenant désactivée.",
    
        "de": '✅ Die ursprünglichen DNS-Server wurden wiederhergestellt.\nDer Cloudflare-Family-Schutz ist jetzt deaktiviert.',
        "es": '✅ Se han restaurado los servidores DNS originales.\nLa protección de Cloudflare Family está ahora desactivada.',
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


def T(key: str, **kwargs) -> str:
    entry = _STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(_current_lang) or entry.get("en") or key
    return text.format(**kwargs) if kwargs else text
