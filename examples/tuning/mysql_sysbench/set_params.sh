params=$1
value=$2
MySQL_EXEC_PATH -uroot -p123456 << EOF
set GLOBAL $params = $2;
quit
EOF

sed -i "s/^$params=.*$/$params=$value/g" /etc/my.cnf
