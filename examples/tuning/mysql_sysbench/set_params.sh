params=$1
value=$2
/usr/local/mysql/bin/mysql -uroot -p123456 << EOF
set GLOBAL $params = $2;
quit
EOF

sed -i "s/^$params=.*$/$params=$value/g" /etc/my.cnf