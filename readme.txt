HOTS Hosts v2.1
===============

A Fluent-Design desktop application for managing the Windows hosts file.
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
- Light and dark themes with 4 accent colors
- Built-in update checker (via GitHub Releases)
- Optional password protection (SHA-256 hash stored machine-wide in the
  Registry) - required both to open the app and to uninstall it
- Raw hosts file editor with syntax highlighting
- Available in 5 languages: English, Polish, French, German, Spanish


PARENTAL CONTROL - KNOWN LIMITATIONS
-------------------------------------
Parental Control blocks domains at the system level using the hosts file
and, optionally, Cloudflare Family DNS. This is effective but has a few
inherent limitations you should know about:

1. Large platforms (TikTok, YouTube, Facebook, etc.) use hundreds of
   changing subdomains and CDN endpoints, so no blocklist can be 100%
   complete at all times. Built-in lists are updated with each release.
   You can add missing domains yourself, either directly from the main
   table or with the dedicated "Block your own domains" list, which
   survives a hosts file restore or uninstall.

2. Modern browsers (Chrome, Firefox, Edge, Brave) have a feature called
   Secure DNS / DNS-over-HTTPS (DoH). When enabled, the browser can
   bypass the hosts file entirely. As of 2.1, HOTS Hosts closes this
   gap natively - see "DNS-over-HTTPS blocking" above - so there is no
   need to change anything manually in each browser's settings.

3. The hosts file only affects this Windows PC. Phones, tablets, and
   traffic tunneled through a VPN service are not covered by these
   rules. This is separate from the VPN client blocking feature above,
   which stops specific VPN apps from launching on this PC - it does
   not affect other devices.


DISCLAIMER
----------
HOTS Hosts is provided in good faith but without any warranty. The author
is not responsible for any damage, data loss, system issues, or other
consequences resulting from the use of this application. Modifying the
hosts file affects system-level network resolution - use with care.
You use this software at your own risk.


SUPPORT
-------
If HOTS Hosts saves you time, or you'd simply like to say thanks:

  PayPal:  paypal.me/darsonodark
  Email:   hots.support@gmail.com
  www:     hotstools.com

No registration required. Any amount is appreciated.


LICENSE
-------
GNU General Public License v3.0
(c) 2026 Darsono
