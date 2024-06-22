# 基础包安装

declare -A ceph1_info=(
    ["ip"]="192.168.122.24"
    ["port"]=22
    ["username"]="root"
    ["password"]="Huawei12#$"
    ["hostname"]="ceph1"
)

declare -A ceph2_info=(
    ["ip"]="192.168.122.23"
    ["port"]=22
    ["username"]="root"
    ["password"]="Huawei12#$"
    ["hostname"]="ceph2"
)

declare -A ceph3_info=(
    ["ip"]="192.168.122.12"
    ["port"]=22
    ["username"]="root"
    ["password"]="Huawei12#$"
    ["hostname"]="ceph3"
)

function remote_sshpass() {
    echo "[remote_sshpass] $1"
    declare -n ref_dict=$1
    # echo "pw: ${ref_dict['password']}"
    command_str=$2
    # local escaped_cmd_str=$(echo "$command_str" | sed 's/"/\\"/g') # 转义双引号
    # escaped_command_str=$(printf '%q ' "$command_str") 
    echo "[CMD] command_str: ${command_str}"
    password=${ref_dict['password']}
    port=${ref_dict['port']}
    username=${ref_dict['username']}
    host_ip=${ref_dict['ip']}
    local com="sshpass -p '${ref_dict['password']}' ssh -p ${ref_dict['port']} ${ref_dict['username']}@${ref_dict['ip']} 'bash -s' <<< \"${command_str}\""
    echo "[INFO] [CMD] $com"
    eval $com
}


function remote_sshpass_shell() {
    echo "[remote_sshpass] $1"
    declare -n ref_dict=$1
    echo "pw: ${ref_dict['password']}"
    script=$2
    if [ ! -f ${script} ];then
        echo "[FATAL] ${script} do not exist"
        exit
    fi
    echo "[CMD] command_str: ${command_str}"
    password=${ref_dict['password']}
    port=${ref_dict['port']}
    username=${ref_dict['username']}
    host_ip=${ref_dict['ip']}
    local com="sshpass -p '${ref_dict['password']}' ssh -p ${ref_dict['port']} ${ref_dict['username']}@${ref_dict['ip']} < '${script}'"
    echo "[CMD] $com"
    eval $com
}

# 1.关闭防火墙和 selinux(或者关闭防火墙策略)
# main ceph
cmd="systemctl stop firewalld;
systemctl disable firewalld;
setenforce 0;
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config;
"

echo "[CEPH1] ${cmd}"
eval ${cmd}
declare -a dict_names=("ceph2_info" "ceph3_info")
for dict_name in ${dict_names[@]}; do
    echo "[INFO] current dict_name: ${dict_name}"
    remote_sshpass ${dict_name} "${cmd}"
done


# 2.安装ntpdata及epel仓库
# 添加时间同步定时任务，如果有内部时间服务器地址，建议配置为内部地址
cmd="
unset http_proxy;
unset https_proxy;
yum -y install ntpdate;
yum -y install expect;
yum -y install sshpass;
crontab -l;
/usr/sbin/ntpdate 172.19.1.63 >> /var/log/szntp01.log 2>&1;
"
echo "[CEPH1] ${cmd}"
eval ${cmd}
declare -a dict_names=("ceph2_info" "ceph3_info")
declare -a host_dict_names=("ceph1_info" "ceph2_info" "ceph3_info")
for dict_name in ${dict_names[@]}; do
    echo "[INFO] current dict_name: ${dict_name}"
    remote_sshpass ${dict_name} "${cmd}"
done
eval ${cmd}

tmpdir=`pwd`'/tmp.sh'
main_match_name="ceph1_info"
chmod a+x ${tmpdir}
# 3.配置hosts解析
echo "sed -i '/ceph/d' /etc/hosts" > ${tmpdir}
for dict_name in ${host_dict_names[@]}; do
    echo "[INFO] host current dict_name: ${dict_name}"
    declare -n ref_dict=$dict_name
    echo "echo \"${ref_dict['ip']} ${ref_dict['hostname']}\" >> /etc/hosts" >> ${tmpdir}
done
./tmp.sh

