#!/bin/bash

param_name="$1"

if [[ -z "$param_name" ]]; then
  echo "Usage: $0 <param_name>"
  exit 1
fi

output=$(gs_guc check -Z datanode -N all -I all -c "${param_name}")
ret=$?

if [[ $ret -ne 0 ]]; then
  exit $ret
else
  echo "$output" | awk -F= "/${param_name}=/{print \$2}"
fi
