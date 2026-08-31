#!/bin/bash

yyyy=$(date --date '1 minute' -u +'%Y')
mm=$(date --date '1 minute' -u +'%m')
dd=$(date --date '1 minute' -u +'%d')
HH=$(date --date '1 minute' -u +'%H')
MM=$(date --date '1 minute' -u +'%M')

lock_dir=/tmp/.nexcomp.lock
lock_pid_file=${lock_dir}/pid

cleanup() {
  if [[ -d "${lock_dir}" && -f "${lock_pid_file}" ]] && [[ "$(cat "${lock_pid_file}")" == "$$" ]]; then
    rm -f "${lock_pid_file}"
    rmdir "${lock_dir}"
  fi
}

if ! mkdir "${lock_dir}" 2>/dev/null; then
  echo "Lock directory exists; another RUNME.sh process is active"
  exit 1
fi

printf '%s\n' "$$" > "${lock_pid_file}"
trap cleanup EXIT HUP INT TERM

# N0R created via N0Q via N0B
bash n0r.sh "${yyyy}" "${mm}" "${dd}" "${HH}" "${MM}"
# DAA one hour
bash grid.sh "${yyyy}" "${mm}" "${dd}" "${HH}" "${MM}" daa
# DTA storm total
bash grid.sh "${yyyy}" "${mm}" "${dd}" "${HH}" "${MM}" dta
