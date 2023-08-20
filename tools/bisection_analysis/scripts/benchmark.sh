#!/bin/bash

# FFMPEG_PATH='/opt/homebrew/bin/ffmpeg'
abs_path="$(cd "$(dirname -- "$1")" >/dev/null; pwd -P)/$(basename -- "$1")"
project_path="${abs_path}/../"
FFMPEG_PATH="${project_path}/projects/FFmpeg/build/bin/ffmpeg"
VIDEO_FILE="${project_path}/data/akiyo_cif.y4m"

start_time=$(date +%s%3)

# set -Eeuo pipefail
# set -x

## input parameters ##
# path of ffmpeg binary, currently only setup for h264
_arg_ffmpeg_path=${FFMPEG_PATH}

# number of parallel ffmpeg jobs
_arg_jobs=1

# how many iteration to run to collect a data to fit in standard distribution
_arg_loops=5

# unused, later for ffmpeg debugging purposes
_arg_debug='off'

#SCRIPT_NAME=${0##*/}
DATE=$(date '+%Y-%m-%d_%H-%M-%S')
STOP_LOOP=0
# trap "trap - SIGTERM && STOP_LOOP=1 && sleep 10 && kill -- -$$" SIGINT SIGTERM EXIT

## Boilerplate command line function ##

function die {
    local _ret=$2
    test -n "$_ret" || _ret=1
    test "$_PRINT_HELP" = yes && print_help >&2
    echo "$1" >&2
    exit ${_ret}
}

function check_bin {
    local bin=$1
    if [ ! -x ${bin} ]; then
        die "${bin} does not exist." 1
    fi
}

function print_help {
    printf "%s\n" "<ffmpeg benchmark for dummies>"
    printf 'Usage: %s [--ffmpeg_path <arg>] [--jobs <arg>] [--loops <arg>] [--(no-)debug] [-h|--help] \n' "$0"
    printf "\t%s\n" "--ffmpeg_path: <ffmpeg path> default: ${_arg_ffmpeg_path}"
    printf "\t%s\n" "--jobs: <no. of jobs in parallel> default: ${_arg_jobs}"
    printf "\t%s\n" "--loops: <no. of loops> default: ${_arg_loops}"
    printf "\t%s\n" "--debug,--no-debug: <debug arg> default: off"
    printf "\t%s\n" "-h,--help: Prints help"
}

function parse_commandline {
    while test $# -gt 0; do
        _key="$1"
        case "$_key" in
        --ffmpeg_path)
            test $# -lt 2 && die "Missing value for the optional argument '$_key'." 1
            _arg_ffmpeg_path="$2"
            shift
            ;;
        --ffmpeg_path=*)
            _arg_ffmpeg_path="${_key##--ffmpeg_path=}"
            ;;
        --jobs)
            test $# -lt 2 && die "Missing value for the optional argument '$_key'." 1
            _arg_jobs="$2"
            shift
            ;;
        --jobs=*)
            _arg_jobs="${_key##--jobs=}"
            ;;
        --loops)
            test $# -lt 2 && die "Missing value for the optional argument '$_key'." 1
            _arg_loops="$2"
            shift
            ;;
        --loops=*)
            _arg_loops="${_key##--loops=}"
            ;;
        --no-debug | --debug)
            _arg_debug="on"
            test "${1:0:5}" = "--no-" && _arg_debug="off"
            ;;
        -h | --help)
            print_help
            exit 0
            ;;
        -h*)
            print_help
            exit 0
            ;;
        *)
            print_help
            ;;
        esac
        shift
    done
}

parse_commandline "$@"

#echo
#echo "--ffmpeg_path is $_arg_ffmpeg_path"
#echo "--jobs is $_arg_jobs"
#echo "--loops is $_arg_loops"

check_bin ${_arg_ffmpeg_path}
export FFMPEG=${_arg_ffmpeg_path}
export MAX_JOBS=${_arg_jobs}
export MAX_LOOPS=${_arg_loops}
PARALLEL="${GNU_PARALLEL} --no-notice -n0 "

# raw YUV file with 300 frames as an input of the test

function execute {
    $@
    local status=$?
    if [ $status -ne 0 ]; then
        echo "error with $1" >&2
    fi
    return $status
}

# function _fetch_http {
#     local FILE=$1
#     local URL="SOMEURLHERE"
#     test $(execute curl --silent -o /tmp/${FILE}.gz  "${URL}/${FILE}.gz") && die "Failed to fetch  /tmp/${FILE}.gz" 1
#     test $(execute curl --silent -o /tmp/${FILE}.gz.sig "${URL}/${FILE}.gz.sig") && die "Failed to fetch /tmp/${FILE}.gz.sig" 1
# }

# function which runs ffmpeg
function run_ffmpeg {
    TS=$(date '+%s')
    echo -n "timestamp=$TS jobs=$MAX_JOBS  "

    # /usr/bin/chrt -r 10: 使用 chrt 命令以实时（-r）调度策略运行接下来的命令，并设置优先级为 10。实时调度策略可以确保进程获得更可预测的响应时间。
    # sudo  /usr/bin/chrt -r 10   ${FFMPEG} -v quiet -stats -benchmark \
    # ${FFMPEG} -v quiet -stats -benchmark \
    #     -f rawvideo \
    #     -pix_fmt yuv420p \
    #     -s:v 1920x1080  \
    #     -r 60 \
    #     -i /tmp/${YUV_FILE}  \
    #     -c:v libx264  \
    #     -an  -preset  veryslow \
    #     -b:v   5M \
    #     -maxrate 5M   \
    #     -bufsize 15M  \
    #     -threads 4 \
    #     -x264opts bframes=12:keyint=24:min-keyint=24:nal-hrd=cbr:force-cfr=1:bframes=8:no-scenecut \
    #     -f null - 2>&1 | awk '{print $3" "$4}'

    # /usr/bin/chrt -r 10: 使用 chrt 命令以实时（-r）调度策略运行接下来的命令，并设置优先级为 10。实时调度策略可以确保进程获得更可预测的响应时间。
    # sudo  /usr/bin/chrt -r 10   ${FFMPEG} -v quiet -stats -benchmark \
    ${FFMPEG} -i ${VIDEO_FILE} -c:v libx264 -preset veryslow -b:v 5M -maxrate 5M -bufsize 15M -threads 4 -x264opts bframes=12:keyint=24:min-keyint=24:nal-hrd=cbr:force-cfr=1:bframes=8:no-scenecut -f null - -benchmark -stats
}
export -f run_ffmpeg

# function which runs above ffmpeg into loop
function run_ffmpeg_loop {

    CNT=0
    while true; do
        test $STOP_LOOP -gt 0 && break
        # scaling_governor 文件用于控制 CPU 频率调度的策略。将其设置为 "performance" 意味着 CPU 将始终运行在最高频率，以获得最佳性能。
        # echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor >/dev/null 2>&1
        # seq $MAX_JOBS |  ${PARALLEL}   run_ffmpeg
        run_ffmpeg

        ((CNT++))

        test $CNT -gt ${MAX_LOOPS} && STOP_LOOP=1
        # echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor >/dev/null 2>&1
    done

}

# log stdout/stderr
exec > >(tee -ia ${BASH_SOURCE}-${DATE}.log)
exec 2> >(tee -ia ${BASH_SOURCE}-${DATE}.log >&2)

run_ffmpeg_loop

end_time=$(date +%s%3)
execution_time=$(expr $end_time - $start_time)

echo "Compile script executed in $execution_time milliseconds."