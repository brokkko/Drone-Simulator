./simulator-cli UDP model 3 lat 59.9921526 lon 30.2805271 enable-magnetometer 1 &

./Autopilot --sim-udp 127.0.0.1 5002 5000 --modem-tcp 127.0.0.1:8000 --camera --type 425 --root ./cache --plazlink-1v6 & #TODO: resolve like in test

wait


