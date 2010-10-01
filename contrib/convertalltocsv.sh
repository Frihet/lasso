#! /bin/bash

SCRIPTDIR="$(cd "$(dirname "$0")"; pwd)"

soffice -headless -accept="socket,port=8100;urp;"
find . -name "*.xls" |
 while read name; do
  newname="$(echo "$name" | sed -e "s+.xls$+.csv+g")"
  "$SCRIPTDIR/DocumentConverter.py" "$name" "$newname";
 done
