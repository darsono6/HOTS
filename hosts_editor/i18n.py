"""
Localisation (i18n) module for HOTS.
Default language: English (EN).
Supported: EN, PL, FR.

Usage anywhere in the project:
    from .i18n import T, set_lang, current_lang

    T("add")          → "Add" / "Dodaj" / "Ajouter"
    T("status_bar")   → "Entries: {n}" (format with .format(n=...))
"""

from __future__ import annotations

LANGUAGES: dict[str, str] = {
    "en": "English",
    "pl": "Polski",
    "fr": "Français",
}

_STRINGS: dict[str, dict[str, str]] = {

    # ── Toolbar ────────────────────────────────────────────────────────────
    "btn_add":      {"en": "Add",    "pl": "Dodaj",    "fr": "Ajouter"},
    "btn_edit":     {"en": "Edit",   "pl": "Edytuj",   "fr": "Modifier"},
    "btn_toggle":   {"en": "On/Off", "pl": "Wł/Wył",   "fr": "Act/Dés"},
    "btn_delete":   {"en": "Delete", "pl": "Usuń",     "fr": "Supprimer"},
    "btn_save":     {"en": "Save",   "pl": "Zapisz",   "fr": "Enregistrer"},
    "btn_import":   {"en": "Import", "pl": "Importuj", "fr": "Importer"},
    "btn_export":   {"en": "Export", "pl": "Eksportuj","fr": "Exporter"},
    "btn_backups":  {"en": "Backups","pl": "Kopie",    "fr": "Sauvegardes"},

    # ── Sidebar ────────────────────────────────────────────────────────────
    "btn_repair":      {"en": "Repair file",       "pl": "Napraw plik",          "fr": "Réparer fichier"},
    "btn_default":     {"en": "Default hosts",     "pl": "Domyślny hosts",       "fr": "Hosts par défaut"},
    "btn_check_dom":   {"en": "Check domains",     "pl": "Sprawdź domeny",       "fr": "Vérifier domaines"},
    "btn_malware":     {"en": "Scan malware",      "pl": "Szukaj malware",       "fr": "Scanner malware"},
    "btn_parental":    {"en": "Parental Control  ","pl": "Ochrona Rodzicielska", "fr": "Contrôle parental"},
    "btn_options":     {"en": "Options",           "pl": "Opcje",                "fr": "Options"},

    # ── Options panel ──────────────────────────────────────────────────────
    "opt_about":       {"en": "About",             "pl": "O programie",          "fr": "À propos"},
    "opt_support":     {"en": "Support",           "pl": "Wsparcie",             "fr": "Soutenir"},
    "opt_show_raw":    {"en": "Show Raw",          "pl": "Pokaż Host",           "fr": "Afficher brut"},
    "opt_language":    {"en": "Language",          "pl": "Język",                "fr": "Langue"},

    # ── Password option (dynamic label) ───────────────────────────────────
    "opt_pass_on":     {"en": "Password: ON",    "pl": "Hasło: WŁ",           "fr": "Passe: ACT"},
    "opt_pass_off":    {"en": "Set Password",   "pl": "Ustaw Hasło",          "fr": "Mot de passe"},

    # ── Table columns ──────────────────────────────────────────────────────
    "col_status":      {"en": "Status",      "pl": "Status",      "fr": "Statut"},
    "col_ip":          {"en": "IP Address",  "pl": "Adres IP",    "fr": "Adresse IP"},
    "col_hostname":    {"en": "Hostname",    "pl": "Hostname",    "fr": "Nom d'hôte"},
    "col_comment":     {"en": "Comment",     "pl": "Komentarz",   "fr": "Commentaire"},
    "status_active":   {"en": "✔ active",   "pl": "✔ aktywny",  "fr": "✔ actif"},
    "status_disabled": {"en": "✘ disabled", "pl": "✘ wyłączony", "fr": "✘ désactivé"},

    # ── Status / search bar ────────────────────────────────────────────────
    "status_entries":   {"en": "Entries: {total}  |  Active: {active}  |  Disabled: {disabled}",
                         "pl": "Wpisów: {total}  |  Aktywnych: {active}  |  Wyłączonych: {disabled}",
                         "fr": "Entrées: {total}  |  Actives: {active}  |  Désactivées: {disabled}"},
    "status_filter":    {"en": "Filter: {shown} of {total} entries",
                         "pl": "Filtr: {shown} z {total} wpisów",
                         "fr": "Filtre: {shown} sur {total} entrées"},
    "status_saving":    {"en": "⏳ Windows DNS Client is verifying structure and updating cache... Please wait.",
                         "pl": "⏳ System Windows (Klient DNS) weryfikuje strukturę i aktualizuje pamięć podatną... Proszę czekać.",
                         "fr": "⏳ Le client DNS Windows vérifie la structure et met à jour le cache... Veuillez patienter."},
    "hint_multiselect": {"en": "Shift+click / Ctrl+click — select multiple entries",
                         "pl": "Shift+klik / Ctrl+klik — zaznacz wiele wpisów",
                         "fr": "Maj+clic / Ctrl+clic — sélectionner plusieurs entrées"},

    # ── Context menu ───────────────────────────────────────────────────────
    "ctx_edit":     {"en": "Edit",         "pl": "Edytuj",        "fr": "Modifier"},
    "ctx_delete":   {"en": "Delete",       "pl": "Usuń",          "fr": "Supprimer"},
    "ctx_toggle":   {"en": "Enable/Disable","pl": "Włącz/Wyłącz","fr": "Activer/Désactiver"},
    "ctx_zero_ip":  {"en": "Change IP to 0.0.0.0","pl": "Zmień IP na 0.0.0.0","fr": "Changer IP en 0.0.0.0"},

    # ── Dialogs: titles ────────────────────────────────────────────────────
    "dlg_unsaved_title":   {"en": "Unsaved changes",     "pl": "Niezapisane zmiany",     "fr": "Modifications non enregistrées"},
    "dlg_unsaved_msg":     {"en": "You have unsaved changes in the hosts file.\n\nExit without saving?",
                            "pl": "Masz niezapisane zmiany w pliku hosts.\n\nWyjść bez zapisywania?",
                            "fr": "Vous avez des modifications non enregistrées dans le fichier hosts.\n\nQuitter sans enregistrer?"},
    "dlg_no_selection":    {"en": "No selection",        "pl": "Brak zaznaczenia",       "fr": "Aucune sélection"},
    "dlg_no_sel_msg":      {"en": "Select entries in the table to check.",
                            "pl": "Zaznacz wpisy w tabeli które chcesz sprawdzić.",
                            "fr": "Sélectionnez des entrées dans le tableau à vérifier."},
    "dlg_about_title":     {"en": "About",               "pl": "O programie",            "fr": "À propos"},

    "about_subtitle":      {"en": "Hosts File Editor",
                            "pl": "Edytor pliku hosts",
                            "fr": "Éditeur de fichier hosts"},
    "about_version":       {"en": "version 1.1",
                            "pl": "wersja 1.1",
                            "fr": "version 1.1"},
    "about_desc":          {"en": "Advanced Windows hosts file editor\nwith dark theme, diagnostics and parental control.",
                            "pl": "Zaawansowany edytor pliku hosts systemu Windows\nz ciemnym motywem, diagnostyką i ochroną rodzicielską.",
                            "fr": "Éditeur avancé du fichier hosts Windows\navec thème sombre, diagnostics et contrôle parental."},
    "about_feat_parental": {"en": "Parental control",
                            "pl": "Ochrona rodzicielska",
                            "fr": "Contrôle parental"},
    "about_feat_diag":     {"en": "Domain & malware diagnostics",
                            "pl": "Diagnostyka domen i malware",
                            "fr": "Diagnostics domaines et malware"},
    "about_feat_backup":   {"en": "Backups with rotation",
                            "pl": "Kopie zapasowe z rotacją",
                            "fr": "Sauvegardes avec rotation"},
    "about_feat_raw":      {"en": "Raw view & edit",
                            "pl": "Podgląd i edycja raw",
                            "fr": "Vue et édition brute"},
    "about_feat_password": {"en": "Password lock",
                            "pl": "Blokada hasłem",
                            "fr": "Verrouillage par mot de passe"},
    "about_feat_lang":     {"en": "Multilingual interface",
                            "pl": "Wielojęzyczny interfejs",
                            "fr": "Interface multilingue"},
    "about_feat_antispy":  {"en": "Windows AntiSpy",
                            "pl": "Windows AntiSpy",
                            "fr": "Windows AntiSpy"},
    "about_feat_export":   {"en": "Export to file",
                            "pl": "Eksport do pliku",
                            "fr": "Export vers un fichier"},
    "about_footer":        {"en": "© 2026 Darsono  •  All rights reserved",
                            "pl": "© 2026 Darsono  •  Wszelkie prawa zastrzeżone",
                            "fr": "© 2026 Darsono  •  Tous droits réservés"},
    "about_close":         {"en": "Close",
                            "pl": "Zamknij",
                            "fr": "Fermer"},

    # ── Save dialogs ───────────────────────────────────────────────────────
    "save_success_title":  {"en": "Success",             "pl": "Sukces",                 "fr": "Succès"},
    "save_success_msg":    {"en": "Hosts file saved successfully!\nBackup created automatically.",
                            "pl": "Plik hosts został pomyślnie zapisany!\nKopia zapasowa utworzona automatycznie.",
                            "fr": "Fichier hosts enregistré avec succès!\nSauvegarde créée automatiquement."},
    "save_dns_ok":         {"en": "The Windows 'DNS Client' service successfully processed the structure and released the file handle.",
                            "pl": "Systemowa usługa 'Klient DNS' pomyślnie przetworzyła strukturę i zwolniła uchwyt pliku.",
                            "fr": "Le service Windows 'Client DNS' a traité la structure avec succès et libéré le descripteur de fichier."},
    "save_dns_slow":       {"en": "Note: File saved, but the DNS service needs more time to fully process changes in the background.",
                            "pl": "Uwaga: Plik zapisany, ale usługa DNS potrzebuje więcej czasu na pełne przetworzenie zmian w tle.",
                            "fr": "Remarque: Fichier enregistré, mais le service DNS a besoin de plus de temps pour traiter les modifications en arrière-plan."},
    "save_err_title":      {"en": "Write error",         "pl": "Błąd zapisu",            "fr": "Erreur d'écriture"},
    "save_perm_title":     {"en": "Access denied (DNS system lock)", "pl": "Odmowa dostępu (Lock systemowy DNS)", "fr": "Accès refusé (verrouillage DNS système)"},
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
    },

    # ── Save: limit warning ────────────────────────────────────────────────
    "save_limit_title": {"en": "Write blocked: Windows performance limit",
                         "pl": "Blokada Zapisu: Limit wydajności Windows",
                         "fr": "Écriture bloquée: Limite de performance Windows"},
    "save_limit_msg":   {
        "en": (
            "SECURITY ERROR: As many as {n} active entries detected!\n\n"
            "Due to critical performance limits of the Windows 'DNS Client' service, "
            "HOTS has blocked the save operation.\n\n"
            "Saving more than 20,000 active domains can cause:\n"
            "• Permanent file lock by the system (Exclusive Lock),\n"
            "• 100% CPU usage and network service freeze,\n"
            "• Complete internet loss on this computer.\n\n"
            "Solution: Disable some domains (keep active count below 20k) "
            "or move filtering to a local DNS server (e.g. AdGuard Home or Acrylic DNS)."
        ),
        "pl": (
            "BŁĄD BEZPIECZEŃSTWA: Wykryto aż {n} aktywnych wpisów!\n\n"
            "Z powodu krytycznych ograniczeń wydajności systemowej usługi 'Klient DNS' w Windows, "
            "program HOTS zablokował operację zapisu.\n\n"
            "Zapisanie ponad 20 000 aktywnych domen może doprowadzić do:\n"
            "• Permanentnego zablokowania pliku hosts przez system (Exclusive Lock),\n"
            "• Zużycia 100% mocy procesora i zawieszenia usług sieciowych,\n"
            "• Całkowitego odcięcia internetu na tym komputerze.\n\n"
            "Rozwiązanie: Wyłącz część domen (odzyskaj status poniżej 20 tys.) "
            "lub przenieś filtrowanie na lokalny serwer DNS (np. AdGuard Home lub Acrylic DNS)."
        ),
        "fr": (
            "ERREUR DE SÉCURITÉ: {n} entrées actives détectées!\n\n"
            "En raison des limites critiques de performance du service Windows 'Client DNS', "
            "HOTS a bloqué l'opération d'enregistrement.\n\n"
            "Enregistrer plus de 20 000 domaines actifs peut causer:\n"
            "• Verrouillage permanent du fichier par le système (Exclusive Lock),\n"
            "• Utilisation à 100% du processeur et gel des services réseau,\n"
            "• Perte totale d'internet sur cet ordinateur.\n\n"
            "Solution: Désactivez certains domaines (gardez le nombre en dessous de 20k) "
            "ou déplacez le filtrage vers un serveur DNS local (ex. AdGuard Home ou Acrylic DNS)."
        ),
    },

    # ── Repair ─────────────────────────────────────────────────────────────
    "repair_no_changes_title": {"en": "No changes",    "pl": "Brak zmian",    "fr": "Aucun changement"},
    "repair_no_changes_msg":   {"en": "The hosts file required no syntax repairs.",
                                "pl": "Plik hosts nie wymagał żadnych napraw składniowych.",
                                "fr": "Le fichier hosts n'a nécessité aucune réparation syntaxique."},
    "repair_done_title":       {"en": "Repaired",      "pl": "Naprawiono",    "fr": "Réparé"},
    "repair_done_header":      {"en": "Hosts file cleaned. Save changes to apply.",
                                "pl": "Plik hosts został oczyszczony z błędów.\nZapisz zmiany, aby je utrwalić.",
                                "fr": "Fichier hosts nettoyé. Enregistrez les modifications pour les appliquer."},
    "repair_wildcards":        {"en": "• Fixed {n} wildcard entry/entries.",
                                "pl": "• Naprawiono {n} wpis(ów) z wildcard.",
                                "fr": "• Corrigé {n} entrée(s) avec wildcard."},
    "repair_dups":             {"en": "• Removed {n} duplicate entry/entries.",
                                "pl": "• Usunięto {n} zduplikowanych wpisów.",
                                "fr": "• Supprimé {n} entrée(s) en double."},
    "repair_invalid":          {"en": "• Removed {n} invalid entry/entries.",
                                "pl": "• Usunięto {n} niepoprawnych wpisów.",
                                "fr": "• Supprimé {n} entrée(s) invalide(s)."},
    "repair_normalized":       {"en": "• Normalized {n} hostname(s) to lowercase.",
                                "pl": "• Znormalizowano {n} hostname(ów) do małych liter.",
                                "fr": "• Normalisé {n} nom(s) d'hôte en minuscules."},

    # ── Restore default ────────────────────────────────────────────────────
    "restore_ask_title": {"en": "Restore default hosts?",
                          "pl": "Przywrócić domyślny hosts?",
                          "fr": "Restaurer le hosts par défaut?"},
    "restore_ask_msg":   {"en": "The current hosts file will be replaced with Microsoft's default version.\nA backup will be created.",
                          "pl": "Obecny plik hosts zostanie zastąpiony domyślną wersją Microsoft.\nZostanie wykonana kopia zapasowa.",
                          "fr": "Le fichier hosts actuel sera remplacé par la version par défaut de Microsoft.\nUne sauvegarde sera créée."},
    "restore_done_title":{"en": "Restored",   "pl": "Przywrócono",   "fr": "Restauré"},
    "restore_done_msg":  {"en": "Hosts file restored to Microsoft's default version.",
                          "pl": "Plik hosts został przywrócony do domyślnej wersji Microsoft.",
                          "fr": "Le fichier hosts a été restauré à la version par défaut de Microsoft."},

    # ── No-selection messages ──────────────────────────────────────────────
    "no_sel_title":      {"en": "No selection",    "pl": "Brak zaznaczenia",    "fr": "Aucune sélection"},
    "no_sel_edit":       {"en": "Select an entry to edit.",
                          "pl": "Zaznacz wpis do edycji.",
                          "fr": "Sélectionnez une entrée à modifier."},
    "no_sel_toggle":     {"en": "Select one or more entries.",
                          "pl": "Zaznacz wpis lub wpisy.",
                          "fr": "Sélectionnez une ou plusieurs entrées."},
    "no_sel_delete":     {"en": "Select one or more entries to delete.",
                          "pl": "Zaznacz wpis lub wpisy do usunięcia.",
                          "fr": "Sélectionnez une ou plusieurs entrées à supprimer."},
    "no_sel_raw_delete": {"en": "Select text or a whole line in the editor to delete.",
                          "pl": "Zaznacz tekst lub całą linię w edytorze, którą chcesz usunąć.",
                          "fr": "Sélectionnez du texte ou une ligne entière dans l'éditeur à supprimer."},
    "no_sel_check":      {"en": "Select entries in the table to check.",
                          "pl": "Zaznacz wpisy w tabeli które chcesz sprawdzić.",
                          "fr": "Sélectionnez des entrées dans le tableau à vérifier."},

    # ── Delete confirmation ────────────────────────────────────────────────
    "del_confirm_title":   {"en": "Confirm",        "pl": "Potwierdzenie",      "fr": "Confirmation"},
    "del_confirm_one":     {"en": "Delete entry:\n{ip}  {hostname}?",
                            "pl": "Usunąć wpis:\n{ip}  {hostname}?",
                            "fr": "Supprimer l'entrée:\n{ip}  {hostname}?"},
    "del_confirm_many":    {"en": "Delete {n} selected entries?\n\n{preview}{suffix}",
                            "pl": "Usunąć {n} zaznaczone wpisy?\n\n{preview}{suffix}",
                            "fr": "Supprimer {n} entrées sélectionnées?\n\n{preview}{suffix}"},
    "del_more":            {"en": "\n… and {n} more",
                            "pl": "\n… i {n} więcej",
                            "fr": "\n… et {n} de plus"},

    # ── Raw view label ─────────────────────────────────────────────────────
    "raw_view_hint":       {"en": "📄  Raw mode — edit the file like Notepad. Use the 💾 Save button above to save changes.",
                            "pl": "📄  Tryb surowy — edytujesz plik jak w Notatniku. Użyj przycisku 💾 Zapisz na górze aby zapisać zmiany.",
                            "fr": "📄  Mode brut — éditez le fichier comme dans le Bloc-notes. Utilisez le bouton 💾 Enregistrer ci-dessus pour sauvegarder."},

    # ── Parse error ────────────────────────────────────────────────────────
    "parse_err_title":     {"en": "Parse error",    "pl": "Błąd parsowania",    "fr": "Erreur d'analyse"},


    "lang_title":        {"en": "Language",   "pl": "Język",         "fr": "Langue"},
    "lang_restart_msg":  {"en": "Language changed. Restart the application to apply.",
                          "pl": "Język zmieniony. Uruchom ponownie aplikację, aby zastosować.",
                          "fr": "Langue modifiée. Redémarrez l'application pour appliquer."},

