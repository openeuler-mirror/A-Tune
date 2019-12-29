#!/bin/bash
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
# Create: 2019-10-29

function perf_cpu () {
	
	if dmidecode -t processor | grep -q -E 'Kunpeng|Hisilicon' ; then
		L1DCA='r0004'
		L1DCM='r0003'
		L1ICA='r0014'
		L1ICM='r0001'

		L2DCA='r0016'
		L2DCM='r0017'
		L2ICA='r0027'
		L2ICM='r0028'

		LLCA='r0032'
		LLCM='r0033'

		ITLBA='r0002'
		ITLBM='r0026'

		DTLBA='r0005'
		DTLBM='r0025'

		Cycles='r0011'
		RetiredInsts='r0008'

		MemStallLoad='r7004'
		MemStallStore='r7005'
		FetchBubbles='r2014'
		DecodedInsts='r001b'
		MemStallL2Miss='r7007'
		
		StallBackend='r0024'

		#Events="-e $LLCA,$LLCM,$ITLBA,$ITLBM,$DTLBA,$DTLBM,$Cycles,$RetiredInsts,$MemStallLoad,$MemStallStore,$FetchBubbles,$DecodedInsts,$MemStallL2Miss"
		
		Events="-e $LLCA,$LLCM,$ITLBA,$ITLBM,$DTLBA,$DTLBM,$Cycles,$RetiredInsts,$StallBackend,$MemStallLoad,$MemStallStore"




	else
		echo "can not support cpu architecture..."
		exit
	fi

	let interval=$interval*1000
 
	timeout $ts perf stat -x ',' -a -I $interval $Events 2>&1 | \
	awk -F, '
	BEGIN {
		tpre=-1;
		first=1;
		pcount=0;
	}
	{
		tcurr=$1;

		if(first==1) {
			tpre=tcurr;
			first=0;
			printf("#######################################################Perf Info##############################################################################\n");
			#printf("  IPC	LLC  MPKI  ITLB  DTLB  Frount-End  Bad-Speculation  Retiring  Back-End  Memory_Bound  DRAM  Store\n");
			printf("  IPC	   MPKI	    LLC	     ITLB    DTLB	StallBackend/Insts StallBackend/cycles Memory_Bound  Store_Bound\n");
		}

		if(tcurr != tpre)
		{
			#printf("%1.3f %10.2f%% %10.2f %10.2f%% %10.2f%% %10.2f%% %10.2f%% %10.2f%% %10.2f%% %10.2f%% %10.2f%% %10.2f%%\n",insts/cycles,llcmiss/llcref*100,llcmiss/insts*1000, itlbmiss/itlbref*100,dtlbmiss/dtlbref*100,fetchbubbles/(4*cycles)*100,(decodedinsts-insts)/(4*cycles)*100,insts/(4*cycles)*100, (1-fetchbubbles/(4*cycles)-(decodedinsts-insts)/(4*cycles)-insts/(4*cycles))*100, (memstallload+memstallstore)/cycles*100, memstalll2miss/cycles*100, memstallstore/cycles*100);
			printf("%1.3f %10.2f %10.2f%% %10.2f%% %10.2f%% %10.2f %10.2f %10.2f%% %10.2f%%\n",insts/cycles,llcmiss/insts*1000,llcmiss/llcref*100,itlbmiss/itlbref*100,dtlbmiss/dtlbref*100,stallbackend/insts, stallbackend/cycles, (memstallload+memstallstore)/cycles*100,memstallstore/cycles*100);

			tpre=tcurr;
			pcount++;
		}

		switch ($4)
		{
			case "r0032":
				llcref=$2;
				break;
			case "r0033":
				llcmiss=$2;
				break;

			case "r0026":
				itlbref=$2;
				break;
			case "r0002":
				itlbmiss=$2;
				break;

			case "r0025":
				dtlbref=$2;
				break;
			case "r0005":
				dtlbmiss=$2;
				break;

			case "r0011":
				cycles=$2;
				break;
			case "r0008":
				insts=$2;
				break;
			case "r7004":
				memstallload=$2;
				break;
			case "r7005":
				memstallstore=$2;
				break;
			case "r2014":
				fetchbubbles=$2;
				break;
			case "r001b":
				decodedinsts=$2;
				break;
			case "r7007":
				memstalll2miss=$2;
				break;
			case "r0024":
				stallbackend=$2;
				break;
		}


	}
	'
}

if [ ! $# == 1 ]; then
        echo "Usage: perf_cpu.sh sample_interval"
        exit
fi

ts=0
interval=$1
perf_cpu
