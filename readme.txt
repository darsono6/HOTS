HOTS Hosts v2.5
===============

A desktop application for managing the Windows hosts file.
Part of the HOTS Tools family. Free and open-source, released under GPLv3.


OVERVIEW
--------
HOTS Hosts lets you view, edit, and manage the Windows "hosts" file through
a clean, modern interface, instead of manually editing it in Notepad with
administrator permissions.

Requires Windows 10 or Windows 11 (64-bit). Must be run as Administrator,
since the hosts file is write-protected by Windows. The installer /
shortcut is already configured to request this automatically.


MAIN FEATURES
-------------
- Real-time table view of all hosts entries, with add/edit/delete/toggle
- Live search, bulk paste, and column sorting
- Automatic backups before every save, with a Backup Manager
- Diff preview before writing changes to disk
- Import/export to .txt (hosts format) or .csv
- Domain diagnostics: DNS existence check and a heuristic malware/
  phishing scanner (typosquatting, suspicious TLDs, homoglyphs, etc.)
- Parental Control: 15 built-in category blocklists (adult content,
  social media, games, torrents, etc.) plus optional Cloudflare Family
  DNS enforcement
- Application blocking: prevent chosen programs (or a curated list of
  common VPN/proxy clients) from launching at all, with an optional
  file-level lock to stop renaming or replacing the blocked .exe
- DNS-over-HTTPS blocking: enforces the same managed-browser policy
  organizations use via Group Policy on Chrome, Edge, Brave and Firefox,
  closing the DoH bypass at the source instead of relying on manual
  browser settings; includes a drift watchdog that flags it if the
  block is ever manually reversed
- Hosts file lock: locks the hosts file itself against changes/deletion
  by other, non-elevated programs
- Block System Restore tool: prevents the Windows System Restore wizard
  from starting at all, closing a way to bypass parental controls.
  Restore points are still created automatically in the background, and
  you can still create one yourself even while this block is active
- Block your own domains: a free-text blocklist for anything not
  covered by the built-in categories - type in any domain and it's
  blocked at the hosts-file level; the list survives a hosts file
  restore or uninstall
- Privacy tools: 37 individual Windows telemetry/privacy tweaks across
  four levels (Basic / Medium / Advanced / Privacy+), with drift
  detection and System Restore integration
- Light and dark themes with 6 accent colors, Mica or Acrylic backdrop
- Built-in update checker (via GitHub Releases); checks on startup by
  default, can be switched off in Options > About
- Optional password protection (salted hash stored machine-wide in the
  Registry) - required both to open the app and to uninstall it
- Raw hosts file editor with syntax highlighting
- Available in 8 languages: English, Polish, French, German, Spanish,
  Russian, Portuguese, Italian


WHAT'S NEW IN 2.5
-----------------
- Internet blocking: a new option for parents on the Parental Protection page
- New visual effects: Acrylic material next to Mica, a glow effect with
  adjustable strength (transparency in Acrylic mode), and a switch to turn
  window effects off
- New Graphite accent color (6 accent colors in total)
- Rebuilt Options page: expandable cards for Language and Appearance, plus
  Updates (check on startup, manual check), About and Support
- License information: the About page opens the full license and the
  third-party notices
- Updates: clicking an available update now downloads the installer
  directly, instead of only opening the repository page
- Copy diagnostics: a new button on the About page copies anonymized
  system and program information to the clipboard, ready to paste into
  a bug report
- Improved blocking of your own domains: the feature has been reworked
  to work better
- Several smaller fixes and improvements throughout the application


DISCLAIMER
----------
HOTS Hosts is provided in good faith but without any warranty. The author
is not responsible for any damage, data loss, system issues, or other
consequences resulting from the use of this application. Modifying the
hosts file affects system-level network resolution - use with care.
You use this software at your own risk.


BUG REPORTS
-----------
Found a bug? In the app open About -> Copy diagnostics and paste the
result into your report (github.com/darsono6/HOTS/issues or email). It
contains the app and Windows version and the end of the error log; your
user name and computer name are replaced. The log may include names of
programs or domains mentioned in error messages - you can review it
before pasting.


SUPPORT
-------
If HOTS Hosts saves you time, or you'd simply like to say thanks:

  Ko-fi:   ko-fi.com/darsono
  PayPal:  paypal.me/darsonodark
  Email:   hots.support@gmail.com
  www:     hotstools.com

No registration required. Any amount is appreciated.


LICENSE
-------
GNU General Public License v3.0
(c) 2026 Darsono
