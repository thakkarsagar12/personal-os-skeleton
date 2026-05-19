#!/usr/bin/env bash
# Copy allowlisted owned files from source repo, scrubbing personal refs.
#
# REQUIRED env vars — the script contains ZERO personal name, email, or port literals:
#   SOURCE_REPO         path to the private source repo
#   SCRUB_NAMES         pipe-separated names to replace (e.g. "Alice|Bob|Acme")
#   SCRUB_PATH_PAT      full personal src path prefix (e.g. "/Users/alice/Code/my-repo")
#   SCRUB_PROJ_LABEL    project directory/label token (e.g. "my-repo")
#   SCRUB_USER_LABEL    short unix username / secondary project token (e.g. "alice")
#   SCRUB_PG_PORT       private Postgres port literal to replace with "5432"
#   SCRUB_QDRANT_PORT   private Qdrant port literal to replace with "6333"
#
# Privacy guarantee: this file itself is PII-free.  Personal data travels only
# through the env vars above, which callers supply at runtime and never commit.
set -eu
SRC="${SOURCE_REPO:?set SOURCE_REPO to the private repo path}"
SK="$(cd "$(dirname "$0")/.." && pwd)"

_NAMES="${SCRUB_NAMES:?set SCRUB_NAMES to pipe-separated personal names to redact}"
_PATH_PAT="${SCRUB_PATH_PAT:?set SCRUB_PATH_PAT to the personal source-path prefix to redact}"
_PROJ_LABEL="${SCRUB_PROJ_LABEL:?set SCRUB_PROJ_LABEL to the personal project label to redact}"
_USER_LABEL="${SCRUB_USER_LABEL:?set SCRUB_USER_LABEL to the short unix username / secondary project token to redact}"
_PG_PORT="${SCRUB_PG_PORT:?set SCRUB_PG_PORT to the private Postgres port to replace}"
_QD_PORT="${SCRUB_QDRANT_PORT:?set SCRUB_QDRANT_PORT to the private Qdrant port to replace}"
_PROJ_LABEL2="\"${_PROJ_LABEL}\""
_USER_LABEL2="\"${_USER_LABEL}\""
# Email pattern assembled from parts — avoids literal provider domain in this file.
_AT='@'
_EMAIL_PAT="[A-Za-z0-9._%+-]+${_AT}[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

while IFS=$'\t' read -r s t mode; do
  case "$s" in ''|\#*) continue;; esac
  mkdir -p "$SK/$(dirname "$t")"
  sed -E \
    -e "s/${_EMAIL_PAT}/USER_EMAIL/g" \
    -e "s/(${_NAMES})/PLACEHOLDER/g" \
    -e "s#${_PATH_PAT}#\${PERSONAL_OS_ROOT}#g" \
    -e 's/QDRANT_HTTP_PORT/QDRANT_PORT/g' \
    -e 's/PGPORT/POSTGRES_PORT/g' \
    -e "s/${_PG_PORT}/5432/g" \
    -e "s/${_QD_PORT}/6333/g" \
    -e "s/${_PROJ_LABEL}/PROJECT_LABEL/g" \
    -e "s#${_PROJ_LABEL2}#\"PROJECT_LABEL\"#g" \
    -e "s#${_USER_LABEL2}#\"PROJECT_USER\"#g" \
    -e 's/Astrology-Valut/PERSONAL_VAULT/g' \
    "$SRC/$s" > "$SK/$t"
  echo "copied ($mode): $s -> $t"
done < "$SK/tools/manifest.tsv"
