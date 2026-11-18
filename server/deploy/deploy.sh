#!/usr/bin/env bash
# HOTS Hosts — console web : installation, mise à jour et désinstallation sur Ubuntu / Debian.
#
#   sudo ./deploy.sh                      assistant graphique (fenêtres dans le terminal)
#   sudo ./deploy.sh --domain console.exemple.fr --email moi@exemple.fr --yes
#   sudo ./deploy.sh --sslip --yes        sans nom de domaine (adresse gratuite <ip>.sslip.io)
#   sudo ./deploy.sh --update --yes       mise à jour en gardant les données
#   sudo ./deploy.sh --uninstall          désinstallation (les données sont conservées par défaut)
#
# Ce qui est installé : Python (environnement isolé), le service « hots-console » (systemd),
# Caddy (serveur web avec certificat HTTPS automatique Let's Encrypt) et une sauvegarde quotidienne.

set -euo pipefail

APP_NAME="Console HOTS Hosts"
INSTALL_DIR="/opt/hots-console"
DATA_DIR="/var/lib/hots-console"
BACKUP_DIR="/var/backups/hots-console"
ENV_FILE="/etc/hots-console.env"
SERVICE="hots-console"
SERVICE_USER="hots"
APP_PORT="8080"
CADDY_SITES="/etc/caddy/sites"
CADDY_SITE_FILE="${CADDY_SITES}/hots-console.caddy"
LOG_FILE="/var/log/hots-console-install.log"
CLI="/usr/local/bin/hots-server"

DOMAIN=""
EMAIL=""
USE_SSLIP=0
ASSUME_YES=0
ACTION=""
TOTAL_STEPS=7

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -d "${SCRIPT_DIR}/hots_server" ]]; then
  SRC_DIR="${SCRIPT_DIR}"               # archive .zip de la release
elif [[ -d "${SCRIPT_DIR}/../hots_server" ]]; then
  SRC_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"   # dépôt git : server/deploy/deploy.sh
elif [[ -d "/opt/hots-console/app/hots_server" ]]; then
  SRC_DIR="/opt/hots-console/app"      # copie installée : sudo /opt/hots-console/deploy.sh
else
  SRC_DIR=""
fi
PKG_VERSION="$(cat "${SRC_DIR}/VERSION" 2>/dev/null || echo "dev")"

# ----------------------------------------------------------------------------------------------
# Interface : whiptail si disponible (fenêtres), sinon questions simples dans le terminal.
# ----------------------------------------------------------------------------------------------

HAS_UI=0
if [[ -t 0 && -t 1 ]] && command -v whiptail >/dev/null 2>&1; then
  HAS_UI=1
fi
export NEWT_COLORS='root=,blue window=,white border=black,white title=blue,white button=white,blue actbutton=white,cyan compactbutton=black,white'

say() { printf '%s\n' "$*"; }
log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" >>"${LOG_FILE}"; }

ui_msg() { # titre, texte
  if [[ ${HAS_UI} -eq 1 ]]; then
    whiptail --title "$1" --msgbox "$2" 20 76
  else
    printf '== %s ==\n%b\n\n' "$1" "$2"
  fi
}

ui_yesno() { # titre, texte -> 0 = oui
  if [[ ${ASSUME_YES} -eq 1 ]]; then return 0; fi
  if [[ ${HAS_UI} -eq 1 ]]; then
    whiptail --title "$1" --yesno "$2" 20 76
  else
    local answer
    printf '%b ' "$2"
    read -r -p "[o/N] " answer
    [[ "${answer}" =~ ^[oOyY] ]]
  fi
}

ui_input() { # titre, texte, valeur par défaut -> réponse sur stdout
  if [[ ${HAS_UI} -eq 1 ]]; then
    whiptail --title "$1" --inputbox "$2" 14 76 "$3" 3>&1 1>&2 2>&3
  else
    local answer
    printf '%b ' "$2"
    read -r -p "[$3] " answer
    printf '%s' "${answer:-$3}"
  fi
}

