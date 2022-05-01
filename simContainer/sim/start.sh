#!/bin/sh
IP=$(ip addr show | grep "172" | awk '{print $2}' | cut -d '/' -f 1)
set -m
echo "Host ip is $IP"
./Autopilot --sim-udp 127.0.0.1 5002 5000 --modem-tcp "$IP:8000" --camera --type 425 --root ./cache --plazlink-1v6 & disown Autopilot & ./simulator-cli UDP model 3 lat "${LAT}" lon "${LON}" enable-magnetometer 1 & wait

