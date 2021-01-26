1.install openGauss reference to  https://opengauss.org/zh/docs/1.1.0/docs/installation/installation.html 
2.install benchmarksql-5.0 as benchmark
3. Prepare the environment
sh prepare.sh
4. Start to tuning
atune-adm tuning --project openGauss_tpcc --detail openGauss-client.yaml
3. Restore the environment
atune-adm tuning --restore --project openGauss_tpcc