ui_menu() { # titre, texte, puis paires clé/libellé -> clé sur stdout
  local title="$1" text="$2"
  shift 2
  if [[ ${HAS_UI} -eq 1 ]]; then
    whiptail --title "${title}" --menu "${text}" 20 76 8 "$@" 3>&1 1>&2 2>&3
  else
    printf '%b\n' "${text}"
    local i=1 keys=()
    while [[ $# -gt 0 ]]; do
      say "  ${i}) $2"
      keys+=("$1")
      shift 2
      i=$((i + 1))
    done
    local choice
    read -r -p "Votre choix : " choice
    [[ "${choice}" =~ ^[0-9]+$ ]] && ((choice >= 1 && choice <= ${#keys[@]})) || return 1
    printf '%s' "${keys[$((choice - 1))]}"
  fi
}

STEP=0
ui_step() { # message
  STEP=$((STEP + 1))
  log "STEP ${STEP}/${TOTAL_STEPS}: $1"
  local filled=$((STEP * 30 / TOTAL_STEPS)) bar=""
  bar="$(printf '%*s' "${filled}" '' | tr ' ' '#')$(printf '%*s' "$((30 - filled))" '' | tr ' ' '.')"
  if [[ ${HAS_UI} -eq 1 ]]; then
    whiptail --title "Installation de la ${APP_NAME}" --infobox \
      "\n  Étape ${STEP} sur ${TOTAL_STEPS}\n\n  [${bar}]\n\n  $1…\n\n  (journal détaillé : ${LOG_FILE})" 13 70
  else
    say "[${STEP}/${TOTAL_STEPS}] $1…"
  fi
}

fail() {
  log "ERROR: $*"
  local tail_log=""
  tail_log="$(tail -n 15 "${LOG_FILE}" 2>/dev/null || true)"
  ui_msg "Erreur" "$*\n\nDernières lignes du journal (${LOG_FILE}) :\n\n${tail_log}"
  exit 1
}

run() { # exécute une commande en journalisant sa sortie
  log "+ $*"
  "$@" >>"${LOG_FILE}" 2>&1
}

# ----------------------------------------------------------------------------------------------
# Vérifications
# ----------------------------------------------------------------------------------------------

usage() {
  sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
  exit 0
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --domain) DOMAIN="${2:-}"; shift 2 ;;
      --email) EMAIL="${2:-}"; shift 2 ;;
      --sslip) USE_SSLIP=1; shift ;;
      --yes|-y) ASSUME_YES=1; shift ;;
      --update) ACTION="update"; shift ;;
      --uninstall) ACTION="uninstall"; shift ;;
      -h|--help) usage ;;
      *) say "Option inconnue : $1"; usage ;;
    esac
  done
}

require_root() {
  if [[ ${EUID} -ne 0 ]]; then
    exec sudo -E bash "$0" "$@"
  fi
}

check_os() {
  [[ -r /etc/os-release ]] || fail "Système non reconnu (fichier /etc/os-release absent)."
  # Lu dans un sous-shell : /etc/os-release définit VERSION, ID… qui écraseraient nos variables.
  local os_ids os_name
  # shellcheck disable=SC1091
  os_ids="$(. /etc/os-release && printf '%s:%s' "${ID:-}" "${ID_LIKE:-}")"
  # shellcheck disable=SC1091
  os_name="$(. /etc/os-release && printf '%s' "${PRETTY_NAME:-inconnu}")"
  case "${os_ids}" in
    ubuntu:*|debian:*|*:*debian*|*:*ubuntu*) ;;
    *) fail "Ce script est prévu pour Ubuntu ou Debian (système détecté : ${os_name})." ;;
  esac
  [[ -n "${SRC_DIR}" ]] || fail "Fichiers de la console introuvables : lancez deploy.sh depuis le dossier dézippé."
  command -v systemctl >/dev/null 2>&1 || fail "systemd est requis."
}