for dict_name in ${dict_names[@]}; do
    echo "[INFO] current dict_name: ${dict_name}"
    echo "sed -i '/ceph/d' /etc/hosts" > ${tmpdir}
    for dict_n in ${dict_names[@]};do
    # if [ "${dict_n}" != "${dict_name}" ];then
    declare -n dict_obj=${dict_n}
    echo "echo \"${dict_obj['ip']} ${dict_obj['hostname']}\" >> /etc/hosts" >> ${tmpdir} 
    # fi
    done
    declare -n ref_dict=${main_match_name}
    echo "echo \"${ref_dict['ip']} ${ref_dict['hostname']}\" >> /etc/hosts" >> ${tmpdir}
    remote_sshpass_shell ${dict_name} "tmp.sh"
done
# 4.添加用户并配置sudo权限
rsa_dir="~/.ssh/id_rsa"
rsa_dir_gen="/root/.ssh/id_rsa.pub"
echo 'if ! id cephadmin &>/dev/null; then
    useradd cephadmin
    echo "Huawei12#$"| passwd --stdin cephadmin
    echo "cephadmin ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/cephadmin
    chmod 0440 /etc/sudoers.d/cephadmin
else
    echo "User cephadmin already exists."
fi' > ${tmpdir}

chmod a+x tmp.sh
./tmp.sh
declare -a dict_names=("ceph2_info" "ceph3_info")
for dict_name in ${dict_names[@]}; do
    echo "[INFO] current dict_name: ${dict_name}"
    remote_sshpass_shell ${dict_name} "tmp.sh"
done
# --------------------------------------------------------------------------
echo "
su -cephadmin -c \"
if [ -f ${rsa_dir} ];then
    rm ${rsa_dir}
fi
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N \\\"\\\"
" > ${tmpdir}

for dict_name in ${dict_names[@]}; do
    declare -n ref_dict=${dict_name}
    echo "sshpass -p ${ref_dict['password']} ssh-copy-id -i ${rsa_dir_gen} -p ${ref_dict['port']} cephadmin@${ref_dict['ip']}" >> ${tmpdir}
done
echo "\"" >> ${tmpdir}
./tmp.sh
echo "Finished load in local tmp.sh cephadmin."


# for normal root
echo "
if [ -f ${rsa_dir} ];then
    rm ${rsa_dir}
fi
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N \\\"\\\"
" > ${tmpdir}

for dict_name in ${dict_names[@]}; do
    declare -n ref_dict=${dict_name}
    echo "sshpass -p ${ref_dict['password']} ssh-copy-id -i ${rsa_dir_gen} -p ${ref_dict['port']} cephadmin@${ref_dict['ip']}" >> ${tmpdir}
done
echo "\"" >> ${tmpdir}
./tmp.sh
echo "Finished load in local tmp.sh root."
# --------------------------------------------------------------------------
echo "[INFO] exec here ceph1_info"
for dict_name in ${dict_names[@]};do
    echo "[INFO] ----------------------------    current info is: ${dict_name}    -----------------------"
    echo "su -cephadmin -c \"                                      
if [ -f ${rsa_dir} ];then
    rm ${rsa_dir}
fi
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N \\\"\\\"
    " > ${tmpdir}
    new_dict=()
    for dict_n in ${dict_names[@]};
    do
        if [ "${dict_n}" != "${dict_name}" ];then
            echo "[DEBUG] dict_n vs dict_name, ${dict_n} vs ${dict_name}"
            declare -n ref_dict=${dict_n}
            echo "sshpass -p ${ref_dict['password']} ssh-copy-id -i ${rsa_dir_gen} -p ${ref_dict['port']} cephadmin@${ref_dict['ip']}" >> ${tmpdir}
        fi
    done
    declare -n ref_dict=${main_match_name}
    echo "sshpass -p ${ref_dict['password']} ssh-copy-id -i ${rsa_dir_gen} -p ${ref_dict['port']} cephadmin@${ref_dict['ip']}" >> ${tmpdir}
    echo "\"" >> ${tmpdir}
    cat "[INFO] cmd: \n :"` cat ${tmpdir}`
    echo "[INFO] current dict_name: ${dict_name}, tmp.sh: `cat ${tmpdir}`"
    echo "[INFO]"
    remote_sshpass_shell ${dict_name} "tmp.sh"
done

# remote_sshpass "ceph2_info" "./tmp.sh"
