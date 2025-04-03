#!/bin/bash
set -x
rm -rf debug_tpcc1.log
rm -rf debug_tpcc2.log

cd PATH
sh tpcc_benchmark.sh > debug_tpcc1.log 2>&1 &
local=$!
sh remote_benchmark.sh > debug_tpcc2.log 2>&1 &
remote=$!

wait $local
wait $remote