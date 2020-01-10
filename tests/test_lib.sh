#!/bin/bash
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
#
# This was a Library for tests
#
# A-Tune is licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
# Create: 2019-12-26

export EXIT_RET_VAL=0
export TST_COUNT=1

# Global variables
ATUNE_SERVICE_NAME="atuned"
ATUNE_CONF="/etc/atuned/atuned.cnf"
ANALYSIS_LOG="analysis.log"
EXIT_FLAG=0
SPECIAL_CHARACTERS="~\!@#%^*"
# 4096 CHARACTERS
ULTRA_LONG_CHARACTERS="0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

ARRAY_WORKLOADTYPE=("default" "webserver" "big_database" "big_data" "in-memory_computing" "in-memory_database" "single_computer_intensive_jobs" "communication" "idle")

tst_resm()
{

    local ret=$1
    shift
    echo "====== $TCID $TST_COUNT $ret : $@ ======"

    case "$ret" in
    TPASS|TFAIL)
    TST_COUNT=$((TST_COUNT+1));;
    esac

    case "$ret" in
    TFAIL)
    EXIT_RET_VAL=$((EXIT_RET_VAL+1));;
    esac
}

tst_exit()
{
    if [ -n "$TST_CLEANUP" ]; then
        $TST_CLEANUP
    fi

    exit ${EXIT_RET_VAL}
}

# get atune conf key's value
# input: key
# example: get_conf_value disk
function get_conf_value()
{
    local key=$1
    if [ -z $key ];then
        echo "You have to input a key name"
        return 1
    fi
    local check_key_exist=`grep -E "^$key" $ATUNE_CONF | tail -n 1 | awk -F ' = ' '{print $1}'`
    if [ -z $check_key_exist ];then
        echo "The key does no exist ,please check"
        return 1
    else
        value=`grep -E "^$key" $ATUNE_CONF | tail -n 1 | awk -F ' = ' '{print $NF}'`
        echo $value
    fi
}

# change atune conf's configuration
# input: key, value
# example: change_conf_value disk sda
function change_conf_value()
{
    local key=$1
    if [ -z $key ];then
        echo "You have to input a key name"
        return 1
    fi
    local value=`echo ${@:2}`
    local curr_value=$(get_conf_value $key)
    if [ "x$curr_value" == "x$value" ];then
        echo "The $key's value had already been set to $value"
        return 0
    fi
    changed_value=`sed -i "s/^$key = .*/$key = $value/g" $ATUNE_CONF  | xargs grep -E "^$key = $value$" $ATUNE_CONF`
    return $?
}

# comment atune conf's configuration
# input: key
# example: comment_conf_value disk
function comment_conf_value()
{
    local key=$1
    if [ -z $key ];then
        echo "You have to input a key name"
        return 1
    fi
    local check_key_exist=`grep -E "^$key" $ATUNE_CONF | tail -n 1 | awk -F ' = ' '{print $1}'`
    if [ -z $check_key_exist ];then
        echo "The key does no exist ,please check"
        return 1
    else
        sed -i "/^$key = .*/s/^/#&/" $ATUNE_CONF | xargs grep "^#$key = " $ATUNE_CONF
    fi
}

# recover atune conf's configuration that had benn commented
# input: key
# example: recover_comment_conf_value disk
function recover_comment_conf_value()
{
    local key=$1
    if [ -z $key ];then
        echo "You have to input a key name"
        return 1
    fi
    sed -i "s/^#$key/$key/g" $ATUNE_CONF | xargs grep "^$key = " $ATUNE_CONF
}

# check result
# input: result, expect result
# example: check_result $? 0
function check_result()
{
    if [ "$1" = "$2" ];then
        echo  "check result succeed!"
    else
        echo  "check result failured!"
        ((EXIT_FLAG++))
    fi
}

# wait until condition is true
# input: max second, condition
# default: second=1, condition=""
# example: wait_condition 10 'greap atuned /var/log/messages'
function wait_condition()
{
    local max_second=${1:-1}
    local condition=${2:-""}
    # cycle every 50ms, calculating the maximum number of cycles based on the maximum second value entered by the user
    local loop_count=`expr ${max_second} \* 1000 / 50`

    for ((wait_loop=1; wait_loop<=$loop_count; wait_loop++)); do
        if eval ${condition} > /dev/null 2>&1; then
          return 0
        fi
        sleep 0.05 # 50ms
    done

    if [ $i -ge $loop_count ]; then
        return 1 # wait condition fail
    fi
}

# wait service running
# input: service name
# example: wait_service_ready atuned
function wait_service_ready()
{
    local service_name=$1
    if [ -z $service_name ];then
        echo "You have to input a service name"
        return 1
    fi
    wait_condition 10 'systemctl status $service_name | grep "Active: active (running)"'
    return $?
}

# install rpm packet
# input: rpm packet name
# example: rpminstall atune
function rpminstall()
{
    rpm_name=$1
    command_name=${3-$rpm_name}
        if which $command_name > /dev/null;then
            return 0
        fi
        if which yum;then
            yum install -y $rpm_name
            if [ $? -ne 0 ];then
                echo "yum install $rpm_name fail" > /dev/null
                exit 1
            fi
        else
            echo "this system not support install command" > /dev/null
            exit 1
        fi
}

# check if service is not started, restart it
# input: service name
# example: check_service_started atuned
function check_service_started()
{
    local service_name=$1
    if [ -z $service_name ];then
        echo "You have to input a service name"
        return 1
    fi

    systemctl status $service_name | grep "Active: active (running)"
    local ret=$?
    if [ $ret -ne 0 ];then
        systemctl restart $service_name
        wait_service_ready $service_name
    fi
}

