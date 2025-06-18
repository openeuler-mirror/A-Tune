# Native-Turbo

## Overview

The code segment and data segment of a large program can reach hundreds of MB, and the TLB miss rate of key service processes is high. The size of the kernel page table affects the performance.

To facilitate the use of huge pages, the Native-Turbo feature enables the system to automatically use huge pages when loading programs. Huge pages can be used for code segments and data segments.

## How to Use

1. Enable the feature.

   This feature has two levels of switches. `sysctl fs.exec-use-hugetlb` determines whether to enable this feature in the system. (This command can only be run by the **root** user. The value `0` indicates that this feature is disabled, and the value `1` indicates that this feature is enabled. Other values are invalid.)

   If not enabled, this feature will not be used even if users set environment variables because the kernel will ignore related processes.

   After this feature is enabled, common users can use the environment variable `HUGEPAGE_PROBE` to determine whether to use huge pages for running programs. If the value is `1`, huge pages are used. If the value is not set, huge pages are not used.

   ```shell
   sysctl fs.exec-use-hugetlb=1 # The main program uses huge pages.
   export HUGEPAGE_PROBE=1 # The dynamic library uses huge pages.
   ```

   You can also configure the environment variable `LD_HUGEPAGE_LIB=1` to force all segments to use huge pages.

2. Mark the segments that need to use huge pages. By default, all segments are marked. `-x` only marks code segments. `-d` clears existing marks.

   ```shell
   hugepageedit [-x] [-d] app
   ```

   This tool is provided by the glibc-devel package.

3. Run the application.

   ./app

## Restrictions

1. The program and dynamic library must be compiled in 2 MB alignment mode by adding the following GCC compilation parameters:

   ```shell
   -zcommon-page-size=0x200000 -zmax-page-size=0x200000
   ```

2. Sufficient huge pages must be reserved before use. Otherwise, the program will fail to be executed.

   If the cgroup is used, pay attention to the `hugetlb` limit. If the limit is less than the number of required huge pages, the system may break down during running.
   
3. The size of the process page table is changed to 2 MB. Therefore, the parameters invoked by the system such as `mprotect` must be aligned by 2 MB. Otherwise, the execution will fail.

4. The LibcarePlus hot patch mechanism is not supported.

5. Huge pages cannot be shared among multiple processes because they will consume multiple times of memory.
