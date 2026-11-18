# Audit de sécurité défensif — contrôle parental HOTS Hosts

*Date : 18/11/2026. Base : commit `467161a` (v2.5) + copie de travail en cours (agent `hosts_editor/remote/`). Les numéros de ligne renvoient à l'état du dépôt à cette date et peuvent bouger avec le développement en parallèle ; les noms de fonctions servent de repère stable.*

*Modèle de menace : enfant curieux avec un compte Windows **standard**, accès physique au PC, clé USB, téléphone (partage de connexion), et Internet pour chercher des astuces. Cas secondaire : enfant **administrateur** du PC.*

*Échelle d'effort : **S** ≤ 2 jours, **M** ≈ 1 à 2 semaines, **L** > 2 semaines.*

---

## 1. Résumé exécutif

Le socle est **bon contre un enfant peu motivé** : les protections sont des réglages persistants du système (fichier hosts, IFEO, pare-feu, stratégies de registre) que le compte standard ne peut pas modifier, et l'agent SYSTEM n'est pas arrêtable par l'enfant. En revanche, la **garantie est faible face à un enfant débrouillard** : plusieurs contournements réalisables **en quelques minutes, sans droits administrateur**, ne sont pas couverts, et l'état affiché au parent peut être **trompeur**. Face à un enfant **administrateur**, il n'y a aucune garantie : la recommandation n°1 est de rendre le compte enfant « standard » **vérifiable et corrigeable depuis la console**.

**Les 5 principaux angles morts :**

