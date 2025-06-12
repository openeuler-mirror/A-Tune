# Common Issues and Solutions

## Issue 1: An error occurs when the  **train** command is used to train a model, and the message "training data failed" is displayed

Cause: Only one type of data is collected by using the  **collection**command.

Solution: Collect data of at least two data types for training.

## Issue 2: atune-adm cannot connect to the atuned service

Possible cause:

1. Check whether the atuned service is started and check the atuned listening address.

    ```shell
    systemctl status atuned
    netstat -nap | grep atuned
    ```

2. The firewall blocks the atuned listening port.
3. The HTTP proxy is configured in the system. As a result, the connection fails.

Solution: 

1. If the atuned service is not started, run the following command to start the service:

    ```shell
    systemctl start atuned
    ```

2. Run the following command on the atuned and atune-adm servers to allow the listening port to receive network packets. In the command,  **60001**  is the listening port number of the atuned server.

    ```shell
    iptables -I INPUT -p tcp --dport 60001 -j ACCEPT
    iptables -I INPUT -p tcp --sport 60001 -j ACCEPT
    ```

3. Run the following command to delete the HTTP proxy or disable the HTTP proxy for the listening IP address without affecting services:

    ```shell
    no_proxy=$no_proxy, Listening_IP_address
    ```

## Issue 3: The atuned service cannot be started, and the message "Job for atuned.service failed because a timeout was exceeded." is displayed

Cause: The hosts file does not contain the localhost information.

Solution: Add localhost to the line starting with  **127.0.0.1**  in the  **/etc/hosts**  file.

```text
127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4
```
