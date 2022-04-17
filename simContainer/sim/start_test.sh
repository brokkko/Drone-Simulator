./Autopilot --sim-udp 127.0.0.1 5002 5000 --modem-tcp 172.17.0.3:8000 --camera --type 425 --root ./cache --plazlink-1v6 & # TODO: resolve ip using bash

./simulator model 3 lat 59.9921526 lon 30.2805271 enable-magnetometer 1 udp-in-port 5002 udp-out-port 5000 &

wait