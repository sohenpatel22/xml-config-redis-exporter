#!/bin/sh
set -eu

VERBOSE=0
if [ "${1-}" = "-v" ] || [ "${1-}" = "--verbose" ]; then
    VERBOSE=1
    shift
fi

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [-v|--verbose] /path/to/config.xml" >&2
    exit 2
fi

XML_PATH=$1
if [ ! -f "$XML_PATH" ]; then
    echo "Error: XML file not found: $XML_PATH" >&2
    exit 2
fi

case "$XML_PATH" in
    /*) ;;
    *) XML_PATH="$PWD/$XML_PATH" ;;
esac

XML_DIR=$(CDPATH= cd -- "$(dirname -- "$XML_PATH")" && pwd)
XML_NAME=$(basename -- "$XML_PATH")
PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_DIR"

if [ "$VERBOSE" -eq 1 ]; then
    set -- -v "/input/$XML_NAME"
else
    set -- "/input/$XML_NAME"
fi

docker compose run --rm --build \
    -v "$XML_DIR:/input:ro" \
    exporter "$@"
