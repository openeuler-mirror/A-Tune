#!/bin/sh
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-02-06

declare -A kmap=(["gro"]="generic-receive-offload" ["gso"]="generic-segmentation-offload"
  ["tso"]="tcp-segmentation-offload" ["lro"]="large-receive-offload")
declare -A cmap=(["adaptive-rx"]="Adaptive" ["adaptive-tx"]="Adaptive")
declare -A lmap=(["combined"]="Combined")
declare -A gmap=(["rx"]="RX:" ["tx"]="TX:")
koption="on off"
xoption="toeplitz xor crc32"
coption="on off"

function get_ethtool_value() {
  OLD_IFS="$IFS"
  IFS=" "
  para=($*)
  IFS="$OLD_IFS"

  if [ "${#para[@]}" -lt 4 ]; then
    echo "\033[31m the length of ethtool parameter must be greater than 4 \033[31m"
    return 1
  fi

  option=${para[0]}
  network=${para[1]}
  case "$option" in
  "-K")
    property=$(ethtool -k "$network" | grep -w "${kmap["${para[2]}"]}")
    value=$(echo "$property" | awk '{print $2}')
    if !(judge_value "$value" $koption); then
      echo "\033[31m the last parameter of ethtool must select in [$koption] \033[31m"
      return 1
    fi
    affix=$(echo "$property" | awk '{print $3}')
    if [[ "$affix" == "[fixed]" ]]; then
      echo "fixed"
    else
      echo "-K $network "${para[2]}" $value"
    fi
    ;;
  "-X")
    for opt in $xoption; do
      switch=$(ethtool -x "$network" | grep -w "$opt" | awk '{print $2}')
      if [[ "$switch" == "on" ]]; then
        value=$opt
        break
      fi
    done
    if !(judge_value "$value" $xoption); then
      echo "\033[31m the last parameter of ethtool must select in [$xoption] \033[31m"
      return 1
    fi
    out=$(echo "${para[@]}" | awk '{$NF="";print}')
    echo "$out""$value"
    ;;
  "-C")
    line=2
    [ "${para[2]}" == "adaptive-rx" ] && line=3
    [ "${para[2]}" == "adaptive-tx" ] && line=5
    value=$(ethtool -c "$network" | grep -w "${cmap["${para[2]}"]}" | awk "{print $"$line"}")
    if !(judge_value "$value" $coption); then
      echo "\033[31m the last parameter of ethtool must select in [$coption] \033[31m"
      return 1
    fi
    echo "-C $network "${para[2]}" $value"
    ;;
  "-L")
    value=$(ethtool -l "$network" | grep -w "${lmap["${para[2]}"]}" | awk 'NR==2{print $2}')
    echo "-L $network "${para[2]}" $value"
    ;;
  "-G")
    value=$(ethtool -g "$network" | grep -w "${gmap["${para[2]}"]}" | awk 'NR==2{print $2}')
    echo "-G $network "${para[2]}" $value"
    ;;
  *)
    echo "\033[31m this option is not supported \033[31m" && return 1
    ;;
  esac
}

function judge_value() {
  if [ $# -lt 1 ]; then
    echo "\033[31m the number of parameter must be greater than 1 \033[31m"
    return 1
  fi
  value="$1"
  shift
  for para in $@; do
    if [[ "$para" == "$value" ]]; then
      return
    fi
  done
  false
}

function cmd_conversion() {
  option=$(echo "$@" | awk '{print $1}')
  network=$(echo "$@" | awk '{print $2}')
  case "$option" in
  "-L")
    if [[ $(echo "$@" | awk '{print $4}') == "max" ]]; then
      max_value=$(ethtool -l "$network" | grep -w "Combined" | awk 'NR==1{print $2}')
      echo "$@" | sed "s/max/$max_value/"
    else
      echo "$@"
    fi
    ;;
  *)
    echo "$@"
    ;;
  esac
}