# ══════════════════════════════════════════════════════════════════════
    # BACKUP DIALOG
    # ══════════════════════════════════════════════════════════════════════
    "bak_title":         {"en": "Backup Manager",               "pl": "Menedżer kopii zapasowych",        "fr": "Gestionnaire de sauvegardes"},
    "bak_header":        {"en": "Hosts file backups",           "pl": "Kopie zapasowe pliku hosts",       "fr": "Sauvegardes du fichier hosts"},
    "bak_subheader":     {"en": "Each save creates a new backup. You can restore any of them.",
                          "pl": "Każdy zapis tworzy nową kopię. Możesz przywrócić dowolną.",
                          "fr": "Chaque enregistrement crée une nouvelle sauvegarde. Vous pouvez restaurer n'importe laquelle."},
    "bak_btn_restore":   {"en": "Restore selected",             "pl": "Przywróć zaznaczoną",              "fr": "Restaurer la sélection"},
    "bak_btn_delete":    {"en": "Delete selected",              "pl": "Usuń zaznaczone",                  "fr": "Supprimer la sélection"},
    "bak_hint_multi":    {"en": "Shift+click or Ctrl+click — select multiple",
                          "pl": "Shift+klik lub Ctrl+klik — zaznacz wiele",
                          "fr": "Maj+clic ou Ctrl+clic — sélectionner plusieurs"},
    "bak_col_date":      {"en": "Date & Time",                  "pl": "Data i godzina",                   "fr": "Date et heure"},
    "bak_col_size":      {"en": "Size",                         "pl": "Rozmiar",                          "fr": "Taille"},
    "bak_col_file":      {"en": "File",                         "pl": "Plik",                             "fr": "Fichier"},
    "bak_empty":         {"en": "No backups",                   "pl": "Brak kopii",                       "fr": "Aucune sauvegarde"},
    "bak_no_sel_msg":    {"en": "Select at least one backup.",  "pl": "Zaznacz co najmniej jedną kopię.", "fr": "Sélectionnez au moins une sauvegarde."},
    "bak_too_many_title":{"en": "Too many selected",            "pl": "Za dużo zaznaczonych",             "fr": "Trop d'éléments sélectionnés"},
    "bak_too_many_msg":  {"en": "Only one backup can be restored at a time.\nSelect exactly one.",
                          "pl": "Przywróć można tylko jedną kopię na raz.\nZaznacz dokładnie jedną.",
                          "fr": "Une seule sauvegarde peut être restaurée à la fois.\nSélectionnez-en exactement une."},
    "bak_restore_ask_title": {"en": "Restore backup",          "pl": "Przywróć kopię",                   "fr": "Restaurer la sauvegarde"},
    "bak_restore_ask_msg":   {"en": "Restore hosts file from:\n{name}\n\nThe current hosts file will be overwritten (a backup will be made).",
                              "pl": "Przywrócić plik hosts z:\n{name}\n\nObecny plik hosts zostanie nadpisany (kopia zostanie wykonana).",
                              "fr": "Restaurer le fichier hosts depuis:\n{name}\n\nLe fichier hosts actuel sera écrasé (une sauvegarde sera créée)."},
    "bak_restore_ok":    {"en": "Hosts file restored successfully.", "pl": "Plik hosts został przywrócony.", "fr": "Fichier hosts restauré avec succès."},
    "bak_del_ask_title": {"en": "Delete backups",               "pl": "Usuń kopie",                       "fr": "Supprimer les sauvegardes"},
    "bak_del_ask_one":   {"en": "Permanently delete:\n{name}?", "pl": "Trwale usunąć:\n{name}?",          "fr": "Supprimer définitivement:\n{name}?"},
    "bak_del_ask_many":  {"en": "Permanently delete {n} selected backups?\n\n{names}",
                          "pl": "Trwale usunąć {n} zaznaczone kopie?\n\n{names}",
                          "fr": "Supprimer définitivement {n} sauvegardes sélectionnées?\n\n{names}"},
    "bak_status_count":    {"en": "Found {n} backup(s).",
                            "pl": "Znaleziono {n} kopii zapasowych.",
                            "fr": "{n} sauvegarde(s) trouvée(s)."},
    "bak_status_restored": {"en": "Restored backup: {name}",
                            "pl": "Przywrócono kopię: {name}",
                            "fr": "Sauvegarde restaurée : {name}"},
    "bak_status_deleted":  {"en": "Deleted {n} backup(s).",
                            "pl": "Usunięto {n} kopii zapasowych.",
                            "fr": "{n} sauvegarde(s) supprimée(s)."},
    # DIFF DIALOG
    "diff_title":        {"en": "Preview changes before saving", "pl": "Podgląd zmian przed zapisem",     "fr": "Aperçu des modifications avant enregistrement"},
    "diff_header":       {"en": "Preview changes",               "pl": "Podgląd zmian",                   "fr": "Aperçu des modifications"},
    "diff_added":        {"en": "  + added  ",                   "pl": "  + dodane  ",                    "fr": "  + ajoutées  "},
    "diff_removed":      {"en": "  − removed  ",                 "pl": "  − usunięte  ",                  "fr": "  − supprimées  "},
    "diff_no_changes":   {"en": "No changes",                    "pl": "Brak zmian",                      "fr": "Aucune modification"},
    "diff_stat":         {"en": "+{adds} added   \u2212{dels} removed", "pl": "+{adds} dodanych   \u2212{dels} usuniętych", "fr": "+{adds} ajoutées   \u2212{dels} supprimées"},
    "diff_save_anyway":  {"en": "Save anyway",                   "pl": "Zapisz mimo to",                  "fr": "Enregistrer quand même"},
    "diff_save":         {"en": "Save",                          "pl": "Zapisz",                          "fr": "Enregistrer"},
    "diff_cancel":       {"en": "Cancel",                        "pl": "Anuluj",                          "fr": "Annuler"},
    "diff_no_changes_body": {"en": "  (no changes — file is identical)\n",
                             "pl": "  (brak zmian — plik jest identyczny)\n",
                             "fr": "  (aucune modification — le fichier est identique)\n"},
    "diff_fromfile":     {"en": "hosts (current)",               "pl": "hosts (obecny)",                  "fr": "hosts (actuel)"},
    "diff_tofile":       {"en": "hosts (new)",                   "pl": "hosts (nowy)",                    "fr": "hosts (nouveau)"},
    # ENTRY DIALOG
    "entry_title_add":   {"en": "Add entry",                     "pl": "Dodaj wpis",                      "fr": "Ajouter une entrée"},
    "entry_title_edit":  {"en": "Edit entry",                    "pl": "Edytuj wpis",                     "fr": "Modifier l'entrée"},
    "entry_lbl_ip":      {"en": "IP Address:",                   "pl": "Adres IP:",                       "fr": "Adresse IP:"},
    "entry_lbl_host":    {"en": "Hostname:",                     "pl": "Hostname:",                       "fr": "Nom d'hôte:"},
    "entry_lbl_comment": {"en": "Comment:",                      "pl": "Komentarz:",                      "fr": "Commentaire:"},
    "entry_lbl_active":  {"en": "Active",                        "pl": "Aktywny",                         "fr": "Actif"},
    "entry_btn_save":    {"en": "Save",                          "pl": "Zapisz",                          "fr": "Enregistrer"},
    "entry_btn_cancel":  {"en": "Cancel",                        "pl": "Anuluj",                          "fr": "Annuler"},
    "entry_hint_bulk":   {"en": "⚠ Multiple lines detected — click Save to add all at once.",
                          "pl": "⚠ Wykryto wiele linii — kliknij Zapisz, aby dodać wszystkie zbiorczo.",
                          "fr": "⚠ Plusieurs lignes détectées — cliquez sur Enregistrer pour tout ajouter."},
    "entry_hint_sanitize":{"en": "⚠ Will be auto-corrected (protocol/slash removal) on save.",
                           "pl": "⚠ Zostanie auto-poprawiony (usunięcie protokołu/ukośników) przy zapisie.",
                           "fr": "⚠ Sera auto-corrigé (suppression protocole/slashes) à l'enregistrement."},
    "entry_hint_dup":    {"en": "✘ This entry already exists in the hosts file.",
                          "pl": "✘ Taki wpis już istnieje w pliku hosts.",
                          "fr": "✘ Cette entrée existe déjà dans le fichier hosts."},
    "entry_hint_bad_ip": {"en": "⚠ Invalid IP address format.",
                          "pl": "⚠ Nieprawidłowy format adresu IP.",
                          "fr": "⚠ Format d'adresse IP invalide."},
    "entry_err_title":   {"en": "Error",                         "pl": "Błąd",                            "fr": "Erreur"},
    "entry_err_bulk_fmt":{"en": "Could not parse format.\nExpected format per line: IP hostname",
                          "pl": "Nie udało się rozpoznać formatu.\nOczekiwany format każdej linii: IP hostname",
                          "fr": "Impossible d'analyser le format.\nFormat attendu par ligne: IP nom_d_hote"},
    "entry_skip_title":  {"en": "All entries already exist",     "pl": "Wszystkie wpisy już istnieją",    "fr": "Toutes les entrées existent déjà"},
    "entry_skip_some":   {"en": "Some entries skipped",          "pl": "Część wpisów pominięta",          "fr": "Certaines entrées ignorées"},
    "entry_skip_msg":    {"en": "Skipped {n} duplicate(s):\n{list}",
                          "pl": "Pominięto {n} duplikat(ów):\n{list}",
                          "fr": "Ignoré {n} doublon(s):\n{list}"},
    "entry_err_required":{"en": "IP and Hostname are required.", "pl": "IP i Hostname są wymagane.",      "fr": "L'IP et le nom d'hôte sont requis."},
    "entry_bad_ip_title":{"en": "Invalid IP",                    "pl": "Nieprawidłowy IP",                "fr": "IP invalide"},
    "entry_bad_ip_ask":  {"en": '"{ip}" does not look like a valid IPv4/IPv6 address.\n\nSave anyway?',
                          "pl": '"{ip}" nie wygląda jak poprawny adres IPv4/IPv6.\n\nZapisać mimo to?',
                          "fr": '"{ip}" ne ressemble pas à une adresse IPv4/IPv6 valide.\n\nEnregistrer quand même?'},
    "entry_dup_title":   {"en": "Duplicate",                     "pl": "Duplikat",                        "fr": "Doublon"},
    "entry_dup_ask":     {"en": 'Entry "{host}" already exists in the hosts file.\n\nAdd anyway?',
                          "pl": 'Wpis "{host}" już istnieje w pliku hosts.\n\nDodać mimo to?',
                          "fr": 'L\'entrée "{host}" existe déjà dans le fichier hosts.\n\nAjouter quand même?'},
    # DIAGNOSTICS DIALOG
    "diag_title_existence": {"en": "Domain existence check",     "pl": "Sprawdzanie istnienia domen",     "fr": "Vérification d'existence des domaines"},
    "diag_title_malware":   {"en": "Suspicious entry detection", "pl": "Wykrywanie podejrzanych wpisów",  "fr": "Détection d'entrées suspectes"},
    "diag_desc_existence":  {"en": "Checks {n} entries via external DNS (8.8.8.8) — bypasses the hosts file.\nIf a domain does not exist on the internet — the block is unnecessary.",
                             "pl": "Sprawdza {n} wpisów przez zewnętrzny DNS (8.8.8.8) — omija plik hosts.\nJeśli domena nie istnieje w internecie — blokada jest zbędna.",
                             "fr": "Vérifie {n} entrées via DNS externe (8.8.8.8) — contourne le fichier hosts.\nSi un domaine n'existe pas sur internet — le blocage est inutile."},
    "diag_desc_malware":    {"en": "Analyzes {n} entries for malware indicators.\nChecks: AV/Windows Update blocks, homoglyphs, suspicious IPs and more.",
                             "pl": "Analizuje {n} wpisów pod kątem złośliwego oprogramowania.\nSprawdza: blokady AV/Windows Update, homoglify, podejrzane IP i inne.",
                             "fr": "Analyse {n} entrées pour des indicateurs de malware.\nVérifie: blocages AV/Windows Update, homoglyphes, IPs suspectes et plus."},
    "diag_btn_run":         {"en": "Run scan",                   "pl": "Uruchom skan",                    "fr": "Lancer le scan"},
    "diag_click_to_start":  {"en": "Click Run scan to start.",   "pl": "Kliknij Uruchom skan aby rozpocząć.", "fr": "Cliquez sur Lancer le scan pour commencer."},
    "diag_col_result":      {"en": "Result",                     "pl": "Wynik",                           "fr": "Résultat"},
    "diag_col_hostname":    {"en": "Hostname",                   "pl": "Hostname",                        "fr": "Nom d'hôte"},
    "diag_col_ip":          {"en": "IP",                         "pl": "IP",                              "fr": "IP"},
    "diag_col_info":        {"en": "Info",                       "pl": "Informacja",                      "fr": "Information"},
    "diag_col_risk":        {"en": "Risk",                       "pl": "Ryzyko",                          "fr": "Risque"},
    "diag_col_reason":      {"en": "Reason",                     "pl": "Powód",                           "fr": "Raison"},
    "diag_btn_del_inactive":{"en": "Delete inactive",            "pl": "Usuń nieaktywne",                 "fr": "Supprimer les inactifs"},
    "diag_btn_del_sel":     {"en": "Delete selected",            "pl": "Usuń zaznaczone",                 "fr": "Supprimer la sélection"},
    "diag_btn_del_sel_hosts":{"en": "Delete selected from hosts","pl": "Usuń zaznaczone z hosts",         "fr": "Supprimer la sélection des hosts"},
    "diag_hint_multi":      {"en": "Shift+click / Ctrl+click — select multiple",
                             "pl": "Shift+klik / Ctrl+klik — zaznacz wiele",
                             "fr": "Maj+clic / Ctrl+clic — sélectionner plusieurs"},
    "diag_no_inactive_title":{"en": "No entries",               "pl": "Brak wpisów",                     "fr": "Aucune entrée"},
    "diag_no_inactive_msg": {"en": "No entries marked as non-existent were found.",
                             "pl": "Nie znaleziono wpisów oznaczonych jako nieistniejące.",
                             "fr": "Aucune entrée marquée comme inexistante n'a été trouvée."},
    "diag_del_confirm_title":{"en": "Confirm deletion",          "pl": "Potwierdź usunięcie",             "fr": "Confirmer la suppression"},
    "diag_del_inactive_msg":{"en": "Delete {n} unnecessary entries?\n\n{preview}{suffix}\n\nSave the file in the main window after closing this window.",
                             "pl": "Usunąć {n} zbędnych wpisów?\n\n{preview}{suffix}\n\nZapisz plik w głównym oknie po zamknięciu tego okna.",
                             "fr": "Supprimer {n} entrées inutiles?\n\n{preview}{suffix}\n\nEnregistrez le fichier dans la fenêtre principale après fermeture."},
    "diag_del_sel_msg":     {"en": "Delete {n} entries from the hosts file?\n\n{preview}{suffix}\n\nChanges will be visible in the main window.\nRemember to save the file after closing this window.",
                             "pl": "Usunąć {n} wpisów z pliku hosts?\n\n{preview}{suffix}\n\nZmiany będą widoczne w głównym oknie.\nPamiętaj aby zapisać plik po zamknięciu tego okna.",
                             "fr": "Supprimer {n} entrées du fichier hosts?\n\n{preview}{suffix}\n\nLes modifications seront visibles dans la fenêtre principale.\nPensez à enregistrer le fichier après fermeture."},
    "diag_more":            {"en": "\n... and {n} more",         "pl": "\n... i {n} więcej",              "fr": "\n... et {n} de plus"},
    "diag_no_sel_msg":      {"en": "Select entries you want to delete.",
                             "pl": "Zaznacz wpisy które chcesz usunąć.",
                             "fr": "Sélectionnez les entrées que vous souhaitez supprimer."},
    "diag_status_deleted_inactive": {"en": "Deleted {n} unnecessary entries. Save the file in the main window.",
                                     "pl": "Usunięto {n} zbędnych wpisów. Zapisz plik w głównym oknie.",
                                     "fr": "Supprimé {n} entrées inutiles. Enregistrez le fichier dans la fenêtre principale."},
    "diag_status_deleted_sel":      {"en": "Deleted {n} entries. Save the file in the main window.",
                                     "pl": "Usunięto {n} wpisów. Zapisz plik w głównym oknie.",
                                     "fr": "Supprimé {n} entrées. Enregistrez le fichier dans la fenêtre principale."},
    "diag_scanning":        {"en": "Scanning: ",                 "pl": "Sprawdzam: ",                     "fr": "Analyse: "},
    "diag_analyzing":       {"en": "Analyzing: ",                "pl": "Analizuję: ",                     "fr": "Analyse: "},
    "diag_scan_done":       {"en": "Scan complete.",             "pl": "Skan zakończony.",                 "fr": "Scan terminé."},
    "diag_summary_exist":   {"en": "Done: {found} active, {missing} unnecessary, {errors} timeout/error.",
                             "pl": "Zakończono: {found} aktywnych, {missing} zbędnych, {errors} timeout/błąd.",
                             "fr": "Terminé: {found} actifs, {missing} inutiles, {errors} timeout/erreur."},
    "diag_summary_malware": {"en": "Done. Found {issues} suspicious entries out of {total} checked.",
                             "pl": "Zakończono. Znaleziono {issues} podejrzanych wpisów z {total} sprawdzonych.",
                             "fr": "Terminé. Trouvé {issues} entrées suspectes sur {total} vérifiées."},
    "diag_exist_ok":        {"en": "✔ exists",                   "pl": "✔ istnieje",                      "fr": "✔ existe"},
    "diag_exist_ok_info":   {"en": "Domain active — block justified",  "pl": "Domena aktywna — blokada uzasadniona", "fr": "Domaine actif — blocage justifié"},
    "diag_exist_miss":      {"en": "✘ not found",                "pl": "✘ nie istnieje",                  "fr": "✘ introuvable"},
    "diag_exist_miss_info": {"en": "Not in DNS — entry unnecessary",   "pl": "Brak w DNS — wpis zbędny",        "fr": "Absent du DNS — entrée inutile"},
    "diag_exist_err":       {"en": "? timeout/error",            "pl": "? timeout/błąd",                  "fr": "? timeout/erreur"},
    "diag_exist_err_info":  {"en": "No response from DNS 8.8.8.8",    "pl": "Brak odpowiedzi z DNS 8.8.8.8",   "fr": "Pas de réponse du DNS 8.8.8.8"},
    "diag_clean":           {"en": "✔ Clean",                    "pl": "✔ Czysto",                         "fr": "✔ Propre"},
    "diag_clean_msg":       {"en": "No suspicious entries",      "pl": "Brak podejrzanych wpisów",        "fr": "Aucune entrée suspecte"},
    "diag_risk_high":       {"en": "\U0001f534 High",            "pl": "\U0001f534 Wysokie",               "fr": "\U0001f534 Élevé"},
    "diag_risk_medium":     {"en": "\U0001f7e1 Medium",          "pl": "\U0001f7e1 Średnie",               "fr": "\U0001f7e1 Moyen"},
    "diag_reason_sys_dom":  {"en": "Known system domain redirected to {ip}",
                             "pl": "Znana domena systemowa przekierowana na {ip}",
                             "fr": "Domaine système connu redirigé vers {ip}"},
    "diag_reason_update":   {"en": "System/AV update block: {host}",
                             "pl": "Blokada aktualizacji systemu/AV: {host}",
                             "fr": "Blocage mise à jour système/AV: {host}"},
    "diag_reason_public_ip":{"en": "Redirect to public IP: {ip}",
                             "pl": "Przekierowanie na publiczny IP: {ip}",
                             "fr": "Redirection vers IP public: {ip}"},
    "diag_reason_many_dom": {"en": "{n} domains on the same IP — suspicious",
                             "pl": "{n} domen na ten sam IP — podejrzane",
                             "fr": "{n} domaines sur le même IP — suspect"},
    "diag_reason_homoglyph":{"en": "Suspicious characters in hostname: {chars}",
                             "pl": "Podejrzane znaki w hostname: {chars}",
                             "fr": "Caractères suspects dans le nom d'hôte: {chars}"},
    "diag_reason_ip_host":  {"en": "Hostname is an IP address — unusual",
                             "pl": "Hostname jest adresem IP — nietypowe",
                             "fr": "Le nom d'hôte est une adresse IP — inhabituel"},
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
    },
    # PARENTAL DIALOG
    "par_title":            {"en": "🛡️ Parental Control",        "pl": "🛡️ Ochrona Rodzicielska",          "fr": "🛡️ Contrôle parental"},
    "par_header":           {"en": "🛡️  Parental Control",       "pl": "🛡️  Ochrona Rodzicielska",         "fr": "🛡️  Contrôle parental"},
    "par_subheader":        {"en": "Block selected services directly at the system level (hosts file).",
                             "pl": "Blokuj wybrane serwisy bezpośrednio na poziomie systemu (plik hosts).",
                             "fr": "Bloquez les services sélectionnés directement au niveau système (fichier hosts)."},
    "par_btn_close":        {"en": "Close",                       "pl": "Zamknij",                          "fr": "Fermer"},
    "par_blocklists_path":  {"en": "Block lists: {path}",         "pl": "Pliki blokad: {path}",             "fr": "Listes de blocage: {path}"},
    "par_file_ok":          {"en": "✔  {file}",                   "pl": "✔  {file}",                        "fr": "✔  {file}"},
    "par_file_missing":     {"en": "✘  Missing file: {file}",     "pl": "✘  Brak pliku: {file}",            "fr": "✘  Fichier manquant: {file}"},
    "par_btn_disable":      {"en": "Disable",                     "pl": "Wyłącz",                           "fr": "Désactiver"},
    "par_btn_enable":       {"en": "Enable",                      "pl": "Włącz",                            "fr": "Activer"},
    "par_btn_no_file":      {"en": "No file",                     "pl": "Brak pliku",                       "fr": "Fichier absent"},
    "par_err_no_file_title":{"en": "Missing block list",          "pl": "Brak pliku blokad",                "fr": "Liste de blocage manquante"},
    "par_err_no_file_msg":  {"en": "File not found:\n{path}\n\nCreate the file {file} in the blocklists/ folder.",
                             "pl": "Nie znaleziono pliku:\n{path}\n\nUtwórz plik {file} w folderze blocklists/.",
                             "fr": "Fichier introuvable:\n{path}\n\nCréez le fichier {file} dans le dossier blocklists/."},
    "par_err_hosts_title":  {"en": "Error",                       "pl": "Błąd",                             "fr": "Erreur"},
    "par_err_hosts_msg":    {"en": "Could not modify the hosts file.\nCheck administrator permissions.",
                             "pl": "Nie udało się zmodyfikować pliku hosts.\nSprawdź uprawnienia administratora.",
                             "fr": "Impossible de modifier le fichier hosts.\nVérifiez les permissions administrateur."},
    "par_success_title":    {"en": "Success",                     "pl": "Sukces",                           "fr": "Succès"},
    "par_success_on":       {"en": "{label} has been activated!",  "pl": "{label} została aktywowana!",      "fr": "{label} a été activé!"},
    "par_success_off":      {"en": "{label} has been deactivated!", "pl": "{label} została dezaktywowana!",  "fr": "{label} a été désactivé!"},
    "par_cat_xxx":          {"en": "Block adult content (XXX)",   "pl": "Blokada stron XXX",                "fr": "Bloquer contenu adulte (XXX)"},
    "par_cat_twitter":      {"en": "Block Twitter / X",           "pl": "Blokada Twitter / X",              "fr": "Bloquer Twitter / X"},
    "par_cat_instagram":    {"en": "Block Instagram",             "pl": "Blokada Instagram",                "fr": "Bloquer Instagram"},
    "par_cat_youtube":      {"en": "Block YouTube",               "pl": "Blokada YouTube",                  "fr": "Bloquer YouTube"},
    "par_cat_facebook":     {"en": "Block Facebook",              "pl": "Blokada Facebook",                 "fr": "Bloquer Facebook"},
    "par_cat_whatsapp":     {"en": "Block WhatsApp",              "pl": "Blokada WhatsApp",                 "fr": "Bloquer WhatsApp"},
    "par_cat_tiktok":       {"en": "Block TikTok",                "pl": "Blokada TikTok",                   "fr": "Bloquer TikTok"},
    "par_cat_twitch":       {"en": "Block Twitch",                "pl": "Blokada Twitch",                   "fr": "Bloquer Twitch"},
    "par_cat_snapchat":     {"en": "Block Snapchat",              "pl": "Blokada Snapchat",                 "fr": "Bloquer Snapchat"},
    "par_btn_working":       {"en": "Working…",                   "pl": "Przetwarzanie…",                   "fr": "Traitement…"},
    "par_antispy_err_title": {"en": "AntiSpy Error",
                             "pl": "Błąd AntiSpy",
                             "fr": "Erreur AntiSpy"},
    "par_antispy_err_msg":  {"en": "Could not apply system protection changes (services / registry / firewall).\nMake sure HOTS is running as Administrator.",
                             "pl": "Nie udało się zastosować zmian systemowych (usługi / rejestr / zapora).\nUpewnij się, że HOTS jest uruchomiony jako Administrator.",
                             "fr": "Impossible d'appliquer les modifications système (services / registre / pare-feu).\nAssurez-vous que HOTS est exécuté en tant qu'administrateur."},
    "par_cat_antispy":      {"en": "Windows AntiSpy",             "pl": "Windows AntiSpy",                  "fr": "Windows AntiSpy"},
    "par_antispy_tooltip":  {
        "en": (
            "Enable:\n"
            "Disables telemetry services (DiagTrack, dmwappushservice).\n"
            "Adds a registry entry: AllowTelemetry = 0.\n"
            "Adds outbound block rules in Windows Firewall (CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\n\n"
            "Disable:\n"
            "Restores the exact state of the services, registry, and firewall that existed on the computer immediately before Windows AntiSpy protection was activated."
        ),
        "pl": (
            "Włączenie:\n"
            "Wyłącza usługi telemetrii (DiagTrack, dmwappushservice).\n"
            "Dodaje wpis w rejestrze: AllowTelemetry = 0.\n"
            "Dodaje reguły blokady wychodzącej w Windows Firewall (CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\n\n"
            "Wyłączenie:\n"
            "Przywraca dokładny stan usług, rejestru oraz zapory, jaki znajdował się na komputerze bezpośrednio przed aktywacją ochrony Windows AntiSpy."
        ),
        "fr": (
            "Activation :\n"
            "Désactive les services de télémétrie (DiagTrack, dmwappushservice).\n"
            "Ajoute une entrée de registre : AllowTelemetry = 0.\n"
            "Ajoute des règles de blocage sortant dans le Pare-feu Windows (CompatTelRunner.exe, devicecensus.exe, WerFault.exe).\n\n"
            "Désactivation :\n"
            "Restaure l'état exact des services, du registre et du pare-feu tel qu'il était sur l'ordinateur immédiatement avant l'activation de la protection Windows AntiSpy."
        ),
    },
    "par_cat_torrent":      {"en": "Block Torrent",               "pl": "Blokada Torrent",                  "fr": "Bloquer Torrent"},
    "par_cat_pinterest":    {"en": "Block Pinterest",             "pl": "Blokada Pinterest",                "fr": "Bloquer Pinterest"},
    "par_cat_reddit":       {"en": "Block Reddit",                "pl": "Blokada Reddit",                   "fr": "Bloquer Reddit"},
    "par_cat_games":        {"en": "Block Games",                 "pl": "Blokada Gier",                     "fr": "Bloquer les jeux"},
    # PASSWORD DIALOGS
    "pwd_set_title":        {"en": "🔒  Password — HOTS program lock",  "pl": "🔒  Hasło — blokada programu HOTS", "fr": "🔒  Mot de passe — verrou HOTS"},
    "pwd_prompt_title":     {"en": "🔒  HOTS — password verification",  "pl": "🔒  HOTS — weryfikacja hasła",      "fr": "🔒  HOTS — vérification du mot de passe"},
    "pwd_info_on":          {"en": "Password is currently ENABLED.\nYou can change it or disable it completely.",
                             "pl": "Hasło jest aktualnie WŁĄCZONE.\nMożesz je zmienić lub całkowicie wyłączyć.",
                             "fr": "Le mot de passe est actuellement ACTIVÉ.\nVous pouvez le modifier ou le désactiver complètement."},
    "pwd_info_off":         {"en": "Password is currently DISABLED.\nEnter a password to protect the program from being launched.",
                             "pl": "Hasło jest aktualnie WYŁĄCZONE.\nWprowadź hasło, aby chronić program przed uruchomieniem.",
                             "fr": "Le mot de passe est actuellement DÉSACTIVÉ.\nEntrez un mot de passe pour protéger le programme."},
    "pwd_lbl_current":      {"en": "Current password:",           "pl": "Aktualne hasło:",                  "fr": "Mot de passe actuel:"},
    "pwd_lbl_new":          {"en": "New password:",               "pl": "Nowe hasło:",                      "fr": "Nouveau mot de passe:"},
    "pwd_lbl_repeat":       {"en": "Repeat new password:",        "pl": "Powtórz nowe hasło:",              "fr": "Répéter le nouveau mot de passe:"},
    "pwd_btn_set":          {"en": "Set password",                "pl": "Ustaw hasło",                      "fr": "Définir le mot de passe"},
    "pwd_btn_remove":       {"en": "Remove password",             "pl": "Usuń hasło",                       "fr": "Supprimer le mot de passe"},
    "pwd_btn_cancel":       {"en": "Cancel",                      "pl": "Anuluj",                           "fr": "Annuler"},
    "pwd_btn_confirm":      {"en": "Confirm",                     "pl": "Zatwierdź",                        "fr": "Confirmer"},
    "pwd_err_no_current":   {"en": "Enter the current password.", "pl": "Podaj aktualne hasło.",            "fr": "Entrez le mot de passe actuel."},
    "pwd_err_wrong":        {"en": "Current password is incorrect.", "pl": "Aktualne hasło jest nieprawidłowe.", "fr": "Le mot de passe actuel est incorrect."},
    "pwd_err_empty":        {"en": "New password cannot be empty.", "pl": "Nowe hasło nie może być puste.", "fr": "Le nouveau mot de passe ne peut pas être vide."},
    "pwd_err_too_short":    {"en": "Password must be at least 4 characters.", "pl": "Hasło musi mieć co najmniej 4 znaki.", "fr": "Le mot de passe doit contenir au moins 4 caractères."},
    "pwd_err_mismatch":     {"en": "Passwords do not match.",     "pl": "Hasła nie są identyczne.",         "fr": "Les mots de passe ne correspondent pas."},
    "pwd_err_no_for_remove":{"en": "Enter the current password to remove it.", "pl": "Podaj aktualne hasło aby je usunąć.", "fr": "Entrez le mot de passe actuel pour le supprimer."},
    "pwd_set_ok_title":     {"en": "Password set",                "pl": "Hasło ustawione",                  "fr": "Mot de passe défini"},
    "pwd_set_ok_msg":       {"en": "Password set successfully.\nFrom the next launch, HOTS will require a password.",
                             "pl": "Hasło zostało pomyślnie ustawione.\nOd następnego uruchomienia HOTS będzie wymagał hasła.",
                             "fr": "Mot de passe défini avec succès.\nDès le prochain lancement, HOTS demandera un mot de passe."},
    "pwd_remove_ok_title":  {"en": "Password removed",            "pl": "Hasło usunięte",                   "fr": "Mot de passe supprimé"},
    "pwd_remove_ok_msg":    {"en": "Password removed.\nThe program will no longer require a password on launch.",
                             "pl": "Hasło zostało usunięte.\nProgram nie będzie już wymagał hasła przy uruchomieniu.",
                             "fr": "Mot de passe supprimé.\nLe programme ne demandera plus de mot de passe au lancement."},
    "pwd_prompt_intro":     {"en": "HOTS is password-protected.\nEnter the password to continue.",
                             "pl": "Program HOTS jest chroniony hasłem.\nPodaj hasło, aby kontynuować.",
                             "fr": "Le programme HOTS est protégé par mot de passe.\nEntrez le mot de passe pour continuer."},
    "pwd_lbl_password":     {"en": "Password:",                   "pl": "Hasło:",                           "fr": "Mot de passe:"},
    "pwd_err_empty_field":  {"en": "Enter password.",             "pl": "Podaj hasło.",                     "fr": "Entrez le mot de passe."},
    "pwd_err_wrong_retry":  {"en": "Incorrect password. Try again.", "pl": "Nieprawidłowe hasło. Spróbuj ponownie.", "fr": "Mot de passe incorrect. Réessayez."},
    # SUPPORT DIALOG
    "sup_title":            {"en": "❤️ Support the HOTS project",  "pl": "❤️ Wesprzyj projekt HOTS",        "fr": "❤️ Soutenir le projet HOTS"},
    "sup_subtitle":         {"en": "Windows Hosts File Editor",    "pl": "Windows Hosts File Editor",       "fr": "Windows Hosts File Editor"},
    "sup_greeting":         {"en": "Hi! I'm Darsono.",             "pl": "Cześć! Jestem Darsono.",          "fr": "Salut! Je suis Darsono."},
    "sup_body":             {"en": "HOTS is a project created in my free time, completely free of charge.\nIf you enjoy it and it makes your work easier — or maybe you're just\nhaving a good day — you can support its further development.\nI'll be truly grateful for any amount, even a small one.",
                             "pl": "HOTS to projekt tworzony w wolnym czasie, całkowicie za darmo.\nJeśli program podoba Ci się i ułatwia pracę — a może po prostu\nmasz dziś dobry dzień — możesz wesprzeć jego dalszy rozwój.\nBędę naprawdę wdzięczny za każdą, nawet drobną kwotę.",
                             "fr": "HOTS est un projet créé pendant mon temps libre, entièrement gratuit.\nSi le programme vous plaît et facilite votre travail — ou peut-être\nque vous passez simplement une bonne journée — vous pouvez soutenir\nson développement. Je serai vraiment reconnaissant pour tout montant."},
    "sup_paypal_sub":       {"en": "One-time payment · No registration", "pl": "Płatność jednorazowa · Bez rejestracji", "fr": "Paiement unique · Sans inscription"},
    "sup_btn_support":      {"en": "Support",                      "pl": "Wesprzyj",                         "fr": "Soutenir"},
    "sup_alt_contact":      {"en": "You can also contact me directly:",  "pl": "Możesz też napisać do mnie bezpośrednio:", "fr": "Vous pouvez aussi me contacter directement:"},
    "sup_footer":           {"en": "Thank you for using HOTS! — Darsono", "pl": "Dziękuję za używanie HOTS! — Darsono", "fr": "Merci d'utiliser HOTS! — Darsono"},
    "sup_btn_close":        {"en": "Close",                        "pl": "Zamknij",                          "fr": "Fermer"},
    "sup_err_browser":      {"en": "Could not open the browser.\n\nGo manually to:\n{url}",
                             "pl": "Nie udało się otworzyć przeglądarki.\n\nWejdź ręcznie na:\n{url}",
                             "fr": "Impossible d'ouvrir le navigateur.\n\nAccédez manuellement à:\n{url}"},
    "sup_copied_title":     {"en": "Copied",                       "pl": "Skopiowano",                       "fr": "Copié"},
    "sup_copied_msg":       {"en": "Email address copied to clipboard!", "pl": "Adres email skopiowany do schowka!", "fr": "Adresse e-mail copiée dans le presse-papiers!"},
    "btn_yes":            {"en": "  Yes  ",   "pl": "  Tak  ",   "fr": "  Oui  "},
    "btn_no":             {"en": "  No  ",    "pl": "  Nie  ",   "fr": "  Non  "},
    "btn_ok":             {"en": "  OK  ",    "pl": "  OK  ",    "fr": "  OK  "},
    "ctx_cut":            {"en": "Cut",       "pl": "Wytnij",    "fr": "Couper"},
    "ctx_copy":           {"en": "Copy",      "pl": "Kopiuj",    "fr": "Copier"},
    "ctx_paste":          {"en": "Paste",     "pl": "Wklej",     "fr": "Coller"},
    "ctx_select_all":     {"en": "Select all","pl": "Zaznacz wszystko","fr": "Tout sélectionner"},
    "import_dialog_title":   {"en": "Select hosts file to import", "pl": "Wybierz plik hosts do importu", "fr": "Sélectionner le fichier hosts à importer"},
    "import_filetypes_hosts":{"en": "Hosts / text files", "pl": "Pliki hosts / tekstowe", "fr": "Fichiers hosts / texte"},
    "import_filetypes_all":  {"en": "All files", "pl": "Wszystkie pliki", "fr": "Tous les fichiers"},
    "import_empty_title":    {"en": "Import", "pl": "Import", "fr": "Import"},
    "import_empty_msg":      {"en": "The selected file contains no valid hosts entries.", "pl": "Wybrany plik nie zawiera prawidłowych wpisów hosts.", "fr": "Le fichier sélectionné ne contient aucune entrée hosts valide."},
    "import_confirm_title":  {"en": "Confirm import", "pl": "Potwierdź import", "fr": "Confirmer l'import"},
    "import_confirm_msg":    {"en": "Found {n} entries in the selected file.\n\nDo you want to import them?\n(Duplicates or formatting errors can be fixed later with 'Repair file').", "pl": "Znaleziono {n} wpisów w wybranym pliku.\n\nCzy chcesz je zaimportować do programu?\n(Ewentualne duplikaty lub błędy formatowania uporządkujesz później funkcją 'Napraw plik').", "fr": "Trouvé {n} entrées dans le fichier sélectionné.\n\nVoulez-vous les importer?\n(Les doublons ou erreurs de formatage peuvent être corrigés avec 'Réparer fichier')."},
    "import_header_comment": {"en": "# Imported from: {path}  [{ts}]", "pl": "# Zaimportowano z: {path}  [{ts}]", "fr": "# Importé depuis: {path}  [{ts}]"},
    "export_dialog_title":   {"en": "Export hosts entries", "pl": "Eksportuj wpisy hosts", "fr": "Exporter les entrées hosts"},
    "export_scope_label":    {"en": "Export scope",                    "pl": "Zakres eksportu",                       "fr": "Portée de l'export"},
    "export_scope_all":      {"en": "All entries ({n})",               "pl": "Wszystkie wpisy ({n})",                 "fr": "Toutes les entrées ({n})"},
    "export_scope_sel":      {"en": "Selected entries ({n})",          "pl": "Zaznaczone wpisy ({n})",               "fr": "Entrées sélectionnées ({n})"},
    "export_scope_sel_none": {"en": "Selected entries (none selected)","pl": "Zaznaczone wpisy (brak zaznaczenia)",  "fr": "Entrées sélectionnées (aucune)"},
    "export_comments_label": {"en": "Comments",                        "pl": "Komentarze",                           "fr": "Commentaires"},
    "export_comments_include":{"en":"Include comments in export",      "pl": "Dołącz komentarze do eksportu",        "fr": "Inclure les commentaires dans l'export"},
    "btn_cancel":            {"en": "Cancel",                          "pl": "Anuluj",                               "fr": "Annuler"},
    "export_filetypes_txt":  {"en": "Hosts text file", "pl": "Plik tekstowy hosts", "fr": "Fichier texte hosts"},
    "export_filetypes_csv":  {"en": "CSV file (IP, Hostname, Comment)", "pl": "Plik CSV (IP, Hostname, Komentarz)", "fr": "Fichier CSV (IP, Nom d'hote, Commentaire)"},
    "export_filetypes_all":  {"en": "All files", "pl": "Wszystkie pliki", "fr": "Tous les fichiers"},
    "export_csv_headers":    {"en": "Status,IP,Hostname,Comment", "pl": "Status,IP,Hostname,Komentarz", "fr": "Statut,IP,Nom d'hote,Commentaire"},
    "export_ok_csv_title":   {"en": "Export", "pl": "Eksport", "fr": "Export"},
    "export_ok_csv_msg":     {"en": "Successfully exported to CSV:\n{path}", "pl": "Pomyślnie wyeksportowano tabelę do pliku CSV:\n{path}", "fr": "Exporté avec succès en CSV:\n{path}"},
    "export_ok_txt_title":   {"en": "Export", "pl": "Eksport", "fr": "Export"},
    "export_ok_txt_msg":     {"en": "Exported hosts file ({n} entries):\n{path}", "pl": "Wyeksportowano plik hosts ({n} wpisów):\n{path}", "fr": "Fichier hosts exporté ({n} entrées):\n{path}"},
    "export_err_title":      {"en": "Export error", "pl": "Błąd eksportu", "fr": "Erreur d'export"},
    "save_backup_err":       {"en": "Failed to create hosts file backup: {ex}", "pl": "Nie udało się utworzyć kopii zapasowej pliku hosts: {ex}", "fr": "Echec de la creation de la sauvegarde: {ex}"},
    "save_perm_err":         {"en": "Access denied to write hosts file. Run the program as Administrator.", "pl": "Brak uprawnień do zapisu pliku hosts. Uruchom program jako Administrator.", "fr": "Acces refuse pour ecrire le fichier hosts. Lancez le programme en tant qu'Administrateur."},
    "save_write_err":        {"en": "Error writing file: {ex}", "pl": "Błąd podczas zapisu pliku: {ex}", "fr": "Erreur lors de l'ecriture du fichier: {ex}"},
    "parental_comment":      {"en": "Parental Control", "pl": "Ochrona Rodzicielska", "fr": "Controle parental"},
    "parental_err":          {"en": "Parental control error: {ex}", "pl": "Błąd ochrony rodzicielskiej: {ex}", "fr": "Erreur de controle parental: {ex}"},

    # ── Parental: Cloudflare Family DNS ───────────────────────────────────────
    "par_cf_title":      {"en": "XXX Block · Cloudflare DNS",
                          "pl": "Blokada XXX · Cloudflare DNS",
                          "fr": "Blocage XXX · Cloudflare DNS"},

    "par_cf_desc":       {"en": "Cloudflare Family (1.1.1.3) — DNS filter",
                          "pl": "Cloudflare Family (1.1.1.3) — filtr DNS",
                          "fr": "Cloudflare Family (1.1.1.3) — filtre DNS"},

    "par_cf_btn_enable": {"en": "Enable",   "pl": "Włącz",    "fr": "Activer"},
    "par_cf_btn_disable":{"en": "Disable",  "pl": "Wyłącz",   "fr": "Désactiver"},

    "par_cf_tooltip": {
        "en": (
            "Cloudflare Family DNS (1.1.1.3 / 1.0.0.3) blocks adult content "
            "and known malware/phishing domains at the network level — it "
            "works for every program and browser on this computer, not "
            "just hosts-file entries.\n\n"
            "Enabling it changes the DNS servers on the active network "
            "interfaces. The hosts-based 'Block XXX Sites' filter is then "
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
            "Filtr 'Blokada stron XXX' oparty na hosts zostaje wtedy "
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
            "réseau actives. Le filtre 'Blocage sites XXX' basé sur hosts "
            "est alors désactivé, car cette protection offre déjà une "
            "couverture plus large.\n\n"
            "Sa désactivation restaure les paramètres DNS qui étaient en "
            "place sur cet ordinateur avant la modification."
        ),
    },

    "par_cf_on_ok": {
        "en": "✅ XXX Block · Cloudflare DNS has been enabled.",
        "pl": "✅ Blokada XXX · Cloudflare DNS została włączona.",
        "fr": "✅ Blocage XXX · Cloudflare DNS a été activé.",
    },

    "par_cf_off_ok": {
        "en": "✅ Original DNS servers have been restored.\nCloudflare Family protection is now disabled.",
        "pl": "✅ Oryginalne serwery DNS zostały przywrócone.\nOchrona Cloudflare Family jest teraz wyłączona.",
        "fr": "✅ Les serveurs DNS d'origine ont été restaurés.\nLa protection Cloudflare Family est maintenant désactivée.",
    },

    "par_cf_on_fail": {
        "en": "Failed to change DNS servers.\nMake sure the program is running as Administrator.",
        "pl": "Nie udało się zmienić serwerów DNS.\nUpewnij się, że program działa jako Administrator.",
        "fr": "Impossible de modifier les serveurs DNS.\nAssurez-vous que le programme s'exécute en tant qu'Administrateur.",
    },

    "par_cf_off_fail": {
        "en": "Failed to restore original DNS servers.\nYou can restore them manually in network adapter settings.",
        "pl": "Nie udało się przywrócić oryginalnych serwerów DNS.\nMożesz je przywrócić ręcznie w ustawieniach karty sieciowej.",
        "fr": "Impossible de restaurer les serveurs DNS d'origine.\nVous pouvez les restaurer manuellement dans les paramètres de la carte réseau.",
    },

    "par_cf_partial_fail": {
        "en": "⚠ Error on interfaces: {ifaces}",
        "pl": "⚠ Błąd na interfejsach: {ifaces}",
        "fr": "⚠ Erreur sur les interfaces: {ifaces}",
    },
}

# ── Active language (mutable singleton) ───────────────────────────────────────
_current_lang: str = "en"


def current_lang() -> str:
    return _current_lang


def set_lang(code: str) -> None:
    global _current_lang
    if code in LANGUAGES:
        _current_lang = code


def T(key: str, **kwargs) -> str:
    """
    Returns the translated string for the current language.
    If the key does not exist, returns the key itself (helps with debugging).
    Supports formatting: T("status_entries", total=10, active=8, disabled=2)
    """
    entry = _STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(_current_lang) or entry.get("en") or key
    return text.format(**kwargs) if kwargs else text
