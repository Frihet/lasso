#! /bin/bash

SCRIPTDIR="$(cd "$(dirname "$0")"; pwd)"


restart_soffice () {
 echo "========{Restarting OO}========"
 killall -KILL soffice
 soffice -headless -accept="socket,port=8100;urp;"
 sleep 5
}

convert_file() {
 name="$1"
 newname="$2"
 out=1
 while [ $out -ne 0 ]; do
  echo "Converting '$name' to '$newname'...";
  "$SCRIPTDIR/DocumentConverter.py" "$name" "$newname";
  out=$?;
  if [ $out -ne 0 ]; then
   restart_soffice
  fi
 done
}

restart_soffice
find . -name "*.xls" |
 while read name; do
  newname="$(echo "$name" | sed -e "s+.xls$+.csv+g")"
  if ! [ -e "$newname" ]; then
   convert_file "$name" "$newname"
  fi
 done