1. **Navigateurs et applis non gérés** (portables, ou installés dans le profil de l'utilisateur) : Opera/Opera GX et leur VPN intégré, Tor Browser, Firefox avec son **VPN gratuit intégré depuis 2026 (disponible en France)**, copies renommées. Le blocage IFEO **par nom d'exe** et la stratégie DoH limitée à 5 navigateurs ne les arrêtent pas.
2. **Filtrage DNS facile à perdre** : Cloudflare Family est posé en **IPv4 seulement**, sur les cartes réseau actives au moment de l'activation. Le DNS IPv6 de la box reste utilisé, et le partage de connexion USB du téléphone crée une nouvelle carte réseau sans filtre. De plus, **activer CF Family retire la liste hosts « adulte »**, donc tout le filtrage adulte repose sur le DNS.
3. **Proxys et VPN sans installation** : extensions VPN/proxy de navigateur, proxy Windows propre à l'utilisateur, **VPN natif de Windows configurable par un compte standard**, sites de proxy web.
4. **Rien ne vérifie le socle** dont tout dépend : compte enfant standard, absence d'autre compte admin faible, BitLocker, Secure Boot, état réel des protections.
5. **États qui mentent et course GUI ↔ agent** : la console lit des caches JSON. Une dérive détectée « oublie » silencieusement l'état voulu. Le verrou d'écriture du hosts ne vaut qu'à l'intérieur d'un processus. Le hash du mot de passe est lisible par l'enfant.

**Phase 1 proposée** (simple, 1 clic ou par défaut) :

- un **état de conformité** remonté à la console, avec la vérification et la correction du compte enfant standard ;
- un **pack « navigateurs verrouillés »** : blocage des extensions proxy, SafeSearch et YouTube restreint, VPN et Tor des navigateurs désactivés, proxy direct, DoH désactivé pour tous les navigateurs même non détectés ;
- un **« DNS verrouillé »** : IPv6, stratégie DNS, pare-feu 53/853 et résolveurs DoH connus, liste adulte conservée ;
- des **correctifs ciblés** dans le code : états réels, ACL du hash, mutex de l'agent, verrou inter-processus, NAT64 ;
- une **alerte « PC hors ligne »** dans la console.

---

## 2. Ce qui est déjà bien couvert

| Point fort | Preuve |
|---|---|
| Protections **persistantes** dans l'OS (hosts, IFEO, pare-feu, stratégies HKLM) : elles restent actives même si l'appli est fermée et ne dépendent pas d'un processus vivant. | `core.py`, `core_appblock.py`, `core_netblock.py`, `core_doh.py` |
| Dossier d'état `C:\ProgramData\HOTS Hosts` **durci** : propriétaire Administrateurs, héritage coupé, SYSTEM + Admins seuls, refus des points de jonction. Le jeton de l'agent n'est donc pas lisible par l'enfant. | `secure_storage.py:18-34`, `remote/config.py:1-16` |
| Les fichiers d'état rejoués en admin sont **validés** avant usage (anti-injection). | `core_appblock.py:356-377` (`_clean_state`), `dns_utils.py:230-243` |
| Noms de stratégies DoH **conformes aux documentations** : `DnsOverHttpsMode=off` (Chromium), `DNSOverHTTPS\Enabled=0` + `Locked=1` (Firefox). | `core_doh.py:16-79` ; [Chromium DnsOverHttpsMode](https://github.com/chromium/chromium/blob/main/components/policy/resources/templates/policy_definitions/Miscellaneous/DnsOverHttpsMode.yaml), [Mozilla DNSOverHTTPS](https://mozilla.github.io/policy-templates/) |
| Coupure Internet : IPv4 + IPv6, tous profils, toutes interfaces (Wi-Fi, câble, partage de connexion), réactivation du pare-feu, **auto-réparation** (aussi par l'agent), exclusion de la console. | `core_netblock.py` (`enable`, `check_drift`), `remote/service.py` (`periodic_checks`) |
| Mot de passe : PBKDF2-SHA256 à 600 000 itérations, comparaison à temps constant ; désinstallation protégée (mode silencieux refusé si un mot de passe existe ; `--uninstall-apply` exige le mot de passe). | `password_utils.py:6-29`, `setup.iss:521-531`, `hosts_editor_launcher.pyw:123-134` |
| Mutex de l'interface avec **vérification du propriétaire** (anti-squat). | `hosts_editor_launcher.pyw:247-306` |
| Agent : **liste blanche d'actions**, aucune commande libre, HTTPS sortant uniquement, révocation propre (401/403/410), contrôle de version (sha256) sur `hosts.save_text`, tâche SYSTEM que le compte standard ne peut ni arrêter ni supprimer. | `remote/actions.py`, `remote/agent.py`, `remote/service.py` |
| Programmes système critiques non bloquables (évite de rendre Windows inutilisable) ; la désinstallation retire toujours l'IFEO et les ACL. | `core_appblock.py:39-50`, `uninstall_flow.py:175-201` |

Deux remarques d'honnêteté sur l'existant :

- **Verrou hosts** : par défaut, le groupe Utilisateurs n'a déjà que la lecture sur `drivers\etc\hosts` (à vérifier avec `icacls`). Le verrou n'ajoute donc **rien contre un enfant standard**, et un enfant admin peut retirer l'ACE (il garde `WRITE_DAC`). Il protège surtout contre les modifications accidentelles et les outils tiers.
- **Blocage de `rstrui.exe`** : un compte standard ne peut pas lancer une restauration système sans identifiants admin. Ce blocage ne sert donc que contre un admin, et ne couvre pas la restauration lancée depuis WinRE.

---

## 3. Tableau des angles morts

Légende : **Facilité** = pour un enfant au compte standard, sauf mention contraire. **Couvert ?** = oui / partiel / non.

### 3.1 Comptes, privilèges, secrets

| # | Vecteur | Facilité | Impact | Couvert ? | Preuve |
|---|---|---|---|---|---|
| A1 | **L'enfant est administrateur**, connaît le mot de passe ou le PIN admin, ou utilise la session ouverte du parent | Élevée si admin | **Total** : tout est désactivable | **Non** : aucune vérification. `is_admin` dans l'état de l'agent mesure **l'agent**, pas l'enfant | `remote/actions.py:742-750` (`_state_system`) |
| A2 | Autre compte admin faible : sans mot de passe, Administrateur intégré activé, ou **ouverture de session automatique** avec `DefaultPassword` en clair dans `HKLM\...\Winlogon` (lisible par les Utilisateurs) | Moyenne | Total | Non | Aucun contrôle dans le code |
| A3 | **Hash du mot de passe de l'appli lisible par le compte standard** : `HKLM\Software\HOTS Hosts` hérite de la lecture pour Utilisateurs. Minimum de 4 caractères, ancien format SHA-256 brut encore accepté. Attaque hors ligne possible. Risque majeur si le mot de passe est **réutilisé** pour le compte admin Windows ou la console | Moyenne | Élevé (si réutilisé) | Partiel (PBKDF2) | `__main__.py:46-75`, `options_page.py:436`, `password_utils.py:29` |
| A4 | Création d'un nouveau compte local | Impossible en standard | — | Oui, via le compte standard | — |
| A5 | Changement de **fuseau horaire** : droit accordé aux Utilisateurs par défaut. Changer l'heure système exige admin | Élevée | Nul aujourd'hui ; **à prévoir si l'agent ajoute des plages horaires** | n/a | [MS Learn – Change the time zone](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/change-the-time-zone) |

### 3.2 Exécution d'applications et navigateurs

| # | Vecteur | Facilité | Impact | Couvert ? | Preuve |
|---|---|---|---|---|---|
| B1 | **Navigateurs portables ou installés par utilisateur** (Opera/GX, Tor Browser, LibreWolf, Waterfox, Yandex, Ungoogled Chromium, Chrome/Firefox portables) lancés depuis Téléchargements, AppData, Bureau ou USB | **Élevée** | Élevé : DoH non désactivé, VPN/Tor intégrés | **Non** | DoH limité à 5 navigateurs à chemins fixes : `core_doh.py:16-79` ; aucun contrôle d'exécution par emplacement |
| B2 | **Copie ou renommage** d'un exe bloqué. L'IFEO agit par **nom**. L'ACL `Deny` ne protège qu'**un seul chemin**. Pour un fichier dans le profil de l'enfant, **l'enfant en est propriétaire**, donc il garde `WRITE_DAC` et peut retirer l'ACE ou copier le fichier | Élevée | Élevé | Non | `core_appblock.py:183-196` (`_set_ifeo_block`), `230-258` (`_lock_file`) |
| B3 | Liste VPN limitée à **10 noms d'exe** | Moyenne | Élevé | Partiel | `core_appblock.py:31-35` |
| B4 | Le sélecteur de programmes installés ne voit pas les installations **dans le profil de l'enfant**. Il lit le `HKCU` du parent (interface élevée) ou de SYSTEM (agent) | n/a | Moyen : le parent ne peut pas cibler Opera, Discord… | Non | `core_appblock.py:25-29`, `116-176` |
| B5 | **VPN intégrés aux navigateurs** : Opera (aucune stratégie documentée trouvée), **Firefox VPN gratuit (50 Go/mois, France incluse, Firefox 149+)**, fenêtre Tor et VPN de Brave, Edge Secure Network (statut incertain) | **Élevée** | Élevé : contourne hosts **et** DNS | **Non** | [Mozilla – VPN intégré](https://blog.mozilla.org/firefox/built-in-vpn/), [Brave Group Policy](https://support.brave.app/hc/en-us/articles/360039248271-Group-Policy), [Tech Community – Edge Secure Network](https://techcommunity.microsoft.com/discussions/edgeinsiderenterprise/policy-request-for-managing-edge-secure-network/4108666) |
| B6 | **Extensions VPN/proxy** (Chrome Web Store, Edge Add-ons, AMO) | **Élevée** | Élevé | Non | Aucune stratégie `ExtensionSettings` posée |
| B7 | Navigation privée / invité | Élevée | Faible pour le filtrage (même DNS) ; perte de supervision (historique) | Non | — |
| B8 | **Applis Microsoft Store** : VPN, navigateurs, jeux installables sans admin ; application de l'IFEO aux applis empaquetées **non vérifiée** | Moyenne | Élevé | Non / incertain | Voir §3.6 test T3 |
| B9 | WSL, Windows Sandbox, VM : demandent une activation admin ; Sandbox réservé à Pro/Entreprise/Éducation. **Si déjà activés**, le trafic WSL passe par le **pare-feu Hyper-V**, distinct des règles `netsh` | Faible (sauf si déjà activé) | Élevé | Non | [Hyper-V Firewall](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/hyper-v-firewall), [Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/) |
| B10 | PowerShell et scripts depuis le profil : lancement d'outils portables, proxys locaux | Moyenne | Moyen | Non | — |

### 3.3 DNS et réseau

| # | Vecteur | Facilité | Impact | Couvert ? | Preuve |
|---|---|---|---|---|---|
| C1 | **DNS IPv6 non forcé** : les serveurs DNS IPv6 annoncés par la box restent actifs. `netsh interface ip` ne traite que l'IPv4, et la lecture d'état ne reconnaît que l'IPv4 | **Aucune action requise** (box FR en IPv6) | Élevé | **Non** | `dns_utils.py:144` (regex IPv4), `167-183`, [Cloudflare : adresses IPv6 Family](https://developers.cloudflare.com/1.1.1.1/setup/) |
| C2 | **Statut « CF actif » trompeur** : il suffit d'**une** interface en IPv4 pour l'afficher (`any`) | n/a | Moyen : fausse assurance | Non | `dns_utils.py:297-305` |
| C3 | **Nouvelle carte réseau** (partage de connexion USB ou Bluetooth du téléphone, clé Wi-Fi ou Ethernet USB) : elle reçoit le DNS du téléphone, CF n'est pas appliqué. Le hosts reste actif | **Élevée** | Élevé | Non | `dns_utils.py:326-346` (cartes actives au moment T) |
| C4 | **Activer CF Family supprime la liste hosts « adulte »**, donc le filtrage adulte dépend à 100 % du DNS (cf. C1, C3, C5, B1, B5, B6) | — | Élevé | Choix de conception | `parental_page.py:259-270`, `remote/actions.py:268-282` |
| C5 | DoH/DoT ou DNS codé en dur dans des applis ou navigateurs non couverts ; **aucun blocage pare-feu de 53/853** vers d'autres résolveurs, ni des résolveurs DoH connus | Moyenne | Élevé | Partiel (5 navigateurs) | `core_doh.py` |
| C6 | **Proxy Windows propre à l'utilisateur** (Paramètres > Proxy) ou proxy web en ligne : la résolution DNS se fait chez le proxy | Élevée | Élevé | Non | — |
| C7 | **VPN natif Windows** (PPTP, L2TP, SSTP, IKEv2) **créable et connectable par un compte standard** | Moyenne (il faut un service VPN) | Élevé | Non | [TrustedSec](https://trustedsec.com/blog/abusing-windows-built-in-vpn-providers) |
| C8 | Limites du hosts : pas de jokers ni de sous-domaines, **liste adulte de 1 324 domaines**, accès par IP, caches et traducteurs (`*.translate.goog`) | Élevée | Moyen | Partiel | `blocklists/adult.txt` (`wc -l`) |
| C9 | **SafeSearch et YouTube restreint non forcés**. La doc Cloudflare Family ne mentionne pas SafeSearch | Élevée (recherche d'images) | Moyen | Non | [Cloudflare setup](https://developers.cloudflare.com/1.1.1.1/setup/) |
| C10 | Coupure Internet contournable via un **proxy sur le réseau local** (téléphone sur le même Wi-Fi ou point d'accès, plages privées autorisées) ; préfixes **NAT64** `64:ff9b::/96` hors de `2000::/3` | Faible à moyenne | Élevé pendant la coupure | Partiel | `core_netblock.py:19-23` |
| C11 | **Exclusion IP de la console** pendant la coupure : si la console est derrière un CDN mutualisé, la même IP sert de nombreux autres sites | Faible | Moyen | À concevoir | `core_netblock.py` (`_excluded_ips`), `remote/config.py:109-127` |

### 3.4 Accès physique, démarrage, récupération

| # | Vecteur | Facilité | Impact | Couvert ? | Preuve |
|---|---|---|---|---|---|
| D1 | **Démarrage sur USB** (système live) : modification hors ligne du hosts ou des comptes si le disque **n'est pas chiffré** | Moyenne | Total | Non (hors logiciel) ; vérifiable | — |
| D2 | **WinRE depuis l'écran de connexion** (Maj + Redémarrer) : « Réinitialiser ce PC » (selon les sources, possible sans mot de passe admin en mode « Supprimer tout », **à tester**) ; mode sans échec (l'agent ne tourne pas) | Moyenne | Total (réinitialisation) / partiel (mode sans échec) | Non ; **détectable** par la console (PC hors ligne, `machine_id` ou ré-enrôlement) | [Guide tiers](https://www.makeuseof.com/windows-11-factory-reset-without-admin-password/) (non officiel) |
| D3 | Restauration système depuis WinRE (hors `rstrui`) | Faible (identifiants admin probablement requis, **à tester**) | Élevé | Partiel | `remote/actions.py` (`rstrui_lock.set`) |

### 3.5 Logiciel et agent

| # | Vecteur | Facilité | Impact | Couvert ? | Preuve |
|---|---|---|---|---|---|
| E1 | **États en cache qui mentent** : l'état remonté à la console lit des JSON pour `hosts_lock`, `netblock` et `vpn`, pas l'état réel (ACL, règles pare-feu, IFEO) | n/a | Moyen : le parent se croit protégé | Non | `remote/actions.py:780-795` |
| E2 | **La dérive « oublie » l'état voulu** : à la première dérive, `enabled` passe à `False` (applis), `state[browser]=False` (DoH) ou `active=False` (verrou). Une alerte unique dans l'interface, puis plus rien | n/a | Moyen | Non | `core_appblock.py:614-619`, `core_doh.py:230-235`, `core_antispy.py:1277-1279` |
| E3 | **Course GUI ↔ agent** : `_HOSTS_FILE_LOCK` est un `threading.Lock` (un seul processus). L'interface enregistre la **table entière** gardée en mémoire et peut écraser une modification de l'agent ; bascule concurrente du verrou hosts | n/a | Moyen (perte silencieuse) | Non | `core.py:20`, `395-447` ; `app.py:132-150` ; `remote/actions.py:124-136` |
| E4 | **Mutex de l'agent sans vérification du propriétaire** : un compte standard peut créer un mutex `Global\` (seuls les file mappings exigent `SeCreateGlobalPrivilege`). Au prochain (re)démarrage, l'agent croit à une autre instance et sort avec le code 0, donc **pas de pilotage ni de remontée** jusqu'au redémarrage | Faible à moyenne | Moyen (les protections persistent) | Non | `remote/service.py:68-83` vs `hosts_editor_launcher.pyw:263-306` ; [Kernel object namespaces](https://learn.microsoft.com/en-us/windows/win32/termserv/kernel-object-namespaces) |
| E5 | URL de console en `http://` acceptée : jeton en clair si le parent tape `http` | Faible | Élevé | Non | `remote/config.py:65` |
| E6 | Dérive après mises à jour : nouvelles fonctions de navigateur (VPN Firefox 2026), nouveaux navigateurs, IPv6, redirection du hosts via `Tcpip\Parameters\DataBasePath` (admin), règles NRPT. Les contrôles de dérive DoH, applis et verrou ne tournent que **quand l'interface est ouverte** | n/a | Moyen | Partiel | `app.py:711-870` ; `remote/service.py` (`periodic_checks` : coupure Internet seulement) |
| E7 | **La console devient la clé maîtresse** : un compte parent compromis désactive tout sur tous les PC | Hors enfant (sauf mot de passe partagé ou deviné) | Total | À concevoir côté serveur | — |
| E8 | La connectivité et le diagnostic de l'appli utilisent `1.1.1.1:53` et `8.8.8.8:53`. **Ils casseront** si l'on verrouille le DNS sortant (Phase 1) | n/a | Fonctionnel | — | `core.py:545-557`, `559` |
| E9 | Désinstallation ou arrêt du logiciel ou de l'agent par l'enfant | Impossible en standard | — | Oui | `setup.iss`, tâche SYSTEM |

### 3.6 Points incertains et protocoles de test

À valider sur **machines virtuelles Windows 11 Famille et Pro** (24H2/25H2 à jour), avec un compte enfant standard :

| Test | Question | Méthode |
|---|---|---|
| T1 | Le DNS IPv6 de la box contourne-t-il CF Family ? | `Get-DnsClientServerAddress -AddressFamily IPv6` ; `Resolve-DnsName <domaine bloqué par CF>` : on attend `0.0.0.0`. Refaire avec CF activé depuis HOTS |
| T2 | La stratégie DNS `NameServer` (`HKLM\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient`) s'applique-t-elle sur Famille et aux **nouvelles** cartes réseau (partage USB) ? Un retour Intune signale un cas sans effet | Poser la valeur, brancher un partage de connexion USB, `Resolve-DnsName` + `pktmon` pour voir le serveur réellement interrogé |
| T3 | L'IFEO `Debugger` bloque-t-il une appli **empaquetée** (Store) ? | Bloquer le nom d'exe d'une appli Store et la lancer depuis Démarrer |
| T4 | Les règles `netsh advfirewall` (coupure, futur verrou DNS) s'appliquent-elles au trafic **WSL** (NAT, miroir) et **Sandbox** ? | Coupure active, puis `curl` depuis WSL ; `Get-NetFirewallHyperVVMSetting` |
| T5 | AppLocker est-il **réellement appliqué sur Famille** ? Microsoft dit oui depuis KB5024351 ; un forum signale des échecs. Et en **mode sans échec** ? | Déploiement via le pont WMI MDM (CSP AppLocker) en SYSTEM, exe dans Téléchargements ; démarrage en mode sans échec avec réseau + `sc query appidsvc` |
| T6 | « Réinitialiser ce PC » depuis WinRE exige-t-il un compte admin ? | VM avec seul compte standard connu ; Maj + Redémarrer depuis l'écran de connexion |
| T7 | Pare-feu actif en mode sans échec avec réseau ? | `Get-NetFirewallProfile`, essai d'accès Internet pendant la coupure |
| T8 | Stratégies prises en compte par les variantes (Chrome/Firefox portables, LibreWolf, Waterfox, Ungoogled, Yandex, Opera) ? | Pages `chrome://policy` et `about:policies` |
| T9 | `IPProtectionAvailable=false` désactive-t-il le VPN Firefox ? Edge Secure Network disparaît-il dès qu'une stratégie est posée ? | `about:policies` + vérifier que le bouton VPN est absent ; `edge://settings/privacy` |
| T10 | Squat du mutex de l'agent | Depuis une session standard, créer `Global\HOTS_RemoteAgent_SingleInstance` puis relancer la tâche en admin ; lire `remote_agent.log` |
| T11 | Hosts `0.0.0.0` et requêtes AAAA sur un réseau IPv6 natif | Domaine listé seulement en `0.0.0.0` : vérifier `Resolve-DnsName -Type AAAA` et l'accès réel |

---

## 4. Plan d'implémentation par phases

Principes transverses, valables pour toutes les mesures :

- **Séparer « voulu » et « observé »** : la console enregistre l'intention, l'agent remonte l'observé, l'écart s'affiche comme « non conforme ».
- **Tout réversible** : chaque mesure garde ce qu'elle a modifié (`ProgramData`, déjà sécurisé) pour une restauration exacte, avec une action console `*.set {enabled:false}`.
- **Pas de nouvelle dépendance**. Les actions de l'agent restent en **liste blanche typée**.

### Phase 1 — gains forts et simples (1 clic ou par défaut)

#### P1.1 — État de conformité et compte enfant standard *(recommandation n°1, rendue vérifiable)*

- **Changement** : nouveau module `hosts_editor/compliance.py`, sans Qt, en lecture seule, utilisé par l'interface et l'agent. Nouvelle section `compliance` dans `_SECTIONS` de `remote/actions.py`. Contrôles :
  - comptes locaux et membres du groupe Administrateurs, ainsi que les comptes marqués « enfant » par le parent. Règle : **un compte enfant ne doit jamais être admin** ;
  - UAC actif (`EnableLUA=1`, `PromptOnSecureDesktop=1`) ;
  - Administrateur intégré et Invité désactivés ;
  - ouverture de session automatique avec `DefaultPassword` en clair ;
  - **BitLocker / chiffrement de l'appareil**, **Secure Boot**, état de WinRE (`reagentc /info`) ;
  - fonctionnalités WSL, VirtualMachinePlatform et Sandbox activées ;
  - `DataBasePath` du hosts inchangé ;
  - **état réel** des protections (ACL du hosts, règles pare-feu, profils activés, IFEO, stratégies navigateur) ;
  - DNS de **toutes** les cartes actives, en IPv4 et IPv6 ;
  - **détection** d'éléments non gérés dans les profils (`C:\Users\*\{Downloads,Desktop,AppData}`) : exe de navigateurs et VPN connus, identifiés par nom et éditeur de signature ;
  - extensions de navigateur demandant la permission `proxy` (lecture des `manifest.json` des profils Chrome, Edge et Brave) ;
  - profils VPN natifs (`rasphone.pbk` des profils) et proxy utilisateur activé (`HKU\<SID>\...\Internet Settings`).

  L'ensemble produit un score et « les 3 actions à faire ».
- **Correction du compte enfant** : action `accounts.make_standard {sid}`. Garde-fous : il reste au moins un admin activé **avec mot de passe** ; ce n'est pas le compte du parent ; confirmation dans la console. L'interface propose la même chose au premier lancement (« Quel compte utilise votre enfant ? »).
- **Console** : actions `compliance.check` (non mutante), `accounts.set_child {sid, is_child}`, `accounts.make_standard {sid}`. État `compliance: {score, checks:[{id, status, detail, fix_action}]}`. Un tableau de bord rouge/orange/vert avec des boutons « Corriger » reliés aux actions existantes.
- **Éditions** : toutes. BitLocker apparaît comme « chiffrement de l'appareil » sur Famille, selon le matériel.
- **Effets de bord** : aucun (lecture seule), sauf `make_standard`, réversible par `accounts.make_admin` réservé à la console.
- **Effort** : M.

#### P1.2 — Pack « navigateurs verrouillés »

- **Changement** : généraliser `core_doh.py` en `core_browser_policy.py`, qui garde `DohBlockManager` pour la compatibilité. Stratégies appliquées **même si le navigateur n'est pas détecté** : la détection par chemins fixes rate les installations par utilisateur et les versions portables, qui lisent les stratégies HKLM. Supprimer le filtre `is_browser_installed` de la dérive (`core_doh.py:227`).
  - **Chromium** (`Google\Chrome`, `Microsoft\Edge`, `BraveSoftware\Brave`, `Vivaldi`, plus `Chromium` à vérifier, T8) :
    - `DnsOverHttpsMode=off` (existant) ;
    - `ExtensionSettings` = `{"*":{"blocked_permissions":["proxy"]}}`, à fusionner avec un JSON existant. Selon Google, une extension qui **exige** une permission bloquée ne peut pas être installée et cesse de se charger si elle est déjà installée ;
    - `ProxySettings` = `{"ProxyMode":"direct"}` ;
    - `ForceGoogleSafeSearch=1` ;
    - `ForceYouTubeRestrict=1` (modéré) ou `2` (strict) ;
    - `BrowserGuestModeEnabled=0` ;
    - Edge : `ForceBingSafeSearch=2` ;
    - Chrome, en option : `SafeSitesFilterBehavior=1`, filtre adulte indépendant du DNS mais qui **envoie les URL à l'API Google SafeSearch** (impact sur la vie privée) ;
    - Brave : `TorDisabled=1`, `BraveVPNDisabled=1` (DWORD).
  - **Firefox** (`Software\Policies\Mozilla\Firefox`) :
    - `DNSOverHTTPS` (existant) ;
    - `IPProtectionAvailable=false` (VPN intégré, à confirmer, T9) ;
    - `Proxy\Mode="none"` + `Proxy\Locked=1`.
  - **Optionnel** (« historique visible ») : `IncognitoModeAvailability=1`, `InPrivateModeAvailability=1`, Firefox `PrivateBrowsingModeAvailability`.
- **Console** : action `browser_policies.set {level:"off"|"standard"|"strict", private_browsing_off:bool, safesites:bool}`. État : valeurs **lues** par navigateur et par stratégie (`observed`), avec un écart éventuel.
- **Éditions** : toutes. Les stratégies sont lues dans le registre ; pas besoin de `gpedit`.
- **Effets de bord** :
  - bannière « Géré par votre organisation » ;
  - extensions VPN/proxy désactivées ;
  - certaines vidéos YouTube masquées ;
  - **s'applique aussi aux comptes des parents**, car c'est HKLM (voir P2.4 pour une version par enfant) ;
  - proxy « direct » gênant uniquement si la famille utilise un proxy, ce qui est rare.

  Réversible : on enregistre les valeurs antérieures et on les restaure.
- **Effort** : S à M.
- **Sources** :
  - Chromium : [IncognitoModeAvailability](https://github.com/chromium/chromium/blob/main/components/policy/resources/templates/policy_definitions/Miscellaneous/IncognitoModeAvailability.yaml), [ForceYouTubeRestrict](https://github.com/chromium/chromium/blob/main/components/policy/resources/templates/policy_definitions/Miscellaneous/ForceYouTubeRestrict.yaml), [SafeSitesFilterBehavior](https://github.com/chromium/chromium/blob/main/components/policy/resources/templates/policy_definitions/Miscellaneous/SafeSitesFilterBehavior.yaml), [BrowserGuestModeEnabled](https://github.com/chromium/chromium/blob/main/components/policy/resources/templates/policy_definitions/Miscellaneous/BrowserGuestModeEnabled.yaml), [ExtensionSettings](https://github.com/chromium/chromium/blob/main/components/policy/resources/templates/policy_definitions/Extensions/ExtensionSettings.yaml), [Google – blocked_permissions](https://support.google.com/chrome/a/answer/9867568) ;
  - Edge : [InPrivateModeAvailability](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-policies/inprivatemodeavailability), [ForceBingSafeSearch](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-policies/forcebingsafesearch), [ForceYouTubeRestrict](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-policies/forceyoutuberestrict), [ExtensionSettings](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-policies/extensionsettings) ;
  - Firefox : [Proxy](https://firefox-admin-docs.mozilla.org/reference/policies/proxy/), [ExtensionSettings](https://firefox-admin-docs.mozilla.org/reference/policies/extensionsettings/), [PrivateBrowsingModeAvailability](https://firefox-admin-docs.mozilla.org/reference/policies/privatebrowsingmodeavailability/) ;
  - Brave : [Group Policy](https://support.brave.app/hc/en-us/articles/360039248271-Group-Policy).
- **Non gérables** (Opera/GX : aucune documentation de prise en charge des stratégies trouvée ; Tor Browser) : la Phase 1 les **détecte** (P1.1) ; la Phase 2 les **bloque** (P2.1).

#### P1.3 — « DNS verrouillé » (extension de l'interrupteur CF Family)

- **Changement** dans `dns_utils.py` et un nouveau `core_dnslock.py` :
  1. poser aussi **CF Family en IPv6** (`2606:4700:4700::1113`, `::1003`) avec `netsh interface ipv6 set dnsservers` ou `Set-DnsClientServerAddress` ;
  2. lire et afficher l'IPv4 **et** l'IPv6 ; `active` seulement si **toutes** les cartes actives sont couvertes, sinon « partiel » ;
  3. poser la stratégie `NameServer` (`HKLM\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient`), qui doit primer sur DHCP et sur toutes les cartes, **sous réserve du test T2** ;
  4. l'agent réapplique toutes les 30 minutes et au démarrage sur toute nouvelle carte (comme `periodic_checks`) ;
  5. **pare-feu** : bloquer en sortie TCP/UDP **53 et 853** vers toute adresse **sauf** CF Family v4/v6. Comme Windows fait primer les règles de blocage sur les règles d'autorisation, on bloque le **complément**, en réutilisant `remote/netutil.carve_ranges` ;
  6. bloquer TCP/UDP 443 vers les **IP de résolveurs DoH publics connus** (Google `8.8.8.8/8.8.4.4`, Cloudflare `1.1.1.1/1.0.0.1/1.1.1.2/1.0.0.2`, Quad9, OpenDNS, AdGuard… avec leurs équivalents IPv6), puis ajouter une catégorie hosts `doh_bypass.txt` (`dns.google`, `cloudflare-dns.com`, `mozilla.cloudflare-dns.com`, `dns.quad9.net`, `doh.opendns.com`, `dns.nextdns.io`, `dns.adguard-dns.com`…, **sans** `family.cloudflare-dns.com`) ;
  7. **conserver la liste hosts « adulte » quand CF est actif** : supprimer l'exclusion mutuelle (`parental_page.py:259-270`, `remote/actions.py:274-277`). La défense en profondeur coûte 1 324 lignes ;
  8. adapter `has_internet_connection` et `dns_lookup_external` (`core.py:545-559`) pour viser `1.1.1.3`, sinon ils casseront (E8).
- **Console** : action `dns_lock.set {enabled}`. État `dns: {interfaces:[{name, v4, v6, dhcp, ok}], policy_nameserver, fw_rules_present, doh_list_active}`.
- **Éditions** : toutes pour le pare-feu et `netsh`. Prise en compte de la stratégie `NameServer` sur Famille : **à tester**.
- **Effets de bord** :
  - Wi-Fi à **portail captif** (hôtel, train) parfois bloqué : désactivation temporaire depuis la console ;
  - **ne pas activer sur un PC professionnel** (VPN d'entreprise, DNS interne) ;
  - noms locaux de la box résolus uniquement s'ils sont publics ;
  - les applis à DNS codé en dur cessent de résoudre, ce qui est voulu.

  Réversible : suppression des règles, de la stratégie et de la sauvegarde DNS (mécanisme existant `dns_backup.json`).
- **Effort** : M.
- **Sources** : [Cloudflare 1.1.1.1 setup](https://developers.cloudflare.com/1.1.1.1/setup/), [MS – DoH client et liste de serveurs connus](https://learn.microsoft.com/en-us/windows-server/networking/dns/doh-client-support), [GPO DNS Servers](https://www.grouppolicy.biz/?p=949), [blog CSS Microsoft](https://learn.microsoft.com/en-us/archive/blogs/csstwplatform/gpodns-serversclient-dns-ip).

#### P1.4 — Correctifs ciblés dans le code (sécurité et fiabilité)

| Correctif | Fichiers | Effort |
|---|---|---|
| ACL de `HKLM\Software\HOTS Hosts` réservée à SYSTEM + Admins (lecture Utilisateurs retirée), via `RegSetKeySecurity` ou PowerShell `Set-Acl` à la création. Minimum **8 caractères**, ancien format SHA-256 refusé (réinitialisation imposée). Avertissement « n'utilisez pas le même mot de passe que Windows ou la console » | `__main__.py:63-75`, `options_page.py:436`, `password_utils.py:28-29` | S |
| Mutex de l'agent : reprendre `_mutex_security_attributes` + `_object_owner_is_trusted` du lanceur, **ou** un fichier verrou dans `ProgramData` (non créable par l'enfant) | `remote/service.py:68-83` | S |
| Verrou d'écriture **inter-processus** du hosts : mutex nommé `Global\HOTS_Hosts_Write` (SDDL SY/BA + vérification du propriétaire) utilisé par `core.py`, l'interface et l'agent. L'interface vérifie le hash du hosts avant d'écrire et propose « recharger » en cas d'écart | `core.py:20`, `395-447`, `app.py:132-150`, `remote/actions.py:124-136` | M |
| États **observés** dans `_state_protections` : `HostsLockManager._real_locked()`, `rules_present() and _firewall_profiles_on()`, IFEO réel par appli. La dérive ne bascule plus l'état voulu à `False` : elle le marque `drift=True`. L'agent **réapplique** (option « auto-réparation ») et l'état reste rouge tant qu'il n'est pas corrigé | `remote/actions.py:780-795`, `core_appblock.py:590-621`, `core_doh.py:214-238`, `core_antispy.py:1272-1283` | M |
| Coupure Internet : ajouter `64:ff9b::/96` et `64:ff9b:1::/48` (NAT64) à la règle v6 | `core_netblock.py:19-23` | S |
| `normalize_server_url` : refuser `http://` (sauf `localhost` en mode développeur) | `remote/config.py:65` | S |
| Sélecteur d'applis : énumérer aussi `HKU\<SID>\...\Uninstall` de chaque profil chargé ou chargeable | `core_appblock.py:25-29` | S |

#### P1.5 — Alertes de présence (côté console)

- **Changement** : surtout côté serveur. Alertes « PC non vu depuis plus de X heures », « `machine_id` changé ou ré-enrôlement » (réinitialisation probable), « redémarrages fréquents ». L'agent ajoute `last_boot` et `boot_id` à `system_info`.
- **Console** : réglage du seuil ; notification (e-mail ou push).
- **Éditions** : toutes.
- **Effets de bord** : faux positifs pendant les vacances, d'où un mode « absence ».
- **Effort** : S à M.

### Phase 2 — contrôle d'exécution et contournements réseau sans installation

#### P2.1 — « Mode anti-portable » : AppLocker **par utilisateur** pour le compte enfant

- **Changement** : nouveau module `core_applocker.py`, appliqué par l'agent SYSTEM. Il passe par `Set-AppLockerPolicy` quand c'est disponible, sinon par le **pont WMI MDM** du CSP AppLocker. Le service `AppIDSvc` est passé en démarrage automatique. Règles ciblant le **SID du compte enfant ou d'un groupe « Enfants »**, sans effet sur les parents :
  - EXE autorisés dans `%WINDIR%` (avec exceptions pour les sous-dossiers inscriptibles connus, par exemple `Windows\Temp`, `Windows\Tasks`, `System32\spool\drivers\color`) et dans `%PROGRAMFILES%` ;
  - applis empaquetées signées (règle « packaged apps ») ;
  - **exceptions validées par le parent** (règles par éditeur ou par hash) ;
  - option « scripts », qui fait passer PowerShell en Constrained Language Mode pour l'enfant.

  Déploiement **en mode audit pendant 7 jours** : l'agent remonte les événements AppLocker « aurait été bloqué » et la console liste les applis concernées. Le parent approuve, puis passe en mode bloquant.
- **Variante allégée P2.1a** (avant la liste blanche) : règles **de refus par éditeur** pour le compte enfant (Opera, The Tor Project, éditeurs VPN…). Elles résistent au renommage, contrairement à l'IFEO, mais ne couvrent pas les exe non signés.
- **Console** : actions `applocker.set {mode:"off"|"audit"|"enforce"}`, `applocker.allow {publisher|hash, label}`, `applocker.deny_publisher {...}`. État : mode, nombre de règles, derniers blocages et audits.
- **Éditions** : selon Microsoft, appliqué sur **toutes les éditions** depuis KB5024351 (Windows 10 2004+ et tout Windows 11). Retours contradictoires sur Famille, **test T5 obligatoire**. Probablement inactif en mode sans échec (dépend d'`AppIDSvc`, T5).
- **Effets de bord** : casse les applis installées dans le profil (Roblox, Discord, Spotify, Teams/Zoom version utilisateur…) et les bibliothèques de jeux hors `Program Files` (par exemple `D:\SteamLibrary`), d'où l'audit préalable et les exceptions. Contournements avancés par binaires système (LOLBins) traités en P3.6. Réversible : politique vide + `AppIDSvc` arrêté, avec une action « panique » dans la console **et** dans l'interface locale.
- **Effort** : L.
- **Sources** : [AppLocker requirements](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/requirements-to-use-applocker), [App Control vs AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/feature-availability), [retour communauté Famille](https://forums.windowscentral.com/threads/why-is-applocker-not-working-on-windows-10-and-11-home-edition.547528).
- **Écartés** :
  - **SRP** (stratégies de restriction logicielle) : dépréciées depuis 1803, et signalées non fonctionnelles d'origine sur certaines images 22H2 ([Born](https://borncity.com/win/2022/11/08/windows-11-22h2-no-longer-supports-software-restriction-policies-srp)) ;
  - **Smart App Control** : réglage pour tout l'appareil fondé sur la réputation, donc les navigateurs grand public signés passent. Ce n'est pas un outil parental.

#### P2.2 — VPN et proxy natifs de Windows

- **Changement** :
  - `SettingsPageVisibility = hide:network-vpn;network-proxy` (`HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer`) ;
  - `ProxySettingsPerUser=0` (proxy par machine, dans `HKLM\Software\Policies\Microsoft\Windows\CurrentVersion\Internet Settings`, **à tester**) ;
  - option pare-feu bloquant IKE (UDP 500/4500), L2TP (UDP 1701), PPTP (TCP 1723 + GRE). SSTP passe par le port 443 et n'est pas bloquable ainsi ;
  - option « désactiver RasMan » ;
  - surveillance des événements RasClient 20221 à 20223, remontés à la console.
- **Console** : `native_vpn.set {hide_settings, block_protocols, disable_rasman}`, état avec les profils VPN détectés.
- **Éditions** : le CSP `PageVisibilityList` liste Pro, Entreprise et Éducation ; la valeur de registre sur Famille est **à tester**.
- **Effets de bord** : masquer la page n'empêche pas PowerShell ni WMI (selon TrustedSec) ; bloquer les protocoles ou RasMan **coupe aussi le VPN des parents**. Réversible.
- **Effort** : M.
- **Sources** : [Policy CSP Settings](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-settings), [TrustedSec](https://trustedsec.com/blog/abusing-windows-built-in-vpn-providers), [ProxySettingsPerUser](https://gp.kapilarya.com/make-proxy-settings-per-machine-rather-than-per-user).

#### P2.3 — Liste blanche d'extensions

- **Changement** :
  - Firefox `ExtensionSettings` : `{"*":{"installation_mode":"blocked"}, "<id>":{"installation_mode":"allowed"}}` (`REG_MULTI_SZ`). Firefox ne sait pas bloquer **par permission** ;
  - mode strict équivalent pour Chromium.
- **Console** : `extensions.set {mode, allow:[ids]}` ; l'enfant peut « demander » une extension, ce qui crée une notification pour le parent.
- **Éditions** : toutes.
- **Effets de bord** : désactive les extensions existantes non listées (gestionnaire de mots de passe, bloqueur de publicités) ; fournir une liste par défaut éditable.
- **Effort** : M.

#### P2.4 — Stratégies navigateur **par enfant**

- **Changement** : écrire les stratégies « supervision » (navigation privée, mode invité, YouTube strict) dans `HKU\<SID enfant>\Software\Policies\...`. Cette branche n'est modifiable que par un admin, mais est lue par Chromium et Firefox. L'agent les applique au chargement de la ruche (déclencheur de tâche à l'ouverture de session) ou via `reg load` hors session. Les parents ne sont pas affectés.
- **Éditions** : toutes.
- **Effort** : M.

#### P2.5 — SafeSearch et YouTube par DNS ou hosts (navigateurs sans stratégie)

- **Changement** : catégorie générée `safesearch.txt` :
  - `www.google.<tld>` vers l'IP de `forcesafesearch.google.com`, avec résolution périodique par l'agent ;
  - les hôtes YouTube listés par Google vers `restrict` ou `restrictmoderate.youtube.com` ;
  - Bing vers `strict.bing.com` (à vérifier).
- **Console** : `safesearch.set {google, youtube:"off|moderate|strict", bing}`.
- **Effets de bord** : si l'IP change et n'est pas rafraîchie, la recherche Google casse, d'où un contrôle quotidien par l'agent et un retrait automatique en cas d'échec.
- **Effort** : M.
- **Sources** : [Google SafeSearch réseau](https://support.google.com/websearch/answer/186669), [YouTube restreint par DNS](https://support.google.com/a/answer/6214622).

#### P2.6 — Détection d'altérations

- **Changement** : signature de `sethc.exe` et `utilman.exe` ; valeurs `Debugger` IFEO non créées par HOTS ; nouveaux comptes locaux ou ajouts au groupe Administrateurs (événements 4720 et 4732) ; `DataBasePath` ; règles NRPT ; changements de la stratégie DNS. Tout est remonté en alertes.
- **Effort** : M.

#### P2.7 — Plages horaires (si elles sont ajoutées à l'agent)

- **Changement** : les évaluer en **UTC** avec le fuseau défini par le parent dans la console, jamais avec le fuseau du système, que l'enfant peut modifier. Le serveur fait foi en cas d'écart d'horloge important.
- **Effort** : M.

### Phase 3 — durcissement avancé (PC dédié à l'enfant, ou parents avertis)

| Mesure | Ce qui change | Console | Éditions | Effets de bord / réversibilité | Effort |
|---|---|---|---|---|---|
| **P3.1 App Control for Business (WDAC) strict** | Politique pour tout l'appareil : règles de chemin (avec contrôle d'inscriptibilité à l'exécution) sur Windows et Program Files, plus éditeurs approuvés. Déploiement `.cip` + `CiTool` (Windows 11) | `appcontrol.set {mode}` | « Policies are effective on all editions » (pas de cmdlets sur Famille) | **Touche aussi les parents** (installations depuis Téléchargements bloquées) ; appliqué même en mode sans échec ; retrait par suppression du `.cip` + redémarrage | L |
| **P3.2 Résolveur DNS local dans l'agent** | Proxy DNS sur `127.0.0.1`, DoH vers `family.cloudflare-dns.com`, **jokers et sous-domaines** (`*.translate.goog`…), journal pour le parent ; le pare-feu force tout le DNS vers lui | `dnsproxy.set`, journal | Toutes | Si l'agent plante, plus de DNS : choisir entre échec fermé (avec chien de garde) et échec ouvert. Désactivation = retour à P1.3 | L |
| **P3.3 Filtrage WFP par utilisateur** | Coupure et plages horaires **pour le seul compte enfant** (conditions utilisateur WFP) : règle le cas du proxy sur le réseau local (C10) sans couper les parents ni l'agent | `netblock.set {scope:"child"}` | Toutes | Complexe ; à prototyper (`New-NetFirewallRule -LocalUser` à évaluer d'abord) | L |
| **P3.4 Assistant « protection physique »** | Contrôle et aide à l'activation de BitLocker ou du chiffrement de l'appareil (clé de récupération **hors de portée de l'enfant**), Secure Boot ; option `reagentc /disable` | `physical.check`, `winre.set` | Chiffrement de l'appareil sur Famille selon le matériel | Désactiver WinRE complique **aussi** les dépannages ; réversible avec `reagentc /enable` | M |
| **P3.5 WSL, Sandbox, Hyper-V** | Désactiver les fonctionnalités inutilisées (DISM) ou poser des règles Hyper-V pour le `VMCreatorId` de WSL | `features.set` | Sandbox : Pro et plus | Gêne un parent développeur ; réversible | M |
| **P3.6 Binaires système détournables** | Refus AppLocker, pour l'enfant, de `mshta`, `wscript`, `cscript`, `msbuild`, `installutil`, `regsvr32`… ; règles de scripts | via P2.1 | Comme P2.1 | Peut casser des scripts scolaires ; journal d'audit d'abord | M |

### Récapitulatif des nouvelles actions et états de l'agent

| Action | Mutante | Phase |
|---|---|---|
| `compliance.check`, `accounts.set_child`, `accounts.make_standard` | non / oui / oui | 1 |
| `browser_policies.set` | oui | 1 |
| `dns_lock.set` | oui | 1 |
| `native_vpn.set`, `extensions.set`, `safesearch.set` | oui | 2 |
| `applocker.set`, `applocker.allow`, `applocker.deny_publisher` | oui | 2 |
| `appcontrol.set`, `dnsproxy.set`, `features.set`, `winre.set` | oui | 3 |
| Section d'état `compliance` + champs `observed` et `drift` dans `protections` | — | 1 |

---

## 5. Recommandations non logicielles pour les parents

1. **Compte Windows standard pour l'enfant**, et un compte admin séparé pour le parent, avec un mot de passe solide **différent** de celui de l'appli et de la console. Ne jamais le taper devant l'enfant ; attention au PIN Windows Hello observé par-dessus l'épaule.
2. **Double authentification sur la console web** (le compte console contrôle tous les PC).
3. **Mot de passe UEFI/BIOS**, démarrage USB et menu de démarrage désactivés, **Secure Boot activé**.
4. **BitLocker / chiffrement de l'appareil** activé, clé de récupération rangée hors de portée (compte Microsoft du parent ou papier sous clé).
5. **Filtrage aussi sur la box** (DNS familial distribué en DHCP) et contrôle parental du **téléphone** (Family Link, Temps d'écran) : le partage de connexion et le téléphone lui-même ne sont pas couverts par ce PC.
6. Option : un compte Microsoft enfant dans **Microsoft Family Safety**. Son filtrage web ne fonctionne que dans Edge et bloque les autres navigateurs ([support Microsoft](https://support.microsoft.com/help/4578151)). Il complète HOTS, ne le remplace pas.
7. PC dans une pièce commune, règles expliquées plutôt que cachées, et un œil sur les alertes de la console chaque semaine.

---

## 6. Limites honnêtes

- **Enfant administrateur ou accès physique prolongé** : aucun logiciel local ne résiste. Réinitialisation du PC, autre système sur USB, retrait du disque, tout reste possible. On peut **détecter** (PC hors ligne, ré-enrôlement) et **compliquer** (BitLocker, UEFI), pas empêcher.
- **Autres appareils et réseaux** : téléphone, console de jeu, PC d'un ami ou de l'école. HOTS ne protège que ce PC.
- **VPN et proxys chiffrés sur le port 443** : ils ressemblent à du HTTPS ordinaire. Sans contrôle de ce qui s'exécute (P2.1/P3.1), il est impossible de tous les bloquer côté réseau. Tor dispose de ponts (obfs4, Snowflake) qui échappent aux listes d'IP.
- **Filtrage DNS et hosts** : il est par catégories et imparfait (nouveaux domaines, faux négatifs, sous-domaines non couverts par le hosts, contenus hébergés sur de grandes plateformes). Il ne voit pas le contenu des pages HTTPS. Ce projet ne doit pas faire d'interception TLS, pour des raisons de vie privée et de sécurité.
- **Failles Windows d'élévation de privilèges** : un compte standard reste vulnérable à une faille non corrigée. Il faut garder Windows et les navigateurs à jour, ce que la conformité peut aussi suivre.
- **Dérive des éditeurs** : les navigateurs ajoutent des fonctions (VPN intégrés en 2026) et des stratégies changent de nom. La liste de P1.2 doit être **revue à chaque version majeure**, et la conformité doit signaler les éléments inconnus.
- **Le logiciel lui-même** : bugs, mises à jour ratées, console compromise. Il faut des états observés (pas déclarés), des alertes, et des actions de retour arrière simples.
- **La relation compte autant que la technique** : face à un adolescent motivé, ces mesures **ralentissent et rendent visibles** les contournements. Elles ne remplacent pas le dialogue.
