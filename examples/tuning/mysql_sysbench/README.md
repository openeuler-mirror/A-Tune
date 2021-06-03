1. Install MySQL according to the guide ([https://blog.csdn.net/weixin_43214408/article/details/116895091](https://blog.csdn.net/weixin_43214408/article/details/116895091))
2. Install sysbench according to the guide ([https://blog.csdn.net/weixin_43214408/article/details/116898751](https://blog.csdn.net/weixin_43214408/article/details/116898751))
3. Prepare the environment
```bash
sh prepare.sh
```
4. Start to tuning
```bash
atune-adm tuning --project mysql_sysbench --detail mysql_sysbench_client.yaml
```
5. Restore the environment
```bash
atune-adm tuning --restore --project mysql_sysbench
```
