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
# Create: 2020-12-03

CONFIG_PATH=
SOURCE_DATA_PATH=$CONFIG_PATH/source_data.ini

cd $CONFIG_PATH
> $SOURCE_DATA_PATH

#############################################################
tikv_config__server__grpc_concurrency=5
echo "server__grpc-concurrency=${tikv_config__server__grpc_concurrency}" >> $SOURCE_DATA_PATH 
tikv_config__server__scheduler_worker_pool_size=4
echo "server__scheduler-worker-pool-size=${tikv_config__server__scheduler_worker_pool_size}" >> $SOURCE_DATA_PATH 
tikv_config__storage_block_cache__capacity=1
echo "storage.block-cache__capacity=\"${tikv_config__storage_block_cache__capacity}G\"" >> $SOURCE_DATA_PATH 
tikv_config__raftstore__region_max_size=256
echo "raftstore__region-max-size=\"${tikv_config__raftstore__region_max_size}MB\"" >> $SOURCE_DATA_PATH 
tikv_config__raftstore__store_pool_size=2
echo "raftstore__store-pool-size=${tikv_config__raftstore__store_pool_size}" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb_defaultcf__bloom_filter_bits_per_key=10
echo "rocksdb.defaultcf__bloom-filter-bits-per-key=${tikv_config__rocksdb_defaultcf__bloom_filter_bits_per_key}" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb_defaultcf__disable_auto_compactions=false
echo "rocksdb.defaultcf__disable-auto-compactions=${tikv_config__rocksdb_defaultcf__disable_auto_compactions}" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb_defaultcf__optimize_filters_for_hits=false
echo "rocksdb.defaultcf__optimize-filters-for-hits=${tikv_config__rocksdb_defaultcf__optimize_filters_for_hits}" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb_defaultcf__block_size=64
echo "rocksdb.defaultcf__block-size=\"${tikv_config__rocksdb_defaultcf__block_size}KB\"" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb_defaultcf__write_buffer_size=128
echo "rocksdb.defaultcf__write-buffer-size=\"${tikv_config__rocksdb_defaultcf__write_buffer_size}MB\"" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb_defaultcf__max_bytes_for_level_base=512
echo "rocksdb.defaultcf__max-bytes-for-level-base=\"${tikv_config__rocksdb_defaultcf__max_bytes_for_level_base}MB\"" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb_defaultcf__target_file_size_base=32
echo "rocksdb.defaultcf__target-file-size-base=\"${tikv_config__rocksdb_defaultcf__target_file_size_base}MB\"" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb_defaultcf__level0_slowdown_writes_trigger=20
echo "rocksdb.defaultcf__level0-slowdown-writes-trigger=${tikv_config__rocksdb_defaultcf__level0_slowdown_writes_trigger}" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb_defaultcf__level0_stop_writes_trigger=32
echo "rocksdb.defaultcf__level0-stop-writes-trigger=${tikv_config__rocksdb_defaultcf__level0_stop_writes_trigger}" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb_defaultcf__max_write_buffer_number=5
echo "rocksdb.defaultcf__max-write-buffer-number=${tikv_config__rocksdb_defaultcf__max_write_buffer_number}" >> $SOURCE_DATA_PATH 
echo "rocksdb.writecf__write-buffer-size=\"${tikv_config__rocksdb_defaultcf__write_buffer_size}MB\"" >> $SOURCE_DATA_PATH 
echo "rocksdb.writecf__max-bytes-for-level-base=\"${tikv_config__rocksdb_defaultcf__max_bytes_for_level_base}MB\"" >> $SOURCE_DATA_PATH 
echo "rocksdb.writecf__target-file-size-base=\"${tikv_config__rocksdb_defaultcf__target_file_size_base}MB\"" >> $SOURCE_DATA_PATH 
echo "raftdb.defaultcf__write-buffer-size=\"${tikv_config__rocksdb_defaultcf__write_buffer_size}MB\"" >> $SOURCE_DATA_PATH 
echo "raftdb.defaultcf__max-bytes-for-level-base=\"${tikv_config__rocksdb_defaultcf__max_bytes_for_level_base}MB\"" >> $SOURCE_DATA_PATH 
echo "raftdb.defaultcf__target-file-size-base=\"${tikv_config__rocksdb_defaultcf__target_file_size_base}MB\"" >> $SOURCE_DATA_PATH 
tikv_config__readpool_unified__max_thread_count=4
echo "readpool.unified__max-thread-count=${tikv_config__readpool_unified__max_thread_count}" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb__max_background_jobs=2
echo "rocksdb__max-background-jobs=${tikv_config__rocksdb__max_background_jobs}" >> $SOURCE_DATA_PATH 
tikv_config__rocksdb__max_sub_compactions=2
echo "rocksdb__max-sub-compactions=${tikv_config__rocksdb__max_sub_compactions}" >> $SOURCE_DATA_PATH 
echo "raftdb__max-background-jobs=${tikv_config__rocksdb__max_background_jobs}" >> $SOURCE_DATA_PATH 

python3 change_config.py -c tikv_config.toml -s $SOURCE_DATA_PATH

REMOTE_HOST=`cat auto_run.sh | grep ^DB_HOST= | awk -F'=' '{print $2}'`

scp tikv_config.toml root@$REMOTE_HOST:$CONFIG_PATH


cd ./
sh auto_run.sh &> /dev/null
cat result/last.log | grep -A14 "SQL statistics"
cd -
    
