#!/bin/bash
set -x

cd PATH
sh tpcc_benchmark.sh >> debug_tpcc1.log 2>&1 &
local=$!
sh remote_benchmark.sh >> debug_tpcc2.log 2>&1 &
remote=$!

wait $local
wait $remote