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


drop table if exists profile;
CREATE TABLE IF NOT EXISTS profile(
  profile_type TEXT PRIMARY KEY NOT NULL,
  profile_information TEXT NOT NULL
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
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("default", "", "", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("webserver", "nginx,httpd", "cpu", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("big_database", "mongoDB,mysql,postgresql,mariadb", "cpu, memory, network, io", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("big_data", "hadoop, spark", "cpu, io", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("in-memory_computing", "specjbb2015", "cpu, memory", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("in-memory_database", "redis", "cpu, network", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("single_computer_intensive_jobs", "speccpu2006", "cpu, memory", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("communication", "dubbo", "cpu, network", 0);
INSERT INTO class_apps(class, apps, resource_limit, deletable) VALUES("idle", "idle", "", 0);

-- class_profile:
INSERT INTO class_profile(class, profile_type, active) VALUES("default", "default", 1);
INSERT INTO class_profile(class, profile_type, active) VALUES("webserver", "ssl_webserver", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("big_database", "database", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("big_data", "big_data", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("in-memory_computing", "in-memory_computing", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("in-memory_database", "in-memory_database", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("single_computer_intensive_jobs", "compute-intensive", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("communication", "rpc_communication", 0);
INSERT INTO class_profile(class, profile_type, active) VALUES("idle", "default", 0);



-- profile:
INSERT INTO profile (profile_type, profile_information) VALUES("default", "
#
# A-Tune configuration for others, which could not be classified
#
[main]
#TODO CONFIG

[kernel_config]
#TODO CONFIG

[bios]
#TODO CONFIG

[bootloader.grub2]
#TODO CONFIG

[sysfs]
#TODO CONFIG

[sysctl]
#TODO CONFIG

[systemctl]
#sysmonitor=stop
#irqbalance=stop

[tip]
#bind network interrupts to its affinity numa node = affinity

[script]
#TODO CONFIG

[ulimit]
#TODO CONFIG

[affinity.task]
#TODO CONFIG

[affinity.irq]
#TODO CONFIG

[check]
check_environment=on

");

INSERT INTO profile (profile_type, profile_information) VALUES("compute-intensive", "
#
# compute-intensive A-Tune configuration
#
[main]
#TODO CONFIG

[kernel_config]
CONFIG_HZ=100
CONFIG_ARM64_64K_PAGES=y

[bios]
Custom Refresh Rate=64ms
Stream Write Mode=Allocate share LLC

[bootloader.grub2]
default_hugepagesz=2M
hugepagesz=2M
hugepages=150000

[sysfs]
kernel/mm/transparent_hugepage/defrag=never
kernel/mm/transparent_hugepage/enabled=never

[sysctl]
kernel.randomize_va_space=0
#vm.nr_hugepages=150000

[tip]
bind task to corresponding cpu core = affinity
use optimized compile = compile

[script]
prefetch = on 

[ulimit]
#TODO CONFIG

[affinity.task]
#TODO CONFIG

[affinity.irq]
#TODO CONFIG

[check]
#TODO CONFIG

");

INSERT INTO profile (profile_type, profile_information) VALUES("io-intensive", "
#
# io-intensive A-Tune configuration
#
[main]
#TODO CONFIG

[kernel_config]
#TODO CONFIG

[bios]
#TODO CONFIG

[bootloader.grub2]
#TODO CONFIG

[sysfs]
block/{disk}/queue/read_ahead_kb=4096

[sysctl]
vm.dirty_ratio=40
vm.dirty_background_ratio=20
vm.dirty_writeback_centisecs=800
vm.dirty_expire_centisecs=30000

[script]
#TODO CONFIG

[tip]
mount your filesystem using noatime and nobarrier option = filesystem

[ulimit]
#TODO CONFIG

[affinity.task]
#TODO CONFIG

[affinity.irq]
#TODO CONFIG

[check]
#TODO CONFIG

");


INSERT INTO profile (profile_type, profile_information) VALUES("rpc_communication", "
#
# rpc_communication A-Tune configuration
#
[main]
include=throughput-performance

[bios]
Custom Refresh Rate=64ms
Power Policy = Performance

[kernel_config]
CONFIG_HZ=100

[bootloader.grub2]
default_hugepagesz=2M
hugepagesz=2M
hugepages=230000

[sysfs]
#TODO CONFIG

[sysctl]
kernel.sched_latency_ns = 16000000 
kernel.sched_min_granularity_ns = 3000000 
kernel.sched_migration_cost_ns = 1000

[systemctl]
sysmonitor=stop
irqbalance=stop

[script]
prefetch = off 
ethtool =  -K {network} gro on
ethtool =  -K {network} gso on
ethtool =  -K {network} tso on
ethtool =  -X {network} hfunc toeplitz
swap = -a off

[tip]
relogin into the system to enable limits setting = OS
bind your master process to the numa node that has the network card = affinity
bind network interrupts to its affinity numa node = affinity

[ulimit]
{user}.hard.stack = unlimited
{user}.soft.stack = unlimited
{user}.hard.nofile = 32768
{user}.soft.nofile = 32768

[affinity.task]
#TODO CONFIG

[affinity.irq]
#TODO CONFIG

[check]
#TODO CONFIG

");


INSERT INTO profile (profile_type, profile_information) VALUES("throughput-performance", "
#
# throughput-performance A-Tune configuration
#
[main]
#TODO CONFIG

[kernel_config]
#TODO CONFIG

[bios]
#TODO CONFIG

[bootloader.grub2]
#TODO CONFIG

[sysfs]
block/{disk}/queue/read_ahead_kb=4096

[sysctl]
kernel.sched_min_granularity_ns = 10000000
kernel.sched_wakeup_granularity_ns = 15000000

vm.dirty_ratio = 40
vm.dirty_background_ratio = 10
vm.swappiness=10

[tip]
#TODO CONFIG

[script]
#TODO CONFIG

[ulimit]
#TODO CONFIG

[affinity.task]
#TODO CONFIG

[affinity.irq]
#TODO CONFIG

[check]
#TODO CONFIG

");


INSERT INTO profile (profile_type, profile_information) VALUES("ssl_webserver", "
#
# webserver A-Tune configuration
#
[main]
#TODO CONFIG

[kernel_config]
#TODO CONFIG

[bios]
#TODO CONFIG

[sysfs]
#TODO CONFIG

[sysctl]
fs.file-max=6553600
fs.suid_dumpable = 1
fs.aio-max-nr = 1048576
kernel.shmmax = 68719476736
kernel.shmall = 4294967296
kernel.shmmni = 4096
kernel.sem = 250 32000 100 128
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_syncookies = 1
net.ipv4.ip_local_port_range = 1024     65500
net.ipv4.tcp_max_tw_buckets = 5000
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 262144
net.ipv4.tcp_max_orphans = 262144
net.ipv4.tcp_max_syn_backlog = 262144
net.ipv4.tcp_timestamps = 0
net.ipv4.tcp_synack_retries = 1
net.ipv4.tcp_syn_retries = 1
net.ipv4.tcp_fin_timeout = 1
net.ipv4.tcp_keepalive_time = 60
net.ipv4.tcp_mem =  362619      483495   725238
net.ipv4.tcp_rmem = 4096         87380   6291456
net.ipv4.tcp_wmem = 4096         16384   4194304
net.core.wmem_default = 8388608
net.core.rmem_default = 8388608
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216

[systemctl]
sysmonitor=stop
irqbalance=stop

[bootloader.grub2]
selinux=0
iommu.passthrough=1

[tip]
bind your master process to the CPU near the network = affinity
bind your network interrupt to the CPU that has this network = affinity
relogin into the system to enable limits setting = OS

[script]
openssl_hpre = 0
prefetch = off

[ulimit]
{user}.hard.nofile = 102400
{user}.soft.nofile = 102400

[affinity.task]
#TODO CONFIG

[affinity.irq]
#TODO CONFIG

[check]
#TODO CONFIG

");

INSERT INTO profile (profile_type, profile_information) VALUES("database", "
#
# database A-Tune configuration
#
[main]
#TODO CONFIG

[kernel_config]
#TODO CONFIG

[bios]
#TODO CONFIG

[tip]
use xfs as filesystem and mount-option using noatime and nobarrier = filesystem
bind network interrupts to its affinity numa node = affinity
relogin into the system to enable limits setting = OS

[bootloader.grub2]
iommu.passthrough=1

[sysctl]
vm.swappiness=1

# schedule
kernel.sched_cfs_bandwidth_slice_us=21000
kernel.sched_migration_cost_ns=1381000
kernel.sched_latency_ns=16110000
kernel.sched_min_granularity_ns=8250000
kernel.sched_nr_migrate=53
kernel.sched_wakeup_granularity_ns=50410000

# network core
net.core.rmem_default=21299200		
net.core.rmem_max=21299200		
net.core.wmem_default=21299200		
net.core.wmem_max=21299200		
net.ipv4.tcp_rmem=40960 8738000 62914560		
net.ipv4.tcp_wmem=40960 8738000 62914560		
net.core.dev_weight=97

# support more connections for mysql
net.ipv4.tcp_max_syn_backlog=20480	
net.core.somaxconn=1280	

[sysfs]
block/{disk}/queue/read_ahead_kb=32
block/{disk}/queue/scheduler=deadline
kernel/mm/transparent_hugepage/defrag=never
kernel/mm/transparent_hugepage/enabled=never

[systemctl]
sysmonitor=stop
irqbalance=stop

[script]
prefetch = off 

[ulimit]
{user}.hard.nofile = 102400
{user}.soft.nofile = 102400

[affinity.task]
#TODO CONFIG

[affinity.irq]
#TODO CONFIG

[check]
#TODO CONFIG

");

INSERT INTO profile (profile_type, profile_information) VALUES("big_data", "
#
# big_data A-Tune configuration
#
[main]
include=io-intensive

[kernel_config]
#TODO CONFIG

[bios]
#TODO CONFIG

[bootloader.grub2]
iommu.passthrough=1

[sysfs]
#TODO CONFIG

[systemctl]
firewalld=stop
sysmonitor=stop
irqbalance=stop

[tip]
bind network interrupts to its affinity numa node  = affinity
relogin into the system to enable limits setting = OS

[sysctl]
fs.file-max=1000000
fs.nr_open=2000000

[script]
#TODO CONFIG

[ulimit]
{user}.hard.nofile = 2000000
{user}.soft.nofile = 1800000

[affinity.task]
#TODO CONFIG

[affinity.irq]
#TODO CONFIG

[check]
#TODO CONFIG

");

INSERT INTO profile (profile_type, profile_information) VALUES("in-memory_computing", "
#
# in-memory_computing A-Tune configuration
#
[main]
include=throughput-performance

[kernel_config]
#TODO CONFIG

[bios]
Custom Refresh Rate=64ms
Power Policy = Performance

[bootloader.grub2]
default_hugepagesz=2M
hugepagesz=2M
hugepages=102400

[sysfs]
#TODO CONFIG

[sysctl]
#vm.nr_hugepages=102400

[script]
prefetch = off 

[tip]
use numactl to bind your task = affinity

[ulimit]
#TODO CONFIG

[affinity.task]
#TODO CONFIG

[affinity.irq]
#TODO CONFIG

[check]
#TODO CONFIG

");

INSERT INTO profile (profile_type, profile_information) VALUES("in-memory_database", "
#
# in-memory_database A-Tune configuration
#
[main]
include=throughput-performance

#[cpu]
#force_latency=70

[kernel_config]
#TODO CONFIG

[bios]
#TODO CONFIG

[bootloader.grub2]
iommu.passthrough=1

[sysctl]
vm.overcommit_memory=1
net.core.netdev_budget =600
net.core.rmem_max =16777216
net.core.somaxconn =2048
net.core.optmem_max =40960
net.core.rmem_default =65535
net.core.wmem_default =65535
net.core.wmem_max =8388608
net.ipv4.tcp_rmem =16384 349520 16777216
net.ipv4.tcp_wmem =16384 349520 16777216
net.ipv4.tcp_mem =8388608 8388608 8388608

kernel.sem = 32000 1024000000 500 32000
kernel.numa_balancing = 0

[sysfs]
kernel/mm/transparent_hugepage/defrag=never
kernel/mm/transparent_hugepage/enabled=never

[systemctl]
sysmonitor=stop
irqbalance=stop

[tip]
leverage numactl to make CPU to access its local memory = affinity
bind network interrupts to its affinity numa node = affinity

[script]
prefetch = off
ifconfig = {network} mtu 1500
ethtool = -C {network} adaptive-rx on
ethtool =  -K {network} gro on
ethtool =  -K {network} gso on
ethtool =  -K {network} tso on
#ethtool =  -K {network} lro on

[ulimit]
{user}.hard.nofile = 102400
{user}.soft.nofile = 102400

[affinity.task]
#TODO CONFIG

[affinity.irq]
#TODO CONFIG

[check]
#TODO CONFIG

");



-- Performance Point
INSERT INTO tuned_item(property, item) VALUES("check_environment", "Check");

INSERT INTO tuned_item(property, item) VALUES("CONFIG_HZ", "Kernel");
INSERT INTO tuned_item(property, item) VALUES("CONFIG_ARM64_64K_PAGES", "Kernel");

INSERT INTO tuned_item(property, item) VALUES("iommu.passthrough", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("default_hugepagesz", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("hugepagesz", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("hugepages", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("selinux", "Bootloader");
INSERT INTO tuned_item(property, item) VALUES("skew_tick", "Bootloader");

INSERT INTO tuned_item(property, item) VALUES("openssl_hpre", "Library");

INSERT INTO tuned_item(property, item) VALUES("Custom Refresh Rate", "BIOS");
INSERT INTO tuned_item(property, item) VALUES("Stream Write Mode", "BIOS");
INSERT INTO tuned_item(property, item) VALUES("Support Smmu", "BIOS");
INSERT INTO tuned_item(property, item) VALUES("Max Payload Size", "BIOS");
INSERT INTO tuned_item(property, item) VALUES("Power Policy", "BIOS");

INSERT INTO tuned_item(property, item) VALUES("vm.nr_hugepages", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.swappiness", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.dirty_ratio", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.max_map_count", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.panic_on_oom", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.dirty_background_ratio", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.dirty_writeback_centisecs", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.dirty_expire_centisecs", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.overcommit_memory", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.zone_reclaim_mode", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.min_free_kbytes", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.hugepages_treat_as_movable", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel/mm/transparent_hugepage/defrag", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel/mm/transparent_hugepage/enabled", "OS");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/scheduler", "OS");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/read_ahead_kb", "OS");
INSERT INTO tuned_item(property, item) VALUES("block/{disk}/queue/nr_requests", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_max_syn_backlog", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.core.somaxconn", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_keepalive_time", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_keepalive_probes", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_keepalive_intvl", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_retries2", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.ip_forward", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.conf.default.rp_filter", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.conf.default.accept_source_route", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_tw_recycle", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_tw_reuse", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_syncookies", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_max", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_tcp_timeout_established", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.bridge.bridge-nf-call-ip6tables", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.bridge.bridge-nf-call-iptables", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.bridge.bridge-nf-call-arptables", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.ip_local_port_range", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_max_tw_buckets", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.core.netdev_max_backlog", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_max_orphans", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_timestamps", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_synack_retries", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_syn_retries", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_fin_timeout", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_mem", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_rmem", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_wmem", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.udp_mem", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.tcp_fastopen", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.core.wmem_default", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.core.rmem_default", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.core.rmem_max", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.core.wmem_max", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_tcp_timeout_close_wait", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_tcp_timeout_fin_wait", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_tcp_timeout_time_wait", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.ipv4.conf.default.forwarding", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_buckets", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.netfilter.nf_conntrack_count", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.core.dev_weight", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.core.optmem_max", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.core.netdev_budget", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.core.busy_read", "OS");
INSERT INTO tuned_item(property, item) VALUES("net.core.busy_poll", "OS");
INSERT INTO tuned_item(property, item) VALUES("ethtool", "OS");
INSERT INTO tuned_item(property, item) VALUES("ifconfig", "OS");
INSERT INTO tuned_item(property, item) VALUES("fs.file-max", "OS");
INSERT INTO tuned_item(property, item) VALUES("fs.nr_open", "OS");
INSERT INTO tuned_item(property, item) VALUES("fs.suid_dumpable", "OS");
INSERT INTO tuned_item(property, item) VALUES("fs.aio-max-nr", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.threads-max", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.sem", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.msgmnb", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.msgmax", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.shmmax", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.shmall", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.shmmni", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.pid_max", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.numa_balancing", "OS");
INSERT INTO tuned_item(property, item) VALUES("{user}.hard.nofile", "OS");
INSERT INTO tuned_item(property, item) VALUES("{user}.soft.nofile", "OS");
INSERT INTO tuned_item(property, item) VALUES("{user}.soft.stack", "OS");
INSERT INTO tuned_item(property, item) VALUES("{user}.hard.stack", "OS");
INSERT INTO tuned_item(property, item) VALUES("swap", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.randomize_va_space", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_cfs_bandwidth_slice_us", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_migration_cost_ns", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_latency_ns", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_nr_migrate", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_min_granularity_ns", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_wakeup_granularity_ns", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.sysrq", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.kstack_depth_to_print", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.panic_on_oops", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.panic", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.hung_task_timeout_secs", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.hung_task_panic", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.oom_dump_tasks", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.softlockup_panic", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.core_uses_pid", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.nmi_watchdog", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.sched_rt_runtime_us", "OS");
INSERT INTO tuned_item(property, item) VALUES("vm.stat_interval", "OS");
INSERT INTO tuned_item(property, item) VALUES("kernel.timer_migration", "OS");

INSERT INTO tuned_item(property, item) VALUES("prefetch", "Chip");

INSERT INTO tuned_item(property, item) VALUES("sysmonitor", "Service");
INSERT INTO tuned_item(property, item) VALUES("irqbalance", "Service");
INSERT INTO tuned_item(property, item) VALUES("firewalld", "Service");

INSERT INTO tuned_item(property, item) VALUES("compile_optimization", "Compiler");
INSERT INTO tuned_item(property, item) VALUES("compile_security", "Compiler");

-- collection table
INSERT INTO collection(name, module, purpose, metrics) VALUES("cpu", "CPU", "STAT", "--interval=5; --fields=usr --fields=nice --fields=sys --fields=iowait --fields=irq --fields=soft --fields=steal --fields=guest --threshold=30 --fields=cutil"); 
INSERT INTO collection(name, module, purpose, metrics) VALUES("storage", "STORAGE", "STAT", "--interval=5;--device={disk} --fields=rs --fields=ws --fields=rMBs --fields=wMBs --fields=rrqm --fields=wrqm --fields=rareq-sz --fields=wareq-sz --fields=r_await --fields=w_await --fields=util --fields=aqu-sz"); 
INSERT INTO collection(name, module, purpose, metrics) VALUES("network", "NET", "STAT", "--interval=5;--nic={network} --fields=rxkBs --fields=txkBs --fields=rxpcks --fields=txpcks --fields=ifutil");
INSERT INTO collection(name, module, purpose, metrics) VALUES("network-err", "NET", "ESTAT", "--interval=5;--nic={network} --fields=errs --fields=util");
INSERT INTO collection(name, module, purpose, metrics) VALUES("mem.util", "MEM", "UTIL", "--interval=5;--fields=memused");
INSERT INTO collection(name, module, purpose, metrics) VALUES("mem.band", "MEM", "BANDWIDTH", "--interval=2;--fields=Total --fields=Total_Util");
INSERT INTO collection(name, module, purpose, metrics) VALUES("perf", "PERF", "STAT", "--interval=5;--fields=IPC --fields=CACHE-MISS-RATIO --fields=MPKI --fields=ITLB-LOAD-MISS-RATIO --fields=DTLB-LOAD-MISS-RATIO --fields=SBPI --fields=SBPC --fields=MEMORY-BOUND --fields=STORE-BOUND");
INSERT INTO collection(name, module, purpose, metrics) VALUES("vmstat", "MEM", "VMSTAT", "--interval=5;--fields=procs.b --fields=memory.swpd --fields=memory.free --fields=memory.buff --fields=memory.cache --fields=io.bi --fields=io.bo --fields=system.in --fields=system.cs --fields=util.swap --fields=util.cpu --fields=procs.r");
INSERT INTO collection(name, module, purpose, metrics) VALUES("sys.task", "SYS", "TASKS", "--interval=5;--fields=procs --fields=cswchs");
INSERT INTO collection(name, module, purpose, metrics) VALUES("sys.ldavg", "SYS", "LDAVG", "--interval=5;--fields=runq-sz --fields=plist-sz --fields=ldavg-1 --fields=ldavg-5 --fields=ldavg-15 --fields=task-util");
INSERT INTO collection(name, module, purpose, metrics) VALUES("file.util", "SYS", "FDUTIL", "--interval=5;--fields=fd-util");

-- Dynamic_tuned table
INSERT INTO rule_tuned(name, class, expression, action, opposite_action, monitor, field) VALUES("hpre", "webserver", "object in ('libssl', 'libcrypto')", "openssl_hpre=1", "openssl_hpre=0","PERF.TOP", ";--fields=overhead --fields=object --fields=symbol --addr-merge=0x3f");

-- AI search table
-- INSERT INTO tuned (class, name, type, value, range) VALUES("single_computer_intensive_jobs", "prefetech", "ENUM", "off", "on,off" );

-- Schedule table
INSERT INTO schedule (type, strategy) VALUES("all", "auto");
