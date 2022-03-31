#!/bin/bash
NIC=$(ip route | grep default | sed -e "s/^.*dev.//" -e "s/.proto.*//")
[ "$NIC" == "" ] && NIC=$(ip link | grep 'state UP' | awk -F': ' '$0 !~ "lo|^[^0-9]"{print $2}' | head -1)
DISK=$(lsblk -b | grep disk | sort -k 4 | head -1 | awk '{print $1}')
[ "$NIC" != "" ] && sed -i "s/^network = .*/network = $NIC/g" /etc/atuned/atuned.cnf
[ "$DISK" != "" ] && sed -i "s/^disk = .*/disk = $DISK/g" /etc/atuned/atuned.cnf

NIC=$(cat /etc/atuned/atuned.cnf | awk -F'=' '/^network =/{print $2}' | tr -d ' ')
DISK=$(cat /etc/atuned/atuned.cnf | awk -F'=' '/^disk =/{print $2}' | tr -d ' ')
echo "NIC *$NIC* is used as default network interface for data collection."
echo "DEV *$DISK* is used as default disk drive for data collection."
echo "modify /etc/atuned/atuned.cnf if wrong devices are used."
