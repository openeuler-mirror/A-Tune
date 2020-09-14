#!/bin/sh
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
#
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-01-09
# Author: zhangtaibo <sonice1755@163.com>

export TCID="atune-adm collection cmd test"

. ./test_lib.sh

# Global variables
file_name="atuneTest"
sys_network=`ip address | grep UP | awk 'NR==1{print $2}' | awk -F ':' '{print $1}'`
sys_disk=`lsscsi | awk '($NF~/dev/){print $NF}' | awk -F '/' '{print $NF}'| awk 'NR==1{print $1}'`
output_path=`pwd`
min_interval=1 # collction interval between 1 and 60 seconds
min_duration=10 # collection duration value must be bigger than interval*10
workload_type="default"

init()
{
    echo "init the system"
    rpminstall psmisc # collection script need killall command.
    check_service_started atuned
}

cleanup()
{
    echo "===================="
    echo "Clean the System"
    echo "===================="
    rm -rf temp.log
    rm -rf $output_path/*.csv
}

test01()
{
    tst_resm TINFO "atune-adm collection cmd test"
    # Help info
    atune-adm collection -h > temp.log
    grep "collect data for train machine learning model, you must set the command options" temp.log
    check_result $? 0

    # Normal test
    atune-adm collection -f $file_name -i $min_interval -d $min_duration -o $output_path -b $sys_disk -n $sys_network -t $workload_type
    check_result $? 0

    ls -l $output_path/$file_name*.csv
    check_result $? 0

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi
}

test02()
{
    tst_clean
    tst_resm TINFO "atune-adm collection cmd --filename input test"
    # The input of the filename is special character and ultra long character and null and boundary value
    local str_129="000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    local str_128="00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "$str_129" "$str_128" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        atune-adm collection -i $min_interval -d $min_duration -o $output_path -b $sys_disk -n $sys_network -t $workload_type -f ${array[i]} >& temp.log

        case ${array[i]} in
            "$SPECIAL_CHARACTERS")
                check_result $? 1
                grep -i "input:.*is invalid" temp.log;;
            $ULTRA_LONG_CHARACTERS)
                check_result $? 1
                grep -i "error: filename length is longer than 128 charaters" temp.log;;
            $str_129)
                check_result $? 1
                grep -i "error: filename length is longer than 128 charaters" temp.log;;
            $str_128)
                check_result $? 0
                grep -i "generate .*csv successfully" temp.log;;
            *)
                check_result $? 1
                grep -i "Incorrect Usage: flag needs an argument: -f" temp.log;;
        esac
        check_result $? 0
    done

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi
}

test03()
{
    tst_clean
    tst_resm TINFO "atune-adm collection cmd --interval input test"
    # The input of the interval is special character and ultra long character and null and boundary value
    local lower=0
    local ceiling=61
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "$lower" "$ceiling" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        atune-adm collection -f $file_name -d $min_duration -o $output_path -b $sys_disk -n $sys_network -t $workload_type -i ${array[i]} >& temp.log
        check_result $? 1

        case ${array[i]} in
            "$SPECIAL_CHARACTERS")
                grep -i "Incorrect Usage: invalid value.*for flag -i" temp.log;;
            $ULTRA_LONG_CHARACTERS)
                grep -i "error: collection interval value must be between 1 and 60 seconds" temp.log;;
            $lower)
                grep -i "error: collection interval value must be between 1 and 60 seconds" temp.log;;
            $ceiling)
                grep -i "error: collection interval value must be between 1 and 60 seconds" temp.log;;
            *)
                grep -i "Incorrect Usage: flag needs an argument: -i" temp.log;;
        esac
        check_result $? 0
    done

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi
}

test04()
{
    tst_clean
    tst_resm TINFO "atune-adm collection cmd --duration input test"
    # The input of the duration is special character and ultra long character and null and boundary value
    local lower=9
    local ceiling=9223372036854775808
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "$lower" "$ceiling" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        atune-adm collection -f $file_name -i $min_interval -o $output_path -b $sys_disk -n $sys_network -t $workload_type -d ${array[i]} >& temp.log
        check_result $? 1

        case ${array[i]} in
            "$SPECIAL_CHARACTERS")
                grep -i "Incorrect Usage: invalid value.*for flag -d" temp.log;;
            $ULTRA_LONG_CHARACTERS)
                grep -i "error: collection duration value must be bigger than interval\*10" temp.log;;
            $lower)
                grep -i "error: collection duration value must be bigger than interval\*10" temp.log;;
            $ceiling)
                grep -i "Incorrect Usage: invalid value.*for flag -d" temp.log;;
            *)
                grep -i "Incorrect Usage: flag needs an argument: -d" temp.log;;
        esac
        check_result $? 0
    done

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi
}

test05()
{
    tst_clean
    tst_resm TINFO "atune-adm collection cmd --output_path input test"
    # The input of the output_path is special character, ultra long character, null and an absolute path that did not exist.
    local path_not_exist="/path_not_exist"
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "$path_not_exist" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        atune-adm collection -f $file_name -i $min_interval -d $min_duration -b $sys_disk -n $sys_network -t $workload_type -o ${array[i]} >& temp.log
        check_result $? 1

        case ${array[i]} in
            "$SPECIAL_CHARACTERS")
                grep -i "error: output path must be absolute path" temp.log;;
            $ULTRA_LONG_CHARACTERS)
                grep -i "error: output path must be absolute path" temp.log;;
            $path_not_exist)
                grep -i "rpc error: code = Unknown desc = output_path.*is not exist" temp.log;;
            *)
                grep -i "Incorrect Usage: flag needs an argument: -o" temp.log;;
        esac
        check_result $? 0
    done

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi
}

test06()
{
    tst_clean
    tst_resm TINFO "atune-adm collection cmd --disk input test"
    # The input of the disk is special character, ultra long character and null
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        atune-adm collection -f $file_name -i $min_interval -d $min_duration -o $output_path -n $sys_network -t $workload_type -b ${array[i]} >& temp.log
        check_result $? 1

        case ${array[i]} in
            "$SPECIAL_CHARACTERS")
                grep -i "rpc error: code = Unknown desc = input:.*is invalid" temp.log;;
            $ULTRA_LONG_CHARACTERS)
                grep -i "rpc error: code = Unknown desc = disk.*is not exist" temp.log;;
            *)
                grep -i "Incorrect Usage: flag needs an argument: -b" temp.log;;
        esac
        check_result $? 0
    done

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi
}

test07()
{
    tst_clean
    tst_resm TINFO "atune-adm collection cmd --network input test"
    # The input of the network is special character, ultra long character and null
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        atune-adm collection -f $file_name -i $min_interval -d $min_duration -o $output_path -b $sys_disk -t $workload_type -n ${array[i]} >& temp.log
        check_result $? 1

        case ${array[i]} in
            "$SPECIAL_CHARACTERS")
                grep -i "rpc error: code = Unknown desc = input:.*is invalid" temp.log;;
            $ULTRA_LONG_CHARACTERS)
                grep -i "rpc error: code = Unknown desc = interface.*is not exist" temp.log;;
            *)
                grep -i "Incorrect Usage: flag needs an argument: -n" temp.log;;
        esac
        check_result $? 0
    done

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi
}

test08()
{
    tst_clean
    tst_resm TINFO "atune-adm collection cmd --workload_type input test"
    # The input of the workload_type is special character, ultra long character and null
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        atune-adm collection -f $file_name -i $min_interval -d $min_duration -o $output_path -b $sys_disk -n $sys_network -t ${array[i]} >& temp.log
        check_result $? 1

        case ${array[i]} in
            "$SPECIAL_CHARACTERS")
                grep -i "rpc error: code = Unknown desc = input:.*is invalid" temp.log;;
            $ULTRA_LONG_CHARACTERS)
                grep -i "rpc error: code = Unknown desc = app type.*is not exist, use define command first" temp.log;;
            *)
                grep -i "Incorrect Usage: flag needs an argument: -t" temp.log;;
        esac
        check_result $? 0
    done

    # Check all the supported workload for collecting
    for ((i=0;i<${#ARRAY_APP[@]};i++));do
        rm -rf $output_path/*.csv
        atune-adm collection -f $file_name -i $min_interval -d $min_duration -o $output_path -b $sys_disk -n $sys_network -t ${ARRAY_APP[i]} >& temp.log

        check_result $? 0

        grep -i "generate .*csv successfully" temp.log
        check_result $? 0

        ls -l $output_path/$file_name*.csv
        check_result $? 0
    done

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi
}

TST_CLEANUP=cleanup

init

test01
test02
test03
test04
test05
test06
test07
test08

tst_exit

