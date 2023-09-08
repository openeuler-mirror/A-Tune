1. Prepare the environment
```bash
sh prepare.sh
```
if running failed, you may try to install mysql and sysbench manually according to following guide:
- Install MySQL according to the guide ([https://blog.csdn.net/weixin_43214408/article/details/116895091](https://blog.csdn.net/weixin_43214408/article/details/116895091))
- Install sysbench according to the guide ([https://blog.csdn.net/weixin_43214408/article/details/116898751](https://blog.csdn.net/weixin_43214408/article/details/116898751))

2. Start to tuning
```bash
atune-adm tuning --project mysql_sysbench --detail mysql_sysbench_client.yaml
```

3. Restore the environment
```bash
atune-adm tuning --restore --project mysql_sysbench
```
