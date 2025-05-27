from src.utils.shell_execute import SshClient

def apply_mysql_config(
    ssh_client,
    mysql_params: dict,
    cnf_path="/etc/my.cnf"
):
    # 逐个检查并修改每个参数
    for key, value in mysql_params.items():
        # 使用 sed 命令检查是否已经有该参数
        check_cmd = f"grep -q '^{key}\\s*=' {cnf_path}"
        result = ssh_client.run_cmd(check_cmd)

        if result.status_code == 0:
            # 如果存在，则使用 sed 修改该参数的值
            update_cmd = f"sed -i 's/^{key}\\s*=.*$/{key} = {value}/' {cnf_path}"
            print(f"更新 {key} 参数为 {value}")
        else:
            # 如果不存在，则在 [mysqld] 部分添加该参数
            add_cmd = f"sed -i '/\\[mysqld\\]/a {key} = {value}' {cnf_path}"
            print(f"添加 {key} 参数为 {value}")
        
        # 执行更新或添加命令
        ssh_client.run_cmd(update_cmd if result.status_code == 0 else add_cmd)

    # 重启 mysqld 服务
    print("🔄 已设置mysql参数，正在重启 mysqld ...")
    result = ssh_client.run_cmd("systemctl restart mysqld")
    exit_status = result.status_code

    for i in range(3):
        if exit_status == 0:
            print("✅ mysqld 重启成功")
            break
        else:
            if i == 2:
                error_msg = result.err_msg
                print(f"❌ mysqld 重启失败，正在重试{i + 1}/3")
                print("错误信息：", error_msg)
                print("日志信息：", result.output)