public_ip() {
  local ip=""
  for url in https://api.ipify.org https://ifconfig.me/ip https://ipv4.icanhazip.com; do
    ip="$(curl -4 -fsS --max-time 6 "${url}" 2>/dev/null | tr -d '[:space:]' || true)"
    if [[ "${ip}" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      printf '%s' "${ip}"
      return 0
    fi
  done
  return 1
}

valid_domain() {
  [[ "$1" =~ ^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$ ]]
}

domain_resolves_to() { # domaine, ip
  local resolved
  resolved="$(getent ahostsv4 "$1" 2>/dev/null | awk '{print $1}' | sort -u | tr '\n' ' ')"
  [[ " ${resolved} " == *" $2 "* ]]
}

ports_in_use_by_others() {
  ss -ltnpH '( sport = :80 or sport = :443 )' 2>/dev/null | grep -v caddy | awk '{print $NF}' | sort -u | tr '\n' ' ' || true
}

is_installed() { [[ -f "/etc/systemd/system/${SERVICE}.service" ]]; }

# ----------------------------------------------------------------------------------------------
# Assistant de première installation
# ----------------------------------------------------------------------------------------------

choose_address() {
  local ip=""
  ip="$(public_ip || true)"
  if [[ -z "${DOMAIN}" && ${USE_SSLIP} -eq 0 && ${ASSUME_YES} -eq 0 ]]; then
    local choice
    choice="$(ui_menu "Adresse de la console" \
      "Quelle adresse vos clients utiliseront-ils ?\n\nAvec un nom de domaine, l'adresse est plus facile à retenir.\nSans domaine, une adresse gratuite basée sur l'IP du serveur est créée." \
      domain "J'ai un nom de domaine (ex. console.mondomaine.fr)" \
      sslip "Je n'ai pas de domaine : adresse automatique gratuite")" || exit 0
    [[ "${choice}" == "sslip" ]] && USE_SSLIP=1
    if [[ "${choice}" == "domain" ]]; then
      DOMAIN="$(ui_input "Nom de domaine" \
        "Saisissez le nom de domaine de la console.\n\nIl doit déjà pointer vers l'adresse IP de ce serveur (${ip:-inconnue}) :\nenregistrement DNS de type A chez votre hébergeur de domaine." "")" || exit 0
    fi
  fi

  if [[ ${USE_SSLIP} -eq 1 ]]; then
    [[ -n "${ip}" ]] || fail "Impossible de déterminer l'adresse IP publique du serveur. Utilisez --domain."
    DOMAIN="${ip//./-}.sslip.io"
  fi
  DOMAIN="$(printf '%s' "${DOMAIN}" | tr '[:upper:]' '[:lower:]' | sed -e 's#^https\?://##' -e 's#/.*$##')"
  valid_domain "${DOMAIN}" || fail "Nom de domaine invalide : « ${DOMAIN} »."

  if [[ -n "${ip}" ]] && ! domain_resolves_to "${DOMAIN}" "${ip}"; then
    ui_yesno "Attention : DNS" "Le domaine ${DOMAIN} ne pointe pas (encore) vers l'IP de ce serveur (${ip}).\n\nSans cela, le certificat HTTPS ne pourra pas être obtenu. Si vous venez de créer l'enregistrement DNS, il peut falloir quelques minutes.\n\nContinuer quand même ?" || exit 0
  fi

  if [[ -z "${EMAIL}" && ${ASSUME_YES} -eq 0 ]]; then
    EMAIL="$(ui_input "Adresse e-mail (facultatif)" \
      "Adresse e-mail pour Let's Encrypt (alertes d'expiration du certificat HTTPS).\nLaissez vide si vous ne souhaitez pas la fournir." "")" || exit 0
  fi
  if [[ -n "${EMAIL}" && ! "${EMAIL}" =~ ^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$ ]]; then
    fail "Adresse e-mail invalide : « ${EMAIL} »."
  fi
}

check_ports() {
  local others
  others="$(ports_in_use_by_others)"
  if [[ -n "${others// /}" ]]; then
    ui_yesno "Ports 80/443 occupés" "Un autre logiciel utilise déjà les ports web 80/443 :\n\n  ${others}\n\nCaddy en a besoin pour le HTTPS automatique. Voulez-vous arrêter et désactiver nginx/apache2 s'ils sont présents ?\n\n(Non = annuler l'installation)" || exit 0
    for svc in nginx apache2; do
      if systemctl is-active --quiet "${svc}" 2>/dev/null; then
        run systemctl disable --now "${svc}" || true
      fi
    done
  fi
}

# ----------------------------------------------------------------------------------------------
# Étapes d'installation
# ----------------------------------------------------------------------------------------------

install_packages() {
  ui_step "Installation des paquets système (Python, outils)"
  export DEBIAN_FRONTEND=noninteractive
  run apt-get update -y || fail "apt-get update a échoué (connexion Internet ?)."
  run apt-get install -y python3 python3-venv curl ca-certificates gnupg debian-keyring debian-archive-keyring apt-transport-https sqlite3 qrencode \
    || run apt-get install -y python3 python3-venv curl ca-certificates gnupg sqlite3 \
    || fail "L'installation des paquets système a échoué."
}

install_caddy() {
  ui_step "Installation de Caddy (HTTPS automatique)"
  if ! command -v caddy >/dev/null 2>&1; then
    run bash -c "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg" \
      && run bash -c "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list" \
      && run apt-get update -y \
      && run apt-get install -y caddy \
      || run apt-get install -y caddy \
      || fail "L'installation de Caddy a échoué."
  fi
}

install_app() {
  ui_step "Copie de la console dans ${INSTALL_DIR}"
  if ! id -u "${SERVICE_USER}" >/dev/null 2>&1; then
    run useradd --system --home-dir "${DATA_DIR}" --shell /usr/sbin/nologin "${SERVICE_USER}"
  fi
  install -d -m 0755 "${INSTALL_DIR}" "${INSTALL_DIR}/app"
  install -d -m 0750 -o "${SERVICE_USER}" -g "${SERVICE_USER}" "${DATA_DIR}"
  install -d -m 0700 -o "${SERVICE_USER}" -g "${SERVICE_USER}" "${BACKUP_DIR}"
  local staging="${INSTALL_DIR}/app.new"
  rm -rf -- "${staging}"
  mkdir -p "${staging}"
  cp -r "${SRC_DIR}/hots_server" "${SRC_DIR}/requirements.txt" "${staging}/"
  printf '%s\n' "${PKG_VERSION}" >"${staging}/VERSION"
  find "${staging}" -name '__pycache__' -type d -prune -exec rm -rf {} +
  rm -rf -- "${INSTALL_DIR}/app.old"
  if [[ -d "${INSTALL_DIR}/app/hots_server" ]]; then mv "${INSTALL_DIR}/app" "${INSTALL_DIR}/app.old"; else rm -rf -- "${INSTALL_DIR}/app"; fi
  mv "${staging}" "${INSTALL_DIR}/app"
  cp "${SCRIPT_DIR}/deploy.sh" "${INSTALL_DIR}/deploy.sh" 2>/dev/null || true
  chmod 0755 "${INSTALL_DIR}/deploy.sh" 2>/dev/null || true

  ui_step "Préparation de l'environnement Python"
  if [[ ! -x "${INSTALL_DIR}/venv/bin/python" ]]; then
    run python3 -m venv "${INSTALL_DIR}/venv" || fail "Création de l'environnement Python impossible."
  fi
  run "${INSTALL_DIR}/venv/bin/pip" install --upgrade pip || true
  run "${INSTALL_DIR}/venv/bin/pip" install -r "${INSTALL_DIR}/app/requirements.txt" || fail "Installation des dépendances Python impossible."
}

write_config() {
  ui_step "Configuration du service et du HTTPS"
  if [[ ! -f "${ENV_FILE}" ]]; then
    cat >"${ENV_FILE}" <<EOF
# Réglages de la console HOTS Hosts (voir hots_server/settings.py)
HOTS_DATA_DIR=${DATA_DIR}
HOTS_COOKIE_SECURE=1
HOTS_AGENT_LANG=fr
EOF
    chmod 0644 "${ENV_FILE}"
  fi

  cat >"/etc/systemd/system/${SERVICE}.service" <<EOF
[Unit]
Description=${APP_NAME}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
EnvironmentFile=${ENV_FILE}
WorkingDirectory=${INSTALL_DIR}/app
ExecStart=${INSTALL_DIR}/venv/bin/python -m hots_server serve --host 127.0.0.1 --port ${APP_PORT}
Restart=always
RestartSec=3
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
ReadWritePaths=${DATA_DIR}
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
LockPersonality=true
UMask=0077

[Install]
WantedBy=multi-user.target
EOF

  cat >"/etc/systemd/system/${SERVICE}-backup.service" <<EOF
[Unit]
Description=Sauvegarde de la ${APP_NAME}

[Service]
Type=oneshot
User=${SERVICE_USER}
Group=${SERVICE_USER}
EnvironmentFile=${ENV_FILE}
WorkingDirectory=${INSTALL_DIR}/app
ExecStart=${INSTALL_DIR}/venv/bin/python -m hots_server backup ${BACKUP_DIR} --keep 14
EOF

  cat >"/etc/systemd/system/${SERVICE}-backup.timer" <<EOF
[Unit]
Description=Sauvegarde quotidienne de la ${APP_NAME}

[Timer]
OnCalendar=*-*-* 03:17:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

  cat >"${CLI}" <<EOF
#!/bin/sh
# Outils de la console HOTS Hosts : setup-link | reset-password EMAIL | info | backup DIR
set -a; . ${ENV_FILE}; set +a
cd ${INSTALL_DIR}/app || exit 1
if [ "\$(id -u)" -ne 0 ]; then echo "Utilisez : sudo hots-server \$*" >&2; exit 1; fi
exec runuser -u ${SERVICE_USER} -- ${INSTALL_DIR}/venv/bin/python -m hots_server "\$@"
EOF
  chmod 0755 "${CLI}"

  install -d -m 0755 "${CADDY_SITES}"
  {
    printf '# Généré par deploy.sh (%s) — %s\n' "${APP_NAME}" "$(date '+%F')"
    printf '%s {\n' "${DOMAIN}"
    if [[ -n "${EMAIL}" ]]; then printf '\ttls %s\n' "${EMAIL}"; fi
    printf '\tencode zstd gzip\n'
    printf '\theader Strict-Transport-Security "max-age=31536000"\n'
    printf '\treverse_proxy 127.0.0.1:%s\n' "${APP_PORT}"
    printf '}\n'
  } >"${CADDY_SITE_FILE}"
  printf '%s\n' "${DOMAIN}" >"${INSTALL_DIR}/DOMAIN"

  local main_caddyfile="/etc/caddy/Caddyfile"
  if [[ ! -f "${main_caddyfile}" ]] || grep -q 'root \* /usr/share/caddy' "${main_caddyfile}"; then
    # Caddyfile d'origine (page d'exemple) : on le remplace.
    [[ -f "${main_caddyfile}" ]] && cp "${main_caddyfile}" "${main_caddyfile}.orig-hots"
    printf '# Sites gérés par deploy.sh\nimport %s/*.caddy\n' "${CADDY_SITES}" >"${main_caddyfile}"
  elif ! grep -q "import ${CADDY_SITES}/\*.caddy" "${main_caddyfile}"; then
    printf '\n# Ajouté par deploy.sh (%s)\nimport %s/*.caddy\n' "${APP_NAME}" "${CADDY_SITES}" >>"${main_caddyfile}"
  fi
  run caddy validate --config "${main_caddyfile}" --adapter caddyfile || fail "La configuration de Caddy est invalide."

  if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q "Status: active"; then
    run ufw allow 80/tcp || true
    run ufw allow 443/tcp || true
  fi
}

start_services() {
  ui_step "Démarrage de la console"
  run systemctl daemon-reload
  run systemctl enable "${SERVICE}" "${SERVICE}-backup.timer"
  run systemctl restart "${SERVICE}"
  run systemctl start "${SERVICE}-backup.timer"
  run systemctl enable caddy
  run systemctl reload-or-restart caddy || run systemctl restart caddy || fail "Caddy n'a pas pu démarrer."

  local ok=0
  for _ in $(seq 1 30); do
    if curl -fsS --max-time 3 "http://127.0.0.1:${APP_PORT}/healthz" >/dev/null 2>&1; then ok=1; break; fi
    sleep 1
  done
  [[ ${ok} -eq 1 ]] || fail "La console ne répond pas. Consultez : journalctl -u ${SERVICE} -n 50"

  ui_step "Obtention du certificat HTTPS (jusqu'à 1 minute)"
  HTTPS_OK=0
  for _ in $(seq 1 30); do
    if curl -fsS --max-time 5 "https://${DOMAIN}/healthz" >/dev/null 2>&1; then HTTPS_OK=1; break; fi
    sleep 2
  done
}

final_screen() {
  local url="https://${DOMAIN}"
  local token=""
  token="$("${CLI}" setup-link 2>/dev/null | tail -n 1 || true)"
  local next
  if [[ -n "${token}" && "${token}" != "already-configured" ]]; then
    next="${url}/#/setup/${token}"
  else
    next="${url}"
  fi
  local https_note=""
  if [[ ${HTTPS_OK:-0} -ne 1 ]]; then
    https_note="\n\n⚠ Le certificat HTTPS n'est pas encore disponible. Vérifiez que :\n  • le domaine ${DOMAIN} pointe vers ce serveur ;\n  • les ports 80 et 443 sont ouverts (pare-feu de l'hébergeur).\n  Caddy réessaie tout seul. Journal : journalctl -u caddy -n 50"
  fi
  local text
  if [[ "${next}" == *"/setup/"* ]]; then
    text="La console est installée ! 🎉\n\nDernière étape : ouvrez ce lien dans votre navigateur pour créer\nle compte administrateur (il est aussi affiché sous cette fenêtre) :\n\n${next}${https_note}"
  else
    text="La console est à jour et fonctionne.\n\nAdresse : ${url}${https_note}"
  fi
  ui_msg "Terminé" "${text}"
  say ""
  say "=================================================================="
  say "  ${APP_NAME} — ${url}"
  if [[ "${next}" == *"/setup/"* ]]; then
    say "  Créez le compte administrateur ici :"
    say "  ${next}"
    if command -v qrencode >/dev/null 2>&1; then qrencode -t ANSIUTF8 -m 1 "${next}" || true; fi
  fi
  say ""
  say "  Gérer plus tard :  sudo ${INSTALL_DIR}/deploy.sh"
  say "  Outils :           sudo hots-server info | reset-password EMAIL | setup-link"
  say "=================================================================="
}

do_install() {
  ui_msg "Bienvenue" "Cet assistant installe la ${APP_NAME} (version ${PKG_VERSION}) :\n\n  • l'application web (multi-clients) ;\n  • le HTTPS automatique (Caddy + Let's Encrypt) ;\n  • une sauvegarde quotidienne de la base de données.\n\nPré-requis : ce serveur doit être joignable depuis Internet sur les ports 80 et 443.\n\nDurée : 2 à 5 minutes."
  choose_address
  ui_yesno "Récapitulatif" "Adresse de la console : https://${DOMAIN}\nE-mail Let's Encrypt : ${EMAIL:-(aucun)}\nDossier du programme : ${INSTALL_DIR}\nDonnées : ${DATA_DIR}\n\nLancer l'installation ?" || exit 0
  check_ports
  install_packages
  install_caddy
  install_app
  write_config
  start_services
  final_screen
}

do_update() {
  TOTAL_STEPS=6
  DOMAIN="$(cat "${INSTALL_DIR}/DOMAIN" 2>/dev/null || true)"
  [[ -n "${DOMAIN}" ]] || fail "Installation existante incomplète (domaine inconnu) : relancez une installation."
  ui_yesno "Mise à jour" "Mettre à jour la console de https://${DOMAIN} vers la version ${PKG_VERSION} ?\n\nLes comptes, PC et réglages sont conservés (sauvegarde automatique avant la mise à jour)." || exit 0
  ui_step "Sauvegarde de la base de données"
  if [[ -x "${CLI}" ]]; then run "${CLI}" backup "${DATA_DIR}/pre-update" --keep 5 || true; fi
  install_app
  if [[ -f "${CADDY_SITE_FILE}" ]]; then
    EMAIL="$(awk '/^\ttls /{print $2}' "${CADDY_SITE_FILE}" 2>/dev/null || true)"
  fi
  write_config
  start_services
  final_screen
}

do_change_domain() {
  TOTAL_STEPS=3
  DOMAIN=""
  USE_SSLIP=0
  choose_address
  write_config
  start_services
  ui_msg "Adresse modifiée" "La console répond maintenant sur https://${DOMAIN}\n\nAttention : les PC déjà reliés utilisent l'ancienne adresse. Si celle-ci ne fonctionne plus, reliez-les à nouveau (Options > Administration à distance)."
}

do_uninstall() {
  ui_yesno "Désinstallation" "Désinstaller la ${APP_NAME} de ce serveur ?\n\nLes PC reliés ne seront plus administrables, mais gardent leurs protections." || exit 0
  local keep_data=0
  if ui_yesno "Données" "Conserver les données (comptes, PC, historique) dans ${DATA_DIR} et les sauvegardes dans ${BACKUP_DIR} ?\n\nOui = conserver (recommandé), Non = tout supprimer définitivement."; then
    keep_data=1
  fi
  if [[ -x "${CLI}" ]]; then "${CLI}" backup "${BACKUP_DIR}" --keep 30 >/dev/null 2>&1 || true; fi
  systemctl disable --now "${SERVICE}" "${SERVICE}-backup.timer" >/dev/null 2>&1 || true
  rm -f "/etc/systemd/system/${SERVICE}.service" "/etc/systemd/system/${SERVICE}-backup.service" \
        "/etc/systemd/system/${SERVICE}-backup.timer" "${CLI}" "${CADDY_SITE_FILE}"
  systemctl daemon-reload
  systemctl reload caddy >/dev/null 2>&1 || true
  rm -rf -- "${INSTALL_DIR}"
  if [[ ${keep_data} -eq 0 ]]; then
    rm -rf -- "${DATA_DIR}" "${BACKUP_DIR}" "${ENV_FILE}"
    userdel "${SERVICE_USER}" >/dev/null 2>&1 || true
  fi
  local kept=""
  if [[ ${keep_data} -eq 1 ]]; then kept="\n\nDonnées conservées dans ${DATA_DIR} (et ${BACKUP_DIR})."; fi
  ui_msg "Désinstallation terminée" "La console a été retirée.${kept}\n\nCaddy reste installé (il peut servir d'autres sites) : sudo apt remove caddy pour le retirer."
}

manage_menu() {
  local domain choice
  domain="$(cat "${INSTALL_DIR}/DOMAIN" 2>/dev/null || echo '?')"
  choice="$(ui_menu "${APP_NAME}" "Console installée : https://${domain}\nVersion installée : $(cat "${INSTALL_DIR}/app/VERSION" 2>/dev/null || echo '?') — version de ce paquet : ${PKG_VERSION}\n\nQue voulez-vous faire ?" \
    update "Mettre à jour (garde toutes les données)" \
    link "Afficher le lien de création du compte administrateur" \
    password "Réinitialiser le mot de passe d'un utilisateur" \
    backup "Faire une sauvegarde maintenant" \
    status "État du service" \
    domain "Changer l'adresse (nom de domaine)" \
    uninstall "Désinstaller" \
    quit "Quitter")" || exit 0
  case "${choice}" in
    update) do_update ;;
    link)
      local token
      token="$("${CLI}" setup-link 2>/dev/null | tail -n 1 || true)"
      if [[ -n "${token}" && "${token}" != "already-configured" ]]; then
        ui_msg "Lien de configuration" "https://${domain}/#/setup/${token}"
        say "https://${domain}/#/setup/${token}"
      else
        ui_msg "Lien de configuration" "Le compte administrateur existe déjà. En cas d'oubli du mot de passe, utilisez « Réinitialiser le mot de passe »."
      fi ;;
    password)
      local email newpw
      email="$(ui_input "Réinitialiser un mot de passe" "Adresse e-mail de l'utilisateur :" "")" || exit 0
      if newpw="$("${CLI}" reset-password "${email}" 2>&1)"; then
        ui_msg "Nouveau mot de passe" "Nouveau mot de passe pour ${email} :\n\n    ${newpw}\n\nNotez-le : il ne sera plus affiché. L'utilisateur pourra le changer dans « Mon compte »."
      else
        ui_msg "Erreur" "${newpw}"
      fi ;;
    backup)
      local file
      file="$("${CLI}" backup "${BACKUP_DIR}" --keep 30 2>&1 | tail -n 1)"
      ui_msg "Sauvegarde" "Sauvegarde créée :\n\n${file}" ;;
    status)
      ui_msg "État" "$(systemctl is-active "${SERVICE}" | sed 's/^/Console : /')\n$(systemctl is-active caddy | sed 's/^/Caddy (HTTPS) : /')\n\n$("${CLI}" info 2>&1 || true)" ;;
    domain) do_change_domain ;;
    uninstall) do_uninstall ;;
    *) exit 0 ;;
  esac
}

main() {
  parse_args "$@"
  require_root "$@"
  touch "${LOG_FILE}" && chmod 0600 "${LOG_FILE}"
  log "deploy.sh ${PKG_VERSION} started: $*"
  check_os
  case "${ACTION}" in
    uninstall) do_uninstall ;;
    update) do_update ;;
    *)
      if is_installed; then
        if [[ ${ASSUME_YES} -eq 1 ]]; then do_update; else manage_menu; fi
      else
        do_install
      fi ;;
  esac
}

main "$@"
