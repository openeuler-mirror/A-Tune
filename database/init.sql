drop table if exists class_apps;
CREATE TABLE IF NOT EXISTS class_apps(
  class TEXT PRIMARY KEY NOT NULL,
  apps TEXT,
  resource_limit TEXT,
  deletable BOOLEN NOT NULL
);


drop table if exists class_profile;
CREATE TABLE IF NOT EXISTS class_profile(
  class TEXT PRIMARY KEY NOT NULL,
  profile_type TEXT NOT NULL,
  active BOOLEN NOT NULL
);

drop table if exists tuned;
CREATE TABLE IF NOT EXISTS tuned(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  class TEXT NOT NULL,
  name TEXT NOT NULL,  
  type TEXT NOT NULL,
  value TEXT NOT NULL,
  range TEXT NOT NULL,
  step INTEGER,
  FOREIGN KEY(class) REFERENCES class_profile(class)
);


drop table if exists collection;
CREATE TABLE IF NOT EXISTS collection(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  name TEXT NOT NULL,
  module TEXT NOT NULL,  
  purpose TEXT NOT NULL,
  metrics TEXT NOT NULL
);


drop table if exists tuned_item;
CREATE TABLE IF NOT EXISTS tuned_item(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  property TEXT NOT NULL,
  item TEXT NOT NULL
);


drop table if exists rule_tuned;
CREATE TABLE IF NOT EXISTS rule_tuned(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  name TEXT NOT NULL,
  class TEXT NOT NULL,
  expression TEXT NOT NULL,
  action TEXT NOT NULL,
  opposite_action TEXT NOT NULL,
  monitor TEXT NOT NULL,
  field TEXT NOT NULL
);


drop table if exists profile_log;
CREATE TABLE IF NOT EXISTS profile_log(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  profile_id TEXT NOT NULL,
  context TEXT NOT NULL,
  backup_path TEXT NOT NULL,
  timestamp DATETIME NOT NULL
);


drop table if exists schedule;
CREATE TABLE IF NOT EXISTS schedule(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  type TEXT NOT NULL,
  strategy TEXT NOT NULL
);


