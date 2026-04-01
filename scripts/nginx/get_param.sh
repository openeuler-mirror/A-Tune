#!/bin/bash

param_name="$1"
config_file="$2"

if [[ -z "$param_name" || -z "$config_file" ]]; then
  echo "Usage: $0 <param_name> <config_file>"
  exit 1
fi

output=$(grep -E "^\s*${param_name}\s+" "$config_file")
ret=$?

if [[ $ret -ne 0 ]]; then
  exit $ret
else
  echo $output | head -1 | sed -E "s/^\s*${param_name}\s+(.*);/\1/"
fi
