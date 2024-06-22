1. Prepare the environment, and warehouses needs to be transmitted for the script
sh prepare.sh 25
2. Start to tuning
atune-adm tuning --project ceph --detail ceph_client.yaml
3. Restore the environment
atune-adm tuning --restore --project ceph