-- class_apps:
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("encryption_AES", "encryption", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("encryption_MD5", "encryption", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("encryption_RSAPublic", "encryption", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("default", "default", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("ceph", "storage-ceph", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("hadoop_hdd", "big-data-hadoop-hdfs", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("hadoop_ssd", "big-data-hadoop-hdfs", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("spark", "big-data-hadoop-spark", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("mongodb", "database-mongodb", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("mariadb", "database-mariadb", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("mysql", "database-mysql", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("postgresql", "database-postgresql", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("nginx_https_long", "web-nginx", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("nginx_https_short", "web-nginx", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("nginx_http_long", "web-nginx", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("nginx_http_short", "web-nginx", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("apache", "web-apache-traffic-server", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("redis", "in-memory-database-redis", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("speccpu", "basic-test-suite-speccpu", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("specjbb", "basic-test-suite-specjbb", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("dubbo", "middleware-dubbo", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("robox", "arm-native-android-container", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("kvm", "cloud-compute-kvm", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("hpc", "hpc-gatk4", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("olc", "virtualization-consumer-cloud", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("mariadb_kvm", "virtualization-mariadb", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("mariadb_docker", "docker-mariadb", "", 0);

-- class_profile:
INSERT INTO class_profile(class, profile_type, active) VALUES("encryption_AES", "encryption-AES-chauffeur", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("encryption_MD5", "encryption-MD5-chauffeur", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("encryption_RSAPublic", "encryption-RSAPublic-chauffeur", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("default", "default-default", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("ceph", "storage-ceph-vdbench-hdd", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("hadoop_hdd", "big-data-hadoop-hdfs-dfsio-hdd", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("hadoop_ssd", "big-data-hadoop-hdfs-dfsio-ssd", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("spark", "big-data-hadoop-spark-kmeans", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("mongodb", "database-mongodb-2p-sysbench", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("mariadb", "database-mariadb-2p-tpcc-c3", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("mysql", "database-mysql-2p-sysbench-hdd", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("postgresql", "database-postgresql-2p-sysbench-hdd", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("nginx_https_short", "web-nginx-https-short-connection", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("nginx_https_long", "web-nginx-https-long-connection", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("nginx_http_short", "web-nginx-http-short-connection", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("nginx_http_long", "web-nginx-http-long-connection", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("apache", "web-apache-traffic-server-spirent-pingpo", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("redis", "in-memory-database-redis-redis-benchmark", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("speccpu", "basic-test-suite-speccpu-speccpu2006", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("specjbb", "basic-test-suite-specjbb-specjbb2015", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("dubbo", "middleware-dubbo-dubbo-benchmark", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("robox", "arm-native-android-container-robox", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("kvm", "cloud-compute-kvm-host", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("hpc", "hpc-gatk4-human-genome", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("olc", "virtualization-consumer-cloud-olc", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("mariadb_kvm", "virtualization-mariadb-2p-tpcc-c3", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("mariadb_docker", "docker-mariadb-2p-tpcc-c3", 0);

-- Performance Point
INSERT INTO tuned_item(property, item) VALUES("check_environment", "Check");

INSERT INTO tuned_item(property, item) VALUES("CONFIG_HZ", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_ARM64_64K_PAGES", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_NUMA_AWARE_SPINLOCKS", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_CGROUP_FILES", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_SLUB_DEBUG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_PM_DEBUG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_PM_SLEEP_DEBUG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_STACKPROTECTOR", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_STACKPROTECTOR_STRONG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_VMAP_STACK", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_BLK_DEBUG_FS", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_BLK_DEBUG_FS_ZONED", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_NET_DROP_MONITOR", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_DM_DEBUG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_MLX4_DEBUG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_VIDEO_ADV_DEBUG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_INFINIBAND_IPOIB_DEBUG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_NFS_DEBUG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_SUNRPC_DEBUG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_CIFS_DEBUG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_BINARY_PRINTF", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_DEBUG_INFO_DWARF4", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_DEBUG_MEMORY_INIT", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_SCHED_DEBUG", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_DEBUG_BUGVERBOSE", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_DEBUG_LIST", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_TRACEPOINTS", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_NOP_TRACER", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_TRACER_MAX_TRACE", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_TRACE_CLOCK", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_RING_BUFFER", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_EVENT_TRACING", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_CONTEXT_SWITCH_TRACER", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_TRACING", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_GENERIC_TRACER", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_FTRACE", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_FUNCTION_TRACER", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_FUNCTION_GRAPH_TRACER", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_SCHED_TRACER", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_HWLAT_TRACER", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_FTRACE_SYSCALLS", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_TRACER_SNAPSHOT", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_BRANCH_PROFILE_NONE", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_STACK_TRACER", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_BLK_DEV_IO_TRACE", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_KPROBE_EVENTS", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_UPROBE_EVENTS", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_BPF_EVENTS", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_PROBE_EVENTS", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_DYNAMIC_FTRACE", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_FTRACE_MCOUNT_RECORD", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_TRACING_MAP", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_HIST_TRIGGERS", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_RING_BUFFER_BENCHMARK", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_DEBUG_ALIGN_RODATA", "Kernel");

INSERT INTO tuned_item(property, item) VALUES("iommu.passthrough", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("iommu.strict", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("default_hugepagesz", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("hugepagesz", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("hugepages", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("selinux", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("skew_tick", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("numa_spinlock", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("scsi_mod.use_blk_mq", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("sched_steal_node_limit", "Bootloader");

INSERT INTO tuned_item(property, item) VALUES("openssl_hpre", "Script");
INSERT INTO tuned_item(property, item) VALUES("hinic", "Script");

INSERT INTO tuned_item(property, item) VALUES("NUMA", "Bios");
INSERT INTO tuned_item(property, item) VALUES("SRIOV", "Bios");
INSERT INTO tuned_item(property, item) VALUES("Custom Refresh Rate", "Bios");
INSERT INTO tuned_item(property, item) VALUES("Stream Write Mode", "Bios");
INSERT INTO tuned_item(property, item) VALUES("Support Smmu", "Bios");
INSERT INTO tuned_item(property, item) VALUES("Support SPCR", "Bios");
INSERT INTO tuned_item(property, item) VALUES("Max Payload Size", "Bios");
INSERT INTO tuned_item(property, item) VALUES("Power Policy", "Bios");
INSERT INTO tuned_item(property, item) VALUES("Rank Interleaving", "Bios");
INSERT INTO tuned_item(property, item) VALUES("Read Policy", "Bios");
INSERT INTO tuned_item(property, item) VALUES("Write Policy", "Bios");
INSERT INTO tuned_item(property, item) VALUES("I/O Policy", "Bios");
INSERT INTO tuned_item(property, item) VALUES("Access Policy", "Bios");
INSERT INTO tuned_item(property, item) VALUES("Drive Cache", "Bios");

INSERT INTO tuned_item(property, item) VALUES("vm.nr_hugepages", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.swappiness", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.dirty_ratio", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.max_map_count", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.panic_on_oom", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.dirty_background_ratio", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.dirty_writeback_centisecs", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.dirty_expire_centisecs", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.overcommit_memory", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.zone_reclaim_mode", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.min_free_kbytes", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel/mm/transparent_hugepage/defrag", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("kernel/mm/transparent_hugepage/enabled", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("kernel/debug/sched_features", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/scheduler", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/read_ahead_kb", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/nr_requests", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/device/queue_depth", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/write_cache", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/nomerges", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/iosched/slice_idle", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/iosched/low_latency", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/rq_affinity", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/max_sectors_kb", "Sysfs");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_max_syn_backlog", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.somaxconn", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_keepalive_time", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_keepalive_probes", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_keepalive_intvl", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_retries2", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.ip_forward", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.conf.default.rp_filter", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.conf.default.accept_source_route", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_tw_reuse", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_syncookies", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_low_latency", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_max", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_tcp_timeout_established", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.bridge.bridge-nf-call-ip6tables", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.bridge.bridge-nf-call-iptables", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.bridge.bridge-nf-call-arptables", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.ip_local_port_range", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_max_tw_buckets", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.netdev_max_backlog", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_max_orphans", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_timestamps", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_synack_retries", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_syn_retries", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_fin_timeout", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_mem", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_rmem", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_wmem", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.udp_mem", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_sack", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_fastopen", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.wmem_default", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.rmem_default", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.rmem_max", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.wmem_max", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_tcp_timeout_close_wait", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_tcp_timeout_fin_wait", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_tcp_timeout_time_wait", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.conf.default.forwarding", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_buckets", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_count", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.nf_conntrack_max", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.dev_weight", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.optmem_max", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.netdev_budget", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.busy_read", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.busy_poll", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("net.core.rps_sock_flow_entries", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("ethtool", "Script");
INSERT INTO tuned_item(property, item) VALUES("ifconfig", "Script");
INSERT INTO tuned_item(property, item) VALUES("fs.file-max", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("fs.nr_open", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("fs.suid_dumpable", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("fs.aio-max-nr", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("fs.inotify.max_user_instances", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.threads-max", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.sem", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.msgmnb", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.msgmax", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.shmmax", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.shmall", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.shmmni", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.pid_max", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.numa_balancing", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("{user}.hard.nofile", "Ulimit");
INSERT INTO tuned_item(property, item) VALUES("{user}.soft.nofile", "Ulimit");
INSERT INTO tuned_item(property, item) VALUES("{user}.soft.stack", "Ulimit");
INSERT INTO tuned_item(property, item) VALUES("{user}.hard.stack", "Ulimit");
INSERT INTO tuned_item(property, item) VALUES("{user}.soft.nproc", "Ulimit");
INSERT INTO tuned_item(property, item) VALUES("{user}.hard.nproc", "Ulimit");
INSERT INTO tuned_item(property, item) VALUES("{user}.soft.memlock", "Ulimit");
INSERT INTO tuned_item(property, item) VALUES("{user}.hard.memlock", "Ulimit");
INSERT INTO tuned_item(property, item) VALUES("swap", "Script");
INSERT INTO tuned_item(property, item) VALUES("kernel.randomize_va_space", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_cfs_bandwidth_slice_us", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_migration_cost_ns", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_latency_ns", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_nr_migrate", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_min_granularity_ns", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_wakeup_granularity_ns", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.sysrq", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.kstack_depth_to_print", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.panic_on_oops", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.panic", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.hung_task_timeout_secs", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.hung_task_panic", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.oom_dump_tasks", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.softlockup_panic", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.core_uses_pid", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.nmi_watchdog", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_rt_runtime_us", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("vm.stat_interval", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.timer_migration", "Sysctl");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_autogroup_enabled", "Sysctl");

INSERT INTO tuned_item(property, item) VALUES("prefetch", "Script");
INSERT INTO tuned_item(property, item) VALUES("logind", "Script");
INSERT INTO tuned_item(property, item) VALUES("blockdev", "Script");
INSERT INTO tuned_item(property, item) VALUES("hugepage", "Script");
INSERT INTO tuned_item(property, item) VALUES("rps_cpus", "Script");
INSERT INTO tuned_item(property, item) VALUES("sched_domain", "Script");
INSERT INTO tuned_item(property, item) VALUES("hdparm", "Script");

INSERT INTO tuned_item(property, item) VALUES("sysmonitor", "Systemctl");
INSERT INTO tuned_item(property, item) VALUES("irqbalance", "Systemctl");
INSERT INTO tuned_item(property, item) VALUES("firewalld", "Systemctl");
INSERT INTO tuned_item(property, item) VALUES("tuned", "Systemctl");

INSERT INTO tuned_item(property, item) VALUES("compile_optimization", "Compiler");
INSERT INTO tuned_item(property, item) VALUES("compile_security", "Compiler");

INSERT INTO tuned_item(property, item) VALUES("/etc/profile", "Profile");

-- collection table
INSERT INTO collection(name, module, purpose, metrics) VALUES("cpu", "CPU", "STAT", "--interval={interval}; --fields=usr --fields=nice --fields=sys --fields=iowait --fields=irq --fields=soft --fields=steal --fields=guest --threshold=30 --fields=util --fields=cutil");
INSERT INTO collection(name, module, purpose, metrics) VALUES("storage", "STORAGE", "STAT", "--interval={interval};--device={disk} --fields=rs --fields=ws --fields=rMBs --fields=wMBs --fields=rrqm --fields=wrqm --fields=rareq-sz --fields=wareq-sz --fields=r_await --fields=w_await --fields=util --fields=aqu-sz");
INSERT INTO collection(name, module, purpose, metrics) VALUES("network", "NET", "STAT", "--interval={interval};--nic={network} --fields=rxkBs --fields=txkBs --fields=rxpcks --fields=txpcks --fields=ifutil");
INSERT INTO collection(name, module, purpose, metrics) VALUES("network-err", "NET", "ESTAT", "--interval={interval};--nic={network} --fields=errs --fields=util");
INSERT INTO collection(name, module, purpose, metrics) VALUES("mem.band", "MEM", "BANDWIDTH", "--interval={interval};--fields=Total_Util");
INSERT INTO collection(name, module, purpose, metrics) VALUES("perf", "PERF", "STAT", "--interval={interval};--fields=IPC --fields=CACHE-MISS-RATIO --fields=MPKI --fields=ITLB-LOAD-MISS-RATIO --fields=DTLB-LOAD-MISS-RATIO --fields=SBPI --fields=SBPC");
INSERT INTO collection(name, module, purpose, metrics) VALUES("vmstat", "MEM", "VMSTAT", "--interval={interval};--fields=procs.b --fields=memory.swpd --fields=io.bo --fields=system.in --fields=system.cs --fields=util.swap --fields=util.cpu --fields=procs.r");
INSERT INTO collection(name, module, purpose, metrics) VALUES("sys.task", "SYS", "TASKS", "--interval={interval};--fields=procs --fields=cswchs");
INSERT INTO collection(name, module, purpose, metrics) VALUES("sys.ldavg", "SYS", "LDAVG", "--interval={interval};--fields=runq-sz --fields=plist-sz --fields=ldavg-1 --fields=ldavg-5");
INSERT INTO collection(name, module, purpose, metrics) VALUES("file.util", "SYS", "FDUTIL", "--interval={interval};--fields=fd-util");

-- Dynamic_tuned table
INSERT INTO rule_tuned(name, class, expression, action, opposite_action, monitor, field) VALUES("hpre", "webserver", "object in ('libssl', 'libcrypto')", "openssl_hpre=1", "openssl_hpre=0","PERF.TOP", ";--fields=overhead --fields=object --fields=symbol --addr-merge=0x3f");

-- AI search table
-- INSERT INTO tuned (class, name, type, value, range) VALUES("single_computer_intensive_jobs", "prefetech", "ENUM", "off", "on,off" );

-- Schedule table
INSERT INTO schedule (type, strategy) VALUES("all", "auto");
