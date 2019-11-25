#!/bin/bash

function perf_Mem_bw () {
	
	if dmidecode -t processor | grep -q -E 'Kunpeng|Hisilicon' ; then

		CPU0_Die0_BW_R="hisi_sccl1_ddrc0/flux_rd/,hisi_sccl1_ddrc1/flux_rd/,hisi_sccl1_ddrc2/flux_rd/,hisi_sccl1_ddrc3/flux_rd/"
		CPU0_Die0_BW_W="hisi_sccl1_ddrc0/flux_wr/,hisi_sccl1_ddrc1/flux_wr/,hisi_sccl1_ddrc2/flux_wr/,hisi_sccl1_ddrc3/flux_wr/"
		CPU0_Die1_BW_R="hisi_sccl3_ddrc0/flux_rd/,hisi_sccl3_ddrc1/flux_rd/,hisi_sccl3_ddrc2/flux_rd/,hisi_sccl3_ddrc3/flux_rd/"
		CPU0_Die1_BW_W="hisi_sccl3_ddrc0/flux_wr/,hisi_sccl3_ddrc1/flux_wr/,hisi_sccl3_ddrc2/flux_wr/,hisi_sccl3_ddrc3/flux_wr/"

		CPU1_Die0_BW_R="hisi_sccl5_ddrc0/flux_rd/,hisi_sccl5_ddrc1/flux_rd/,hisi_sccl5_ddrc2/flux_rd/,hisi_sccl5_ddrc3/flux_rd/"
		CPU1_Die0_BW_W="hisi_sccl5_ddrc0/flux_wr/,hisi_sccl5_ddrc1/flux_wr/,hisi_sccl5_ddrc2/flux_wr/,hisi_sccl5_ddrc3/flux_wr/"
		CPU1_Die1_BW_R="hisi_sccl7_ddrc0/flux_rd/,hisi_sccl7_ddrc1/flux_rd/,hisi_sccl7_ddrc2/flux_rd/,hisi_sccl7_ddrc3/flux_rd/"
		CPU1_Die1_BW_W="hisi_sccl7_ddrc0/flux_wr/,hisi_sccl7_ddrc1/flux_wr/,hisi_sccl7_ddrc2/flux_wr/,hisi_sccl7_ddrc3/flux_wr/"

		BW_Events=" $CPU0_Die0_BW_R,$CPU0_Die0_BW_W,$CPU0_Die1_BW_R,$CPU0_Die1_BW_W,$CPU1_Die0_BW_R,$CPU1_Die0_BW_W,$CPU1_Die1_BW_R,$CPU1_Die1_BW_W"
	else

		echo "not Support This CPU Architecture..."
		exit

	fi

	let interval=$interval*1000
 
	timeout $ts perf stat -x ',' -a -I $interval -e $BW_Events 2>&1 | \
	awk -F, '
		BEGIN {
			tpre=-1;
			first=1;
		}
		{
			tcurr=$1;
			if(first==1)
			{
				tpre=tcurr;
				first=0;
 			  printf("#################################Start to monitor The System DDR Bandwidth##################################################\n");
			  printf("  MEM_Total	CPU0  CPU1  CPU0_Die0  CPU0_Die1  CPU1_Die0  CPU1_Die1  MEM_CPU0_Die0_R  MEM_CPU0_Die1_R  MEM_CPU1_Die0_R  MEM_CPU1_Die1_R  MEM_CPU0_Die0_W  MEM_CPU0_Die1_W  MEM_CPU1_Die0_W  MEM_CPU1_Die1_W\n");
			}
							
			if(tcurr != tpre)
			{

				MEM_CPU0_Die0_R = CPU0_Die0_R*32/1024/1024;
				MEM_CPU0_Die1_R = CPU0_Die1_R*32/1024/1024;
				MEM_CPU1_Die0_R = CPU1_Die0_R*32/1024/1024;
				MEM_CPU1_Die1_R = CPU1_Die1_R*32/1024/1024;
				
				MEM_CPU0_Die0_W = CPU0_Die0_W*32/1024/1024;
				MEM_CPU0_Die1_W = CPU0_Die1_W*32/1024/1024;
				MEM_CPU1_Die0_W = CPU1_Die0_W*32/1024/1024;
				MEM_CPU1_Die1_W = CPU1_Die1_W*32/1024/1024;
				
				MEM_CPU0_Die0 = MEM_CPU0_Die0_R + MEM_CPU0_Die0_W;
				MEM_CPU0_Die1 = MEM_CPU0_Die1_R + MEM_CPU0_Die1_W;
				
				MEM_CPU1_Die0 = MEM_CPU1_Die0_R + MEM_CPU1_Die0_W;
				MEM_CPU1_Die1 = MEM_CPU1_Die1_R + MEM_CPU1_Die1_W;      
				
				MEM_CPU0 = MEM_CPU0_Die0_R + MEM_CPU0_Die0_W + MEM_CPU0_Die1_R + MEM_CPU0_Die1_W;
				MEM_CPU1 = MEM_CPU1_Die0_R + MEM_CPU1_Die0_W + MEM_CPU1_Die1_R + MEM_CPU1_Die1_W;
				
				MEM_Total = MEM_CPU0 + MEM_CPU1;
				
				printf("%10.2f %10.2f %10.2f %10.2f %10.2f %10.2f %10.2f %10.2f %10.2f %10.2f %10.2f %10.2f %10.2f %10.2f %10.2f\n",MEM_Total,MEM_CPU0,MEM_CPU1,MEM_CPU0_Die0,MEM_CPU0_Die1,MEM_CPU1_Die0,MEM_CPU1_Die1,MEM_CPU0_Die0_R,MEM_CPU0_Die1_R,MEM_CPU1_Die0_R,MEM_CPU1_Die1_R,MEM_CPU0_Die0_W,MEM_CPU0_Die1_W,MEM_CPU1_Die0_W,MEM_CPU1_Die1_W);
					             				
				CPU0_Die0_R=0;
				CPU0_Die0_W=0;
				CPU0_Die1_R=0;
				CPU0_Die1_W=0;
				CPU1_Die0_R=0;
				CPU1_Die0_W=0;
				CPU1_Die1_R=0;
				CPU1_Die1_W=0;

				tpre=tcurr;
		
			}

			switch ($4)
			{
				case /sccl1.*rd/:
					CPU0_Die0_R += $2;
					break;
				case /sccl1.*wr/:
					CPU0_Die0_W += $2;
					break;
				case /sccl3.*rd/:
					CPU0_Die1_R += $2;
					break;
				case /sccl3.*wr/:
					CPU0_Die1_W += $2;
					break;
				case /sccl5.*rd/:
					CPU1_Die0_R += $2;
					break;
				case /sccl5.*wr/:
					CPU1_Die0_W += $2;
					break;
				case /sccl7.*rd/:
					CPU1_Die1_R += $2;
					break;
				case /sccl7.*wr/:
					CPU1_Die1_W += $2;
					break;
			}

		}
	'

}


if [ ! $# == 1 ]; then
        echo "Usage: perf_mem.sh sample_interval"
        exit
fi


ts=0
interval=$1
perf_Mem_bw

